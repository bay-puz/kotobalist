# list

言葉のリストを置く。

リストは、他の人やプロジェクトが集めた言葉を加工しているため、それぞれにライセンスがある。

## buta.txt
本家（第12版）の配布場所は[豚辞書の詳細情報 : Vector ソフトを探す！](https://www.vector.co.jp/soft/dl/dos/game/se018509.html)だが、より新しい第14版を[【非公式】豚辞書 第14版【再頒布】](https://kinosei.ml/2015/02/11/%E3%80%90%E9%9D%9E%E5%85%AC%E5%BC%8F%E3%80%91%E8%B1%9A%E8%BE%9E%E6%9B%B8-%E7%AC%AC14%E7%89%88%E3%80%90%E5%86%8D%E9%A0%92%E5%B8%83%E3%80%91/)で再配布している。
ここでは第14版を使う。

### ライセンスについて
豚辞書のアーカイブ(butah014)を再配布し、butah014/buta014.dicを変形したリスト(buta.txt)を公開する。
利用する場合は、豚辞書の利用条件(butah0144/permit.doc)に従うこと。

permit.docに、「当アーカイブ・ファイルの内容に一切の変更を加えず、オリジナルのまま」であれば自由に再配布して良く、また、引用・抽出などしたデータ集を公開する場合は「結果として出来上がったデータ集の付属ドキュメントに当豚辞書から｛引用、参照、抜出、抽出、改造、‥‥｝した旨の記載」をするように書いてあるため。

### 作成方法
```
python ../script/normalize.py butah014/buta014.dic > buta.txt
```

## wikipedia.txt
[Wikipedia:データベースダウンロード](https://ja.wikipedia.org/wiki/Wikipedia:%E3%83%87%E3%83%BC%E3%82%BF%E3%83%99%E3%83%BC%E3%82%B9%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89)

### ライセンスについて
wikipedia.txtはCC-BY-SAで公開する。
元データであるWikipediaのライセンスがCC-BY-SAであるため。

### 作成方法
[wikipedia/README](wikipedia/README.md) を参考。


## nico-pixiv.txt
[ncaq/dic-nico-intersection-pixiv](https://github.com/ncaq/dic-nico-intersection-pixiv)を加工したもの。

### ライセンスについて
nico-pixiv.txtには著作権を主張しない。
元データ(dic-nico-intersection-pixiv.txt)の公開者が著作権を主張しないと宣言しているため。

> 生成物はスクレイピング結果を利用している都合上、 著作権は主張しません。
> https://github.com/ncaq/dic-nico-intersection-pixiv#%E3%83%A9%E3%82%A4%E3%82%BB%E3%83%B3%E3%82%B9

### 作成方法
```
wget https://cdn.ncaq.net/dic-nico-intersection-pixiv.txt
python ../script/normalize.py dic-nico-intersection-pixiv.txt --ime  > nico-pixiv.txt
```


## yojijukugo.txt
[漢字四文字言葉集](http://nikolist.jpn.org/puzzle/kanjinuke/)を加工したもの。

### ライセンスについて
yojijukugo.txt は[CC BY-NC-SA 2.1 JP](https://creativecommons.org/licenses/by-nc-sa/2.1/jp/)に準拠する。
元データがこのライセンスに準拠しているため。

> プログラムのソースなどはクリエイティブコモンズの帰属・非営利・同一条件配布に準拠。
> http://nikolist.jpn.org/index.html

### 作成方法
```
wget http://nikolist.jpn.org/puzzle/kanjinuke/yojijukugo.txt -o yoji.txt
nkf --overwrite -w yoji.txt
python3 normalize.py -k2 yoji.txt > yojijukugo.txt
```