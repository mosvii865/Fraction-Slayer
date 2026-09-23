"""Real CDP multitouch regression suite against Streamlit (not synthetic clicks).
Run: python tests/mobile_controls.py. A few state fixtures keep tests in the safe room.
"""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'test-results'; OUT.mkdir(exist_ok=True)

class Touches:
    def __init__(self,context,page):
        self.cdp=context.new_cdp_session(page);self.points={}
    def send(self,kind):
        self.cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':list(self.points.values())})
    def down(self,i,x,y):
        self.points[i]={'id':i,'x':x,'y':y,'radiusX':14,'radiusY':14};self.send('touchStart')
    def move(self,i,x,y):
        self.points[i].update(x=x,y=y);self.send('touchMove')
    def up(self,i):
        ended=self.points.pop(i)
        # Chromium ends the IDs supplied here; remaining contacts stay down.
        self.cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[ended]})
    def clear(self):
        if self.points:
            self.points={};self.send('touchCancel')

def center(frame,selector):
    b=frame.locator(selector).bounding_box();assert b,selector
    return b['x']+b['width']/2,b['y']+b['height']/2

def main():
    log=open(OUT/'controls-streamlit.log','w')
    server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port','8523','--server.address','127.0.0.1'],cwd=ROOT,stdout=log,stderr=log)
    results=[]
    def ok(label):results.append(label);print('PASS:',label,flush=True)
    try:
        for _ in range(100):
            try:
                assert urllib.request.urlopen('http://127.0.0.1:8523/_stcore/health',timeout=.5).read()==b'ok';break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('Streamlit startup failed')
        ok('Streamlit HTTP health 200')
        with sync_playwright() as pw:
            kwargs={'headless':True,'args':['--no-sandbox']}
            if os.environ.get('CHROME_PATH'):kwargs['executable_path']=os.environ['CHROME_PATH']
            browser=pw.chromium.launch(**kwargs)
            ctx=browser.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True)
            page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8523');page.locator('iframe').first.wait_for()
            f=page.locator('iframe').first.element_handle().content_frame()
            f.locator('#new').tap();f.locator('#name').fill('Prueba táctil');f.locator('#next').tap();f.locator('#start').tap();f.locator('#enter').tap()
            f.wait_for_function('FS.playing');f.evaluate('FS.state.player.x=6.5;FS.state.player.y=6.5;pickups();FS.state.player.x=3.5;FS.state.player.y=4.5;selectWeapon("pistol")')
            assert f.evaluate('FS.settings.controlSize')=='medium'
            t=Touches(ctx,page)
            f.evaluate('window.events=[];for(const type of ["pointerdown","pointerup","pointercancel","lostpointercapture"])document.addEventListener(type,e=>events.push({type,id:e.pointerId,target:e.target.id,move:InputControls.movementPointer,size:InputControls.active.size}));window.addEventListener("resize",()=>events.push({type:"resize"}));window.addEventListener("blur",()=>events.push({type:"blur"}))')
            def prep():
                t.clear();f.evaluate('releaseInput();FS.state.player.x=3.5;FS.state.player.y=4.5;FS.state.player.angle=0;FS.cooldown=0;FS.reloading=0;FS.lastSync=performance.now()/1000')
            def joystick():
                b=f.locator('#move-zone').bounding_box();x=b['x']+b['width']*.4;y=b['y']+b['height']*.68
                t.down(0,x,y);t.move(0,x,y-58);return x,y
            def moving():return f.evaluate('Math.hypot(FS.move.x,FS.move.y)>.1 && InputControls.movementPointer!==null && FS.playing')
            def position():return f.evaluate('({x:FS.state.player.x,y:FS.state.player.y})')
            def forward_progress(before):
                page.wait_for_timeout(100);after=position();assert abs(after['x']-before['x'])+abs(after['y']-before['y'])>.03,(before,after)
            if not any(flag in sys.argv for flag in ['--layout-only','--orientation-only']):
                # Origin stays exactly at first contact. Analog deadzone, diagonal and saturation.
                prep();b=f.locator('#move-zone').bounding_box();x=b['x']+140;y=b['y']+155
                t.down(0,x,y);p=f.locator('#pad').bounding_box();assert abs(p['x']+p['width']/2-x)<1 and abs(p['y']+p['height']/2-y)<1
                assert f.evaluate('FS.move.x===0&&FS.move.y===0')
                t.move(0,x+3,y+3);assert f.evaluate('FS.move.x===0&&FS.move.y===0')
                t.move(0,x+22,y-22);v=f.evaluate('FS.move');assert 0<v['x']<.7 and -.7<v['y']<0
                t.move(0,x+110,y-110);assert abs(f.evaluate('Math.hypot(FS.move.x,FS.move.y)')-1)<.001
                p2=f.locator('#pad').bounding_box();assert p2['x']==p['x'] and p2['y']==p['y']
                t.up(0);assert f.evaluate('FS.move.x===0&&FS.move.y===0&&!document.querySelector("#pad").classList.contains("active")')
                ok('Floating origin, deadzone, analog magnitude, smooth diagonals, clamp and release')
                prep();joystick();ammo=f.evaluate('FS.state.stats.ammo_used');t.down(1,*center(f,'#fire'));assert f.evaluate('InputControls.active.size')==2
                before=position();forward_progress(before);assert f.evaluate('FS.state.stats.ammo_used')>ammo
                t.up(1);assert moving(),f.evaluate('({events,move:FS.move,playing:FS.playing,active:[...InputControls.active].map(([id,p])=>[id,p.role])})');t.up(0);ok('Joystick + fire; releasing fire preserves movement')
                prep();x,y=joystick();owner=f.evaluate('InputControls.movementPointer');t.down(1,x+70,y+20);assert f.evaluate('InputControls.movementPointer')==owner
                t.up(1);assert moving();t.up(0);ok('Second movement contact cannot steal/reset the joystick')
                prep();joystick();angle=f.evaluate('FS.state.player.angle');lb=f.locator('#look').bounding_box();lx=lb['x']+24;ly=lb['y']+25
                t.down(1,lx,ly);t.move(1,lx+32,ly);assert f.evaluate('FS.state.player.angle')!=angle and moving()
                t.up(1);assert moving();t.up(0);ok('Joystick + camera with independent capture')
                prep();joystick();t.down(1,lx,ly);t.down(2,*center(f,'#fire'));assert f.evaluate('InputControls.active.size')==3
                angle=f.evaluate('FS.state.player.angle');t.move(1,lx+22,ly);assert f.evaluate('FS.state.player.angle')!=angle
                before=position();forward_progress(before);assert moving() and f.evaluate('FS.fireHeld')
                # Fourth finger opens and chooses without stopping the first three.
                t.down(3,*center(f,'#weapon-toggle'));assert f.evaluate('InputControls.active.size')==4
                f.locator('#weapon-picker').wait_for(state='visible');assert moving() and f.evaluate('FS.fireHeld')
                page.screenshot(path=str(OUT/'v011-multitouch-selector.png'))
                t.up(3);before=position();t.down(3,*center(f,'[data-select-weapon="shotgun"]'));t.up(3)
                assert f.evaluate('FS.state.weapon')=='shotgun' and moving() and f.evaluate('FS.fireHeld')
                assert f.locator('#weapon-picker').is_hidden();forward_progress(before)
                t.up(2);assert moving() and f.evaluate('InputControls.cameraPointer!==null');t.up(1);assert moving();t.up(0)
                ok('Joystick + camera + fire + weapon selector: four fingers and weapon switch while moving')
                prep();joystick();before=position();angle=f.evaluate('FS.state.player.angle')
                t.down(1,*center(f,'#weapon-toggle'));t.up(1);t.down(1,*center(f,'[data-select-weapon="pistol"]'));t.up(1)
                assert f.evaluate('FS.state.weapon')=='pistol' and moving();forward_progress(before);assert f.evaluate('FS.state.player.angle')==angle
                t.up(0);ok('Two-finger weapon switching works without a synthetic click')
                prep();joystick();f.evaluate('FS.state.weapons.pistol.loaded=3;FS.reloading=0');t.down(1,*center(f,'#reload-touch'));t.up(1)
                assert moving() and f.evaluate('FS.reloading>0');angle=f.evaluate('FS.state.player.angle');t.down(1,*center(f,'#interact'));t.up(1)
                assert moving() and f.evaluate('FS.state.player.angle')==angle
                t.up(0);ok('Reload and interaction away from stations preserve movement; buttons do not rotate camera')
                prep();joystick();t.down(1,*center(f,'#fire'));t.down(2,*center(f,'#fire'));t.up(1);assert f.evaluate('FS.fireHeld')
                t.up(2);assert not f.evaluate('FS.fireHeld') and moving();t.clear();assert f.evaluate('InputControls.active.size===0 && FS.move.x===0 && FS.move.y===0')
                ok('Independent fire contacts and OS touch cancellation leave no stuck inputs')
                # Preferences are changed through the actual UI and survive a reload.
                f.locator('#pause').tap();f.locator('#settings').tap();f.locator('[data-size="large"]').tap();f.locator('[data-zone="corner"]').tap();f.locator('#vibration').check();f.locator('#joystick-radius').evaluate("e=>{e.value='75';e.dispatchEvent(new Event('input',{bubbles:true}))}");f.locator('#back').tap();f.locator('#resume').tap()
                assert f.evaluate('FS.settings.controlSize==="large"&&FS.settings.movementZone==="corner"&&FS.settings.joystickRadius===75&&FS.settings.vibration')
                prep();controls=f.locator('#controls').bounding_box();t.down(0,controls['x']+100,controls['y']+15);assert f.evaluate('InputControls.movementPointer===null');t.up(0)
                joystick();assert moving();t.clear();ok('Corner-only zone ignores upper-left touches; size, radius and vibration settings applied')
                # Browser vibration mocked only to verify calls; this cannot assess real haptic feel.
                f.evaluate('window.hapticCalls=[];Object.defineProperty(navigator,"vibrate",{configurable:true,value:(n)=>{hapticCalls.push(n);return true}});FS.settings.vibration=true')
                f.evaluate('InputControls.haptic("shot")');page.wait_for_timeout(60);f.evaluate('InputControls.haptic("hurt")');page.wait_for_timeout(60);f.evaluate('InputControls.haptic("weapon")')
                assert f.evaluate('hapticCalls')==[6,14,8]
                f.evaluate('FS.settings.vibration=false;InputControls.haptic("shot")');assert f.evaluate('hapticCalls.length')==3
                f.evaluate('Object.defineProperty(navigator,"vibrate",{configurable:true,value:undefined});FS.settings.vibration=true;InputControls.haptic("shot")');ok('Haptics gated, minimal pulses, unsupported browser is silent (API mocked)')
                page.reload();page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame();f.locator('#continue').wait_for();assert f.evaluate('FS.settings.controlSize==="large"&&FS.settings.movementZone==="corner"&&FS.settings.joystickRadius===75&&FS.settings.vibration')
                f.locator('#continue').tap();f.wait_for_function('FS.playing');t=Touches(ctx,page);ok('Preferences and v0.1 save key persist across page reload')
            sizes={}
            if '--orientation-only' not in sys.argv:
                # Sizes and hit boxes across real emulated viewports.
                sizes={}
                for width,height in [(568,320),(667,375),(844,390),(932,430),(1024,768)]:
                    page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(180)
                    if not f.evaluate('FS.playing'):f.locator('#resume').tap()
                    for size in ['small','medium','large']:
                        f.evaluate('(size)=>{FS.settings.controlSize=size;InputControls.layout()}',size)
                        boxes={k:f.locator('#'+k).bounding_box() for k in ['fire','interact','reload-touch','weapon-toggle']}
                        bounds=f.locator('#controls').bounding_box()
                        for k,b in boxes.items():
                            assert b['width']>=44 and b['height']>=44,(width,size,k,b)
                            assert b['x']>=bounds['x'] and b['x']+b['width']<=bounds['x']+bounds['width']+.5
                            assert b['y']>=bounds['y'] and b['y']+b['height']<=bounds['y']+bounds['height']+.5,(width,size,k,b,bounds)
                        def overlaps(a,b):return min(a['x']+a['width'],b['x']+b['width'])>max(a['x'],b['x']) and min(a['y']+a['height'],b['y']+b['height'])>max(a['y'],b['y'])
                        vals=list(boxes.values());assert all(not overlaps(a,b) for i,a in enumerate(vals) for b in vals[i+1:])
                        t.down(8,*center(f,'#weapon-toggle'));t.up(8);picker=f.locator('#weapon-picker').bounding_box();assert picker['y']>=bounds['y']-.5,(width,size,picker,bounds)
                        assert all(not overlaps(picker,b) for b in vals)
                        t.down(8,*center(f,'#weapon-close'));t.up(8)
                        sizes[f'{width}x{height}/{size}']=round(boxes['fire']['width'])
                    page.screenshot(path=str(OUT/f'v011-{width}x{height}.png'))
                assert sizes['844x390/small']<sizes['844x390/medium']<sizes['844x390/large']
                ok('5 landscape viewports × 3 presets: large nonoverlapping buttons and selector inside safe gameplay bounds')
                # Simulated CSS safe-area values are geometry tests, not hardware-notch tests.
                page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(180)
                f.evaluate('const s=document.querySelector("#app").style;s.setProperty("--safe-left","44px");s.setProperty("--safe-right","44px");s.setProperty("--safe-top","12px");s.setProperty("--safe-bottom","21px");InputControls.layout();Render.resize()')
                for key in ['fire','interact','reload-touch','weapon-toggle']:
                    b=f.locator('#'+key).bounding_box();assert b['x']>=44 and b['x']+b['width']<=800 and b['y']+b['height']<=390-21-70
                page.screenshot(path=str(OUT/'v011-safe-areas.png'));ok('Simulated notch/system-bar insets respected on all four sides')
                f.evaluate('for(const k of ["left","right","top","bottom"])document.querySelector("#app").style.removeProperty("--safe-"+k);InputControls.layout()')
            prep();joystick();page.set_viewport_size({'width':390,'height':844});f.locator('#rotate').wait_for(state='visible');f.wait_for_function('InputControls.active.size===0 && !FS.playing')
            t.clear();page.set_viewport_size({'width':844,'height':390});f.locator('#resume').wait_for();f.locator('#resume').tap();joystick();assert moving();t.clear();ok('Portrait pause releases contacts; landscape restores layout and movement')
            assert not errors,errors;ok('No JavaScript page errors')
            (OUT/('mobile-orientation-results.json' if '--orientation-only' in sys.argv else 'mobile-layout-results.json' if '--layout-only' in sys.argv else 'mobile-results.json')).write_text(json.dumps({'passed':len(results),'checks':results,'fire_sizes':sizes},indent=2))
            browser.close()
    finally:
        server.terminate();server.wait(timeout=10);log.close()
if __name__=='__main__':main()
