# coding=utf-8
import arcpy
import numpy as np
from arcpy import env
import math
#统计所画剖面的错误个数
#直线剖面的方向需要一致


tablepath = r"D:\zhongrong\Mars_LS\processsing\pou1.dbf" #处理过的剖面地址
shppath = r"D:\zhongrong\Mars_LS\cl\profile.shp" #剖面shp地址
Createtablepath = r"D:\zhongrong\Mars_LS\111.gdb" #新建表格地址 结果
Createwrongtablepath = r"D:\zhongrong\Mars_LS\111.gdb" #新建表格地址 结果

def getwrongidfromlist(distandheigth):
    start = distandheigth[0]
    end = distandheigth[-1]
    middle = distandheigth[len(distandheigth)/2-1]
    if middle[1] < start[1] or middle[1] < end[1]:
        return False
    return  True
#统计最重要的曲线参数
#得到第一个截面最低点
def getlow1(distandheigth,heighid): #2
    low1 = distandheigth[heighid]
    for i in range(0,heighid):
        if distandheigth[i][1] < low1[1]:
            low1 = distandheigth[i]
    return low1
#得到第二个截面最低点
def getlow2(distandheigth,heighid):  #3
    low1 = distandheigth[heighid]
    for i in range(heighid,len(distandheigth)):
        if distandheigth[i][1] < low1[1]:
            low1 = distandheigth[i]
    return low1
#得到截面最高点
def getH(distandheigth):#1
    heigh = distandheigth[0]
    heighid = 0
    # 首先遍历出最高点
    for i in range(0, len(distandheigth)):
        if distandheigth[i][1] > heigh[1]:
            heigh = distandheigth[i]
            heighid = i
    return heigh,heighid
#宽度
def getWidth(low1,low2):
    return low2[0]-low1[0]
#不对称度
def getAsymmetry(distandheigth,width,cor,low1):
    heigh,id = getH(distandheigth)
    middle = width / 2.0
    heigh_c = heigh[0] - low1[0] - middle
    if width == 0:
        return 0
    Asymme = heigh_c / width * cor
    if Asymme <-0.5 or Asymme>0.5:
        print "?"
    return Asymme,heigh_c
#计算波峰曲率
def getSlope(width,H):
    return H/width*2*180/math.pi

#计算剖面高度
def geth(low1,low2,height):
    xie = (low2[1]-low1[1])/(low2[0]-low1[0])
    b = low1[1]-xie*low1[0]
    h1 = xie*height[0]+b
    return height[1]-h1

#计算床型宽度
def getbedformWidth(low1,low2):
    width = low2[0] - low1[0]
    H = low2[1] - low1[1]
    return math.sqrt(width*width+H*H)

def getwronglist(table1):
    wronglist = []  # 错误id数量
    dist = []
    heigh = []
    id_proi = table1[0][2]
    for pm in table1:
        id_next = pm[2]
        if id_next == id_proi:
            dist.append(pm[0])
            heigh.append(pm[1])
        else:
            distandhie = zip(dist, heigh)
            iswrong = getwrongidfromlist(distandhie)
            if iswrong == False:
                wronglist.append(id_proi)
            id_proi = id_next
            dis = []
            heigh = []
    print "wronglist:"
    print wronglist
    print "lengthofwronglist:"
    print len(wronglist)
    return  wronglist

#对直线进行计算得到方向改正值
def corrOri(linegeo):
    '''
    linego:线矢量
    :param linegeo:
    :return: 方向改正值
    '''
    geo = linegeo.getPart(0)
    if geo[0].Y > geo[geo.count-1]:
        return 1
    return -1
#查询id并得到方向改正值
def refId(id,idarray):
    for i in idarray:
        if id == i[0]:
            return i[1]
    return 1

def createWrongtable(wronglist):
    table1 = arcpy.CreateTable_management(Createwrongtablepath, "wronglist")
    arcpy.AddField_management(table1, "ID")
    cursor1 = arcpy.da.InsertCursor(table1, ["ID"])
    for i in wronglist:
        cursor1.insertRow([i])

if __name__ == '__main__':
    env = r"D:\zhongrong\workplace.gdb"
    # 得到改正数组
    cu = arcpy.da.SearchCursor(shppath, ["OID@", "SHAPE@"])#打开shp文件
    cor = []
    for line in cu:
        corr = corrOri(line[1])
        cor.append((line[0], corr))
    # print cor
    # 计算剖面
    table1 = arcpy.da.TableToNumPyArray(tablepath, ('FIRST_DIST', 'FIRST_Z', 'LINE_ID')) #打开表

    #产生错误表格
    wronglist = getwronglist(table1)
    createWrongtable(wronglist)

    table = arcpy.CreateTable_management(Createtablepath, "result")
    arcpy.AddField_management(table, "ID", "SHORT")
    arcpy.AddField_management(table, "TARsWidth", "FLOAT")
    arcpy.AddField_management(table, "TARsHeight", "FLOAT")
    # arcpy.AddField_management(table,"Averageslope","FLOAT")
    arcpy.AddField_management(table, "symmetry", "FLOAT")
    arcpy.AddField_management(table, "bedformWidth", "FLOAT")
    arcpy.AddField_management(table,"h","FLOAT")
    arcpy.AddField_management(table,"slope","FLOAT")
    arcpy.AddField_management(table,"symmetrydistance","FLOAT")

    cursor = arcpy.da.InsertCursor(table, ["ID", "TARsWidth", "TARsHeight", "symmetry", "bedformWidth","h","slope","symmetrydistance"])


    dist = []
    ele = []
    id_proi = table1[0][2]
    for pm in table1:
        id_next = pm[2]
        if id_next in wronglist: #如果id在错误序号中则直接跳过该错误序号id
            continue
        if id_next == id_proi:
            dist.append(pm[0]) #第一项是平面点在平面上的x 第二项是高程
            ele.append(pm[1])
        else:
            print id_proi
            distandhie = zip(dist, ele)
            #统计剖面性质
            cor1 = refId(pm[2], cor)  # 线方向改正数
            heigh, heighid = getH(distandhie)
            low1 = getlow1(distandhie, heighid)
            low2 = getlow2(distandhie, heighid)
            width = getWidth(low1, low2)
            asmy,sydist = getAsymmetry(distandhie, width, cor1,low1)
            bedrooms = getbedformWidth(low1, low2)
            h = geth(low1,low2,heigh)
            slope = getSlope(width,h)
            cursor.insertRow([id_proi, width, heigh[1], asmy, bedrooms, h, slope,sydist])
            id_proi = id_next
            print 1
            dist = []
            ele = []

        if pm == table1[-1]:
            print id_proi
            distandhie = zip(dist, ele)
            # 统计剖面性质
            cor1 = refId(pm[2], cor)  # 线方向改正数
            heigh, heighid = getH(distandhie)
            low1 = getlow1(distandhie, heighid)
            low2 = getlow2(distandhie, heighid)
            width = getWidth(low1, low2)
            asmy,sydist = getAsymmetry(distandhie, width, cor1, low1)
            bedrooms = getbedformWidth(low1, low2)
            h = geth(low1, low2, heigh)
            slope = getSlope(width, h)
            cursor.insertRow([id_proi, width, heigh[1], asmy, bedrooms, h, slope,sydist])

    print "finished"

