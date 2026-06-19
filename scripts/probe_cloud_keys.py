"""Probe: can we drive the CEF 'Load Autodesk Family' web view by keyboard?
Focus the dialog, type a search term, Enter, screenshot the result."""
import sys, time, win32gui
from pywinauto import Desktop
from pywinauto.keyboard import send_keys

def find_hwnd():
    out=[]
    def cb(h,_):
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h)=="Load Autodesk Family":
            out.append(h)
        return True
    win32gui.EnumWindows(cb,None)
    return out[0] if out else None

term = sys.argv[1] if len(sys.argv)>1 else "Dimension Lumber"
hwnd = find_hwnd()
if not hwnd:
    print("NO_DIALOG"); sys.exit(1)
dlg = Desktop(backend="uia").window(handle=hwnd)
dlg.set_focus(); time.sleep(0.6)
# Many web content browsers auto-focus the search box. Try typing directly.
send_keys("^a", pause=0.05)      # select any existing text
send_keys("{BACKSPACE}", pause=0.05)
send_keys(term, with_spaces=True, pause=0.02)
time.sleep(0.4)
send_keys("{ENTER}", pause=0.05)
print("typed+enter:", term)
time.sleep(3.5)
# screenshot the dialog region
import ctypes
ctypes.windll.user32.SetProcessDPIAware()
from PIL import ImageGrab
l,t,r,b = win32gui.GetWindowRect(hwnd)
img = ImageGrab.grab(bbox=(l,t,r,b), all_screens=True)
img.save(r"D:\RevitMCPBridge2026\scripts\_probe_search.png")
print("SHOT", l,t,r,b)
