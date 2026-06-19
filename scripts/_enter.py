import time, ctypes, win32gui
from PIL import ImageGrab
from pywinauto.keyboard import send_keys
def find():
    o=[]
    def cb(h,_):
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h)=="Load Autodesk Family": o.append(h)
        return True
    win32gui.EnumWindows(cb,None); return o[0] if o else None
h=find()
ctypes.windll.user32.keybd_event(0x12,0,0,0)
try: win32gui.SetForegroundWindow(h)
except: pass
ctypes.windll.user32.keybd_event(0x12,0,2,0)
time.sleep(0.3)
send_keys("{ENTER}", pause=0.1)
time.sleep(3.0)
l,t,r,b=win32gui.GetWindowRect(h)
ImageGrab.grab(bbox=(l,t,r,b),all_screens=True).save(r"D:\RevitMCPBridge2026\scripts\_filtered.png")
print("saved")
