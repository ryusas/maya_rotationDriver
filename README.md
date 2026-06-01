English | [日本語](README.ja.md)

# maya_rotationDriver
This is a simple sample Python implementation of a Maya plug-in that decomposes and composes bone Euler rotations into three independent angles based on the bone's orientation: "twist", "vertical bend", and "horizontal bend".

In addition, the preliminary operation of separating bend into vertical and horizontal directions (separating bend and twist) can be achieved using Maya's standard features without this plug-in. A sample scene is included to provide a simple explanation of the concept.


## About this method
By using this method, you can precisely drive another element based on how much and in which direction a joint is bent or twisted. If you try to do this using Euler rotations, you will run into the following obstacles:

* Since there are countless combinations of values representing a single posture, it is difficult to build a driven structure based on them (the same posture might yield different results).
* Individual axis rotations do not necessarily represent twist or bend (for example, the twist of a bone extending in the X-axis direction is not always the X-axis rotation of the Euler rotation).
* Based on the `rotateOrder` specification, there is a sequential hierarchy between vertical and horizontal rotations, meaning they are not treated equally.

The disadvantages of Euler rotation are precisely the advantages of this method.
This method provides both a decomposition node and a composition node. You can take the decomposed values, filter them using driven keys or other methods, and then recompose them to drive another bone (for example, having a bone follow only 50% of the bend).


## Directory Structure
* `scripts`: MEL scripts for defining Attribute Editor layouts.
* `plug-ins`: Python plug-ins.
* `examples`: Very simple examples of Maya scenes and a sample script for plotting trajectories.


## About the Nodes
The plug-in `rotationDriver.py` contains the following two nodes:

* `decomposeRotate`
  A node that takes Euler rotations as input and outputs "twist, vertical bend, and horizontal bend".
  It has the following attributes:
  - `method`: Choice of decomposition method.
  - `reverseOrder`: When OFF, decomposes in the order of bend then twist; when ON, decomposes in the order of twist then bend (this only has an effect when `method` is set to `Stereographic Projection`).
  - `rotate`: Input Euler rotation.
  - `rotateOrder`: Order of the input rotation.
  - `axisOrient`: Rotation to define the bone direction.
  - `outDecomposedAngle`: Outputs the three decomposed angles.

* `composeRotate`
  A node that takes "twist, vertical bend, and horizontal bend" as input and outputs Euler rotations.
  It has the following attributes:
  - `method`: Choice of composition method.
  - `reverseOrder`: When OFF, composes in the order of bend then twist; when ON, composes in the order of twist then bend (this only has an effect when `method` is set to `Stereographic Projection`).
  - `decomposedAngle`: Input of the three decomposed angles.
  - `axisOrient`: Rotation to define the bone direction.
  - `rotateOrder`: Order specification of the output rotation.
  - `outRotate`: Outputs the composed Euler rotation.

## Selecting the Angle Decomposition/Composition Method
With the `method` attribute, you can select either `Stereographic Projection` or `Exponential Map` as the angle decomposition/composition method.

Decomposition in `Stereographic Projection` first separates the input rotation into bend and twist, and then separates the bend rotation into vertical and horizontal directions using [Stereographic Projection](https://en.wikipedia.org/wiki/Stereographic_projection). Composition does the reverse. While there is no rotation order between vertical and horizontal bends, there is an order between bend and twist.
When `reverseOrder` is OFF, the order is bend then twist from the parent's perspective; when ON, the order is twist then bend.

Decomposition in `Exponential Map` is twice the `log()` of the quaternion, and composition is `exp()` of half of the input. Since Maya API's `MQuaternion` class provides these methods, it has a very simple implementation that just calls them.
While it calculates values close to `Stereographic Projection`, there is no rotation order between bend and twist here. Therefore, changing `reverseOrder` ON/OFF does not affect the result.
Strictly speaking, it is probably better to think of the three angles obtained here as another representation of angles rather than bend and twist.

As you can see from the [source code](/plug-ins/rotationDriver.py), when `reverseOrder` is ON, inversion processing is performed regardless of the selected `method`. Interestingly, in the case of `Exponential Map`, this difference does not appear. This also shows that the three angles of the `Exponential Map` are free from the concept of rotation order.

Running the sample script [examples/plotBendHV.py](/examples/plotBendHV.py) in Maya plots the trajectory drawn on the spherical surface when the vertical and horizontal bends are varied. This allows you to verify the difference in results between the two types of bend rotations (although as mentioned earlier, what is obtained with the `Exponential Map` is not purely bend).

![SS](/plotBendHV.png)

In terms of pure bend rotation, `Stereographic Projection` produces a cleaner plotted trajectory. In `Stereographic Projection`, a 180-degree bend converges exactly to the opposite pole, whereas in `Exponential Map`, the lines overshoot the pole and intersect.

I have always had the concept of "separating bend and twist + separating bend into two directions" in mind. Since `Exponential Map` yields values close to this, I tested this plug-in to compare the two. By additionally implementing the `reverseOrder` attribute, the difference became clear.
It may be obvious now, but I think `Stereographic Projection` is suitable for the concept of treating rotation by separating it into bend and twist, while `Exponential Map` is effective when you want to handle them without even the order of bend and twist.


## Defining Bone Axis Orientation
By default, the local X-axis is the bone direction, the Y-axis is the vertical direction, and the Z-axis is the horizontal direction, and decomposition/composition is performed based on this setup.
You can rotate this orientation using the `axisOrient` attribute.
As long as the settings of the `decomposeRotate` node and the `composeRotate` node are identical, you can recompose the decomposed values back to their original state.


## Sample Scenes
* [rotationDriver.ma](/examples/rotationDriver.ma)

  An example where the rotation of one cube `pCube1` directly drives the rotation of another cube `pCube2`.
  The rotation of `pCube1` is decomposed by `decomposeRotate`, and the three decomposed rotations are connected directly to `composeRotate`, which drives `pCube2`.
  You can verify that both objects have the exact same posture. If you play around with settings like `method` and `reverseOrder` on `decomposeRotate` and `composeRotate`, you will see that both nodes must have identical settings.

* [rotationDriver_joints.ma](/examples/rotationDriver_joints.ma)

  An example where the rotation of one bone `src` directly drives the rotation of another bone `dst`.
  This is identical to the cube example, but the bone's local axis orientation has been intentionally changed, and the orientations are matched using the `axisOrient` attribute on `composeRotate`.

* [bend_roll.ma](/examples/bend_roll.ma)

  An example connecting rotations separated into bend and twist to two joint hierarchies with different orders of bend and twist.
  To change the `reverseOrder`, two `decomposeRotate` nodes are created to obtain two different types of decomposition results. These are connected to two joint hierarchies with different sequence orders of bend and twist.
  The expected results will not be achieved unless the respective `reverseOrder` settings are correct.
  Also, the `method` used here is `Stereographic Projection`; if changed to `Exponential Map`, you will not get the expected results.
  
* [withoutPlugin.ma](/examples/withoutPlugin.ma)

  An example of implementing bend/twist separation using only Maya's standard features (`aimConstraint` and `orientConstraint`) without using this plug-in.



## Revision History
* 2016.11.9: Added [withoutPlugin.ma](/examples/withoutPlugin.ma).
* 2016.9.20: Added the `reverseOrder` attribute, added sample scenes, and expanded documentation.
* 2016.7.9: Initial release.
