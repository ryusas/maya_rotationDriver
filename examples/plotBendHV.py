# -*- coding: utf-8 -*-
u"""
rotationDriver プラグインの composeRotate ノードの bendH & bendV の描く軌跡のプロット。
stereographic projection と exponential maps の比較。
"""
from math import pi as PI
import maya.cmds as cmds
import maya.api.OpenMaya as api
from maya.api.OpenMaya import MVector, MEulerRotation, MAngle

_TO_DEG = 180. / PI
_TO_RAD = PI / 180.


#------------------------------------------------------------------------------
def _createInsideSphere(name, radius, parent):
    node = cmds.sphere(r=radius * .999)[0]
    cmds.parent(node, parent)
    cmds.rename(node, name)
    return node


def _createCurve(name, angle, cvs, parent):
    node = cmds.curve(d=1, p=cvs)
    cmds.parent(node, parent)
    name += '_n%03d' if angle < 0. else '_p%03d'
    cmds.rename(node, name % abs(round(angle)))
    return node


def _plotBendHV(node_or, node_h, node_v, name, radius, num):
    assert MAngle.uiUnit() == MAngle.kDegrees

    top = cmds.createNode('transform', n=name)

    #_createInsideSphere('insideSphere', radius, top)

    bone = MVector.kXaxisVector * radius
    invNum = 1. / float(num)
    angles = [360. * x * invNum - 180. for x in range(num + 1)]

    def evalPos(attr, val):
        cmds.setAttr(attr, val)
        return bone.rotateBy(MEulerRotation([x * _TO_RAD for x in cmds.getAttr(node_or)[0]]))

    grp = cmds.createNode('transform', n='plotBendH', p=top)
    for v in angles:
        cmds.setAttr(node_v, v)
        _createCurve('plogH', v, [evalPos(node_h, h) for h in angles], grp)

    grp = cmds.createNode('transform', n='plotBendV', p=top)
    for h in angles:
        cmds.setAttr(node_h, h)
        _createCurve('plotV', h, [evalPos(node_v, v) for v in angles], grp)

    return top


#------------------------------------------------------------------------------
def doit(radius=5., num=36):
    cmds.loadPlugin('rotationDriver', qt=True)
    node = cmds.createNode('composeRotate')
    node_or = node + '.outRotate'
    node_h = node + '.bendH'
    node_v = node + '.bendV'

    shiftX = radius * 1.25

    top0 = _plotBendHV(node_or, node_h, node_v, 'plotStereoProj', radius, num)
    cmds.setAttr(top0 + '.tx', -shiftX)

    cmds.setAttr(node + '.method', 1)
    top1 = _plotBendHV(node_or, node_h, node_v, 'plotExpmap', radius, num)
    cmds.setAttr(top1 + '.tx', shiftX)

    cmds.delete(node)

    cmds.select([top0, top1])

doit()
