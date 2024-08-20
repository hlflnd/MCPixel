#coding=gbk
from mcpi.minecraft import Minecraft
import mcpi.block as block
from PIL import Image
import os
import json
import time
import PixelCounter
import Debug

#----------------------------------------------------------------------
filename = "cjt.jpg"   #程序使用的图片名称（带扩展名）
fillmode = "x-y"        #填充方式:x-y,x-z,y-z
player_name = "hlflnd"  #使用该玩家的坐标

update_JSON = False     #是否刷新json文件
time_monitor = True     #是否监测程序运行时间
wait = True            #控制台输出是否等待

warning = 30000        #图片像素高于该值时警告
compress_rate = 1.0      #图片压缩初始比例    
step = 0.05              #每次压缩降低的比例
#----------------------------------------------------------------------

PixelCounter.getWait(wait)
logger = Debug.Logger(wait)
bReporter=Debug.BugReporter(filename,fillmode,wait)

if time_monitor:
    t1=time.time()
    PixelCounter.countSample()
    
filename = PixelCounter.countImage(filename,warning,compress_rate,step)
    
def setJSON():
    global RGB_to_file
    newRTF=dict()
    for key in RGB_to_file.keys():
        newRTF.update({str(key):RGB_to_file[key]}) #转换为字符串
    try:
        with open("./Colormap.json","w") as f:
            json.dump(newRTF,f,indent=4) #写入json
        return 1
    except:
        return 0

def getJSON():
    global RGB_to_file
    RGB_to_file=dict()
    try:
        with open("./Colormap.json","r") as f:
            newRTF = json.load(f) #解析json，得到键为字符串类型的字典
        for key in newRTF.keys():
            k=key.strip("()").split(",")
            RGB_to_file.update({(k[0],k[1],k[2]):newRTF[key]}) #将字符串转换为元组
        return 1
    except:
        return 0

def loadColormap():     #加载Sample_Folder文件夹，读取bmp模板的RGB和id数据
    global RGB_to_file
    RGB_to_file=dict()
    for file in os.listdir("./Sample_Folder"):
        img = Image.open(f"./Sample_Folder/{file}")   
        w,h=img.size
        r=0;g=0;b=0
        for i in range(w):
            for j in range(h):
                pix=img.getpixel((i,j))    #获取每个像素的RGB数据
                r+=pix[0];g+=pix[1];b+=pix[2]
        s=w*h
        key=(r/s,g/s,b/s)
        ids=file.split('.')[0].split('-')
        value=(int(ids[0]),int(ids[1]))
        RGB_to_file.update({key:value})    #计算平均RGB值后，以键值对形式将RGB和
                                            #id存储在RGB_to_file字典中
def getImage(img):    #加载Image_Folder文件夹，读取目标图片
    global width,height,newImg
    try:
        logger.Log("\nParsing picture...")
        image = Image.open(f"./Image_Folder/{img}")
        width,height=image.size    #目标图片的长宽（像素）
        newImg=[]
        logger.Log(f"Image mode:{image.mode}")
        if image.mode == "RGB":
            for i in range(width):
                newImg.append([])
                for j in range(height):
                    r,g,b = image.getpixel((i,j))
                    newImg[i].append((r,g,b))    #读取目标图片各个像素的RGB/RGBA数据
        elif image.mode == "RGBA":
            for i in range(width):
                newImg.append([])
                for j in range(height):
                    r,g,b,alpha = image.getpixel((i,j))
                    newImg[i].append((r,g,b,alpha)) 
        image.close()
        logger.Log("Parsing is complete.\n")
        return image.mode
    except:
        return 0

def getVarp(r,g,b,key):    #计算图片RGB和模板RGB的方差
    nr=float(key[0]);ng=float(key[1]);nb=float(key[2])
    varp=((nr-r)**2+(ng-g)**2+(nb-b)**2)/3
    return varp

def match(img_mode):    #将RGB数据形式的目标图片与最为匹配的模板相匹配，将id另外存储在列表中返回
    global newImg,RGB_to_file,width,height
    blockmap=[]
    logger.Log("\nMatching picture...")
    for i in range(width):
        blockmap.append([])
        for j in range(height):
            pix=newImg[i][j]
            r=pix[0];g=pix[1];b=pix[2]
            minvarp=10e5    #每次更新方差最大值（应该不会有比这个数更大的了吧）
            for key in RGB_to_file.keys():    #遍历模板的RGB数据
                varp = getVarp(r,g,b,key)    #计算当前模板与目标像素的方差
                if varp < minvarp:    #取最小方差，若更小则记录id
                    minvarp = varp
                    blockid = RGB_to_file[key]
            if img_mode == "RGBA" and pix[-1] == 0:
                blockid = (0,0)
            blockmap[i].append(blockid)    #取最为匹配的模板id记录在对应像素
    logger.Log("Matching is complete.")
    return blockmap

def drawFrame(blockmap,Id,fillmode):    #在mc中填充方块
    global width,height,mc
    x,y,z=mc.entity.getTilePos()
    
    match fillmode:
        case "x-y":
            for i in range(width):
                 for j in range(height):
                    fillblock=blockmap[i][j] 
                    mc.setBlock(x+i,y+height-j,z-3,fillblock[0],fillblock[1])
            return 1
        case "x-z":
            for i in range(width):
                 for j in range(height):
                    fillblock=blockmap[i][j] 
                    mc.setBlock(x+i,y-3,z+j,fillblock[0],fillblock[1])
            return 1
        case "y-z":
             for i in range(width):
                 for j in range(height):
                    fillblock=blockmap[i][j] 
                    mc.setBlock(x-3,y+height-j,z-i,fillblock[0],fillblock[1])
             return 1
        case _:
             return 0

if update_JSON:
    loadColormap()
    if setJSON()==0:
        bReporter.Report(3)
if getJSON()==0:
    bReporter.Report(4)
img_mode=getImage(filename)
if img_mode == 0:
    bReporter.Report(1)

blockmap = match(img_mode)
'''
mc=Minecraft.create()
playerId = mc.getPlayerEntityId(player_name)
if (drawFrame(blockmap,playerId,fillmode))==0:
    bReporter.Report(2)
else:
    logger.Log("Complete!",endl="")
'''
if time_monitor:
    t2=time.time()
    logger.Log(f"Cost {t2-t1} seconds.")
