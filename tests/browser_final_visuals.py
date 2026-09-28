"""Real Streamlit browser validation; positions/grace are explicit test fixtures.
Ammo operations, pickups, reload countdown and renderer are production functions.
"""
from pathlib import Path
import json,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results/final-visuals';OUT.mkdir(parents=True,exist_ok=True)
PORT=8553
WEAPONS={'sawed_off':('factory',['break_open','reload_insert','close']),'assault':('factory',['reload_start','reload_swap','reload_end']),'sniper':('laboratory',['reload']),'lmg':('foundry',['reload_start','reload_box','reload_end']),'rocket':('foundry',['reload_open','reload_insert','reload_close'])}
def main():
 log=(OUT/'streamlit.log').open('w');server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port',str(PORT),'--server.address','127.0.0.1'],cwd=ROOT,stdout=log,stderr=log);results=[]
 try:
  for _ in range(150):
   try:
    if urllib.request.urlopen(f'http://127.0.0.1:{PORT}/_stcore/health',timeout=.5).status==200:break
   except Exception:time.sleep(.1)
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
   for mobile in [False,True]:
    label='mobile' if mobile else 'desktop';context=browser.new_context(viewport={'width':900 if mobile else 1280,'height':405 if mobile else 720},has_touch=mobile,is_mobile=mobile);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{PORT}');page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame()
    f.locator('#new').click();f.locator('#next').click();f.locator('#start').click();f.locator('#enter').click();f.wait_for_function('FS.playing && !Bridge.busy && FSArt.has("weapons","rocket_reload_close") && FSArt.has("sprites","boss_death")')
    f.evaluate(r'''()=>{window.draws=[];const c=document.querySelector('#world').getContext('2d'),draw=c.drawImage;c.drawImage=function(img,...a){if(/\/art\/(weapons|pickups)\/|\/sprites\/boss_/.test(img.src||'')){draws.push({key:img.src.split('/').pop(),scale:a[6]/a[2],height:a[7],bottom:a[5]+a[7]});if(draws.length>9000)draws.shift();}return draw.call(this,img,...a)}}''')
    f.evaluate('()=>{const render=Render.world;Render.world=(fs,t)=>render(fs,window.visualFixtureTime??t)}')
    def new(level):
     f.evaluate('window.visualFixtureTime=null')
     f.evaluate('freeze()');f.wait_for_function('!Bridge.busy')
     assert f.evaluate('''async a=>{const r=await rpc('new',{name:'Final visual test',difficulty:a.mobile?'doom':'clasico',level_id:a.level},false);applyStart(r);freeze();return FS.state.level_id===a.level}''',{'mobile':mobile,'level':level})
     f.wait_for_function('!Bridge.busy')
    for w,(level,stages) in WEAPONS.items():
     new(level)
     f.evaluate('''w=>{window.item=FS.config.level.items.find(i=>i.type==='weapon'&&i.weapon===w);if(!item)throw Error('Missing item '+w);const p=FS.state.player;window.spawn={x:p.x,y:p.y,angle:p.angle};
       // Find a clear approach to the real pickup for render verification.
       let spot;for(const [dx,dy,a] of [[-2,0,0],[2,0,Math.PI],[0,2,-Math.PI/2],[0,-2,Math.PI/2]])if(!solid(item.x+dx,item.y+dy)&&clearLine(item.x+dx,item.y+dy,item.x,item.y)){spot={x:item.x+dx,y:item.y+dy,angle:a};break;}
       if(!spot)throw Error('No pickup sightline');Object.assign(p,spot);draws=[];Render.world(FS,performance.now()/1000);
     }''',w)
     assert f.evaluate('(w)=>draws.some(d=>d.key===w+"_pickup.png")',w)
     f.locator('#world').screenshot(path=str(OUT/f'{label}-{w}-pickup.png'))
     data=f.evaluate('''w=>{Object.assign(FS.state.player,{x:item.x,y:item.y});pickups();const result={collected:FS.state.collected.includes(item.id),ammo:clone(FS.state.weapons[w])};Object.assign(FS.state.player,{...spawn,grace:FS.config.level.respawn_rules.grace});selectWeapon(w);FS.playing=true;FS.cooldown=0;draws=[];Render.world(FS,performance.now()/1000);return result;}''',w)
     assert data['collected'] and data['ammo']['loaded']>0
     f.wait_for_function('!Bridge.busy')
     assert f.evaluate('async()=>{const r=await rpc("sync");return !!r&&!r.error;}')
     f.evaluate('FS.state.enemies.forEach(e=>e.active=false)')
     f.locator('#world').screenshot(path=str(OUT/f'{label}-{w}-idle.png'))
     if mobile:f.locator('#fire').tap()
     else:f.locator('#world').focus();page.mouse.click(600,300)
     page.wait_for_timeout(750)
     keys=f.evaluate('(w)=>[...new Set(draws.filter(d=>d.key.startsWith(w)).map(d=>d.key))]',w)
     assert w+'_fire.png' in keys,(w,keys)
     if w=='sniper':assert {'sniper_bolt_back.png','sniper_bolt_forward.png'}<=set(keys),keys
     before=f.evaluate('(w)=>clone(FS.state.weapons[w])',w)
     f.evaluate('draws=[]')
     if mobile:f.locator('#reload-touch').tap()
     else:f.locator('#world').focus();page.keyboard.press('r')
     f.wait_for_function('FS.reloading>0');f.wait_for_function('FS.reloading===0',timeout=12000);page.wait_for_timeout(80)
     rows=f.evaluate('(w)=>draws.filter(d=>d.key.startsWith(w)&&!d.key.includes("pickup"))',w);observed={d['key'] for d in rows}
     assert {w+'_'+stage+'.png' for stage in stages}<=observed,(w,observed)
     scales=[d['scale'] for d in rows];assert max(scales)-min(scales)<1e-8,(w,scales)
     after=f.evaluate('(w)=>clone(FS.state.weapons[w])',w);assert before['loaded']+before['reserve']==after['loaded']+after['reserve'];assert after['loaded']==f.evaluate('(w)=>FS.config.weapons[w].capacity',w)
     f.evaluate('freeze()');f.wait_for_function('!Bridge.busy')
     for stage,remaining in [('start',.95),('mid',.5),('end',.05)]:
      f.evaluate('''a=>{FS.reloading=FS.config.weapons[a.w].reload*a.remaining;Render.world(FS,performance.now()/1000)}''',{'w':w,'remaining':remaining});f.locator('#world').screenshot(path=str(OUT/f'{label}-{w}-reload-{stage}.png'))
     assert f.evaluate('''w=>{selectWeapon('pistol');Render.world(FS,performance.now()/1000);selectWeapon(w);draws=[];Render.world(FS,performance.now()/1000);return FS.reloading===0 && draws.some(d=>d.key===w+'.png')}''',w)
     results.append({'viewport':label,'weapon':w,'pickup':data,'fireFrames':keys,'reloadFrames':sorted(observed),'scaleStable':True,'ammoBefore':before,'ammoAfter':after,'switchReset':True})
    # Actual final entity, not an invented enemy. Controlled poses without phase edits to production.
    new('foundry')
    f.evaluate('''()=>{window.boss=FS.state.enemies.find(e=>e.type==='crucible');if(!boss)throw Error('Missing actual Crucible');FS.state.enemies.forEach(e=>e.active=false);
      const g=FS.config.level.grid;let pos;outer:for(let y=1;y<g.length-4;y++)for(let x=1;x<g[0].length-7;x++){if(Array.from({length:4},(_,dy)=>Array.from({length:7},(_,dx)=>g[y+dy][x+dx]===0).every(Boolean)).every(Boolean)){pos={x:x+.5,y:y+1.5};break outer;}}
      Object.assign(FS.state.player,{...pos,angle:0,grace:99});Object.assign(boss,{active:true,x:pos.x+4,y:pos.y});FS.settings.minimap=false;
    }''')
    poses={}
    for pose in ['idle','walk_1','walk_2','attack','hurt','death']:
     data=f.evaluate('''pose=>{const t=pose==='walk_2'?10.2:10;window.visualFixtureTime=t;FS.enemyVisuals={};boss.hp=FS.config.enemies.crucible.hp;FSArt.observeEnemy(FS,boss,t);const v=FS.enemyVisuals[boss.id];if(pose.startsWith('walk'))v.movingUntil=11;if(pose==='attack')v.attackUntil=11;if(pose==='hurt')v.hurtUntil=11;if(pose==='death')boss.hp=0;draws=[];Render.world(FS,t);const rows=draws.filter(d=>d.key==='boss_'+pose+'.png');if(!rows.length)throw Error('Missing '+pose);return rows[0]}''',pose)
     poses[pose]=data;f.locator('#world').screenshot(path=str(OUT/f'{label}-boss-{pose}.png'))
    assert len({round(v['height'],5) for v in poses.values()})==1
    assert len({round(v['bottom'],5) for v in poses.values()})==1
    assert not errors and not f.evaluate('!!FS.engineFault'),errors
    results.append({'viewport':label,'boss':'crucible','poses':poses,'errors':errors})
    context.close()
   browser.close()
  (OUT/'results.json').write_text(json.dumps(results,indent=2));print('PASS: 5 weapons, pickups, real fire/reload/ammo, bolt cycle, switch cleanup; actual Crucible six poses; desktop/mobile; no page/engine errors')
 finally:server.terminate();server.wait(timeout=10);log.close()
if __name__=='__main__':main()
