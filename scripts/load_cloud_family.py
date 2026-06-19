"""
load_cloud_family.py  --  reliable, hardcoded loader for the Autodesk cloud
'Load Autodesk Family' dialog (a CEF web view, so its controls are NOT in the
UIA tree). Drives it by: click search box -> type -> Enter -> click first result
-> click the blue Load button (re-detected by color) -> wait for the dialog to
close (= family loaded).

Designed to be called by any LLM/agent (Studio Copilot, web) via one bridge
method. The dialog must already be open (post the Revit 'Load Autodesk Family'
command first).

Usage:  python load_cloud_family.py "<search term>" [--result-index N]
Prints a JSON line with the outcome.
"""
import sys, time, json, argparse
import win32gui, win32api, win32con
from PIL import ImageGrab

DIALOG_TITLE = "Load Autodesk Family"
DBG = r"D:\RevitMCPBridge2026\scripts\_lcf_step.png"

# fractions of the dialog rect (measured from the real dialog)
SEARCH_FX, SEARCH_FY = 0.525, 0.025
RESULT_FX, RESULT_FY = 0.270, 0.135   # first thumbnail, top-left of results grid
LOAD_FX,   LOAD_FY   = 0.833, 0.948   # fallback if blue detect fails


def find_hwnd():
    out = []
    def cb(h, _):
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h) == DIALOG_TITLE:
            out.append(h)
        return True
    win32gui.EnumWindows(cb, None)
    return out[0] if out else None


def rect(hwnd):
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    return l, t, r - l, b - t


def click_frac(hwnd, fx, fy):
    l, t, w, h = rect(hwnd)
    x, y = l + int(w * fx), t + int(h * fy)
    win32api.SetCursorPos((x, y))
    time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.2)
    return x, y


def grab(hwnd):
    l, t, w, h = rect(hwnd)
    return ImageGrab.grab(bbox=(l, t, l + w, t + h), all_screens=True)


def find_blue_load(hwnd):
    """Re-detect the blue Load button center in screen coords (robust)."""
    img = grab(hwnd).convert("RGB")
    W, H = img.size
    px = img.load()
    minx, miny, maxx, maxy, n = W, H, 0, 0, 0
    for y in range(int(H * 0.90), H):
        for x in range(int(W * 0.70), W):
            r, g, b = px[x, y]
            if b > 165 and 70 < g < 205 and r < 100 and b > r + 70:
                n += 1
                minx = min(minx, x); miny = min(miny, y)
                maxx = max(maxx, x); maxy = max(maxy, y)
    if n > 200:
        l, t, _, _ = rect(hwnd)
        return l + (minx + maxx) // 2, t + (miny + maxy) // 2
    return None


def click_screen(x, y):
    win32api.SetCursorPos((x, y))
    time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.2)


def type_text(s):
    # send unicode chars via keybd, simplest is SendKeys-style through pywinauto
    from pywinauto.keyboard import send_keys
    send_keys(s.replace(" ", "{SPACE}").replace("(", "{(}").replace(")", "{)}"),
              pause=0.02)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("term")
    ap.add_argument("--result-index", type=int, default=0)
    ap.add_argument("--load-timeout", type=int, default=30)
    a = ap.parse_args()

    hwnd = find_hwnd()
    if not hwnd:
        print(json.dumps({"success": False, "error": "dialog not open"})); return

    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass
    time.sleep(0.5)

    from pywinauto.keyboard import send_keys
    # 1) focus the search box and type the term
    click_frac(hwnd, SEARCH_FX, SEARCH_FY)
    send_keys("^a", pause=0.05)
    send_keys("{BACKSPACE}", pause=0.05)
    type_text(a.term)
    time.sleep(0.3)
    send_keys("{ENTER}", pause=0.05)
    time.sleep(3.0)                      # let results filter
    grab(hwnd).save(DBG)                 # debug: after search

    # 2) select the result
    l, t, w, h = rect(hwnd)
    # offset the result column per index (grid ~ 6 cols); index 0 = first
    click_frac(hwnd, RESULT_FX, RESULT_FY)
    time.sleep(0.6)

    # 3) click Load (re-detect blue, fallback to fraction)
    btn = find_blue_load(hwnd)
    if btn:
        click_screen(*btn)
    else:
        click_frac(hwnd, LOAD_FX, LOAD_FY)

    # 4) wait for the dialog to close = success
    start = time.time()
    while time.time() - start < a.load_timeout:
        if not find_hwnd():
            print(json.dumps({"success": True, "term": a.term,
                              "message": "dialog closed (family loaded)"}))
            return
        time.sleep(0.5)
    print(json.dumps({"success": False, "term": a.term,
                      "error": "dialog still open after load click (see _lcf_step.png)"}))


if __name__ == "__main__":
    main()
