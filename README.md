--mc像素生成器：用于在Minecraft服务器中生成像素图--
首先，你得有个mc服务器，并安装raspberryjuice插件
程序使用mcpi库：pip install mcpi

*Image_Folder*
图片文件夹，程序使用该文件夹下的图片生成

*Sample_Folder*
模板文件夹，像素图所用方块的材质，文件名：ID-Data (Type-Subtype) 
当update_JSON为True时，会读取其中内容并写入Colormap.json，否则直接读取

*_pycache_*
不必理会

*Colormap.json*
用于存储模板rgb与id信息，update_JSON为True时会刷新

*Debug.py*
含2个类，Logger用于输出信息，BugReporter用于根据返回值输出问题

*PixelCounter.py*
用于计算目标图片与模板的像素个数，并判断是否压缩图片

*Main.py*
文件import下面的部分可修改：

--filename，程序使用的图片名称（带扩展名），图片放在Image_Folder文件夹中

--fillmode，填充方式:x-y,x-z,y-z三种，表示mc坐标轴

--player_name，使用该玩家的坐标

--update_JSON，是否刷新json文件，如不手动添加模板建议设为False

--time_monitor = True，是否监测程序运行时间

--wait = True，控制台输出是否等待，有无差距不大

--warning = 30000，图片像素高于该值时警告，像素过高可能导致服务器严重卡顿！

--compress_rate = 1.0，图片压缩初始比例，无需修改

--step = 0.05，每次压缩降低的比例，无需修改

Main.py用于连接mc并填充方块，使用时将166-173行的注释解除
