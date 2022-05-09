# Wikipediaのデータベース・ダンプから読み仮名を抽出する

## 使い方
[Wikipedia:データベースダウンロード - Wikipedia](https://ja.wikipedia.org/wiki/Wikipedia:%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89)のリンク先からjawiki-latest-abstract.xml.gzをダウンロードし、解凍する。

wikipedia_yomi.pyで抽出する。
抽出された言葉は規格化されていないので、normalize.pyにかけて言葉リストにする。

```
python wikipedia_yomi.py jawiki-latest-abstract.xml > wp.dat
python ../normalize.py wp.dat > ../list/wikipedia.txt
```
