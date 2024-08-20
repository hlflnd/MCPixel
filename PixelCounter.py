from PIL import Image
import time
import os
import shutil
import Debug

wait=False
def getWait(Wait):
    global wait
    wait = Wait

logger = Debug.Logger(wait)

def countSample():
    su=0
    for file in os.listdir("./Sample_Folder"):
        img = Image.open(f"./Sample_Folder/{file}")   
        w,h=img.size
        su+=w*h
    logger.Log(f"{su} pixels in samples.")

def countImage(filename,warning,compress_rate=1.0,step=0.05):
    img = Image.open(f"./Image_Folder/{filename}")
    w,h=img.size
    su=w*h
    new_fn=filename
    logger.Log(f"{su} pixels in {filename}.")

    if(su>warning):
        logger.Warning(f"Warning!Target picture {filename} has over {warning} pixels.")
        logger.Warning("Compress the picture? Y/N")
        while 1:
            ans = input()
            if ans=="Y":
                img_resize = None
                while su>warning:
                    compress_rate-=step
                    img_resize = img.resize((int(w*compress_rate),int(h*compress_rate)))
                    resize_w,resize_h=img_resize.size
                    su=resize_h*resize_w
                img_resize.save("compressed_"+filename)
                new_fn="compressed_"+filename
                shutil.move(new_fn,f"./Image_Folder/{new_fn}")   
                logger.Log(f"New image {new_fn} has {su} pixels.")
                time.sleep(0.2)
                break
            elif ans=="N":
                break

    return new_fn
