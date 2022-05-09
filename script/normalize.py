# -*- coding: utf-8 -*-
import argparse


def load(file_name: str, key_pos: int = -1, is_ime: bool = False) -> list:
    if is_ime:
        return load_ime(file_name)

    with open(file_name) as file:
        splits = file.read().splitlines()
        if key_pos < 0:
            return splits
        words = []
        for line_split in splits:
            words.append(line_split.split()[key_pos])
        return words


def load_ime(file_name: str) -> list:
    with open(file_name) as file:
        ime = file.read().splitlines()
        words = []
        for line in ime:
            if len(line) == 0 or line[0] == '#':
                continue
            word = line.split()[0]
            words.append(word)
        return words


def kata_to_hira(word: str) -> str:
    hira_word = ''
    for char in word:
        if ord("ァ") <= ord(char) <= ord("ヶ"):
            hira_word += chr(ord(char) - 96)
        else:
            hira_word += char
    return hira_word


def convert_hira(word: str) -> str:
    word = kata_to_hira(word)

    def _convert_v(char: str, char_next: str) -> (str, str):
        if char != 'ゔ':
            return char, char_next
        str_a = 'ぁぃぇぉ'
        str_y = 'ゃゅょ'
        str_b = 'ばびべぼ'
        if len(char_next) == 0 or char_next not in str_a + str_y:
            return 'ぶ', char_next
        if char_next in str_a:
            return str_b[str_a.index(char_next)], ''
        return 'び', char_next

    def _dakuon(char: str):
        str_sei = 'かきくけこさしすせそたちつてとはひふへほう'
        str_daku = 'がぎぐげござじずぜぞだぢづでどばびぶべぼゔ'
        if char not in str_sei:
            return char
        return str_daku[str_sei.index(char)]

    def _convert_odoriji(char_pre: str, char: str) -> (str, str):
        odoriji = 'ゝヽゞヾ'
        if len(char) == 0 or char not in odoriji:
            return char_pre, char
        if char in odoriji[:2]:
            return char_pre, char_pre
        return char_pre, _dakuon(char_pre)

    def _convert_suteji(char: str) -> str:
        str_before = "ぁぃぅぇぉゕゖっゃゅょゎゐゑ〜"
        str_after = "あいうえおかけつやゆよわいえー"
        if char in str_before:
            return str_after[str_before.index(char)]
        return char

    def _remove_garbage(char: str) -> str:
        all_kana = 'あいうえおかきくけこさしすせそたちつてとなにぬねの'
        all_kana += 'はひふへほまみむめもやゆよらりるれろわをんー'
        all_kana += 'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ'
        if char in all_kana:
            return char
        return ''

    word_l = list(word)
    i = 0
    while i < len(word_l):
        char = word_l[i]
        char_next = '' if i + 1 >= len(word_l) else word_l[i+1]
        char, char_next = _convert_v(char, char_next)
        char, char_next = _convert_odoriji(char, char_next)
        word_l[i] = char
        if i + 1 < len(word_l):
            if len(char_next) == 0:
                word_l.pop(i+1)
                i -= 1
            else:
                word_l[i+1] = char_next
        i += 1

    converted = ''
    for char in word_l:
        converted += _remove_garbage(_convert_suteji(char))

    return converted


def sort_len(words: list) -> list:
    return sorted(sorted(set(words)), key=len)


def main():
    parser = argparse.ArgumentParser(description='言葉リストを正規化する')
    parser.add_argument('file', type=str, help='入力ファイル')
    parser.add_argument('--ime', action='store_true', help='IMEファイルを変換')
    parser.add_argument('-k', '--key', type=int, default=0, help='位置を指定')
    args = parser.parse_args()

    loads = load(args.file, args.key - 1, args.ime)

    words = []
    for word in loads:
        words.append(convert_hira(word))

    words = sort_len(words)
    for word in words:
        if len(word) < 2:
            continue
        print(word)


if __name__ == '__main__':
    main()
