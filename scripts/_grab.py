import sys, win32gui
from PIL import ImageGrab
def find():
    o=[]
    def cb(h,_):
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h)=="Load Autodesk Family": o.append(h)
        return True
    win32gui.EnumWindows(cb,None); return o[0] if o else None
h=find()
if not h: print("NO DIALOG"); sys.exit()
l,t,r,b=win32gui.GetWindowRect(h)
ImageGrab.grab(bbox=(l,t,r,b),all_screens=True).save(r"D:\RevitMCPBridge2026\scripts\_grab.png")
print("saved", l,t,r,b)
