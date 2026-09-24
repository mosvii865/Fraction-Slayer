"""Real Streamlit Workshop campaign walkthrough, both modes.
Accelerated navigation uses production tick/collision/shots and real Python RPC.
Only routing refreshes grace; this is a functional test, NOT a balance/playtime claim.
Loader attack damage is separately tested without grace. No enemy HP is edited in route.
"""
from pathlib import Path
import json, os, subprocess, sys, time, urllib.request
from playwright.sync_api import sync_playwright
from mobile_controls import Touches, center
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
PORT=8527

def main():
    log=open(OUT/'workshop-streamlit.log','w')
    server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port',str(PORT),'--server.address','127.0.0.1'],cwd=ROOT,stdout=log,stderr=log)
    results=[]
    def ok(s):results.append(s);print('PASS:',s,flush=True)
    try:
        for _ in range(100):
            try:
                if urllib.request.urlopen(f'http://127.0.0.1:{PORT}/_stcore/health').read()==b'ok':break
            except Exception:time.sleep(.1)
        with sync_playwright() as pw:
            opts=dict(headless=True,args=['--no-sandbox'])
            if os.environ.get('CHROME_PATH'):opts['executable_path']=os.environ['CHROME_PATH']
            browser=pw.chromium.launch(**opts)
            for diff in (('doom',) if '--doom-only' in sys.argv else ('clasico','doom')):
                mobile=diff=='doom'
                ctx=browser.new_context(viewport={'width':844 if mobile else 1280,'height':390 if mobile else 720},has_touch=mobile,is_mobile=mobile)
                page=ctx.new_page();errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('console',lambda m:errors.append(m.text) if m.type=='error' and 'ENGINE' in m.text else None)
                page.goto(f'http://127.0.0.1:{PORT}');page.locator('iframe').first.wait_for()
                f=page.locator('iframe').first.element_handle().content_frame()
                f.locator('#new').click();assert f.locator('#level').input_value()=='workshop'
                f.locator('#name').fill('Alpha2 '+diff);f.locator('#next').click()
                if mobile:f.locator('#doom').click()
                f.locator('#start').click();f.locator('#enter').click();f.wait_for_function('FS.playing&&!Bridge.busy')
                assert f.evaluate('FS.state.level_id')=='workshop'
                assert f.locator('#world').is_visible() and f.locator('#hud').is_visible()
                if mobile:
                    t=Touches(ctx,page);b=f.locator('#move-zone').bounding_box();x=b['x']+110;y=b['y']+140
                    t.down(0,x,y);t.move(0,x,y-50);t.down(1,*center(f,'#fire'))
                    before=f.evaluate('FS.state.player.x');page.wait_for_timeout(100)
                    assert f.evaluate('FS.state.player.x')>before and f.evaluate('InputControls.active.size')==2
                    t.clear()
                else:
                    f.locator('#world').focus();before=f.evaluate('FS.state.player.x');page.keyboard.down('w');page.wait_for_timeout(120);page.keyboard.up('w');assert f.evaluate('FS.state.player.x')>before
                f.evaluate('freeze()');f.wait_for_function('!Bridge.busy')
                f.evaluate((ROOT/'tests/workshop_driver.js').read_text())
                ok(diff+': new default Workshop, canvas/HUD and physical input events')
                def sync():
                    f.wait_for_function('!Bridge.busy')
                    assert f.evaluate('async()=>{await syncWorld();return !FS.engineFault&&!FS.sessionUnavailable}'),f.evaluate('FS.lastEngineError')
                    assert not errors,errors
                def travel(x,y):
                    for _ in range(150):
                        p=f.evaluate('FS.state.player')
                        if f.evaluate('FS.state.progress.complete'):break
                        if abs(p['x']-x)+abs(p['y']-y)<.25:break
                        f.evaluate('(p)=>walkTest.batch(p)',[x,y]);sync()
                    else:raise AssertionError(('route stuck',x,y,f.evaluate('FS.state.player'),f.evaluate('FS.state.weapons')))
                def clear(*groups):
                    for _ in range(220):
                        es=f.evaluate('(gs)=>FS.state.enemies.filter(e=>e.active&&e.hp>0&&gs.includes(e.group))',list(groups))
                        if not es:break
                        p=f.evaluate('FS.state.player');e=min(es,key=lambda e:(e['x']-p['x'])**2+(e['y']-p['y'])**2)
                        f.evaluate('(a)=>walkTest.batch([a.x,a.y],a.groups,true)',dict(x=e['x'],y=e['y'],groups=list(groups)));sync()
                    else:raise AssertionError(('combat stuck',groups,es,f.evaluate('FS.state.weapons')))
                    ok(diff+': encounter '+','.join(groups))
                def question(ident,answer,weapon='pistol',wrong=False):
                    f.wait_for_function('!Bridge.busy');f.evaluate('(a)=>ask(a.id,a.weapon)',dict(id=ident,weapon=weapon));f.wait_for_function('modalQuestion!==null')
                    if wrong:
                        f.evaluate('submitAnswer("999")');f.locator('#again').wait_for();assert 'CALIBRATION ERROR' in f.locator('#overlay').inner_text();f.locator('#again').click();f.wait_for_function('modalQuestion!==null')
                    q=f.evaluate('modalQuestion')
                    if q['mode']=='manual':
                        for ch in answer:f.locator(f'[data-key="{ch}"]').click()
                        f.locator('#confirm').click()
                    else:
                        from fractions import Fraction
                        i=next(i for i,c in enumerate(q['choices']) if Fraction(c)==Fraction(answer));f.locator(f'[data-choice="{i}"]').click()
                    f.locator('#return').wait_for();assert 'CALIBRATION ERROR' not in f.locator('#overlay').inner_text()
                    f.locator('#return').click();f.evaluate('freeze()');f.wait_for_function('!Bridge.busy')
                travel(6,5.5);clear('welcome');travel(2.5,14.5)
                question('tool_storage_terminal','.50',wrong=True)
                travel(12.5,5.5);travel(14.5,6.5);sync()
                assert f.evaluate('FS.state.enemies.some(e=>e.group==="assembly_first" && e.active && e.hp>0)'), 'Shotgun pickup occurs during first wave'
                clear('assembly_first','assembly_second')
                assert f.evaluate('FS.state.weapons.shotgun.loaded+FS.state.weapons.shotgun.reserve')>0
                travel(27.5,5.5);f.evaluate('checkpoint("calibration")');f.wait_for_function('!Bridge.busy');assert f.evaluate('FS.state.checkpoint')=='calibration'
                question('mad_calibration_01','.75','shotgun')
                assert f.evaluate('FS.state.weapons.shotgun.mods')==1
                travel(28.5,11.5);clear('maintenance');travel(30.5,16.5);travel(26.5,16.5)
                if diff=='clasico':
                    travel(20.5,15.5);f.evaluate('FS.playing=true;FS.state.player.angle=Math.PI;selectWeapon("pistol");FS.cooldown=0;shoot();FS.playing=false');sync()
                    assert f.evaluate('FS.state.progress.utcj_found.length')==1
                travel(20.5,16.5);question('mad_secret_01','.875','pistol')
                assert f.evaluate('FS.state.weapons.pistol.mods')==1
                travel(39.5,10.5);question('power_door_terminal','3/8');travel(39.5,4.5);sync()
                assert f.evaluate('FS.state.inventory.quest_items.main_power_fuse')==1
                # Real enemy proximity denies the normal door terminal during the ambush.
                travel(39.5,11.5)
                blocked=f.evaluate('async()=>{const r=await Bridge.request("question",{station:"power_door_terminal",snapshot:clone(FS.state)});return r.error;}')
                assert blocked=='AREA NOT SECURE',blocked
                clear('fuse_ambush');travel(39.5,14.5)
                f.evaluate('checkpoint("fuse_recovered")');f.wait_for_function('!Bridge.busy');assert f.evaluate('FS.state.checkpoint')=='fuse_recovered'
                travel(42.5,14.5);question('secure_cache_01','.625')
                # Save/reload through real localStorage and a new Streamlit session.
                sync();page.reload();page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame();f.locator('#continue').click();f.wait_for_function('FS.playing&&!Bridge.busy');f.evaluate('freeze()');f.evaluate((ROOT/'tests/workshop_driver.js').read_text())
                assert f.evaluate('FS.state.inventory.quest_items.main_power_fuse')==1
                assert f.evaluate('FS.state.enemies.filter(e=>e.group==="fuse_ambush").every(e=>e.hp===0)')
                travel(28.5,20.5);clear('generator_entry');travel(28.5,20.5)
                f.evaluate('checkpoint("before_loader")');f.wait_for_function('!Bridge.busy');assert f.evaluate('FS.state.checkpoint')=='before_loader'
                f.evaluate('FS.state.player.grace=0;FS.playing=true;hurt(1000)');f.locator('#restart').click();f.wait_for_function('FS.playing&&!Bridge.busy');f.evaluate('freeze()')
                assert f.evaluate('FS.state.player.hp')>=50 and f.evaluate('FS.state.player.grace')>0
                travel(28.5,21.5);sync()
                f.evaluate('resume()');f.wait_for_function('FS.nearest?.id==="generator_socket" && !Bridge.busy')
                f.locator('#interact').click();f.wait_for_function('FS.state.progress.objectives.power_restored && !Bridge.busy');f.evaluate('freeze()')
                assert f.evaluate('FS.state.progress.objectives.power_restored && FS.state.progress.objectives.loader_spawned')
                attacks=f.evaluate('walkTest.loaderAttacks()');assert all(attacks[k] for k in ('melee','slamTelegraph','slam','prep','locked','wall','recovery')),attacks
                assert attacks['rear']>attacks['front']>0,attacks
                ok(diff+': Loader melee/slam/locked charge/wall stun/recovery/rear damage')
                f.evaluate('const boss=FS.state.enemies.find(e=>e.type==="loader");FS.state.player.angle=Math.atan2(boss.y-FS.state.player.y,boss.x-FS.state.player.x);FS.shotFlash=FS.hurtFlash=0;resume()');page.wait_for_timeout(80);page.screenshot(path=str(OUT/f'workshop-{diff}-loader.png'));f.evaluate('freeze()')
                clear('loader');sync()
                assert f.evaluate('FS.state.progress.objectives.loader_defeated && FS.state.progress.doors.elevator_gate')
                assert f.evaluate('FS.state.progress.triggers.loader_warning'), f.evaluate('FS.state.progress')
                for _ in range(3):
                    f.evaluate('walkTest.batch([FS.state.player.x,FS.state.player.y])');sync()
                assert f.evaluate('FS.state.progress.waves.loader_support')
                # Optional support kills are not required for the elevator.
                travel(18.5,25.5)
                assert f.evaluate('FS.state.progress.complete'), 'Auto-elevator must finish through production UI'
                f.locator('h2.success').wait_for();text=f.locator('#overlay').inner_text()
                assert 'MISSION COMPLETE' in text and 'THE FACTORY' in text and '212%' in text
                assert ('UTCJ: 1/4' if diff=='clasico' else 'UTCJ: ???') in text,text
                page.screenshot(path=str(OUT/f'workshop-{diff}-complete.png'))
                assert not f.evaluate('FS.engineFault') and not errors,errors
                stats=f.evaluate('lastStats');ok(diff+': full route, both MADs, fuse ambush once, power, death/respawn, v2 CONTINUAR, elevator + teaser; '+json.dumps(stats))
                ctx.close()
            browser.close()
    finally:
        server.terminate();server.wait(timeout=10);log.close()
        (OUT/'workshop-results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
