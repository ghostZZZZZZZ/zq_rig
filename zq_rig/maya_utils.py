import pymel.core as pm
from pymel.core.animation import bakeSimulation
from pymel.core.general import spaceLocator




def quickCreateNode(**kwargs):
    name=None
    if kwargs.has_key("name"):
        name=kwargs.pop("name")
    nodeType = kwargs.pop("type")
    if name:
        result_node = pm.createNode(nodeType,name=name)
    else:
        result_node = pm.createNode(nodeType)
    for i,v in kwargs.items():
        attr = getattr(result_node,i)
        if type(v)==pm.general.Attribute:
            v.connect(attr)
        elif type(v) == str:
            pm.connectAttr(v,attr)
        else:
            attr.set(v)
    return result_node


class NodeCreate(object):

    @staticmethod
    def conditionCreate(ft,st,op,ct,cf,name=None):
        dataDict = {
                "firstTerm":ft,
                "secondTerm":st,
                "operation":op,
                "colorIfTrueR":ct[0],
                "colorIfTrueG":ct[1],
                "colorIfTrueB":ct[2],
                "colorIfFalseR":cf[0],
                "colorIfFalseG":cf[1],
                "colorIfFalseB":cf[2],
            }
        return NodeCreate.createNode("condition",attrMap=dataDict,name=name)
    @staticmethod
    def multiDiviCreate(**kwargs):
        name=None
        if kwargs.has_key("name"):
            name=kwargs.pop("name")
        return NodeCreate.createNode("multiplyDivide",attrMap=kwargs,name=name)
    @staticmethod
    def angleBetweenCreate(**kwargs):
        name=None
        if kwargs.has_key("name"):
            name=kwargs.pop("name")
        return NodeCreate.createNode("angleBetween",attrMap=kwargs,name=name)
    @staticmethod
    def defaultCreate(**kwargs):
        name=None
        if kwargs.has_key("name"):
            name=kwargs.pop("name")
        nodeType = kwargs.pop("type")
        return NodeCreate.createNode(nodeType,attrMap=kwargs,name=name)
    @staticmethod
    def plusMinusCreate(d1=[],d2=[],d3=[],op=1,name=None):
        dataDict = {}
        for index,i in enumerate(d1):
            dataDict["input1D[%s]"%index] = i
        for index,i in enumerate(d2):
            if type(i)==list:
                #for j in i:
                dataDict["input2D[%s].input2Dx"%index] = i[0]
                dataDict["input2D[%s].input2Dy"%index] = i[1]
            else:
                dataDict["input2D[%s]"%index] = i
        for index,i in enumerate(d3):
            if type(i)==list:
                dataDict["input3D[%s].input3Dx"%index] = i[0]
                dataDict["input3D[%s].input3Dy"%index] = i[1]
                dataDict["input3D[%s].input3Dz"%index] = i[2]
            else:
                dataDict["input3D[%s]"%index] = i
        dataDict["operation"] = op

        return NodeCreate.createNode("plusMinusAverage",attrMap=dataDict,name=name)
    @staticmethod
    def createNode(nodeType,attrMap=None,name=None):
        if not name:
            newNode = pm.createNode(nodeType)
        else:
            newNode = pm.createNode(nodeType,name=name)
        if not attrMap:
            return newNode

        if not isinstance(attrMap,dict):
            return newNode

        for attr,value in attrMap.items():

            if type(value)==pm.general.Attribute:
                value.connect(newNode.name() + "." + attr)
            elif type(value) == str:
                pm.connectAttr(value,newNode.name() + "." + attr)
            else:
                newNode.setAttr(attr,value)
        return newNode


