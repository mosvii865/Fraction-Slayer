"""New alpha contracts in Chromium + actual session_state-loss recovery.
Only this test creates a temporary wrapper to drop server state; no debug API ships.
"""

from pathlib import Path
import os
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright
from mobile_controls import Touches

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)


def main():
    wrapper = ROOT / "_test_recovery_app.py"
    signal = ROOT / "_test_drop_session"
    wrapper.write_text(
        "import streamlit as st\nfrom pathlib import Path\np=Path('_test_drop_session')\nif p.exists():\n    p.unlink()\n    st.session_state.pop('engine',None)\nexec(compile(Path('app.py').read_text(),'app.py','exec'))\n"
    )
    log = open(OUT / "engine-streamlit.log", "w")
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(wrapper),
            "--server.port",
            "8525",
            "--server.address",
            "127.0.0.1",
        ],
        cwd=ROOT,
        stdout=log,
        stderr=log,
    )
    results = []

    def ok(s):
        results.append(s)
        print("PASS:", s, flush=True)

    try:
        for _ in range(100):
            try:
                assert (
                    urllib.request.urlopen(
                        "http://127.0.0.1:8525/_stcore/health", timeout=0.5
                    ).status
                    == 200
                )
                break
            except Exception:
                time.sleep(0.1)
        else:
            raise RuntimeError("Startup failed")
        with sync_playwright() as pw:
            opts = {"headless": True, "args": ["--no-sandbox"]}
            if os.environ.get("CHROME_PATH"):
                opts["executable_path"] = os.environ["CHROME_PATH"]
            browser = pw.chromium.launch(**opts)
            ctx = browser.new_context(
                viewport={"width": 844, "height": 390}, is_mobile=True, has_touch=True
            )
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto("http://127.0.0.1:8525")
            page.locator("iframe").first.wait_for()
            f = page.locator("iframe").first.element_handle().content_frame()
            f.locator("#new").tap()
            f.locator("#level").select_option("industrial_test");f.locator("#next").tap()
            f.locator("#start").tap()
            f.locator("#enter").tap()
            f.wait_for_function("FS.playing")
            f.wait_for_function("!Bridge.busy")
            f.evaluate("freeze()")
            assert f.evaluate("async()=>!!(await rpc('sync'))")
            original = f.evaluate("FS.state.run_id")
            signal.touch()
            assert f.evaluate("async()=>!!(await rpc('sync'))")
            assert f.evaluate("FS.state.run_id") == original and not signal.exists()
            assert "Sesión restaurada" in f.locator("#toast").inner_text()
            ok("Actual Streamlit engine loss -> local slot restore -> sync, same run")
            # Reissue the question after losing the backend while a hologram is open.
            f.evaluate("FS.state.player.x=4;FS.state.player.y=3;ask('terminal')")
            f.wait_for_function("modalQuestion!==null")
            qid = f.evaluate("modalQuestion.id")
            signal.touch()
            f.evaluate("submitAnswer('999')")
            f.wait_for_function(
                "(id)=>modalQuestion!==null&&modalQuestion.id!==id", arg=qid
            )
            assert f.evaluate("FS.state.stats.attempted") == 0
            f.locator("#cancel").tap()
            ok("Pending question renewed after session loss, no false attempt/reward")
            # Browser chrome height notifications must not release a captured thumb.
            touch = Touches(ctx, page)
            b = f.locator("#move-zone").bounding_box()
            x = b["x"] + 100
            y = b["y"] + 150
            touch.down(0, x, y)
            touch.move(0, x, y - 40)
            pointer = f.evaluate("InputControls.movementPointer")
            origin = f.evaluate(
                "({left:document.querySelector('#pad').style.left,top:document.querySelector('#pad').style.top})"
            )
            f.evaluate("visualViewport.dispatchEvent(new Event('resize'))")
            page.wait_for_timeout(80)
            assert (
                f.evaluate("InputControls.movementPointer") == pointer
                and f.evaluate("FS.move.y") < 0
            )
            assert (
                f.evaluate(
                    "({left:document.querySelector('#pad').style.left,top:document.querySelector('#pad').style.top})"
                )
                == origin
            )
            page.set_viewport_size({"width": 844, "height": 422})
            page.wait_for_timeout(250)
            assert (
                f.evaluate("InputControls.movementPointer") == pointer
                and f.evaluate("FS.move.y") < 0
            )
            touch.clear()
            page.set_viewport_size({"width": 844, "height": 390})
            ok(
                "Small visualViewport resize keeps pointerId, joystick origin and movement"
            )
            # Deterministic realtime fixtures; pause the automatic RAF tick, not game functions.
            f.evaluate(
                "freeze();FS.engineFault=true;FS.playing=true;FS.lastSync=1e12;window.baseState=clone(FS.state);window.baseConfig=clone(FS.config)"
            )
            result = f.evaluate(
                """()=>{
              FS.state.player={...FS.state.player,x:3.5,y:4.5,angle:0};FS.state.weapons.shotgun={loaded:8,reserve:12,mods:0};FS.state.weapon='shotgun';FS.cooldown=0;shoot();const cd=FS.cooldown,ammo=FS.state.weapons.shotgun.loaded;selectWeapon('pistol');selectWeapon('shotgun');shoot();return {cd,after:FS.cooldown,ammo,afterAmmo:FS.state.weapons.shotgun.loaded};
            }"""
            )
            assert (
                result["cd"] == result["after"] == 0.85
                and result["ammo"] == result["afterAmmo"]
            )
            ok(
                "Shotgun switch exploit blocked: remaining cooldown and ammunition preserved"
            )
            result = f.evaluate(
                """()=>{
              const e=FS.state.enemies[0];e.x=5;e.y=4.5;e.active=false;e.hp=60;const before=JSON.stringify(e);FS.state.weapon='pistol';FS.cooldown=0;shoot();tick(.04,1);return {hp:e.hp,x:e.x,unsafe:areaUnsafe()};
            }"""
            )
            assert result["hp"] == 60 and result["x"] == 5 and not result["unsafe"]
            ok("Dormant enemy: no hit, no AI and no combat threat")
            result = f.evaluate(
                """()=>{
              FS.config.level.items.push({id:'unknown',type:'mystery',x:3.5,y:4.5,amount:10});const a=FS.state.weapons.pistol.reserve;pickups();return !FS.state.collected.includes('unknown')&&FS.state.weapons.pistol.reserve===a;
            }"""
            )
            assert result
            ok(
                "Unknown pickup leaves inventory and collected unchanged; loop continues"
            )
            result = f.evaluate(
                """()=>{
              const e=FS.state.enemies[0];e.active=true;e.x=6.5;e.y=4.5;e.hp=60;e.search_time=0;FS.state.player.x=3.5;FS.state.player.y=4.5;FS.state.player.angle=0;FS.cooldown=0;FS.reloading=0;shoot();
              FS.state.player.x=12.5;FS.state.player.y=2.5;const x=e.x;tick(.04,2);return {state:e.ai_state,moved:e.x!==x};
            }"""
            )
            assert result["state"] == "searching" and result["moved"]
            ok("Lost LOS searches last known position instead of permanently freezing")
            result = f.evaluate(
                """()=>{
              const e=FS.state.enemies[0],c=FS.config.enemies.worker;e.active=true;e.x=7.7;e.y=3.5;e.facing=0;e.charge_state='charging';e.search_time=4;e.last_known={x:7.7,y:3.5};c.charge_speed=8;FS.state.player.x=6;FS.state.player.y=3.5;tick(.04,3);return {blocked:e.charge_blocked,state:e.charge_state,stun:e.stun_time};
            }"""
            )
            assert (
                result["blocked"]
                and result["state"] == "blocked"
                and result["stun"] > 0
            )
            ok("Generic charge collision produces explicit blocked/stun state")
            result = f.evaluate(
                """()=>{
              const e=FS.state.enemies[0];e.x=5;e.y=4.5;e.active=true;e.hp=60;e.facing=0;FS.config.enemies.worker.rear_multiplier=2;FS.state.player.x=3.5;FS.state.player.y=4.5;FS.state.player.angle=0;FS.state.weapon='pistol';FS.cooldown=0;FS.reloading=0;shoot();return e.hp;
            }"""
            )
            assert result == 12
            ok("Rear angular multiplier uses facing, without a 3D hitbox")
            result = f.evaluate(
                """()=>{
              FS.state.player.grace=2;const hp=FS.state.player.hp;hurt(99);return hp===FS.state.player.hp;
            }"""
            )
            assert result
            ok("Respawn grace blocks damage only while timer is active")
            # Error recovery: renderer is replaced once, restored by user retry.
            f.evaluate(
                "FS.state=baseState;FS.config=baseConfig;FS.engineFault=false;window.realWorld=Render.world;Render.world=()=>{throw new Error('injected render failure')};resume()"
            )
            f.locator("#retry-frame").wait_for()
            assert f.evaluate("FS.engineFault")
            f.evaluate("()=>{Render.world=realWorld;}")
            f.locator("#retry-frame").tap()
            page.wait_for_timeout(150)
            assert f.evaluate("FS.playing&&!FS.engineFault")
            ok("RAF exception shows error and retry restores rendering")
            assert not errors, errors
            page.screenshot(path=str(OUT / "v02-engine-mobile.png"))
            f.wait_for_function("!Bridge.busy")
            signal.touch()
            f.evaluate("slot=null;ask('terminal')")
            f.locator("#new").wait_for()
            assert f.evaluate("FS.sessionUnavailable&&!FS.playing")
            f.evaluate("resume()")
            assert not f.evaluate("FS.playing")
            ok(
                "Missing session without save stays at menu; stale callbacks cannot resume orphan gameplay"
            )
            browser.close()
        (OUT / "engine-results.txt").write_text(
            "\n".join("PASS: " + s for s in results) + "\n"
        )
    finally:
        server.terminate()
        server.wait(timeout=10)
        log.close()
        wrapper.unlink(missing_ok=True)
        signal.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
