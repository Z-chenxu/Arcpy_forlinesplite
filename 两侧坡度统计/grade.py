# coding=utf-8
import arcpy
import numpy as np
from arcpy import env


#统计两侧坡度
#提取剖面线高程分别拟合两侧坡度并写在表格中

path = r""
table_path = r""

def getH(distandheigth):#1
    heigh = distandheigth[0]
    heighid = 0
    # 首先遍历出最高点
    for i in range(0, len(distandheigth)):
        if distandheigth[i][1] > heigh[1]:
            heigh = distandheigth[i]
            heighid = i
    return heigh,heighid

def getlow1(distandheigth,heighid): #2
    low1 = distandheigth[heighid]
    low1id = 0
    for i in range(0,heighid):
        if distandheigth[i][1] < low1[1]:
            low1 = distandheigth[i]
            low1id = i
    return low1,low1id

#得到第二个截面最低点
def getlow2(distandheigth,heighid):  #3
    low1 = distandheigth[heighid]
    low1id = 0
    for i in range(heighid,len(distandheigth)):
        if distandheigth[i][1] < low1[1]:
            low1 = distandheigth[i]
            low1id = i
    return low1,low1id

def extractHei(path):
    '''

    :param path: 输入的线采样高程序列
    :return: 输出格式 [[id,[dist:ele]],[]]
    '''
    table1 = arcpy.da.TableToNumPyArray(path,('FIRST_DIST', 'FIRST_Z', 'LINE_ID'))
    dist = []
    ele = []
    id_proi = table1[0][2]
    result = []
    for pm in table1:
        id_next = pm[2]
        if id_next == id_proi:
            dist.append(pm[0])  # 第一项是平面点在平面上的x 第二项是高程
            ele.append(pm[1])
        else:
            print id_proi
            distandhie = zip(dist, ele)
            poum = [id_proi,distandhie]
            result.append(poum)
            id_proi = id_next
            dist = []
            ele = []
    return result

def fitting(disandheig,id1,id2):
    id = []
    heig = []
    for i in range(id1,id2):
        id.append(i)
        heig.append(disandheig[i][1])
    f1 = np.polyfit(id, heig, 1)  # 直线拟合
    return f1


def processpoum(poum1):
    id = poum1[0]
    disandheig = poum1[1]
    highest,heighid = getH(disandheig)
    low1,low1id = getlow1(disandheig,heighid)
    low2,low2id = getlow2(disandheig,heighid)
    poum_xielv1 = fitting(disandheig,low1id,heighid)
    poum_xielv2 = fitting(disandheig,heighid,low2id)
    return poum_xielv1,poum_xielv2

def createtable():
    table1 = arcpy.CreateTable_management(table_path, path)
    arcpy.AddField_management(table1, "ID","SHORT")
    arcpy.AddField_management(table1,"fit_upshill","FLOAT")
    arcpy.AddField_management(table1,"fit_downshill","FLOAT")

def insertTable(table1,id,fit1,fit2):
    cursor1 = arcpy.da.InsertCursor(table1, ["ID","fit_upshill","fit_downshill"])
    cursor1.insertRow(id,fit1,fit2)

if __name__ == '__main__':
    env = r"D:\zhongrong\workplace.gdb"
    result = extractHei(path)

    table1 = arcpy.CreateTable_management(table_path, path)
    arcpy.AddField_management(table1, "ID", "SHORT")
    arcpy.AddField_management(table1, "fit_upshill", "FLOAT")
    arcpy.AddField_management(table1, "fit_downshill", "FLOAT")
    cursor1 = arcpy.da.InsertCursor(table1, ["ID", "fit_upshill", "fit_downshill"])


    for poum in result:
        fit1,fit2 = processpoum(poum)
        cursor1.insertRow(id, fit1, fit2)
