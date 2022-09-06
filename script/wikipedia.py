# -*- coding: utf-8 -*-
import argparse
import bz2
import re
from bs4 import BeautifulSoup
from sys import stderr
from typing import Tuple


def is_kana(char: str) -> bool:
    """
    ひらがな・カタカナ・記号であればTrue
    """
    kana_pattern = '[ぁ-ヿ 　＝、，,。〜~！？!?⁉‼⁈★☆♡♪♂♀-]'
    return re.fullmatch(kana_pattern, char)


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
    denied_patterns += [r'Category:.+', r'Wikipedia:.+', r'プロジェクト:.+', r'ファイル:.+']
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


def get_yomigana_in_template(abst: str) -> Tuple[bool, str]:
    """
    Templateの"よみがな"から読み仮名を取り出す
    """
    comp = re.compile(r'^\|[ 　]*よみがな[ 　]*=[ 　]*(.+)$')
    s = comp.search(abst)
    if s is None:
       return False, ''
    yomigana = s.group(1)
    if not is_kana_word(yomigana):
        return False, ''

    return True, yomigana


def get_yomi_by_parenthesis(body: str, title: str) -> Tuple[bool, str]:
    """
    本文冒頭に"項目名（読み仮名）"と書かれていることが多いのでそれを取り出す
    - "項目名（こうもくめい）では、〜"といったabstractの場合は、
        項目名が語ではないことが多いので除外する
    - 読み仮名と閉じ括弧のあいだに"、"などで区切られた別の語がある場合は削る
        - ただし、項目名にその区切りの記号が含まれる場合は削らない
    """
    body = body.replace(' ', '').replace('　', '')
    body = body.replace('(', '（').replace(')', '）')

    comp_deha = re.compile(r'）((一覧)?(の記事)?では|の一覧)')
    search_deha = comp_deha.search(body)
    if search_deha is not None:
        return False, ''

    comp = re.compile('\'\'\'[「『]?{}[」』]?\'\'\'（(.*?)）'.format(title))
    searched = comp.search(body)
    if searched is None:
        return False, ''

    yomi = searched.group(1)

    comp_delimitor = re.compile(r'([、，,・]|もしくは|または)')
    delimitors = ['、', '，', ',', '・', 'もしくは', 'または']
    if comp_delimitor.search(yomi):
        for delimitor in delimitors:
            if re.search(delimitor, title):
                continue
            searched = re.search(delimitor, yomi)
            if searched:
                yomi = yomi[:searched.start()]
                continue

    return True, yomi


def get_yomi(title: str, body: str) -> Tuple[bool, str]:
    title = trim_title(title)
    if not is_worthful_title(title):
        return False, ''

    if is_kana_word(title):
        return True, title

    is_ok, yomi = get_yomigana_in_template(body)
    if is_ok:
        return True, yomi

    is_ok, yomi = get_yomi_by_parenthesis(body, title)
    if is_ok:
        return True, yomi
    
    return False, ''


def load_file(file_name: str) -> list:
    blocks = []
    with open(file_name, 'rb') as file:
        pos = 711
        next_pos = 928215
        file.seek(pos)
        blocks.append(file.read(next_pos - pos))

    return blocks


def read_xml(block: str) -> list:
    xml = bz2.decompress(block).decode(encoding="utf-8")
    soup = BeautifulSoup("<root>" + xml + "</root>", 'xml')

    text_list = soup.find_all("text")
    title_list = soup.find_all("title")

    yomi_list = []
    for i, t in enumerate(title_list):
        title = str(t.string)
        body = str(text_list[i].string)
        is_ok, yomi = get_yomi(title, body)
        if is_ok:
            yomi_list.append(yomi)
    return yomi_list


def main():
    parser = argparse.ArgumentParser(description="Wikipediaのデータベース・ダンプから項目名の読み仮名を抽出し表示する")
    parser.add_argument('file', type=str, help='ダンプファイル (xml.bz2)')
    args = parser.parse_args()
    
    blocks = load_file(args.file)
    for block in blocks:
        yomi_list = read_xml(block)
        print(len(yomi_list), file=stderr)
        for y in yomi_list:
            print(y)


if __name__ == '__main__':
    main()