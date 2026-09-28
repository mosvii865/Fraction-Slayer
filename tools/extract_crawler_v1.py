"""Offline extraction only; requires Pillow, numpy and scipy (not game dependencies)."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage as nd
root=Path(__file__).resolve().parents[1]
src=Image.open(root/'docs/crawler_v1_approved_reference.png').convert('RGB')
out=root/'ui/frontend/art/sprites'
# Equal source widths and common sampling scale; translations only align contact planes.
frames=[('idle',0,235,477),('walk_1',514,235,477),('walk_2',1027,235,477),('attack',0,625,886),('hurt',514,625,886),('death',1027,690,903)]
preview=Image.new('RGB',(960,480),'#283239');d=ImageDraw.Draw(preview)
for i,(name,x,top,floor) in enumerate(frames):
    rgb=src.crop((x+8,top,min(x+508,1536),floor+1))
    a=np.asarray(rgb).astype(int)
    # Connected dark outlines + chromatic panels, then fill enclosed steel highlights.
    mask=(a.max(2)<105)|((a.max(2)-a.min(2)>18)&(a.min(2)<150))
    mask=nd.binary_closing(mask,iterations=1)
    mask=nd.binary_fill_holes(mask)
    labels,n=nd.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0
    mask=sizes[labels]>60
    rgba=rgb.convert('RGBA');rgba.putalpha(Image.fromarray((mask*255).astype('uint8')))
    # Fixed 0.15 scale for all frames; no individual bounding-box fit.
    scaled=rgba.resize((round(rgb.width*.15),round(rgb.height*.15)),Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',(80,56));canvas.alpha_composite(scaled,((80-scaled.width)//2,56-scaled.height))
    canvas.save(out/f'crawler_{name}.png')
    pos=((i%3)*320,(i//3)*240)
    preview.paste(canvas.resize((320,224),Image.Resampling.NEAREST),pos,canvas.resize((320,224),Image.Resampling.NEAREST))
    d.text((pos[0]+8,pos[1]+225),f'crawler_{name}',fill='white')
(root/'docs').mkdir(exist_ok=True)
preview.save(root/'docs/crawler_v1_preview.png')
