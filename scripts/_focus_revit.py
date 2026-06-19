import time, ctypes, win32gui
def find(sub):
    o=[]
    def cb(h,_):
        if win32gui.IsWindowVisible(h) and sub in win32gui.GetWindowText(h): o.append(h)
        return True
    win32gui.EnumWindows(cb,None); return o[0] if o else None
h=find("Autodesk Revit 2026")
print("revit hwnd", h)
if h:
    ctypes.windll.user32.keybd_event(0x12,0,0,0)
    try: win32gui.SetForegroundWindow(h)
    except Exception as e: print("warn",e)
    ctypes.windll.user32.keybd_event(0x12,0,2,0)
    time.sleep(0.4)
    print("fg now:", win32gui.GetWindowText(win32gui.GetForegroundWindow()))
