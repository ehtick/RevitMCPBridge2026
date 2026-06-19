"""Detect the left-column category text rows in a dialog screenshot.
Validates the runtime approach: find evenly-spaced text rows, index to a target
category by its known position in the Autodesk content category list."""
from PIL import Image

# Known Browse category order in the Load Autodesk Family dialog (alphabetical)
CATS = ["Annotations","Boundary Conditions","Cable Tray","Casework","Columns",
"Conduit","Curtain Panel by Pattern","Curtain Wall Panels","Detail Items","Doors",
"Duct","Electrical","Entourage","Fire Protection","Furniture","Furniture System",
"Lighting","Mass","Mechanical","MEP Fabrication","Openings","Pipe","Planting",
"Plumbing","Profiles","Railings","Route Analysis","Site","Specialty Equipment",
"Structural Connections","Structural Foundations","Structural Framing",
"Structural Precast","Structural Rebar Couplers","Structural Rebar Shapes",
"Structural Retaining Walls","Structural Stiffeners","Structural Trusses",
"Sustainable Building","Titleblocks","Vertical Circulation"]

im = Image.open(r"D:\RevitMCPBridge2026\scripts\_probe_search.png").convert("L")
W,H = im.size
px = im.load()
x0,x1 = int(W*0.012), int(W*0.14)   # left category column band
rows=[]
y=int(H*0.02)
while y < int(H*0.98):
    dark = sum(1 for x in range(x0,x1) if px[x,y] < 120)
    rows.append((y, dark))
    y+=1
# group consecutive dark rows into text-row centers
centers=[]
in_row=False; start=0
for y,dark in rows:
    if dark >= 6 and not in_row:
        in_row=True; start=y
    elif dark < 6 and in_row:
        in_row=False; centers.append((start+y)//2)
print("detected text rows:", len(centers))
# Find the longest evenly-spaced run (the category list)
if len(centers) >= 10:
    # compute pitches
    import statistics
    pitches=[centers[i+1]-centers[i] for i in range(len(centers)-1)]
    med=statistics.median(pitches)
    print("median pitch", med)
    # keep run where pitch ~ med
    run=[centers[0]]
    for i in range(1,len(centers)):
        if abs((centers[i]-run[-1]) - med) <= max(4, med*0.4):
            run.append(centers[i])
        else:
            if len(run) >= len(CATS)-3: break
            run=[centers[i]]
    print("category run length", len(run), "first y", run[0], "last y", run[-1])
    for name in ["Structural Framing","Structural Trusses"]:
        idx=CATS.index(name)
        if idx < len(run):
            yy=run[idx]
            print(f"  {name}: idx {idx}, y={yy}, frac_y={round(yy/H,4)}")
        else:
            print(f"  {name}: idx {idx} beyond detected run ({len(run)})")
