import time

class Logger:
    def __init__(self,wait=False):
        self.wait=wait

    def Log(self,msg,endl="\n"):
        print("\033[0m"+msg,end=endl)
        if self.wait:
            time.sleep(0.1)
    
    def Warning(self,msg,endl="\n"):
        print("\033[33m"+msg+"\033[0m",end=endl)
        if self.wait:
            time.sleep(0.5)
    
    def Error(self,msg,endl="\n"):
        print("\033[31m"+msg+"\033[0m",end=endl)
        if self.wait:
            time.sleep(0.7)

class BugReporter(Logger):
    def __init__(self,filename,fillmode,wait=False):
        self.wait=wait
        self.filename=filename
        self.fillmode=fillmode

    def Report(self,code):
        match code:
            case 1:
                self.Error(f"Wrong picture:{self.filename}.")
            case 2:
                self.Error(f"Invalid fill mode:{self.fillmode}.")
            case 3:
                self.Error("Failed to write Colormap.json.")
            case 4:
                self.Error("Failed to read Colormap.json.")
            case _:
                self.Error("Unknown error?!")
