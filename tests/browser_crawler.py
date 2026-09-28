"""Real Streamlit + Chromium. Controlled enemy positions/cues are visual fixtures,
not a full level/balance playthrough; production tick, shooting and renderer execute.
"""
from pathlib import Path
import json,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results/crawler-v1';OUT.mkdir(parents=True,exist_ok=True)
PORT=8543

def main():
    log=(OUT/'streamlit.log').open('w');server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port',str(PORT),'--server.address','127.0.0.1'],cwd=ROOT,stdout=log,stderr=log)
    results=[]
    try:
        for _ in range(150):
            try:
                if urllib.request.urlopen(f'http://127.0.0.1:{PORT}/_stcore/health',timeout=.5).status==200:break
            except Exception:time.sleep(.1)
        else:raise AssertionError('Streamlit startup')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
            for mobile in (False,True):
                name='mobile' if mobile else 'desktop';errors=[]
                context=browser.new_context(viewport={'width':900 if mobile else 1280,'height':405 if mobile else 720},has_touch=mobile,is_mobile=mobile)
                page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{PORT}');page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame()
                f.locator('#new').click();f.locator('#next').click()
                if mobile:f.locator('#doom').click()
                f.locator('#start').click();f.locator('#enter').click()
                f.wait_for_function('FS.playing && FSArt.has("sprites","crawler_death") && !Bridge.busy')
                assert f.locator('#world').is_visible()
                f.evaluate('freeze()');f.wait_for_function('!Bridge.busy')
                f.evaluate('''()=>{
                  window.draws=[];const ctx=document.querySelector('#world').getContext('2d'),draw=ctx.drawImage;
                  ctx.drawImage=function(img,...a){if(img.src?.includes('/art/sprites/crawler_') || img.src?.includes('/art/sprites/worker_'))draws.push({key:img.src.split('/').pop(),bottom:a[5]+a[7],height:a[7],sourceH:a[3]});return draw.call(this,img,...a)};
                  window.crawler=FS.state.enemies.find(e=>e.type==='crawler');window.worker=FS.state.enemies.find(e=>e.type==='worker');
                  FS.state.enemies.forEach(e=>e.active=false);
                  // Find a real 5x3 open region, never modify map or collision.
                  let spot;const g=FS.config.level.grid;
                  outer:for(let y=1;y<g.length-3;y++)for(let x=1;x<g[0].length-5;x++){
                    if(Array.from({length:3},(_,dy)=>Array.from({length:5},(_,dx)=>g[y+dy][x+dx]===0).every(Boolean)).every(Boolean)){spot={x:x+.5,y:y+1.5};break outer;}
                  }
                  if(!spot||!crawler||!worker)throw Error('Workshop visual fixture missing');
                  Object.assign(FS.state.player,{...spot,angle:0,grace:0});
                  Object.assign(crawler,{x:spot.x+2.6,y:spot.y-.45,active:true});
                  Object.assign(worker,{x:spot.x+2.6,y:spot.y+.7,active:true});
                  FS.enemyVisuals={};FS.settings.minimap=false;
                }''')
                frames={}
                for pose in ['idle','walk_1','walk_2','attack','hurt','death']:
                    data=f.evaluate('''pose=>{
                      const t=pose==='walk_2'?10.2:10;
                      FS.enemyVisuals={};crawler.hp=FS.config.enemies.crawler.hp;
                      const v=enemyVisualState(crawler);
                      if(pose.startsWith('walk'))v.movingUntil=11;
                      if(pose==='attack')v.attackUntil=11;
                      if(pose==='hurt')v.hurtUntil=11;
                      if(pose==='death'){crawler.hp=0;v.deadUntil=11;v.deadX=crawler.x;v.deadY=crawler.y;}
                      draws=[];Render.world(FS,t);
                      return draws.filter(d=>d.key.startsWith('crawler_'));
                    }''',pose)
                    assert data and {d['key'] for d in data}=={f'crawler_{pose}.png'},(pose,data)
                    frames[pose]=data[0]
                    f.locator('#world').screenshot(path=str(OUT/f'{name}-{pose}.png'))
                assert len({round(v['height'],6) for v in frames.values()})==1,frames
                assert len({round(v['bottom'],6) for v in frames.values()})==1,frames
                # Real AI movement + contact attack (no altered enemy config).
                combat=f.evaluate('''()=>{
                  FS.enemyVisuals={};worker.active=false;crawler.hp=FS.config.enemies.crawler.hp;
                  crawler.cooldown=0;FS.playing=true;
                  const oldX=crawler.x;let t=performance.now()/1000;
                  tick(.016,t);tick(.016,t+.016);
                  const moving=enemyVisualState(crawler).movingUntil>t;
                  crawler.x=FS.state.player.x+.4;crawler.y=FS.state.player.y;crawler.cooldown=0;
                  const hp=FS.state.player.hp;tick(.016,t+.032);
                  const attack=enemyVisualState(crawler).attackUntil>t;
                  const damaged=FS.state.player.hp<hp;
                  crawler.x=FS.state.player.x+1.5;crawler.y=FS.state.player.y;
                  FS.state.player.angle=0;selectWeapon('pistol');FS.cooldown=0;shoot();
                  const hurt=enemyVisualState(crawler).hurtUntil>performance.now()/1000;
                  let shots=1;
                  while(crawler.hp>0&&shots<10){FS.cooldown=0;shoot();shots++;}
                  const death=crawler.hp===0&&enemyVisualState(crawler).deadUntil>performance.now()/1000;
                  FS.playing=false;Render.world(FS,performance.now()/1000);
                  return {moving,attack,damaged,hurt,death,shots};
                }''')
                assert all(combat[k] for k in ['moving','attack','damaged','hurt','death']),combat
                # New run is the existing reset path, no stale corpse across campaign levels.
                f.wait_for_function('!Bridge.busy')
                assert f.evaluate("async()=>{const r=await rpc('new',{name:'Crawler reset',difficulty:'clasico',level_id:'workshop'},false);applyStart(r);return Object.keys(FS.enemyVisuals).length===0;}")
                assert not errors and not f.evaluate('!!FS.engineFault'),errors
                results.append({'viewport':name,'difficulty':'doom' if mobile else 'clasico','frames':frames,'combat':combat,'errors':errors})
                context.close()
            browser.close()
        (OUT/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
    finally:server.terminate();server.wait(timeout=10);log.close()
if __name__=='__main__':main()
