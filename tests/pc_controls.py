"""Targeted desktop regression for the v0.1.1 input changes."""
from pathlib import Path
import os
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)

def main():
    log=open(OUT/'pc-streamlit.log','w')
    proc=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port','8524','--server.address','127.0.0.1'],cwd=ROOT,stdout=log,stderr=log)
    try:
        for _ in range(100):
            try:
                assert urllib.request.urlopen('http://127.0.0.1:8524/_stcore/health',timeout=.5).status==200;break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('Startup failed')
        with sync_playwright() as p:
            opts={'headless':True,'args':['--no-sandbox']}
            if os.environ.get('CHROME_PATH'):opts['executable_path']=os.environ['CHROME_PATH']
            b=p.chromium.launch(**opts);page=b.new_page(viewport={'width':1280,'height':720});errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8524')
            page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame()
            f.locator('#new').click();f.locator("#level").select_option("industrial_test");f.locator('#next').click();f.locator('#start').click();f.locator('#enter').click()
            assert not f.evaluate('InputControls.touchMode')
            f.evaluate('FS.state.player.x=6.5;FS.state.player.y=6.5;pickups();FS.state.player.x=3.5;FS.state.player.y=4.5;FS.state.player.angle=0')
            f.locator('#world').focus()
            for key,axis,sign in [('w','x',1),('s','x',-1),('d','y',1),('a','y',-1)]:
                before=f.evaluate(f'FS.state.player.{axis}');page.keyboard.down(key);page.wait_for_timeout(100);page.keyboard.up(key)
                after=f.evaluate(f'FS.state.player.{axis}');assert (after-before)*sign>.1,(key,before,after)
            print('PASS: WASD movement',flush=True)
            page.keyboard.down('w');page.keyboard.press('1');assert f.evaluate('FS.state.weapon')=='pistol'
            x=f.evaluate('FS.state.player.x');page.keyboard.press('2');page.wait_for_timeout(100);assert f.evaluate('FS.state.weapon')=='shotgun' and f.evaluate('FS.state.player.x')>x;page.keyboard.up('w')
            print('PASS: 1/2 weapon selection while walking',flush=True)
            f.evaluate('FS.state.weapons.shotgun.loaded=2;FS.reloading=0');page.keyboard.press('r');assert f.evaluate('FS.reloading>0')
            f.evaluate('FS.reloading=0;FS.cooldown=0')
            region=f.locator('#look').bounding_box();mx=region['x']+100;my=region['y']+100
            page.mouse.move(mx,my);angle=f.evaluate('FS.state.player.angle')
            page.mouse.down(button='right');page.mouse.move(mx+40,my);page.mouse.up(button='right');page.wait_for_timeout(80)
            assert f.evaluate('FS.state.player.angle')!=angle
            used=f.evaluate('FS.state.stats.ammo_used');page.mouse.down();page.wait_for_timeout(100);assert f.evaluate('FS.state.stats.ammo_used')>used;page.mouse.up();assert not f.evaluate('FS.fireHeld')
            print('PASS: R, real mouse drag/rotation and left-click shooting',flush=True)
            page.keyboard.press('Escape');f.locator('#resume').wait_for();assert not f.evaluate('FS.playing');f.locator('#resume').click()
            f.wait_for_function('!Bridge.busy');f.evaluate('FS.state.player.x=4;FS.state.player.y=3');page.wait_for_timeout(100)
            f.locator('#world').focus();page.keyboard.press('e');f.wait_for_function('modalQuestion!==null');assert not f.evaluate('FS.playing');f.locator('#cancel').click();assert f.evaluate('FS.playing')
            print('PASS: Esc pauses, E opens unchanged hologram, cancel resumes',flush=True)
            assert not errors,errors
            page.screenshot(path=str(OUT/'v011-desktop.png'));b.close()
            (OUT/'pc-results.txt').write_text('PASS: WASD, 1/2 while moving, R, mouse drag and rotation, click fire, Esc, E, cancel. No JS errors.\n')
    finally:proc.terminate();proc.wait(timeout=10);log.close()
if __name__=='__main__':main()
