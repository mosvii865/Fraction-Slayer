"""Real Streamlit startup/save regression. No substitute frontend harness.
The null checkpoint and unpatched comparison are explicitly injected fixtures;
Python's actual initial checkpoint must remain 'inicio'.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright
from mobile_controls import Touches

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'test-results'
OUT.mkdir(exist_ok=True)
PORT = 8526


def main():
    log = open(OUT / 'startup-streamlit.log', 'w')
    proc = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.port', str(PORT), '--server.address', '127.0.0.1'], cwd=ROOT, stdout=log, stderr=log)
    results = []
    try:
        for _ in range(100):
            try:
                assert urllib.request.urlopen(f'http://127.0.0.1:{PORT}/_stcore/health', timeout=.5).read() == b'ok'
                break
            except Exception:
                time.sleep(.1)
        else:
            raise RuntimeError('Streamlit startup failed')
        with sync_playwright() as pw:
            opts = {'headless': True, 'args': ['--no-sandbox']}
            if os.environ.get('CHROME_PATH'):
                opts['executable_path'] = os.environ['CHROME_PATH']
            browser = pw.chromium.launch(**opts)
            for mobile in (False, True):
                for difficulty in ('clasico', 'doom'):
                    ctx = browser.new_context(viewport={'width':844 if mobile else 1280, 'height':390 if mobile else 720}, has_touch=mobile, is_mobile=mobile)
                    page = ctx.new_page()
                    errors, console = [], []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    page.on('console', lambda m: console.append({'type':m.type,'text':m.text}) if m.type == 'error' else None)
                    page.goto(f'http://127.0.0.1:{PORT}')
                    page.locator('iframe').first.wait_for()
                    f = page.locator('iframe').first.element_handle().content_frame()
                    f.locator('#new').click()
                    f.locator("#level").select_option("industrial_test");f.locator('#next').click()
                    if difficulty == 'doom': f.locator('#doom').click()
                    f.locator('#start').click()
                    f.locator('#enter').click()
                    f.wait_for_function('FS.playing && FS.debugStage === "FRAME_END"')
                    assert f.evaluate('FS.state.checkpoint') == 'inicio'
                    assert f.evaluate('FS.state.level_id') == 'industrial_test'
                    assert f.evaluate('slot.version') == 2
                    assert f.evaluate('FS.state.enemies.length') == (6 if difficulty == 'doom' else 3)
                    assert f.locator('#hud').is_visible()
                    assert f.locator('#world').is_visible()
                    # Verify pixels, not merely a present canvas element.
                    assert f.evaluate("()=>{const c=document.querySelector('#world');const a=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return new Set(a).size>16;}")
                    initial = f.evaluate('({x:FS.state.player.x,angle:FS.state.player.angle,ammo:FS.state.weapons.pistol.loaded})')
                    if mobile:
                        t=Touches(ctx,page);b=f.locator('#move-zone').bounding_box();x=b['x']+120;y=b['y']+150
                        t.down(0,x,y);t.move(0,x,y-55);page.wait_for_timeout(150);t.clear()
                        b=f.locator('#look').bounding_box();x=b['x']+60;y=b['y']+35
                        t.down(1,x,y);t.move(1,x+35,y);t.clear()
                    else:
                        f.locator('#world').focus();page.keyboard.down('w');page.wait_for_timeout(150);page.keyboard.up('w')
                        page.keyboard.down('ArrowRight');page.wait_for_timeout(100);page.keyboard.up('ArrowRight')
                    assert f.evaluate('FS.state.player.x') > initial['x']
                    assert f.evaluate('FS.state.player.angle') != initial['angle']
                    f.locator('#fire').click()
                    assert f.evaluate('FS.state.weapons.pistol.loaded') < initial['ammo']
                    f.evaluate('freeze()')
                    f.wait_for_function('!Bridge.busy')
                    assert f.evaluate("async()=>{const r=await rpc('sync');return !!r&&!r.error&&r.state.checkpoint==='inicio';}")
                    # Null fixture: actual tick/filter/render code on the Streamlit-mounted frame.
                    fixture = f.evaluate("""()=>{
                      const original=FS.state.checkpoint, oldCheckpoint=checkpoint;
                      const oldLastSync=FS.lastSync;
                      let selected=null;
                      checkpoint=id=>{selected=id;};
                      FS.state.checkpoint=null;FS.state.player.x=3.5;FS.state.player.y=4.5;
                      FS.playing=true;FS.lastSync=1e12;FS.checkpointAttempts={};
                      try {tick(.016,performance.now()/1000);Render.world(FS,1);return {selected,fault:!!FS.engineFault};}
                      finally {FS.state.checkpoint=original;checkpoint=oldCheckpoint;FS.lastSync=oldLastSync;FS.playing=false;}
                    }""")
                    assert fixture == {'selected':'inicio','fault':False}, fixture
                    # Load v2 by CONTINUAR after a real page reload and new session.
                    assert f.evaluate("async()=>!!(await rpc('pause'))")
                    page.reload();page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame()
                    f.locator('#continue').click();f.wait_for_function('FS.playing&&!FS.engineFault')
                    assert f.evaluate('FS.state.checkpoint') == 'inicio'
                    # Advanced checkpoint created by Python, with a known safe fixture location.
                    f.evaluate('freeze();FS.state.player.x=11;FS.state.player.y=4.5')
                    f.wait_for_function('!Bridge.busy')
                    assert f.evaluate("async()=>{const r=await rpc('checkpoint',{checkpoint:'arena'});return !!r&&r.state.checkpoint==='arena';}")
                    page.reload();page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame()
                    f.locator('#continue').click();f.wait_for_function('FS.playing&&!FS.engineFault')
                    assert f.evaluate('FS.state.checkpoint') == 'arena'
                    f.evaluate('freeze()');f.wait_for_function('!Bridge.busy')
                    assert f.evaluate("async()=>{const save=clone(slot);save.state.player.hp='bad';const r=await rpc('load',{save},false);return r===null&&!FS.engineFault;}")
                    # A v1 slot must remain at the menu with a clear rejection, no auto-load loop.
                    f.evaluate("slot.version=1;localStorage.setItem('fraction-slayer-save',JSON.stringify(slot));mainMenu()")
                    f.locator('#continue').click();f.wait_for_function('!Bridge.busy')
                    assert 'incompatible' in f.locator('#toast').inner_text().lower()
                    assert not f.evaluate('FS.playing||FS.engineFault')
                    event=f.evaluate('Bridge.last_event.id');page.wait_for_timeout(300)
                    assert f.evaluate('Bridge.last_event.id') == event
                    # Failed load must not prevent starting another game.
                    f.locator('#new').click();f.locator("#level").select_option("industrial_test");f.locator('#next').click()
                    if difficulty=='doom':f.locator('#doom').click()
                    f.locator('#start').click();f.locator('#enter').click()
                    f.wait_for_function('FS.playing && FS.debugStage === "FRAME_END"')
                    assert f.evaluate('FS.state.checkpoint')=='inicio'
                    assert not errors,errors
                    assert not [e for e in console if 'Fraction Slayer frame error' in e['text']],console
                    page.screenshot(path=str(OUT/f'stable-{difficulty}-{"mobile" if mobile else "pc"}.png'))
                    label=f'{difficulty} / {"mobile" if mobile else "PC"}: clean startup, pixels, HUD, input, first sync, null JS fixture, continue v2, advanced v2, v1/invalid rejected'
                    results.append(label);print('PASS:',label,flush=True)
                    if mobile and difficulty=='doom':
                        # A/B comparison: remove only the candidate guard in memory, never on disk.
                        f.evaluate("""()=>{
                          freeze();FS.state.checkpoint=null;FS.playing=true;FS.lastSync=1e12;
                          const source=tick.toString().replace('const currentOrder = current?.order ?? -1;', 'const currentOrder = current.order;');
                          window.originalTick=tick;window.tick=eval('('+source+')');
                        }""")
                        f.locator('#engine-error-details').wait_for()
                        report=f.evaluate('FS.lastEngineError')
                        assert report['name']=='TypeError' and 'order' in report['message'] and report['stage']=='CHECKPOINT_UPDATE',report
                        (OUT/'controlled-null-first-error.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
                        assert f.evaluate("()=>{const r=document.querySelector('.engine-error-panel').getBoundingClientRect();return r.width<=innerWidth&&r.height<=innerHeight;}")
                        f.evaluate("Object.defineProperty(navigator,'clipboard',{value:undefined,configurable:true})")
                        f.locator('#copy-engine-error').click()
                        assert 'copiar' in f.locator('#copy-error-status').inner_text()
                        f.evaluate('()=>{tick=originalTick;FS.state.checkpoint="inicio";}')
                        f.locator('#retry-frame').click();f.wait_for_function('FS.playing&&!FS.engineFault&&FS.debugStage==="FRAME_END"')
                        print('PASS: controlled unpatched-null crash captured, selectable diagnostics, patched retry succeeds',flush=True)
                    ctx.close()
            browser.close()
        (OUT/'startup-results.json').write_text(json.dumps({'passed':results,'production_crashes':0,'controlled_unpatched_null_crash':True},indent=2,ensure_ascii=False))
    finally:
        proc.terminate();proc.wait(timeout=10);log.close()

if __name__=='__main__':main()
