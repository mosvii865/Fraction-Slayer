"""Streamlit real + Chromium: visual fixtures in all four existing levels.
Not a campaign walkthrough or balance test. No production gameplay code changed.
"""
from pathlib import Path
import json,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results/visual-sprint';OUT.mkdir(parents=True,exist_ok=True)
PORT=8550
LEVELS={'workshop':['loader'],'factory':['sentinel','gunner','foreman'],'laboratory':['stalker','k32'],'foundry':['furnace_hound','forge_brute']}
def main():
 log=(OUT/'streamlit.log').open('w');server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port',str(PORT),'--server.address','127.0.0.1'],cwd=ROOT,stdout=log,stderr=log);results=[]
 try:
  for _ in range(200):
   try:
    if urllib.request.urlopen(f'http://127.0.0.1:{PORT}/_stcore/health',timeout=.5).status==200:break
   except Exception:time.sleep(.1)
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for mobile in [False,True]:
    context=browser.new_context(viewport={'width':900 if mobile else 1280,'height':405 if mobile else 720},has_touch=mobile,is_mobile=mobile);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{PORT}');page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame()
    f.locator('#new').click();f.locator('#next').click();f.locator('#start').click();f.locator('#enter').click();f.wait_for_function('FS.playing&&!Bridge.busy&&FSArt.has("sprites","forge_brute_death")')
    f.evaluate('''()=>{window.draws=[];const c=document.querySelector('#world').getContext('2d'),draw=c.drawImage;c.drawImage=function(img,...a){if(img.src?.includes('/art/sprites/')||img.src?.includes('/art/props/sign_'))draws.push({key:img.src.split('/').pop(),height:a[7],bottom:a[5]+a[7]});return draw.call(this,img,...a)}}''')
    for level,types in LEVELS.items():
     f.evaluate('freeze()');f.wait_for_function('!Bridge.busy')
     assert f.evaluate('''async a=>{const r=await rpc('new',{name:'Visual sprint',difficulty:a.mobile?'doom':'clasico',level_id:a.level},false);applyStart(r);freeze();return FS.state.level_id===a.level}''',{'level':level,'mobile':mobile})
     f.wait_for_function('!Bridge.busy')
     f.evaluate('''()=>{
       const g=FS.config.level.grid;let pos;
       outer:for(let y=1;y<g.length-4;y++)for(let x=1;x<g[0].length-6;x++){
        if(Array.from({length:4},(_,dy)=>Array.from({length:6},(_,dx)=>g[y+dy][x+dx]===0).every(Boolean)).every(Boolean)){pos={x:x+.5,y:y+1.5};break outer;}}
       if(!pos)throw Error('No fixture room');window.testPos=pos;Object.assign(FS.state.player,{...pos,angle:0,grace:99});FS.settings.minimap=false;FS.state.enemies.forEach(e=>e.active=false);
     }''')
     for type in types:
      f.evaluate('''type=>{FS.state.enemies.forEach(e=>e.active=false);window.subject=FS.state.enemies.find(e=>e.type===type);if(!subject)throw Error('Missing '+type);Object.assign(subject,{x:testPos.x+3.4,y:testPos.y,active:true,hp:FS.config.enemies[type].hp});}''',type)
      frames={}
      for pose in ['idle','walk_1','walk_2','attack','hurt','death']:
       data=f.evaluate('''pose=>{
        const t=pose==='walk_2'?10.2:10;FS.enemyVisuals={};subject.hp=FS.config.enemies[subject.type].hp;FSArt.observeEnemy(FS,subject,t);
        const v=FS.enemyVisuals[subject.id];if(pose.startsWith('walk'))v.movingUntil=11;if(pose==='attack')v.attackUntil=11;if(pose==='hurt')v.hurtUntil=11;if(pose==='death')subject.hp=0;
        draws=[];Render.world(FS,t);const expected=FSArt.enemyProfiles[subject.type][pose==='walk_1'?'walk':pose==='walk_2'?'walk':pose];const key=(Array.isArray(expected)?expected[pose==='walk_2'?1:0]:expected)+'.png';
        const rows=draws.filter(d=>d.key===key);if(!rows.length)throw Error('Not rendered '+key);return {key,height:rows[0].height,bottom:rows[0].bottom};
       }''',pose)
       frames[pose]=data
       if pose in ['idle','attack','death']:f.locator('#world').screenshot(path=str(OUT/(f'{level}-{type}-{pose}-'+('mobile' if mobile else 'desktop')+'.png')))
      assert len({round(v['height'],5) for v in frames.values()})==1
      assert len({round(v['bottom'],5) for v in frames.values()})==1
      # Run real enemy behavior and real shots briefly in this room, with grace only for fixture safety.
      combat=f.evaluate('''()=>{subject.hp=FS.config.enemies[subject.type].hp;FS.enemyVisuals={};FS.playing=true;FSArt.observeEnemy(FS,subject,performance.now()/1000);let hp=subject.hp;selectWeapon('pistol');FS.cooldown=0;shoot();for(let i=0;i<90;i++){tick(.016,performance.now()/1000+i*.016);Render.world(FS,performance.now()/1000+i*.016);}FS.playing=false;return {hpBefore:hp,hpAfter:subject.hp,mode:subject.ai_state,projectiles:FS.projectiles.length,fault:!!FS.engineFault};}''')
      assert not combat['fault']
      results.append({'level':level,'type':type,'mobile':mobile,'frames':frames,'combat':combat})
     assert not errors and not f.evaluate('!!FS.engineFault'),errors
    # Review a genuine Workshop signage prop, unchanged world coordinates.
    f.wait_for_function('!Bridge.busy')
    f.evaluate("async()=>{const r=await rpc('new',{name:'Signs',difficulty:'clasico',level_id:'workshop'},false);applyStart(r);freeze();}")
    f.wait_for_function('!Bridge.busy')
    for key in ['sign_qc','sign_tools','sign_assembly']:
     assert f.evaluate('''key=>{const p=FS.config.level.props.find(p=>p.art===key);FS.state.player.x=p.x;FS.state.player.y=p.y+2.5;FS.state.player.angle=-Math.PI/2;draws=[];Render.world(FS,0);return draws.some(d=>d.key===key+'.png')}''',key)
     f.locator('#world').screenshot(path=str(OUT/(f'{key}-'+('mobile' if mobile else 'desktop')+'.png')))
    context.close()
   browser.close()
  (OUT/'results.json').write_text(json.dumps(results,indent=2));print('PASS: 8 enemy sets x 6 frames x 2 viewports; four levels; combat ticks; signage; no engine/page errors')
 finally:server.terminate();server.wait(timeout=10);log.close()
if __name__=='__main__':main()
