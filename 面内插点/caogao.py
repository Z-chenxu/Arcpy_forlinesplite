# coding=utf-8
import arcpy
from arcpy import env
from arcpy.sa import *
import os

#该代码存在错误

env.workplace = r"D:\zhongrong"
shpPath = r"D:\zhongrong\Mars_LS\Mars_s1.shp" #所引用的面要素类集合
sp = arcpy.Describe(shpPath).spatialReference #参考系
print(sp)
DemPath = r"D:\zhongrong\DTEEC_069665_2055_069731_2055_A01.IMG" #高程栅格
pointfeatureclass = r"D:\zhongrong\points.shp"
cur = arcpy.da.SearchCursor(shpPath,["FID","SHAPE@"])
if os.path.exists( r"D:\zhongrong\gouzaopoints.shp"):
    arcpy.Delete_management( r"D:\zhongrong\gouzaopoints.shp")
creatpoints = r"D:\zhongrong\gouzaopoints.shp"
arcpy.CreateFeatureclass_management(
    "D:\zhongrong",
    "gouzaopoints",
    "POINT","","","",
    sp
)

for i in cur:
    fid = i[0]
    area = i[1]
    # 面转换线
    #print(area.type)
    arcpy.PolygonToLine_management(area,"in_memory/templines","IGNORE_NEIGHBORS")#仅针对单个面，其实不用考虑领域面关系
    #对每条线进行加密
    temcur = arcpy.da.SearchCursor("in_memory/templines",["SHAPE@","SHAPE@LENGTH"])

    #遍历每条新线
    for row in temcur:
        geometry = row[0]
        length = row[1]
        INT = int(length/2) #得到遍历长度
        #对线进行加密
        for index in range(INT):
            point = geometry.positionAlongLine(index*2+1,False)
            curPoint = arcpy.InsertCursor(creatpoints)
            newRowpoint = curPoint.newRow()
            newRowpoint.shape = point
            curPoint.insertRow(newRowpoint)#将加密的点插入到新的点集合中

    arcpy.management.Delete("in_memory/templines")

print "finished"
