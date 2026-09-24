"""Small real-Streamlit regression: late boss hit keeps the reinforcement warning visible."""
import os, subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'test-results';out.mkdir(exist_ok=True)
    with (out/'feedback-streamlit.log').open('w') as log:
        server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port','8528','--server.address','127.0.0.1'],cwd=ROOT,stdout=log,stderr=log)
        try:
            for _ in range(100):
                try:
                    if urllib.request.urlopen('http://127.0.0.1:8528/_stcore/health').read()==b'ok':break
                except Exception:time.sleep(.1)
            with sync_playwright() as pw:
                opts=dict(headless=True,args=['--no-sandbox'])
                if os.environ.get('CHROME_PATH'):opts['executable_path']=os.environ['CHROME_PATH']
                browser=pw.chromium.launch(**opts);page=browser.new_page(viewport=dict(width=844,height=390));errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto('http://127.0.0.1:8528');page.locator('iframe').first.wait_for();f=page.locator('iframe').first.element_handle().content_frame()
                f.locator('#new').click();f.locator('#next').click();f.locator('#start').click();f.locator('#enter').click();f.evaluate('freeze()')
                f.evaluate('''()=>{const before=clone(FS.state.progress), after=clone(before);after.triggers.loader_warning=true;after.triggers.elevator_unlock=true;worldFeedback(before,after);}''')
                assert 'refuerzos en 2 segundos' in f.locator('#toast').inner_text()
                assert not errors,errors
                browser.close();print('PASS: simultaneous threshold/elevator events preserve reinforcement telegraph')
        finally:server.terminate();server.wait(timeout=10)
if __name__=='__main__':main()
