# coding=utf-8
import arcpy
from arcpy import env
from arcpy.sa import *
import os

#先依次遍历所有面，每个面转线
#再对每条线，进行多点加密，将点存储到新的点地理要素类中

env.workplace = r"D:\zhongrong"
shpPath = r"D:\zhongrong\Mars_LS\cl\Mars_s1.shp" #所引用的面要素类集合
creatpoints = r"D:\zhongrong\Mars_LS\result\gouzaopoints.shp" #存储插入点的要素集
sp = arcpy.Describe(shpPath).spatialReference #参考系
print("1")
DemPath = r"D:\zhongrong\DTEEC_069665_2055_069731_2055_A01.IMG" #高程栅格


cur = arcpy.da.SearchCursor(shpPath,["FID","SHAPE@"])

#创建要素类

arcpy.CreateFeatureclass_management(
    r"D:\zhongrong\Mars_LS\result",
    "gouzaopoints",
    "POINT","","","",
    sp
)
arcpy.AddField_management(creatpoints,"circurid","LONG")
pointcursor = arcpy.da.InsertCursor(creatpoints,["SHAPE@","circurid"])

for i in cur:
    print ("2")
    fid = i[0]
    area = i[1]
    # 面转换线
    #print(area.type)
    arcpy.PolygonToLine_management(area,"in_memory/templines","IGNORE_NEIGHBORS")#仅针对单个面，其实不用考虑领域面关系
    #对每条线进行加密
    temcur = arcpy.da.SearchCursor("in_memory/templines",["SHAPE@","SHAPE@LENGTH"])

    #遍历每条新线
    for row in temcur:
        print ("3")
        geometry = row[0]
        length = row[1]
        INT = int(length/2) #得到遍历长度
        #对线进行加密
        for index in range(INT):
            print (INT)
            point = geometry.positionAlongLine(index*3+1,False)
            pointcursor.insertRow([point,fid])
    arcpy.management.Delete("in_memory/templines")

print "finished"
