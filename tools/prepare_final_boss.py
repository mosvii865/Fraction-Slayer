"""Offline packaging of generated sheets, fixed per-family scale; Pillow only."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
import numpy as np
from scipy import ndimage as nd
ROOT=Path(__file__).resolve().parents[1]
SIZES={'boss':(128,128)}
POSES=['idle','walk_1','walk_2','attack','hurt','death']
preview=Image.new('RGB',(960,8*150),'#283239');draw=ImageDraw.Draw(preview);metadata={}
for row,(name,size) in enumerate(SIZES.items()):
 im=Image.open(ROOT/f'docs/final-sources/{name}.png').convert('RGBA');cw,ch=im.width//3,im.height//2
 # Isolate connected characters before cropping: several attack limbs cross grid edges.
 alpha=np.array(im.getchannel('A'));lab,n=nd.label(nd.binary_dilation(alpha>16,iterations=3))
 counts=np.bincount(lab.ravel());main=np.argsort(counts[1:])[-6:]+1
 centers={int(k):nd.center_of_mass(alpha>16,lab,int(k)) for k in main}
 main=sorted(main,key=lambda k:(int(centers[int(k)][0]>=im.height/2),centers[int(k)][1]))
 owner=np.zeros(n+1,int)-1
 for k in range(1,n+1):
  cy,cx=nd.center_of_mass(alpha>16,lab,k)
  if not np.isfinite(cx):continue
  owner[k]=min(range(6),key=lambda j:(cx-centers[int(main[j])][1])**2+(cy-centers[int(main[j])][0])**2)
 cells=[]
 for i in range(6):
  isolated=im.copy();isolated.putalpha(Image.fromarray(np.where(owner[lab]==i,alpha,0).astype('uint8')))
  cells.append(isolated.crop(((i%3)*cw-100,(i//3)*ch-100,(i%3+1)*cw+100,(i//3+1)*ch+100)))
 # The generated alternate stride faced the other way in these families.
 # Normalize heading by reflection, not by redrawing or changing per-frame scale.
 if name in {'stalker','furnace_hound'}:
  cells[2]=cells[2].transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 cw+=200;ch+=200
 bounds=[c.getchannel('A').point(lambda x:255 if x>16 else 0).getbbox() for c in cells]
 # One uniform scale for entire family, NEVER fit each pose separately.
 spread=max(max(cw/2-b[0],b[2]-cw/2) for b in bounds)*2
 height=max(b[3]-b[1] for b in bounds)
 scale=min((size[0]-4)/spread,(size[1]-4)/height)
 metadata[name]={'canvas':size,'scale':scale,'bounds':bounds}
 for col,(pose,cell,b) in enumerate(zip(POSES,cells,bounds)):
  scaled=cell.resize((round(cw*scale),round(ch*scale)),Image.Resampling.NEAREST)
  canvas=Image.new('RGBA',size)
  canvas.alpha_composite(scaled,(round((size[0]-scaled.width)/2),size[1]-1-round(b[3]*scale)))
  canvas.save(ROOT/f'ui/frontend/art/sprites/{name}_{pose}.png')
  big=canvas.resize((int(size[0]*1.2),int(size[1]*1.2)),Image.Resampling.NEAREST)
  preview.paste(big,(col*160+(160-big.width)//2,row*150+12),big)
 draw.text((3,row*150),name,fill='white')
preview.save(ROOT/'docs/final_boss_preview.png')
(ROOT/'docs/final_boss_normalization.json').write_text(json.dumps(metadata,indent=2))
