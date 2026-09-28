"""Deterministic extraction of approved sheet; offline Pillow/numpy/scipy only."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage as nd
root=Path(__file__).resolve().parents[1]
src=Image.open(root/'docs/rivet_v1_approved_reference.png').convert('RGB')
# Fixed sampling scale, equal column widths. Bottom contact translations only.
frames=[('idle',255,178,522),('walk_1',678,178,523),('walk_2',1107,178,524),
        ('attack',255,613,944),('hurt',678,613,944),('death',1107,805,948)]
preview=Image.new('RGB',(960,680),'#283239');d=ImageDraw.Draw(preview)
for i,(name,x,top,bottom) in enumerate(frames):
 rgb=src.crop((x,top,x+410,bottom+1));a=np.asarray(rgb).astype(int)
 mask=(a.max(2)<125)|((a.max(2)-a.min(2))>30)
 mask=nd.binary_closing(mask,iterations=1);mask=nd.binary_fill_holes(mask)
 labels,n=nd.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0;mask=sizes[labels]>14
 # Ground streak belongs to the presentation sheet, not to the character.
 if name!='death':
  yy,xx=np.indices(mask.shape);globalx=xx+x;globaly=yy+top
  feet={'idle':[(356,399),(463,531)],'walk_1':[(759,818),(895,967)],'walk_2':[(1198,1254),(1339,1408)],'attack':[(294,332),(481,527)],'hurt':[(819,867),(963,1027)]}[name]
  allowed=np.zeros(mask.shape,bool)
  for l,r in feet:allowed|=(globalx>=l)&(globalx<=r)
  mask&=(globaly<bottom-7)|allowed
 # Remove enclosed sheet background between legs and inside the harness loop.
 mask&=~((a.min(2)>185)&((a.max(2)-a.min(2))<22))
 rgba=rgb.convert('RGBA');rgba.putalpha(Image.fromarray((mask*255).astype('uint8')))
 scaled=rgba.resize((round(410*.19),round(rgb.height*.19)),Image.Resampling.NEAREST)
 canvas=Image.new('RGBA',(80,80));canvas.alpha_composite(scaled,((80-scaled.width)//2,80-scaled.height))
 canvas.save(root/f'ui/frontend/art/sprites/rivet_{name}.png')
 big=canvas.resize((320,320),Image.Resampling.NEAREST);pos=((i%3)*320,(i//3)*340);preview.paste(big,pos,big);d.text((pos[0]+8,pos[1]+321),'rivet_'+name,fill='white')
preview.save(root/'docs/rivet_v1_preview.png')
