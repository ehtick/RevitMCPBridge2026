import win32gui, win32con
def find():
    o=[]
    def cb(h,_):
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h)=="Load Autodesk Family": o.append(h)
        return True
    win32gui.EnumWindows(cb,None); return o[0] if o else None
h=find()
if h:
    win32gui.SendMessage(h, win32con.WM_CLOSE, 0, 0)
    print("closed", h)
else:
    print("no dialog")
