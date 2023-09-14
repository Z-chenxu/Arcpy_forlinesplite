# coding=utf-8
import arcpy
from arcpy import env
#得到每条顺势线的中点
env = r"D:\zhongrong\workplace.gdb"
#得到参考空间
shpPath = r"D:\zhongrong\Mars_LS\Mars_L.shp"
sp = arcpy.Describe(shpPath).spatialReference #参考系
#创建要素类
creatpoints = r"D:\zhongrong\zz.shp" #存储插入点的要素集  #需要更改的参数
arcpy.CreateFeatureclass_management(
    "D:\zhongrong",
    "zz",#需要更改的参数
    "POINT","","","",
    sp
)
pointcursor = arcpy.da.InsertCursor(creatpoints,["SHAPE@"])

cur = arcpy.da.SearchCursor(shpPath,["SHAPE@"])
#得到中点
for i in cur:
    print "1"
    geo = i[0]
    point = geo.positionAlongLine(0.5,use_percentage=True)

    pointcursor.insertRow([point])
print "finished"