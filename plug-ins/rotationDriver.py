# -*- coding: utf-8 -*-
u"""
ボーン回転を３方向の独立した角度（捻り、横曲げ、縦曲げ）に分解・合成する Maya ノード。
"""
__author__ = 'ryusas'
__version__ = '1.1.20160920'

#==================================================================================
maya_useNewAPI = True

_TYPE_IDS = (  # 0x00000000 ～ 0x0007ffff
    0x00070001,
    0x00070002,
)

import sys
import math
from math import sin, cos, tan, atan2, pi as _PI

import maya.api.OpenMaya as api
from maya.api.OpenMaya import MQuaternion, MVector, MEulerRotation

_X_VEC = MVector.kXaxisVector
_Y_VEC = MVector.kYaxisVector
_Z_VEC = MVector.kZaxisVector

_2PI = 2. * _PI
_boundAngle = lambda x: (x - _2PI) if x > _PI else ((x + _2PI) if x < -_PI else x)


#==================================================================================
def _toRollBendHV(quat):
    vec = _X_VEC.rotateBy(quat)
    bendQ = MQuaternion(_X_VEC, vec)
    b = (_X_VEC * vec) + 1.

    rollQ = quat * bendQ.inverse()
    return (
        _boundAngle(atan2(rollQ[0], rollQ[3]) * 2.),
        atan2(_Z_VEC * vec, b) * -2.,
        atan2(_Y_VEC * vec, b) * 2.,
    )


def _fromRollBendHV(rhv):
    half = .5 * rhv[0]
    f = sin(half)
    quat = MQuaternion(_X_VEC[0] * f, _X_VEC[1] * f, _X_VEC[2] * f, cos(half))

    h = tan(-.5 * rhv[1])
    v = tan(.5 * rhv[2])
    f = 2. / (h * h + v * v + 1.)
    quat *= MQuaternion(_X_VEC, _X_VEC * (f - 1.) + _Y_VEC * (v * f) + _Z_VEC * (h * f))
    return quat


#==================================================================================
class DecomposeRotate(api.MPxNode):
    type_name = 'decomposeRotate'
    type_id = api.MTypeId(_TYPE_IDS[0])

    @classmethod
    def initialize(cls):
        fnUnit = api.MFnUnitAttribute()
        fnNumeric = api.MFnNumericAttribute()
        fnEnum = api.MFnEnumAttribute()

        cls.aMethod = fnEnum.create('method', 'met')
        fnEnum.addField('Stereographic Projection', 0)
        fnEnum.addField('Exponential Map', 1)
        cls.addAttribute(cls.aMethod)

        cls.aReverseOrder = fnNumeric.create('reverseOrder', 'ror', api.MFnNumericData.kBoolean, False)
        cls.addAttribute(cls.aReverseOrder)

        cls.aRotateX = fnUnit.create('rotateX', 'rx', api.MFnUnitAttribute.kAngle, 0.)
        cls.aRotateY = fnUnit.create('rotateY', 'ry', api.MFnUnitAttribute.kAngle, 0.)
        cls.aRotateZ = fnUnit.create('rotateZ', 'rz', api.MFnUnitAttribute.kAngle, 0.)
        cls.aRotate = fnNumeric.create('rotate', 'r', cls.aRotateX, cls.aRotateY, cls.aRotateZ)
        cls.addAttribute(cls.aRotate)

        cls.aRotateOrder = fnEnum.create('rotateOrder', 'ro')
        fnEnum.addField('xyz', 0)
        fnEnum.addField('yzx', 1)
        fnEnum.addField('zxy', 2)
        fnEnum.addField('xzy', 3)
        fnEnum.addField('yxz', 4)
        fnEnum.addField('zyx', 5)
        cls.addAttribute(cls.aRotateOrder)

        cls.aAxisOrientX = fnUnit.create('axisOrientX', 'aox', api.MFnUnitAttribute.kAngle, 0.)
        cls.aAxisOrientY = fnUnit.create('axisOrientY', 'aoy', api.MFnUnitAttribute.kAngle, 0.)
        cls.aAxisOrientZ = fnUnit.create('axisOrientZ', 'aoz', api.MFnUnitAttribute.kAngle, 0.)
        cls.aAxisOrient = fnNumeric.create('axisOrient', 'ao', cls.aAxisOrientX, cls.aAxisOrientY, cls.aAxisOrientZ)
        cls.addAttribute(cls.aAxisOrient)

        cls.aOutRoll = fnUnit.create('outRoll', 'orl', api.MFnUnitAttribute.kAngle, 0.)
        cls.aOutBendH = fnUnit.create('outBendH', 'obh', api.MFnUnitAttribute.kAngle, 0.)
        cls.aOutBendV = fnUnit.create('outBendV', 'obv', api.MFnUnitAttribute.kAngle, 0.)
        cls.aOutDecomposedAngle = fnNumeric.create('outDecomposedAngle', 'oda', cls.aOutRoll, cls.aOutBendH, cls.aOutBendV)
        fnNumeric.writable = False
        fnNumeric.storable = False
        cls.addAttribute(cls.aOutDecomposedAngle)

        cls.attributeAffects(cls.aMethod, cls.aOutDecomposedAngle)
        cls.attributeAffects(cls.aReverseOrder, cls.aOutDecomposedAngle)
        cls.attributeAffects(cls.aRotate, cls.aOutDecomposedAngle)
        cls.attributeAffects(cls.aRotateOrder, cls.aOutDecomposedAngle)
        cls.attributeAffects(cls.aAxisOrient, cls.aOutDecomposedAngle)

    def compute(self, plug, block):
        if plug.isChild:
            plug = plug.parent()
        if plug != self.aOutDecomposedAngle:
            return

        quat = MEulerRotation(block.inputValue(self.aAxisOrient).asDouble3()).asQuaternion()
        oriQ = quat.inverse()
        quat *= MEulerRotation(block.inputValue(self.aRotate).asDouble3(), block.inputValue(self.aRotateOrder).asShort()).asQuaternion()
        quat *= oriQ

        reverse = block.inputValue(self.aReverseOrder).asBool()
        if reverse:
            quat = quat.inverse()
        if block.inputValue(self.aMethod).asShort():
            rhv = quat.log()
            rhv = (rhv[0] * 2., rhv[1] * 2., rhv[2] * 2.)
        else:
            rhv = _toRollBendHV(quat)
        if reverse:
            rhv = (-rhv[0], -rhv[1], -rhv[2])

        block.outputValue(self.aOutDecomposedAngle).set3Double(*rhv)


#------------------------------------------------------------------------------
class ComposeRotate(api.MPxNode):
    type_name = 'composeRotate'
    type_id = api.MTypeId(_TYPE_IDS[1])

    @classmethod
    def initialize(cls):
        fnUnit = api.MFnUnitAttribute()
        fnNumeric = api.MFnNumericAttribute()
        fnEnum = api.MFnEnumAttribute()

        cls.aMethod = fnEnum.create('method', 'met')
        fnEnum.addField('Stereographic Projection', 0)
        fnEnum.addField('Exponential Map', 1)
        cls.addAttribute(cls.aMethod)

        cls.aReverseOrder = fnNumeric.create('reverseOrder', 'ror', api.MFnNumericData.kBoolean, False)
        cls.addAttribute(cls.aReverseOrder)

        cls.aRoll = fnUnit.create('roll', 'rl', api.MFnUnitAttribute.kAngle, 0.)
        cls.aBendH = fnUnit.create('bendH', 'bh', api.MFnUnitAttribute.kAngle, 0.)
        cls.aBendV = fnUnit.create('bendV', 'bv', api.MFnUnitAttribute.kAngle, 0.)
        cls.aDecomposedAngle = fnNumeric.create('decomposedAngle', 'da', cls.aRoll, cls.aBendH, cls.aBendV)
        cls.addAttribute(cls.aDecomposedAngle)

        cls.aAxisOrientX = fnUnit.create('axisOrientX', 'aox', api.MFnUnitAttribute.kAngle, 0.)
        cls.aAxisOrientY = fnUnit.create('axisOrientY', 'aoy', api.MFnUnitAttribute.kAngle, 0.)
        cls.aAxisOrientZ = fnUnit.create('axisOrientZ', 'aoz', api.MFnUnitAttribute.kAngle, 0.)
        cls.aAxisOrient = fnNumeric.create('axisOrient', 'ao', cls.aAxisOrientX, cls.aAxisOrientY, cls.aAxisOrientZ)
        cls.addAttribute(cls.aAxisOrient)

        cls.aRotateOrder = fnEnum.create('rotateOrder', 'ro')
        fnEnum.addField('xyz', 0)
        fnEnum.addField('yzx', 1)
        fnEnum.addField('zxy', 2)
        fnEnum.addField('xzy', 3)
        fnEnum.addField('yxz', 4)
        fnEnum.addField('zyx', 5)
        cls.addAttribute(cls.aRotateOrder)

        cls.aOutRotateX = fnUnit.create('outRotateX', 'orx', api.MFnUnitAttribute.kAngle, 0.)
        cls.aOutRotateY = fnUnit.create('outRotateY', 'ory', api.MFnUnitAttribute.kAngle, 0.)
        cls.aOutRotateZ = fnUnit.create('outRotateZ', 'orz', api.MFnUnitAttribute.kAngle, 0.)
        cls.aOutRotate = fnNumeric.create('outRotate', 'or', cls.aOutRotateX, cls.aOutRotateY, cls.aOutRotateZ)
        fnNumeric.writable = False
        fnNumeric.storable = False
        cls.addAttribute(cls.aOutRotate)

        cls.attributeAffects(cls.aMethod, cls.aOutRotate)
        cls.attributeAffects(cls.aReverseOrder, cls.aOutRotate)
        cls.attributeAffects(cls.aDecomposedAngle, cls.aOutRotate)
        cls.attributeAffects(cls.aAxisOrient, cls.aOutRotate)
        cls.attributeAffects(cls.aRotateOrder, cls.aOutRotate)

    def compute(self, plug, block):
        if plug.isChild:
            plug = plug.parent()
        if plug != self.aOutRotate:
            return

        rhv = block.inputValue(self.aDecomposedAngle).asDouble3()

        reverse = block.inputValue(self.aReverseOrder).asBool()
        if reverse:
            rhv = (-rhv[0], -rhv[1], -rhv[2])
        if block.inputValue(self.aMethod).asShort():
            quat = MQuaternion(rhv[0] * .5, rhv[1] * .5, rhv[2] * .5, 0.).exp()
        else:
            quat = _fromRollBendHV(rhv)
        if reverse:
            quat = quat.inverse()

        oriQ = MEulerRotation(block.inputValue(self.aAxisOrient).asDouble3()).asQuaternion()
        quat = oriQ.inverse() * quat
        quat *= oriQ

        rot = MEulerRotation(0., 0., 0., block.inputValue(self.aRotateOrder).asShort())
        rot.setValue(quat)
        block.outputValue(self.aOutRotate).set3Double(*rot)


#------------------------------------------------------------------------------
def _registerNode(plugin, cls):
    try:
        plugin.registerNode(cls.type_name, cls.type_id, lambda: cls(), cls.initialize)
    except:
        sys.stderr.write('Failed to register node: ' + cls.type_name)
        raise


def _deregisterNode(plugin, cls):
    try:
        plugin.deregisterNode(cls.type_id)
    except:
        sys.stderr.write('Failed to deregister node: ' + cls.type_name)
        raise


def initializePlugin(mobj):
    plugin = api.MFnPlugin(mobj, __author__, __version__, 'Any')
    _registerNode(plugin, DecomposeRotate)
    _registerNode(plugin, ComposeRotate)


def uninitializePlugin(mobj):
    plugin = api.MFnPlugin(mobj)
    _deregisterNode(plugin, DecomposeRotate)
    _deregisterNode(plugin, ComposeRotate)

