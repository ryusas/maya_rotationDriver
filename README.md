# maya_rotationDriver
ボーンのオイラー角回転を、ボーン方向を元にした「捻り／縦方向の曲げ／横方向の曲げ」という独立した三つの角度に分解・合成するMayaプラグインのPython実装の簡単なサンプルです。

##ディレクトリ構成
* scripts: アトリビュートエディタレイアウト定義用のmelスクリプト。
* plug-ins: Pythonによるプラグイン。
* examples: ごく簡単なMaya 2016シーンの例と、軌跡をプロットするサンプルスクリプト。

##ノードについて
プラグイン rotationDriver.py は以下の二つのノードを含んでいます。

* decomposeRotate
  オイラー角回転を入力して「捻り／縦方向の曲げ／横方向の曲げ」を出力するノード。
  以下のアトリビュートを持ちます。
  - method: 分解方法の選択。
  - rotate: オイラー角回転の入力。
  - rotateOrder: 入力回転のオーダー。
  - axisOrient: ボーン方向を定義するための回転。
  - outDecomposedAngle: 分解された三つの角度の出力。

* composeRotate
  「捻り／縦方向の曲げ／横方向の曲げ」を入力してオイラー角回転を出力するノード。
  以下のアトリビュートを持ちます。
  - method: 分解方法の選択。
  - decomposedAngle: 分解された三つの角度の入力。
  - axisOrient: ボーン方向を定義するための回転。
  - rotateOrder: 出力回転のオーダー指定。
  - outRotate: 合成されたオイラー角回転の出力。

##ボーン軸方向の定義について
デフォルトでは、ローカルX軸がボーン方向、Y軸が縦方向、Z軸が横方向となっていて、それに基づいた分解・合成がされます。
axisOrient アトリビュートによって、この方向を回転させることが出来ます。
decomposeRotate ノードと composeRotate ノードの設定が同じであれば、分解したものを合成して元に戻すことが出来ます。

[examples/rotationDriver_joints.ma](https://github.com/ryusas/maya_rotationDriver/tree/master/examples/rotationDriver_joints.ma) は、ローカル軸の異なる二つのボーンを axisOrient 設定を使って同期させている例です。

##Exponential Map での近似について
method アトリビュートによって、角度の分解・合成手法を、
[Stereographic Projection](https://ja.wikipedia.org/wiki/%E3%82%B9%E3%83%86%E3%83%AC%E3%82%AA%E6%8A%95%E5%BD%B1)
と Exponential Map のどちらかを選択することが出来ます。

ソースコードを見れば分かりますが、Exponential Map は Maya API の MQuaternion をクラスを用いた非常に簡単な実装です。
分解は log() を２倍して出力、合成は入力の半分を exp() しているだけです。

サンプルスクリプト [examples/plotBendHV.py](https://github.com/ryusas/maya_rotationDriver/tree/master/examples/plotBendHV.py) を Maya 上で実行すると、縦方向と横方向の曲げを変化させた時に描かれる球面上の軌跡がプロットされます。これで二種類の結果の違いを確認出来ます。

![SS](/plotBendHV.png)
