"""Dump the UIA control tree of the 'Load Autodesk Family' dialog by HANDLE.
Tells us whether the search box / results / Load button are real UIA controls
or an opaque web (CEF) view."""
import sys, io, traceback
import win32gui

OUT = r"D:\RevitMCPBridge2026\scripts\_cloud_dialog_tree.txt"

def find_hwnd():
    hwnds = []
    def cb(h, _):
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h) == "Load Autodesk Family":
            hwnds.append(h)
        return True
    win32gui.EnumWindows(cb, None)
    return hwnds[0] if hwnds else None

def main():
    from pywinauto import Desktop
    buf = io.StringIO()
    try:
        hwnd = find_hwnd()
        if not hwnd:
            buf.write("NO dialog window found\n")
        else:
            buf.write("hwnd = %s\n" % hwnd)
            dlg = Desktop(backend="uia").window(handle=hwnd)
            old = sys.stdout
            sys.stdout = buf
            try:
                dlg.print_control_identifiers(depth=8)
            finally:
                sys.stdout = old
    except Exception as e:
        buf.write("ERROR: %s\n%s\n" % (e, traceback.format_exc()))
    txt = buf.getvalue()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(txt)
    print("WROTE", OUT, "len", len(txt))
    # compact summary
    import re
    for line in txt.splitlines():
        low = line.lower()
        if any(k in low for k in ("edit", "button", "search", "load", "cancel",
                                  "list", "document", "chrome", "custom", "pane",
                                  "hyperlink", "text", "combobox", "group")):
            print(line.strip()[:170])

if __name__ == "__main__":
    main()
