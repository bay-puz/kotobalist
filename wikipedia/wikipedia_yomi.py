# -*- coding: utf-8 -*-
import argparse
import re
from sys import stderr
from bs4 import BeautifulSoup


# 項目名・読み仮名に使われるかな文字
KANA_PATTERN = '[ぁ-ヿ 　＝、，,。〜~！？!?⁉‼⁈★☆♡♪♂♀-]'


def is_kana(char: str) -> bool:
    return re.fullmatch(KANA_PATTERN, char)


def is_kana_word(word: str) -> bool:
    for char in word:
        if not is_kana(char):
            return False
    return True


def is_worthful(word: str) -> bool:
    """
    言葉として適しているどうかを判定する
    - 空白またはかな1文字はFalse
    - 一覧、年代、日付はFalse
    """
    if len(word) < 1 or is_kana(word):
        return False

    denied_patterns = ['.+一覧', '.+年表', '.+順リスト']
    denied_patterns += ['[0-9]+月[0-9]+日', '[0-9]+年']
    denied_patterns += ['[0-9]+年代', '(紀元前)?[0-9]+(世|千年)紀']
    for pat in denied_patterns:
        if re.fullmatch(pat, word):
            return False

    return True


def trim_title(word: str) -> str:
    """
    titleタグから余分な文字を削る
    - 先頭の"Wikipedia: "を削る
    - " (曖昧さ回避)"のように括弧があれば削る
    """
    title_prefix = 'Wikipedia: '
    word = word.replace(title_prefix, '')

    trim_pattern = '[ 　]?[（(].+[）)]'
    searched = re.search(trim_pattern, word)
    if searched:
        word = word[:searched.start()]
    return word


def get_yomi_by_yomigana(abst: str) -> str:
    """
    abstractタグにTemplateの"よみがな"が入ることがあるのでそれを取り出す
    """
    yomigana_prefix = re.escape("|よみがな = ")
    yomigana_pattern = yomigana_prefix + KANA_PATTERN + '+'
    if re.fullmatch(yomigana_pattern, abst):
        return re.sub(yomigana_prefix, '', abst)

    return ''


def get_yomi_by_parenthesis(abst: str, title: str) -> str:
    """
    abstractの冒頭に"項目名（読み仮名）"と書かれるのでそれを取り出す
    - "項目名（こうもくめい）では、〜"といったabstractの場合は、
    　項目名が語ではないことが多いので除外する
    - 読み仮名と閉じ括弧のあいだに"、"などで区切られた別の語がある場合は削る
        - ただし、項目名にその区切りの記号が含まれる場合は削らない
    """
    abst = abst.replace(' ', '').replace('　', '')
    abst = abst.replace('(', '（').replace(')', '）')

    deha_pattern = '）((一覧)?(の記事)?では|の一覧)'
    searched = re.search(deha_pattern, abst)
    if searched:
        if re.search('）', abst).start() == searched.start():
            return ''

    yomi_pattern = '[「『]?' + re.escape(title) + '[」』]?' + '（' + KANA_PATTERN + '+' + '）'
    searched = re.match(yomi_pattern, abst)
    if searched is None:
        return ''

    yomi = searched.group(0)
    yomi = yomi.replace(title, '')
    yomi = re.sub('[『』「」（）]', '', yomi)

    all_delimitors = '([、，,・]|もしくは|または)'
    delimitors = ['、', '，', ',', '・', 'もしくは', 'または']
    if re.search(all_delimitors, yomi):
        for delimitor in delimitors:
            if re.search(delimitor, title):
                continue
            searched = re.search(delimitor, yomi)
            if searched:
                yomi = yomi[:searched.start()]
                continue

    return yomi


def get_yomi(abst: str, title: str) -> str:
    yomi = get_yomi_by_yomigana(abst)
    if len(yomi) > 0:
        return yomi

    return get_yomi_by_parenthesis(abst, title)


def parse_title(xml_line: str) -> str:
    soup = BeautifulSoup(xml_line, 'lxml-xml')

    title = soup.find('title')
    if title is None or len(title.contents) == 0:
        return ''

    return trim_title(title.contents[0])


def find_title(xml_line: str) -> str:
    if not re.match('<title>', xml_line):
        return ''

    title = parse_title(xml_line)
    if len(title) > 0 and is_worthful(title):
        return title
    return ''


def parse_abstract(xml_line: str, title: str) -> (bool, str):
    soup = BeautifulSoup(xml_line, 'lxml-xml')

    abst = soup.find('abstract')
    if not abst or len(abst.contents) == 0:
        return False, ''

    return True, get_yomi(abst.contents[0], title)


def find_yomi(xml_line: str, latest_title: str) -> str:
    if len(latest_title) < 1:
        return ''
    if not re.match('<abstract>', xml_line):
        return ''

    is_parsed, yomi = parse_abstract(xml_line, latest_title)
    if is_parsed:
        if is_worthful(yomi) and is_kana_word(yomi):
            return yomi
    return ''


def load_xml(file_name: str) -> int:
    word_n = 0
    latest_title = ''
    with open(file_name) as file:
        for line in file:
            if not re.match("<(title|abstract)>", line):
                continue
            title = find_title(line)
            if len(title) > 0:
                if is_kana_word(title):
                    print(title)
                    word_n += 1
                else:
                    latest_title = title
                continue

            yomi = find_yomi(line, latest_title)
            if len(yomi) > 0:
                print(yomi)
                word_n += 1
    return word_n


def main():
    parser = argparse.ArgumentParser(
        description='Wikipediaのデータベース・ダンプから項目名の読み仮名を抽出し表示する')
    parser.add_argument('xml', type=str, help='ダンプファイル (xml)')
    args = parser.parse_args()

    count_word = load_xml(args.xml)
    print(count_word, file=stderr)


if __name__ == '__main__':
    main()
