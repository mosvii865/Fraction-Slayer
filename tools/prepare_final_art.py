"""Offline normalization only: Pillow/numpy/scipy; no game dependencies added."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
import numpy as np
from scipy import ndimage as nd
ROOT=Path(__file__).resolve().parents[1]
FRAMES={
'sawed_off':['sawed_off','sawed_off_fire','sawed_off_break_open','sawed_off_reload_insert','sawed_off_close'],
'assault':['assault','assault_fire','assault_reload_start','assault_reload_swap','assault_reload_end'],
'sniper':['sniper','sniper_fire','sniper_bolt_back','sniper_bolt_forward','sniper_reload'],
'lmg':['lmg','lmg_fire','lmg_reload_start','lmg_reload_box','lmg_reload_end'],
'rocket':['rocket','rocket_fire','rocket_reload_open','rocket_reload_insert','rocket_reload_close']}
preview=Image.new('RGB',(960,650),'#283239');d=ImageDraw.Draw(preview);meta={}
for row,(name,keys) in enumerate(FRAMES.items()):
 im=Image.open(ROOT/f'docs/final-sources/{name}.png').convert('RGBA');cw,ch=im.width//3,im.height//2
 for i,key in enumerate(keys):
  cell=im.crop(((i%3)*cw,(i//3)*ch,(i%3+1)*cw,(i//3+1)*ch))
  # Remove disconnected neighboring-cell fragments touching a vertical crop edge.
  alpha=np.array(cell.getchannel('A'));labels,n=nd.label(alpha>8);counts=np.bincount(labels.ravel());counts[0]=0;main=int(counts.argmax())
  edge=set(labels[:,0])|set(labels[:,-1]);edge.discard(main);edge.discard(0)
  for k in edge:alpha[labels==k]=0
  cell.putalpha(Image.fromarray(alpha))
  # Exact same source-cell transform for all five poses, idle is the renderer master.
  scale=min(160/cw,120/ch);reduced=cell.resize((round(cw*scale),round(ch*scale)),Image.Resampling.NEAREST)
  out=Image.new('RGBA',(160,120));out.alpha_composite(reduced,((160-reduced.width)//2,120-reduced.height));out.save(ROOT/f'ui/frontend/art/weapons/{key}.png')
  preview.paste(out,(i*160,row*130+10),out)
 cell=im.crop((2*cw,ch,3*cw,2*ch));box=cell.getbbox();crop=cell.crop(box)
 scale=min(60/crop.width,35/crop.height);small=crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.NEAREST)
 out=Image.new('RGBA',(64,40));out.alpha_composite(small,((64-small.width)//2,40-small.height));out.save(ROOT/f'ui/frontend/art/pickups/{name}_pickup.png')
 b=out.getbbox();meta[name]=[b[0],b[1],b[2]-b[0],b[3]-b[1]]
 preview.paste(out.resize((128,80),Image.Resampling.NEAREST),(810,row*130+45),out.resize((128,80),Image.Resampling.NEAREST));d.text((3,row*130),name,fill='white')
preview.save(ROOT/'docs/final_weapons_preview.png');(ROOT/'docs/final_pickup_bounds.json').write_text(json.dumps(meta,indent=2))
