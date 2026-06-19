from PIL import Image
im = Image.open(r"D:\RevitMCPBridge2026\scripts\_probe_search.png").convert("RGB")
W,H = im.size
print("img size", W, H)
px = im.load()
# Blue Load button (Autodesk blue). Scan bottom-right quadrant.
minx,miny,maxx,maxy = W,H,0,0; cnt=0
for y in range(int(H*0.90), H):
    for x in range(int(W*0.70), W):
        r,g,b = px[x,y]
        if b>165 and 70<g<205 and r<100 and b>r+70:
            cnt+=1
            minx=min(minx,x);miny=min(miny,y);maxx=max(maxx,x);maxy=max(maxy,y)
if cnt>20:
    cx=(minx+maxx)//2; cy=(miny+maxy)//2
    print("LOAD bbox", minx,miny,maxx,maxy, "center", cx,cy, "frac", round(cx/W,4), round(cy/H,4), "n", cnt)
else:
    print("blue not found, cnt", cnt)
