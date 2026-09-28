from pathlib import Path
import hashlib,json,struct,subprocess
import pytest
ROOT=Path(__file__).resolve().parents[1]
ASSETS={
'sawed_off':['sawed_off','sawed_off_fire','sawed_off_break_open','sawed_off_reload_insert','sawed_off_close'],
'assault':['assault','assault_fire','assault_reload_start','assault_reload_swap','assault_reload_end'],
'sniper':['sniper','sniper_fire','sniper_bolt_back','sniper_bolt_forward','sniper_reload'],
'lmg':['lmg','lmg_fire','lmg_reload_start','lmg_reload_box','lmg_reload_end'],
'rocket':['rocket','rocket_fire','rocket_reload_open','rocket_reload_insert','rocket_reload_close']}
@pytest.mark.parametrize('asset',[n for names in ASSETS.values() for n in names])
def test_viewmodel_canvas(asset):
 d=(ROOT/f'ui/frontend/art/weapons/{asset}.png').read_bytes();assert struct.unpack('>II',d[16:24])==(160,120) and d[25]==6
@pytest.mark.parametrize('weapon',ASSETS)
def test_pickup_canvas(weapon):
 d=(ROOT/f'ui/frontend/art/pickups/{weapon}_pickup.png').read_bytes();assert struct.unpack('>II',d[16:24])==(64,40) and d[25]==6
@pytest.mark.parametrize('pose',['idle','walk_1','walk_2','attack','hurt','death'])
def test_boss_canvas(pose):
 d=(ROOT/f'ui/frontend/art/sprites/boss_{pose}.png').read_bytes();assert struct.unpack('>II',d[16:24])==(128,128) and d[25]==6

def test_actual_selectors_and_cleanup():
 subprocess.run(['node','tests/js_final_visuals.js'],cwd=ROOT,check=True,capture_output=True)

def test_gameplay_and_previous_art_unchanged():
 for name,digest in json.loads((ROOT/'tests/final_preserved.json').read_text()).items():
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name

def test_no_double_procedural_flash_and_shared_master():
 s=(ROOT/'ui/frontend/renderer.js').read_text()
 assert 'if (rasterWeapon) ctx.globalAlpha = 0;' in s
 assert 'referenceBounds.h' in s and 'referenceCenterSrcX' in s
 assert 'o._weaponPickup && o.type===o.weapon' in s
