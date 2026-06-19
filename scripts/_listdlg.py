import win32gui
def cb(h,acc):
    if win32gui.IsWindowVisible(h):
        t=win32gui.GetWindowText(h)
        if t and t!="" and ("Revit" in t or "Family" in t or "amily" in t or len(t)<40):
            acc.append((h,t))
    return True
acc=[]
win32gui.EnumWindows(cb,acc)
for h,t in acc: print(h, "|", t)
