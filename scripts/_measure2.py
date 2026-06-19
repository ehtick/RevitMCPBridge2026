from PIL import Image
im = Image.open(r"D:\RevitMCPBridge2026\scripts\_probe_search.png").convert("RGB")
W,H = im.size
px = im.load()
# Search box: a near-white rounded input bar in the top strip (y 1%..8%), wide, centered.
# Scan each row in top strip for the longest run of near-white pixels.
best=None
for y in range(int(H*0.01), int(H*0.09)):
    run=0; runstart=0; bestrun=0; bs=0
    for x in range(int(W*0.20), int(W*0.85)):
        r,g,b=px[x,y]
        if r>240 and g>240 and b>240:
            if run==0: runstart=x
            run+=1
            if run>bestrun: bestrun=run; bs=runstart
        else:
            run=0
    if bestrun>200 and (best is None or bestrun>best[0]):
        best=(bestrun, bs, y)
if best:
    bestrun,bs,y=best
    cx=bs+bestrun//2
    print("SEARCH box row y",y,"runlen",bestrun,"xstart",bs,"center_x",cx,
          "frac", round(cx/W,4), round(y/H,4))
else:
    print("search box not found")
