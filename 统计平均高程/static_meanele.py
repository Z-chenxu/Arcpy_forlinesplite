# coding=utf-8
import arcpy
from arcpy import env
from arcpy.sa import *
env = r"D:\zhongrong\Mars_LS\cl.mdb"

table = arcpy.CreateTable_management("D:\zhongrong\Mars_LS\cl.mdb", "battomelev")
arcpy.AddField_management(table, "id", "LONG")
arcpy.AddField_management(table, "elev", "FLOAT", field_scale=8)
cursor = arcpy.da.InsertCursor(table, ["id","elev"])

pointPath = r"D:\zhongrong\Mars_LS\result\Extract_gouzaop1.shp"
arrays=arcpy.da.FeatureClassToNumPyArray(pointPath,['RASTERVALU','circurid'])
print(arrays)
print(arrays[-1])

k = 0
k_1 = 0
ele = 0
count = 0
for i in arrays:
    print i#打印出每个元组
    id = i[1] #每个元组的id
    if i == arrays[-1]:
        ele = ele + i[0]  # 统计总高程
        count = count + 1  # 对点数进行统计
        ele = ele/count
        cursor.insertRow([k_1,ele])
        break
    if k==id:
        ele=ele+i[0] #统计总高程
        count=count+1 #对点数进行统计
        k_1=id #记录上一个点的id
        continue
    else:
        k=id #更改k为下一个圆的id
        ele = ele/count #计算平均高程
        cursor.insertRow([k_1, ele]) #插入表
        ele = i[0] #重新赋值ele
        count = 1 #重复赋值count





print "finished"