"""Integration + viewport smoke test. Starts a real Streamlit server.
Run from repo root: python tests/browser_smoke.py
Uses controlled positions to reach systems quickly; not a full balance/playthrough test.
"""

import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.request
from fractions import Fraction
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)
PORT = 8517


def answer_for(q):
    prompt = q["prompt"]
    if q["category"] == "theory":
        if "diámetro" in prompt:
            return "Micrómetro"
        if "aceptable" in prompt:
            return "0.503"
        return "La calibración del instrumento"
    if q["category"] == "special":
        return re.search(r"/(\d+)", prompt).group(1)
    f = re.search(r"(\d+/\d+)", prompt)
    value = Fraction(f.group(1) if f else re.search(r"\d+\.\d+", prompt).group(0))
    if q["category"] in ["to_fraction", "simplify"]:
        return str(value)
    return str(float(value))


def solve(frame):
    frame.wait_for_function("modalQuestion !== null")
    q = frame.evaluate("modalQuestion")
    answer = answer_for(q)
    if q["mode"] == "manual":
        for ch in answer:
            frame.locator(f'[data-key="{ch}"]').click()
        frame.locator("#confirm").click()
    else:
        choice = next(
            i
            for i, c in enumerate(q["choices"])
            if c == answer
            or (q["category"] != "theory" and Fraction(c) == Fraction(answer))
        )
        frame.locator(f'[data-choice="{choice}"]').click()
    frame.locator("#return").wait_for()
    assert "CALIBRATION ERROR" not in frame.locator("#overlay").inner_text()
    frame.locator("#return").click()


def main():
    log = open(OUT / "streamlit.log", "w")
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.port",
            str(PORT),
            "--server.address",
            "127.0.0.1",
        ],
        cwd=ROOT,
        stdout=log,
        stderr=log,
    )
    try:
        for _ in range(100):
            try:
                if (
                    urllib.request.urlopen(
                        f"http://127.0.0.1:{PORT}/_stcore/health", timeout=0.5
                    ).status
                    == 200
                ):
                    break
            except Exception:
                time.sleep(0.1)
        else:
            raise RuntimeError("Streamlit did not start")
        with sync_playwright() as pw:
            kwargs = {"headless": True, "args": ["--no-sandbox"]}
            if os.environ.get("CHROME_PATH"):
                kwargs["executable_path"] = os.environ["CHROME_PATH"]
            browser = pw.chromium.launch(**kwargs)
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto(f"http://127.0.0.1:{PORT}")
            page.locator("iframe").first.wait_for()
            iframe = page.locator("iframe").first.element_handle()
            frame = iframe.content_frame()
            frame.locator("#new").wait_for()
            page.screenshot(path=str(OUT / "01-menu.png"))
            frame.locator("#new").click()
            frame.locator("#name").fill("Esteban")
            frame.locator("#next").click()
            if "--doom" in sys.argv:
                frame.locator("#doom").click()
            frame.locator("#start").click()
            frame.locator("#enter").click()
            frame.wait_for_function("FS.playing && FS.state !== null")
            before = frame.evaluate("FS.state.player.x")
            frame.locator("#world").focus()
            page.keyboard.down("w")
            page.wait_for_timeout(200)
            page.keyboard.up("w")
            after = frame.evaluate("FS.state.player.x")
            assert after > before, (before, after)
            ammo = frame.evaluate("FS.state.weapons.pistol.loaded")
            frame.locator("#fire").click()
            page.wait_for_timeout(120)
            assert frame.evaluate("FS.state.weapons.pistol.loaded") < ammo
            page.screenshot(path=str(OUT / "02-game-desktop.png"))
            # Pause and resume preserves world; there is no iframe remount per action.
            frame.locator("#pause").click()
            frame.locator("#resume").wait_for()
            frame.locator("#resume").click()
            assert frame.evaluate("FS.state.player.x") >= after
            # Pick up actual shotgun and armor using the game's collision handler.
            frame.evaluate("FS.state.player.x=6.5;FS.state.player.y=6.5;pickups()")
            assert frame.evaluate("FS.state.weapons.shotgun.loaded") == 8
            frame.wait_for_function("!Bridge.busy")
            frame.evaluate('FS.state.player.x=4;FS.state.player.y=3;ask("terminal")')
            frame.wait_for_function("modalQuestion !== null")
            frame.evaluate('submitAnswer("999")')
            frame.locator("#again").wait_for()
            assert "CALIBRATION ERROR" in frame.locator("#overlay").inner_text()
            frame.locator("#again").click()
            solve(frame)
            assert frame.evaluate("FS.state.stats.attempted") == 2
            # Controlled test arena, no immunity: actual shoot(), damage, ammo, kills.
            frame.evaluate(
                "FS.state.player.x=13;FS.state.player.y=8;FS.state.player.angle=0;FS.state.player.hp=100;FS.state.enemies.forEach((e,i)=>{e.x=14+i;e.y=8;e.cooldown=99});FS.cooldown=0;shoot()"
            )
            assert frame.evaluate("FS.state.stats.ammo_used") >= 2
            assert frame.evaluate("FS.state.enemies.some(e=>e.hp<34)")
            frame.evaluate("FS.state.enemies.forEach(e=>e.hp=0)")
            # M.A.D. applies the Python-owned upgrade.
            frame.wait_for_function("!Bridge.busy")
            frame.evaluate(
                'FS.state.player.x=13.5;FS.state.player.y=2.5;ask("mad","shotgun")'
            )
            solve(frame)
            assert frame.evaluate("FS.state.weapons.shotgun.mods") == 1
            assert frame.evaluate("FS.config.weapons.shotgun.range") == 10
            # Door hologram, then real enemy combat.
            frame.wait_for_function("!Bridge.busy")
            frame.evaluate('FS.state.player.x=20;FS.state.player.y=7.5;ask("door")')
            frame.wait_for_function("modalQuestion !== null")
            page.screenshot(path=str(OUT / "03-hologram.png"))
            solve(frame)
            assert frame.evaluate("FS.state.progress.doors.power_door")
            # Fixture clears remaining enemies to check finishing/checkpoint flow, not balance.
            frame.evaluate(
                "FS.state.enemies.forEach(e=>e.hp=0);FS.state.player.x=19;FS.state.player.y=7.5"
            )
            frame.wait_for_function('FS.state.checkpoint === "final"')
            frame.evaluate("FS.state.player.hp=0;death()")
            frame.locator("#restart").click()
            frame.wait_for_function("FS.playing && FS.state.player.hp>0")
            frame.evaluate("FS.state.player.x=25;FS.state.player.y=7.5")
            page.wait_for_timeout(100)
            frame.locator("#interact").click()
            frame.locator("#menu").wait_for()
            assert "MISSION COMPLETE" in frame.locator("#overlay").inner_text()
            page.screenshot(path=str(OUT / "04-mission.png"))
            frame.locator("#menu").click()
            # Reload: restore portable browser slot in a new Streamlit session.
            page.reload()
            page.locator("iframe").first.wait_for()
            frame = page.locator("iframe").first.element_handle().content_frame()
            frame.locator("#continue").wait_for()
            assert frame.locator("#continue").is_enabled()
            frame.locator("#continue").click()
            frame.locator("#menu").wait_for()
            assert "MISSION COMPLETE" in frame.locator("#overlay").inner_text()
            # Mobile landscape and portrait; mobile difficulty and manual keypad.
            mobile = browser.new_context(
                viewport={"width": 844, "height": 390},
                is_mobile=True,
                has_touch=True,
                device_scale_factor=1,
            )
            mp = mobile.new_page()
            mp.on("pageerror", lambda err: errors.append(str(err)))
            mp.goto(f"http://127.0.0.1:{PORT}")
            mp.locator("iframe").first.wait_for()
            mf = mp.locator("iframe").first.element_handle().content_frame()
            mf.locator("#new").wait_for()
            mp.screenshot(path=str(OUT / "05-mobile-menu.png"))
            mf.locator("#new").tap()
            mf.locator("#name").fill("Practicante móvil")
            mf.locator("#next").tap()
            mf.locator("#doom").tap()
            mf.locator("#start").tap()
            mf.locator("#enter").tap()
            mf.wait_for_function("FS.playing")
            assert mf.evaluate("FS.state.enemies.length") == 6
            mp.screenshot(path=str(OUT / "06-mobile-game.png"))
            # Pointer capture multitouch tested with actual CDP touch events below.
            bb = mf.locator("#move-zone").bounding_box()
            lb = mf.locator("#look").bounding_box()
            cdp = mobile.new_cdp_session(mp)
            px = bb["x"] + bb["width"] / 2
            py = bb["y"] + bb["height"] * 0.65
            lx = lb["x"] + lb["width"] / 2
            ly = lb["y"] + 40
            initial = mf.evaluate("({x:FS.state.player.x,angle:FS.state.player.angle})")
            cdp.send(
                "Input.dispatchTouchEvent",
                {
                    "type": "touchStart",
                    "touchPoints": [
                        {"x": px, "y": py, "id": 0},
                        {"x": lx, "y": ly, "id": 1},
                    ],
                },
            )
            mp.wait_for_timeout(150)
            cdp.send(
                "Input.dispatchTouchEvent",
                {
                    "type": "touchMove",
                    "touchPoints": [
                        {"x": px, "y": py - 60, "id": 0},
                        {"x": lx + 30, "y": ly, "id": 1},
                    ],
                },
            )
            mp.wait_for_timeout(150)
            cdp.send(
                "Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}
            )
            changed = mf.evaluate("({x:FS.state.player.x,angle:FS.state.player.angle})")
            assert (
                changed["x"] > initial["x"] and changed["angle"] != initial["angle"]
            ), (initial, changed)
            # Request until server generates a manual question (real random bank).
            for _ in range(20):
                mf.wait_for_function("!Bridge.busy")
                mf.evaluate('FS.state.player.x=4;FS.state.player.y=3;ask("terminal")')
                mf.wait_for_function("modalQuestion !== null")
                if mf.evaluate("modalQuestion.mode") == "manual":
                    break
                mf.locator("#cancel").tap()
            else:
                raise AssertionError("No manual question generated")
            mp.screenshot(path=str(OUT / "07-mobile-keypad.png"))
            solve(mf)
            mp.set_viewport_size({"width": 390, "height": 844})
            mf.locator("#rotate").wait_for(state="visible")
            mp.screenshot(path=str(OUT / "08-rotate.png"))
            assert not errors, errors
            print(
                "PASS: menus, movement, shooting, pause, pickup, wrong/correct math, M.A.D., door, combat, checkpoint, death, completion, reload/continue, mobile multitouch, keypad, portrait. No JS errors."
            )
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)
        log.close()


if __name__ == "__main__":
    main()
