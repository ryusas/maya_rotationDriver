# maya_rotationDriver
ボーンのオイラー角回転を、ボーン方向を元にした「捻り／縦方向の曲げ／横方向の曲げ」という独立した三つの角度に分解・合成するMayaプラグインのPython実装の簡単なサンプルです。

##この手法について
この手法を用いると、関節がどの方向にどれくらい曲がったか捻られたかによって、別の何かを駆動させることが的確に出来ます。もし、オイラー角回転を用いてそれをやろうとすると以下のような障害があります。

* 一つの姿勢を表す値の組み合わせが無数に存在する為、それに基づくドリブン構造を作りにくい（同じ姿勢でも別の結果が導出されることもある）。
* 個々の軸回転が捻りや曲げを表すわけではない（X軸方向に伸びた骨の捻りがオイラー角のX軸回転とは限らない）。
* rotateOrder 指定に基き縦方向の回転と横方向の回転にも順番があり、平等な扱いではない。

オイラー角回転のデメリットがそのままこの手法のメリットです。
この手法では、分解のノードと共に合成のノードもあり、分解した値を受けてドリブンキー等でフィルタした上で再合成して別の骨を駆動させることが出来ます（例えば、曲げの50%だけ追従したりなど）。

##ディレクトリ構成
* scripts: アトリビュートエディタレイアウト定義用のmelスクリプト。
* plug-ins: Pythonによるプラグイン。
* examples: ごく簡単なMayaシーンの例と、軌跡をプロットするサンプルスクリプト。

##ノードについて
プラグイン rotationDriver.py は以下の二つのノードを含んでいます。

* decomposeRotate
  オイラー角回転を入力して「捻り／縦方向の曲げ／横方向の曲げ」を出力するノード。
  以下のアトリビュートを持ちます。
  - method: 分解方法の選択。
  - reverseOrder: OFFだと曲げ・捻りの順、ONだと捻り・曲げの順になるように分解する（効果があるのは method が Stereographic Projection の場合のみ）。
  - rotate: オイラー角回転の入力。
  - rotateOrder: 入力回転のオーダー。
  - axisOrient: ボーン方向を定義するための回転。
  - outDecomposedAngle: 分解された三つの角度の出力。

* composeRotate
  「捻り／縦方向の曲げ／横方向の曲げ」を入力してオイラー角回転を出力するノード。
  以下のアトリビュートを持ちます。
  - method: 分解方法の選択。
  - reverseOrder: OFFだと曲げ・捻りの順、ONだと捻り・曲げの順になるように合成する（効果があるのは method が Stereographic Projection の場合のみ）。
  - decomposedAngle: 分解された三つの角度の入力。
  - axisOrient: ボーン方向を定義するための回転。
  - rotateOrder: 出力回転のオーダー指定。
  - outRotate: 合成されたオイラー角回転の出力。

##角度の分解・合成手法の選択
method アトリビュートによって、角度の分解・合成手法を、
Stereographic Projection と Exponential Map のどちらかを選択することが出来ます。

Stereographic Projection での分解は、まず入力回転を曲げと捻りに分離した後に、曲げ回転を
[ステレオ投影](https://ja.wikipedia.org/wiki/%E3%82%B9%E3%83%86%E3%83%AC%E3%82%AA%E6%8A%95%E5%BD%B1)
によって縦横方向に分離します。合成ではその逆をやります。縦横の曲げには回転の順番はありませんが、曲げと捻りには順番があります。
reverseOrder が OFF の場合は階層上位から見て曲げ・捻りの順、ON の場合は捻り・曲げの順となります。

Exponential Map での分解はクォータニオンの log() の２倍、合成は入力の1/2倍の exp() としています。Maya API の MQuaternion クラスにはそれらのメソッドがあるので、それらを呼び出すだけの非常に簡単な実装となっています。
Stereographic Projection に近い値が算出されますが、こちらは曲げ・捻りの順番もありません。よって、reverseOrder を ON/OFF しても結果は変わりません。
こちらで得られるのは、曲げと捻りに近い値が得られるものの、別の表現による３つの角度と考えた方が良いと思います。

ソースコードを見れば分かりますが、実は method がどちらの場合にも reverseOrder が ON の場合は反転処理を行っています。興味深いことに、Exponential Map の場合はその違いが現れません。このことからも Exponential Map の３つの角度は回転の順番という概念から解放されていることがわかります。

サンプルスクリプト [examples/plotBendHV.py](https://github.com/ryusas/maya_rotationDriver/tree/master/examples/plotBendHV.py) を Maya 上で実行すると、縦方向と横方向の曲げを変化させた時に描かれる球面上の軌跡がプロットされます。これで二種類の曲げ回転の結果の違いを確認出来ます（先に述べたように Exponential Map で得られているのは純粋な曲げではありませんが）。

![SS](/plotBendHV.png)

純粋な曲げ回転という点では Stereographic Projection の方が綺麗なプロット結果が得られます。Stereographic Projection では 180度の曲げはちょうど反対側の極に収束しますが、Exponential Map では極をオーバーして線が交差してしまいます。

私は当初から「曲げと捻りの分離＋曲げは２方向に分離」という考えが頭にあり、Exponential Map ではそれに近い値が得られることから、両者を比較出来るようにこのプラグインをテストしてみたのですが、reverseOrder アトリビュートを追加実装してみて、その違いが鮮明になりました。
もはや当たり前のことかも知れませんが、
回転を曲げと捻りに分離して扱うという考えでは Stereographic Projection が適していて、
曲げと捻りの順番さえも無くして扱いたい場合には Exponential Map が有効といえるのではないかと思います。

##ボーン軸方向の定義
デフォルトでは、ローカルX軸がボーン方向、Y軸が縦方向、Z軸が横方向となっていて、それに基づいた分解・合成がされます。
axisOrient アトリビュートによって、この方向を回転させることが出来ます。
decomposeRotate ノードと composeRotate ノードの設定が同じであれば、分解したものを合成して元に戻すことが出来ます。

##サンプルシーン
* [examples/rotationDriver.ma](https://github.com/ryusas/maya_rotationDriver/tree/master/examples/rotationDriver.ma)

  一つのキューブ pCube1 の回転がもう一方のキューブ pCube2 の回転をそのまま駆動する例。
  pCube1 の回転を decomposeRotate で分解し、分解された３つ回転を pCube2 の入力となっている composeRotate にそのまま繋げています。
  双方が全く同じ姿勢になるのが確認出来ます。decomposeRotate と composeRotate の method や reverseOrder 等の設定をいじってみると分かりますが、双方が全く同じ設定になっている必要があります。

* [examples/rotationDriver_joints.ma](https://github.com/ryusas/maya_rotationDriver/tree/master/examples/rotationDriver_joints.ma)

  一つのボーン src の回転がもう一方のボーン dst の回転をそのまま駆動する例。
  キューブの例と同じですが、ボーンのローカル軸方向をあえて変えてあり、composeRotate の axisOrient アトリビュートによって方向を一致させています。

* [examples/bend_roll.ma](https://github.com/ryusas/maya_rotationDriver/tree/master/examples/bend_roll.ma)
  曲げと捻りに分離した回転を、曲げと捻りの順番が異なる二つの階層に分けて接続している例。
  reverseOrder を変えるために decomposeRotate ノードを二つ作って二種類の分解結果を得ています。それを曲げと捻りの順序が異なる二つの joint 階層に接続しています。
  それぞれの reverseOrder の設定が適切でないと期待する結果は得られません。
  また method は Stereographic Projection ですが、Exponential Map にすると期待する結果は得られません。

##改訂履歴
* 2016.9.20: reverseOrderアトリビュート追加、サンプルシーン追加とドキュメント加筆。
* 2016.7.9: 初版

