"""Actual Streamlit/Chromium visual micro-iteration. Explicit position/ammo fixtures.
No gameplay parameters or enemy damage are changed by this test or release.
"""
from pathlib import Path
import json,subprocess,sys,time,urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results/shotgun-polish';OUT.mkdir(parents=True,exist_ok=True)
PORT=8541

def main():
    log=(OUT/'streamlit.log').open('w');proc=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port',str(PORT),'--server.address','127.0.0.1'],cwd=ROOT,stdout=log,stderr=log)
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
                name='mobile' if mobile else 'desktop'
                ctx=browser.new_context(viewport={'width':900 if mobile else 1280,'height':405 if mobile else 720},has_touch=mobile,is_mobile=mobile)
                page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{PORT}');page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame()
                f.locator('#new').click();f.locator('#next').click();f.locator('#start').click();f.locator('#enter').click()
                f.wait_for_function('FS.playing && FSArt.has("weapons","shotgun_reload_end") && FSArt.has("pickups","shotgun_pickup")')
                f.evaluate('freeze()');f.wait_for_function('!Bridge.busy')
                f.evaluate('''()=>{
                  window.visualDraws=[];
                  const c=document.querySelector('#world').getContext('2d'),draw=c.drawImage;
                  c.drawImage=function(img,...a){
                    if(img.src?.includes('/art/weapons/')||img.src?.includes('/art/pickups/')){
                      const key=img.src.split('/').pop();visualDraws.push({key,reloading:FS.reloading,loaded:FS.state.weapons[FS.state.weapon].loaded,scale:a.length===8?a[6]/a[2]:null});
                      if(visualDraws.length>3000)visualDraws.shift();
                    }
                    return draw.call(this,img,...a);
                  };
                  const i=FS.config.level.items.find(i=>i.type==='weapon'&&i.weapon==='shotgun');
                  FS.state.player.x=i.x-2;FS.state.player.y=i.y;FS.state.player.angle=0;
                  FS.settings.minimap=false;Render.world(FS,0);
                }''')
                assert f.evaluate('visualDraws.some(v=>v.key==="shotgun_pickup.png")')
                f.locator('#world').screenshot(path=str(OUT/(name+'-pickup.png')))
                pickup=f.evaluate('''()=>{
                  const i=FS.config.level.items.find(i=>i.type==='weapon'&&i.weapon==='shotgun');
                  FS.state.player.x=i.x;FS.state.player.y=i.y;pickups();
                  const result={collected:FS.state.collected.includes(i.id),weapon:clone(FS.state.weapons.shotgun)};
                  FS.state.player.x=3.5;FS.state.player.y=5.5;FS.state.player.angle=0;
                  FS.state.player.grace=FS.config.level.respawn_rules.grace;selectWeapon('shotgun');FS.playing=true;return result;
                }''')
                assert pickup['collected'] and pickup['weapon']['loaded']>0
                f.wait_for_function('!Bridge.busy')
                assert f.evaluate("async()=>{const r=await rpc('sync');return !!r&&!r.error&&!!r.state.weapons.shotgun;}"), 'Pickup sync must be accepted'
                f.evaluate('visualDraws=[];FS.cooldown=0')
                if mobile:f.locator('#fire').tap()
                else:
                    f.locator('#world').focus();page.mouse.click(600,300)
                page.wait_for_timeout(430)
                keys=f.evaluate('[...new Set(visualDraws.map(v=>v.key))]')
                assert all(k+'.png' in keys for k in ['shotgun_fire','shotgun_pump_back','shotgun_pump_forward','shotgun']),keys
                before=f.evaluate('clone(FS.state.weapons.shotgun)')
                f.evaluate('visualDraws=[]')
                if mobile:f.locator('#reload-touch').tap()
                else:f.locator('#world').focus();page.keyboard.press('r')
                f.wait_for_function('FS.reloading>0')
                f.wait_for_function('FS.reloading<=0',timeout=10000)
                page.wait_for_timeout(80)
                frames=f.evaluate('visualDraws.filter(v=>v.key.startsWith("shotgun"))')
                reloadkeys={v['key'] for v in frames}
                assert {'shotgun_reload_start.png','shotgun_reload_insert.png','shotgun_reload_end.png','shotgun.png'}<=reloadkeys,reloadkeys
                scales=[v['scale'] for v in frames if v['scale']]
                assert max(scales)-min(scales)<1e-8,scales
                after=f.evaluate('clone(FS.state.weapons.shotgun)')
                assert before['loaded']+before['reserve']==after['loaded']+after['reserve']
                assert after['loaded']==f.evaluate('FS.config.weapons.shotgun.capacity')
                # Close snapshots of each real render branch, with no gameplay tick during fixtures.
                f.evaluate('freeze()');f.wait_for_function('!Bridge.busy')
                for stage,remaining in [('start',None),('insert',.2),('end',.05)]:
                    f.evaluate('''a=>{FS.reloading=a.stage==='start'?FS.config.weapons.shotgun.reload:a.stage==='insert'?FS.config.weapons.shotgun.reload-.15:a.remaining;Render.world(FS,0)}''',{'stage':stage,'remaining':remaining})
                    f.locator('#world').screenshot(path=str(OUT/(name+'-reload-'+stage+'.png')))
                f.evaluate('''()=>{FS.reloading=1;selectWeapon('pistol');selectWeapon('shotgun');Render.world(FS,0)}''')
                assert f.evaluate('FS.reloading===0 && FS.pumpAnim===0')
                assert f.evaluate('visualDraws[visualDraws.length-1].key')=='shotgun.png'
                for _ in range(6):f.evaluate("selectWeapon('pistol');selectWeapon('shotgun')")
                # Death/checkpoint restore must clear the existing countdown too.
                f.wait_for_function('!Bridge.busy')
                f.evaluate('FS.reloading=.7;FS.state.player.hp=0;death()')
                f.locator('#restart').click();f.wait_for_function('FS.playing && FS.state.player.hp>0')
                assert f.evaluate('FS.reloading===0 && FS.pumpAnim===0')
                # A new backend session/run goes through the existing reset path.
                f.wait_for_function('!Bridge.busy')
                assert f.evaluate('''async()=>{FS.reloading=1;const r=await rpc('new',{name:'Reload reset',difficulty:'clasico',level_id:'workshop'},false);applyStart(r);return FS.reloading===0&&FS.pumpAnim===0;}''')
                # Restart/load reset uses this same applyStart (no new visual state).
                assert not errors and not f.evaluate('!!FS.engineFault'),errors
                results.append({'viewport':name,'pickup':pickup,'firePumpKeys':keys,'reloadFrames':sorted(reloadkeys),'scaleConstant':True,'ammoBefore':before,'ammoAfter':after,'switchAndNewRunReset':True,'pageErrors':errors})
                ctx.close()
            browser.close()
        (OUT/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
    finally:proc.terminate();proc.wait(timeout=10);log.close()
if __name__=='__main__':main()
