# -*- coding: utf-8 -*-
import argparse
import bz2
import re
from bs4 import BeautifulSoup
from sys import stderr
from typing import Tuple

DEBUG = True
DEBUG_LEN = 10
KANA = '[ぁ-ヿ 　＝、，,。〜~！？!?⁉‼⁈★☆♡♪♂♀-]'

def is_kana(char: str) -> bool:
    """
    ひらがな・カタカナ・記号であればTrue
    """
    return re.fullmatch(KANA, char)


def is_kana_word(word: str) -> bool:
    for char in word:
        if not is_kana(char):
            return False
    return True


def is_worthful_title(word: str) -> bool:
    """
    見出しが言葉として適しているどうかを判定する
    - 空白またはかな1文字はFalse
    - 一覧、年代、日付はFalse
    - カテゴリーなどはFalse
    """
    if len(word) < 1 or is_kana(word):
        return False

    denied_patterns = [r'.+一覧', r'.+年表', r'.+順リスト']
    denied_patterns += [r'[0-9]+月[0-9]+日', r'[0-9]+年']
    denied_patterns += [r'[0-9]+年代', r'(紀元前)?[0-9]+(世|千年)紀']
    categories = ['Category', 'Wikipedia','Help', 'Template', 'Portal', 'プロジェクト', 'ファイル']
    for cat in categories:
        denied_patterns.append(cat + r':.+')

    for pat in denied_patterns:
        if re.fullmatch(pat, word):
            return False
    return True


def trim_title(word: str) -> str:
    """
    titleタグから余分な文字を削る
    - " (曖昧さ回避)"のように括弧があれば削る
    """
    trim_pattern = r'[ 　]?[（\(].+[）\)]'
    return re.sub(trim_pattern, '', word)


def get_yomigana_in_template(body: str, title: str) -> Tuple[bool, str]:
    """
    Templateの"よみがな"などから読み仮名を取り出す
    """
    body = body.replace(' ', '').replace('　', '')
    regexs = [r'^\|(?:よみがな|nativename)=(.+)$', r'^\|name=\{\{ruby\|.+?\|(.+?)(\}\}|\|)']
    comp_count = 0
    for regex in regexs:
        comp = re.compile(regex, re.MULTILINE)
        comp_count += 1
        searched = comp.search(body)
        if searched is None:
            continue
        yomigana = searched.group(1)
        if is_kana_word(yomigana):
            if DEBUG:
                print(f'template(comp={comp_count}): {title} -> {yomigana}', file=stderr)
            return True, yomigana
    return False, ''



def get_yomigana_in_meta(body: str, title: str) -> Tuple[bool, str]:
    """
    '{{読み仮名|'''漢字'''|ふりがな|...}}'という書式から読み仮名を取り出す
    """
    comp = re.compile(r'\{\{読み仮名.*?\|\'\'\'' + re.escape(title) + r'\'\'\'\|(.+?)(\}\}|\|)')
    searched = comp.search(body)
    if searched is None:
       return False, ''
    yomigana = searched.group(1)
    if not is_kana_word(yomigana):
        return False, ''
    if DEBUG:
        print(f'meta: {title} -> {yomigana}', file=stderr)
    return True, yomigana


def get_yomi_by_parenthesis(body: str, title: str) -> Tuple[bool, str]:
    """
    本文冒頭に"項目名（読み仮名）"と書かれていることが多いのでそれを取り出す
    - "項目名（こうもくめい）では、〜"といった文章の場合は、
        項目名が語ではないことが多いので除外する
    - 読み仮名と閉じ括弧のあいだに"、"などで区切られた別の語がある場合は削る
        - ただし、項目名にその区切りの記号が含まれる場合は削らない
    """

    escaped = re.escape(title)
    comp_count = 1
    comp = re.compile(r'\'\'\'' + escaped + r'\'\'\'（' + f'({KANA}+)' + r'）(.+)')
    comp_detail = re.compile(r'[「『]?\'\'\'[「『]?' + escaped + r'[」』]?\'\'\'[」』]?(?:<ref.+?>)?（\'*' + f'({KANA}+)' + r'\'*.*?）(.*)')
 
    searched = comp.search(body)
    if searched is None:
        searched = comp_detail.search(body)
        comp_count += 1
        if searched is None:
            return False, 'no parenthesis'

    after = searched.group(2)
    if after is not None:
        comp_deha = re.compile(r'((一覧)?(の記事)?では|の一覧)')
        searched_deha = comp_deha.match(after)
        if searched_deha is not None:
            return False, 'there is deha'

    yomi = searched.group(1)

    comp_delimitor = re.compile(r'([、，,・]|もしくは|または)')
    delimitors = ['、', '，', ',', '・', 'もしくは', 'または']
    if comp_delimitor.search(yomi):
        for delimitor in delimitors:
            if re.search(delimitor, title):
                continue
            searched_d = re.search(delimitor, yomi)
            if searched_d:
                yomi = yomi[:searched_d.start()]
                continue
    if DEBUG:
        print(f'parenthesis(comp={comp_count}): {title} -> {yomi}', file=stderr)
    return True, yomi


def get_yomi(title: str, body: str) -> bool:
    title = trim_title(title)
    if not is_worthful_title(title):
        print(f"not worthful: {title}", file=stderr)
        return False

    if is_kana_word(title):
        print(title)
        print(f"kana-word {title}", file=stderr)
        return True

    is_ok, yomi = get_yomigana_in_template(body, title)
    if is_ok:
        print(yomi)
        return True

    is_ok, yomi = get_yomigana_in_meta(body, title)
    if is_ok:
        print(yomi)
        return True

    def _reduce(text: str) -> str:
        text = text.replace(' ', '').replace('　', '')
        text = text.replace('(', '（').replace(')', '）')
        comp_metadata = re.compile(r'\{\{.+?\}\}')
        comp_metadata_lines = re.compile(r'\{\{.+?\}\}', re.DOTALL)
        comp_template = re.compile(r'^\|.+?$', re.MULTILINE)
        text = comp_metadata.sub('', text)
        text = comp_metadata_lines.sub('', text)
        text = comp_template.sub('', text)
        return text

    is_ok, yomi = get_yomi_by_parenthesis(_reduce(body), title)
    if is_ok:
        print(yomi)
        return True

    if DEBUG:
        print(f"failed({yomi}): {title}", file=stderr)            
    return False


def load_index(file_name: str) -> list:
    with open(file_name) as file:
        pos_list = []
        for line in file:
            splits = line.split(":")
            pos = int(splits[0])
            if pos in pos_list:
                continue
            pos_list.append(pos)

            if DEBUG:
                if len(pos_list) > DEBUG_LEN:
                    return pos_list
        return pos_list


def load_file(file_name: str, index_list: list) -> list:
    blocks = []
    with open(file_name, 'rb') as file:
        for i in range(0, len(index_list)):
            offset = index_list[i]
            file.seek(offset)
            if i + 1 < len(index_list):
                block_len = index_list[i+1] - offset
                blocks.append(file.read(block_len))
            else: 
                if not DEBUG:
                    blocks.append(file.read())
    return blocks


def read_xml(block: str) -> int:
    xml = bz2.decompress(block).decode(encoding="utf-8")
    soup = BeautifulSoup("<root>" + xml + "</root>", 'xml')

    text_list = soup.find_all("text")
    title_list = soup.find_all("title")

    count = 0
    for i, t in enumerate(title_list):
        title = str(t.string)
        body = str(text_list[i].string)
        if get_yomi(title, body):
            count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description="Wikipediaのデータベース・ダンプから項目名の読み仮名を抽出し表示する")
    parser.add_argument('file', type=str, help='ダンプファイル (jawiki-latest-pages-articles-multistream.xml.bz2)')
    parser.add_argument('index', type=str, help='インデックスファイル (jawiki-latest-pages-articles-multistream-index.txt)')
    args = parser.parse_args()

    index_list = load_index(args.index)
    print(f'pages: {len(index_list)}*100', file=stderr)

    blocks = load_file(args.file, index_list)
    sum = 0
    for block in blocks:
        count = read_xml(block)
        if DEBUG:
            print(f'word = {count}', file=stderr)
        sum += count
    print(f'sum: {sum}', file=stderr)

    return 


if __name__ == '__main__':
    main()