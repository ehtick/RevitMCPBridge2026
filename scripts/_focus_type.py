import sys, time, ctypes
import win32gui, win32api, win32con
from PIL import ImageGrab
from pywinauto.keyboard import send_keys

TITLE="Load Autodesk Family"
def find():
    o=[]
    def cb(h,_):
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h)==TITLE: o.append(h)
        return True
    win32gui.EnumWindows(cb,None); return o[0] if o else None

def force_fg(h):
    # ALT-key trick to bypass Windows foreground lock
    ctypes.windll.user32.keybd_event(0x12,0,0,0)
    time.sleep(0.05)
    try: win32gui.SetForegroundWindow(h)
    except Exception as e: print("SFW warn",e)
    ctypes.windll.user32.keybd_event(0x12,0,2,0)
    time.sleep(0.3)

def click(h,fx,fy):
    l,t,r,b=win32gui.GetWindowRect(h); w,ht=r-l,b-t
    x,y=l+int(w*fx),t+int(ht*fy)
    win32api.SetCursorPos((x,y)); time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)
    time.sleep(0.25)

h=find()
print("hwnd",h)
force_fg(h)
print("foreground now:", win32gui.GetWindowText(win32gui.GetForegroundWindow()))
click(h,0.50,0.040)    # search box (lower, clear of title bar)
time.sleep(0.3)
send_keys("^a", pause=0.05)
send_keys("{BACKSPACE}", pause=0.05)
send_keys("lumber", pause=0.06)
time.sleep(1.0)
l,t,r,b=win32gui.GetWindowRect(h)
ImageGrab.grab(bbox=(l,t,r,b),all_screens=True).save(r"D:\RevitMCPBridge2026\scripts\_focus_type.png")
print("saved shot")
