from pathlib import Path
import hashlib,json,struct,subprocess
import pytest
ROOT=Path(__file__).resolve().parents[1]
FAMILIES={'sentinel':(80,64),'gunner':(80,80),'stalker':(80,80),'specimen_k32':(112,112),'furnace_hound':(96,64),'forge_brute':(112,112),'loader':(112,96),'foreman_mk2':(112,112)}
@pytest.mark.parametrize('family,size',FAMILIES.items())
@pytest.mark.parametrize('pose',['idle','walk_1','walk_2','attack','hurt','death'])
def test_asset(family,size,pose):
 data=(ROOT/f'ui/frontend/art/sprites/{family}_{pose}.png').read_bytes()
 assert data[:8]==b'\x89PNG\r\n\x1a\n' and data[25]==6
 assert struct.unpack('>II',data[16:24])==size

def test_selectors_observer_and_telegraphs():
 subprocess.run(['node','tests/js_sprint_smoke.js'],cwd=ROOT,check=True,capture_output=True)

def test_base_gameplay_and_validated_assets_unchanged():
 for name,digest in json.loads((ROOT/'tests/sprint_preserved.json').read_text()).items():
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name

@pytest.mark.parametrize('key',['qc','tools','assembly','power','exit','generator'])
def test_sign_canvas(key):
 data=(ROOT/f'ui/frontend/art/props/sign_{key}.png').read_bytes()
 assert struct.unpack('>II',data[16:24])==(256,128)
 assert data[25]==6

def test_frames_are_distinct():
 for family in FAMILIES:
  assert len({hashlib.sha256((ROOT/f'ui/frontend/art/sprites/{family}_{p}.png').read_bytes()).hexdigest() for p in ['idle','walk_1','walk_2','attack','hurt','death']})==6
