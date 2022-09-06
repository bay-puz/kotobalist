# スクリプト

言葉リストを作るためのスクリプトを置く。

## normalize.py

言葉のリストを変形・正規化する。

入力ファイルに対して、文字の変換、重複の削除、並び替えなどを行い標準出力に書き出す。
タブ区切りでかな表記以外の項目も書いてあるファイルの場合は、`-k KEY`で何番目の項目を取り出すかを指定できる。
IME用のファイルのときは、`--ime`を付けると読み仮名だけを抽出して正規化する。

```
python normalize.py kotoba.list > kotoba.txt
```

## wikipedia_yomi.py

Wikipediaのデータベース・ダンプから読み仮名を抽出する。

### 使い方

[Wikipedia:データベースダウンロード - Wikipedia](https://ja.wikipedia.org/wiki/Wikipedia:%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89)のリンク先からjawiki-latest-abstract.xml.gzをダウンロードし、解凍する。

wikipedia_yomi.pyで抽出する。
抽出された言葉は規格化されていないので、normalize.pyにかけて言葉リストにする。

```
wget https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-abstract.xml.gz
gzip -d jawiki-latest-abstract.xml.gz
python wikipedia_yomi.py jawiki-latest-abstract.xml > wp.dat
python normalize.py wp.dat > ../list/wikipedia.txt
```
