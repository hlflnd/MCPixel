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
filename = "cjt.jpg"   #����ʹ�õ�ͼƬ���ƣ�����չ����
fillmode = "x-y"        #��䷽ʽ:x-y,x-z,y-z
player_name = "hlflnd"  #ʹ�ø���ҵ�����

update_JSON = False     #�Ƿ�ˢ��json�ļ�
time_monitor = True     #�Ƿ����������ʱ��
wait = True            #����̨����Ƿ�ȴ�

warning = 30000        #ͼƬ���ظ��ڸ�ֵʱ����
compress_rate = 1.0      #ͼƬѹ����ʼ����    
step = 0.05              #ÿ��ѹ�����͵ı���
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
        newRTF.update({str(key):RGB_to_file[key]}) #ת��Ϊ�ַ���
    try:
        with open("./Colormap.json","w") as f:
            json.dump(newRTF,f,indent=4) #д��json
        return 1
    except:
        return 0

def getJSON():
    global RGB_to_file
    RGB_to_file=dict()
    try:
        with open("./Colormap.json","r") as f:
            newRTF = json.load(f) #����json���õ���Ϊ�ַ������͵��ֵ�
        for key in newRTF.keys():
            k=key.strip("()").split(",")
            RGB_to_file.update({(k[0],k[1],k[2]):newRTF[key]}) #���ַ���ת��ΪԪ��
        return 1
    except:
        return 0

def loadColormap():     #����Sample_Folder�ļ��У���ȡbmpģ���RGB��id����
    global RGB_to_file
    RGB_to_file=dict()
    for file in os.listdir("./Sample_Folder"):
        img = Image.open(f"./Sample_Folder/{file}")   
        w,h=img.size
        r=0;g=0;b=0
        for i in range(w):
            for j in range(h):
                pix=img.getpixel((i,j))    #��ȡÿ�����ص�RGB����
                r+=pix[0];g+=pix[1];b+=pix[2]
        s=w*h
        key=(r/s,g/s,b/s)
        ids=file.split('.')[0].split('-')
        value=(int(ids[0]),int(ids[1]))
        RGB_to_file.update({key:value})    #����ƽ��RGBֵ���Լ�ֵ����ʽ��RGB��
                                            #id�洢��RGB_to_file�ֵ���
def getImage(img):    #����Image_Folder�ļ��У���ȡĿ��ͼƬ
    global width,height,newImg
    try:
        logger.Log("\nParsing picture...")
        image = Image.open(f"./Image_Folder/{img}")
        width,height=image.size    #Ŀ��ͼƬ�ĳ������أ�
        newImg=[]
        logger.Log(f"Image mode:{image.mode}")
        if image.mode == "RGB":
            for i in range(width):
                newImg.append([])
                for j in range(height):
                    r,g,b = image.getpixel((i,j))
                    newImg[i].append((r,g,b))    #��ȡĿ��ͼƬ�������ص�RGB/RGBA����
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

def getVarp(r,g,b,key):    #����ͼƬRGB��ģ��RGB�ķ���
    nr=float(key[0]);ng=float(key[1]);nb=float(key[2])
    varp=((nr-r)**2+(ng-g)**2+(nb-b)**2)/3
    return varp

def match(img_mode):    #��RGB������ʽ��Ŀ��ͼƬ����Ϊƥ���ģ����ƥ�䣬��id����洢���б��з���
    global newImg,RGB_to_file,width,height
    blockmap=[]
    logger.Log("\nMatching picture...")
    for i in range(width):
        blockmap.append([])
        for j in range(height):
            pix=newImg[i][j]
            r=pix[0];g=pix[1];b=pix[2]
            minvarp=10e5    #ÿ�θ��·������ֵ��Ӧ�ò����б������������˰ɣ�
            for key in RGB_to_file.keys():    #����ģ���RGB����
                varp = getVarp(r,g,b,key)    #���㵱ǰģ����Ŀ�����صķ���
                if varp < minvarp:    #ȡ��С�������С���¼id
                    minvarp = varp
                    blockid = RGB_to_file[key]
            if img_mode == "RGBA" and pix[-1] == 0:
                blockid = (0,0)
            blockmap[i].append(blockid)    #ȡ��Ϊƥ���ģ��id��¼�ڶ�Ӧ����
    logger.Log("Matching is complete.")
    return blockmap

def drawFrame(blockmap,Id,fillmode):    #��mc����䷽��
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
