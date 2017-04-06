﻿# nlink3d 覚書

<div style="text-align:right;">
松永 裕介
</div>

## はじめに

このプログラムはDAシンポジウム2016アルゴリズムデザインコンテスト用に開発されたものである．
このドキュメントでは内部仕様や，現在の課題，将来の拡張予定などを書き留めておく．

## 問題のルール

W x H マスの長方形を D 枚重ねたものが盤面となる．
各々のマス目は
* 空
* 数字
* アルファベット(最大で２文字)
の内容を持つ．

同じ数字を持つマス目は必ず２つ存在する．同じアルファベットを持つマス目は同じX座標とY座標を持ち，
なおかつ，Z座標は連続していなければならない．

例)
 * (1, 1, 1) (1, 1, 2) (1, 1, 3) が同じアルファベットを持つのはOK
 * (2, 3, 1) (2, 3, 3) は (2, 3, 2) が抜けているのでNG
 * (4, 4, 1) (4, 5, 2) はY座標が異なるのでNG

このパズルの目的は対となった数字のマスの間を結ぶ経路を求めることである．
経路は1つのマスに1本だけ引くことができる．
1つのマス目上で２本の経路が交わることはできない．
要するに，空のマス目に数字を埋めていき，同じ数字のマス目を辿って相方のマス目まで到達できればよい．

アルファベットのマス目は層の異なる長方形間を移動するために用いられる．
例えば1番の数字のマス目の一つが1層目にあり，もう一つのマス目が２層にあるときには，
１層目と２層目をつなぐアルファベットのマス目を用いて経路を作る必要がある．
以降，このアルファベットのマス目(の集合)をビアと呼ぶことにする．

一つの経路に対して用いることのできるビアは高々１つである．
よって，もともと２つのマス目が異なる層に配置されている数字の数と使用されるビアの数は等しい．
ADC2016 では未使用のビアはないことになっている．


## SATソルバを用いた解法

### グラフ問題としての定式化

まず，問題をより数学的に定義するためにグラフ理論の言葉で再定義する．
一つの層を格子グラフと考える．格子グラフは節点が格子状にならんだグラフで
上下左右の節点間に枝がある．ここでは枝の向きは考えない．
節点はマス目と同様に，
* 自由節点(空)
* 終端節点(数字)
* ビア節点(アルファベット)
の3種類からなる．

1つの層からなる問題の場合，ビアは存在しないので単純に同じ数字の終端節点を結ぶ素な経路を求める問題となる．
複数の層からなる問題の場合，まず各数字とビアの割り当てを行う．
すると個々の層ごとに独立した問題となるのでそれを個々に解けばよいことになる．
もっともこのやり方では多層にまたがる線分数の階乗に比例した割り当て方があるので
実用的ではない．

### SAT問題へのエンコーディング(単層)

まず単層問題を考える．
最終結果は各接点が何番の経路として使われるか(あるいは使われないか)，
ということであるが，そうすると場合の数は (線分数)^(節点数) となり莫大な
探索空間となる．
答が素な経路であることに着目して，経路として用いられる枝の集合で答を表すことを
考える．
この場合，探索空間は 2^(枝数) となる．
今までの経験上，このエンコーディングがもっともシンプルかつ効率的と思われる．

ただし，これだけでは同じ数字同士が一つで経路で結ばれていることを表すのが難しいので
補助的に各節点が何番の経路として用いられているかを表す変数を導入する．
つまり，結局は最初と同じことになる．
さらに，この線分番号を表すやり方が通常の２進符号方式とone-hot符号方式の２通りが
考えられる．明らかに線分数が多いときにはone-hot方式は不利であるが，
制約が簡潔に書けるという利点がある．
現在はone-hot方式のほうが有利のように思われる．

### 多層問題への拡張

考え方としては前述のように，まずビアと線分の割り当てを考え，
各層ごとの配線問題に落としたあとで個別に解く．
実際には個々の割り当てを明示的に列挙するのは効率が悪いので，
割り当てを表す変数を用意してその変数の割り当てまで含めて一気にSATで解く．
単純には線分とビアの組み合わせに対して１つの論理変数を用意し，
線分iとビアjが結ばれる時1になるようにすれば良い．
実際には，層の関係で決して使われることのない線分とビアの関係があるので，
実装は少し複雑になる．
まず，層Aと層Bにまたがる線分の場合，使えるビアは層Aから層Bまでを含んでいなければならない．
また，各々の層に対して，対応する終端とビアの間が結線可能でなければならない．
もちろん，これは他の配線の影響は無視したうえでの結線可能性である．

もう一つ重要なのが線分番号のエンコーディングである．
一つの線分は複数の層にまたがる場合でもたかだか２つの層にしか現れない．
そのため，すべての層においてすべての線分を同時に扱うことはないので層ごとに
使われる線分番号に改めてラベルを振ったほうがコンパクトに表せる．
そこで，各層ごとに使われている線分のリストをつくり，層ごとにことなったラベル
を割り振るようにする．
すこし注意が必要なのがスルービアで，その上下の層に終端とつながったビアがあるが，
自分自身はどことも接続しないビアにはラベルを振らないようにする．


### ２進符号方式の詳細

２進符号方式の場合には一つのノードにつき log2(ラベル数 + 1) ビットの変数を用意する．
経路に用いられない場合には 0 のラベル値を使う．
枝 e で隣接している２つのノード n1 と n2 のラベルに関する制約は以下の通りである．
* e が選ばれているとき n1 と n2 のラベルは等しい．
* e が選ばれていない時 n1 と n2 のラベルは等しくないか，ともに 0 である．
2つのラベルが等しい時は各ビットごとに独立に e -> n1 = n2 のCNF式を作ればよい．
問題は２番めの条件で，まず，各ビットごとに等しくない時に1となる変数を作る．
その論理和が全体としての n1 != n2 となる．
さらに，全ビットが０の条件が必要となるので，
各ノードに対して1ビットの変数を予め用意しておいてラベル値が 0 の時に1となる
ように制約を追加する．こうすることでこのゼロ変数を参照するだけで判断できる．
ただ，現時点では後述の one-hot 方式のほうが効率的のようである．

### one-hot 方式の詳細

one-hot 方式の場合には一つのノードにつきラベル数の変数を用意する．
大まかには one-hot と呼んでいるが，実際には all-0 の場合もある．
隣接するノード間の制約は２進符号方式とほぼ同様であるが，より簡単になる．
具体的には
* e -> n1 = n2 これは各ビット独立
* e' -> n1 != n2 これも各ビットごとに e' -> n1' or n2'だけでOK
となる．
ラベル数が多くなると変数の数が増える欠点があるが，
扱える範囲内であればこちらの方式のほうが効率がよい．


### 性能改善のためのヒューリスティック

上のエンコーディングを用いてCNF式を作りSATソルバで解いてもそこそこのものができるが，
実はあまりうまくは行かない．そこでいくつかのヒューリスティックが提案されている．

#### 全マス使用制約

これはオリジナルのナンバーリンク問題が課している暗黙の制約みたいなもので，
すべてのマスがいずれかの経路に用いられると言う制約である．
ナンバーリンクのルールにはそんなことは一言も書いていないし，
アルゴリズムデザインコンテストでは意図的に全マスを使用しない問題が出されている
ので，この制約を加えて問題を解くと本当は答があるのに答なしという誤った解を出すことに
なるが，実際に全マスを使う問題に対しては圧倒的なスピードアップとなる．
最初にこの制約付きでトライしてみてUNSATの時に次のヒューリスティックを試すのが
効果的である．

#### L字制約

L字型に折れ曲がることのできるマス目を制約することで探索空間を狭めるヒューリスティックである．
例えば，下方向と右方向のL字を考えると，そのマスでL字に折れ曲がることができるのは
そのマスから右下へ45度進んでいった先に終端(あるいはビア)がある時のみ，という制約である．
その心は，そうしないとどこかにすき間が生じることになるから，ということである．
つまり上の全マス使用制約を考えたときには自動的にこのL字制約は考慮されたことになっている．

ただし，この制約はきつすぎるので，L字の水平と垂直方向の先に終端(あるいはビア)がある時も
そこで曲がって良い，とする緩和が考えられる．

現在の実装ではさらに外周部では折れ曲がりを常に許可している．

#### Y字制約

これは説明が難しいが，下図のような状態で，枝Aと枝Bが共に選ばれていた時，

~~~
       |
 o --- o --- o
 |     |     |
 A     |     B
 |     |     |
 o --- x --- o
       |
       C
       |
~~~

枝Cも選ばれるという制約である．ただし，x は終端やビアではない．
これも完全な制約ではなくこの制約を満たさない解もあるので探索空間を狭めるヒューリスティックである．
全マス使用制約はこの制約も含んでいる．


#### U字制約

コの字とも言う．

~~~
 o --- o
 |     |
 |     |
 o --- o
~~~

の３辺の枝は同時に使われないという制約である．これはほぼ完全な制約で，
この制約を満たさない解は存在するが，その場合，残りの１辺のみを使った制約充足解も
必ず存在するので入れておいて損はない制約である．


#### W字制約

~~~
 o -B- o -C- o
 |     |     |
 A           D
 |     |     |
 o --- x --- o
~~~

の形で，x が終端やビアでないときには A, B, C, D が同時に選ばれないという制約である．
これもほぼ完全な制約なので常に入れておく．


### 戦略

以下の順に試す．
* 全マス制約 + U字制約 + W字制約
* L字制約 + Y字制約 + U字制約 + W字制約
* L字制約 + U字制約 + W字制約
* Y字制約 + U字制約 + W字制約
* U字制約 + W字制約

だいたいUNSATの場合には数秒でわかるのできつい制約から先に試す．

## 現状

ADC2015, ADC2016 のテストスートに対する現状を以下に示す．

~~~
        plan-A plan-11 plan-10 plan-01 plan-C
2015-01      0
2015-02      0
2015-03      0
2015-04      0
2015-05      0
2015-06
2015-07              0
2015-08                                     0
2015-09              0
2015-10      0
2015-11              ?
2015-12      0
2015-13      0
2015-14      0
2015-15      0
2015-16      0
2015-17                                     0
2015-18      0
2015-19      0
2015-20                              ?
2015-21                      ?
2015-22      0
2015-23      0
2015-24      0
2015-25      0
2015-26      0
2015-27              0
2015-28      0
2015-29                              0
2015-30      0
2015-31      0
2015-32
2015-33      0
2015-34      0
2015-35      0
2015-36      0
2016-01              ?
2016-02              ?
2016-03
2016-04              ?
2016-05              ?
2016-06      0
2016-07      0
2016-08      0
2016-09 ERROR!
2016-10             5s
2016-11                                       1m20s
2016-12            25s
2016-13              0
2016-14            25s
2016-15              ?
2016-16              ?
2016-17      0
2016-18      0
2016-19              ?
2016-20      0
2016-21              ?
2016-22              ?
2016-23                      ?
2016-24      0
2016-25                      ?
2016-26              ?
2016-27      0
2016-28      0
2016-29              ?
2016-30
2016-31                      ?
~~~

現状５分以内に解けないのは
2015-06
2015-32
2016-03
2036-30
の４つ