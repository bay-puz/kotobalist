# -*- coding: utf-8 -*-
import argparse
import json
import re
from sys import stderr


def gen_dict(words: list) -> dict:
    len_dict = {}
    for pos, word in enumerate(words):
        word_l = len(word)
        if word_l in len_dict:
            len_dict[word_l]["count"] += 1
        else:
            len_dict[word_l] = {"length": word_l, "start": pos, "count": 1}
    return len_dict


def load_list(file: str) -> list:
    with open(file, 'r') as fin:
        return fin.read().splitlines()


def main():
    parser = argparse.ArgumentParser(description='言葉リストのインデックスを作る')
    parser.add_argument('list', type=str, nargs='+', help='言葉リスト')
    args = parser.parse_args()

    index_dict = {}
    for file in args.list:
        file_name = re.sub(r'(.*/|\..*)', '', file)
        print(f'index {file_name}', file=stderr)
        words = load_list(file)
        words_d = gen_dict(words)
        index_dict[file_name] = words_d

    print(json.dumps(index_dict))
    return


if __name__ == '__main__':
    main()
