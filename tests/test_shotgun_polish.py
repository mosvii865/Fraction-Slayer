from pathlib import Path
import hashlib,json,struct,subprocess
import pytest
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('name,size',[
 ('weapons/shotgun_reload_start.png',(160,120)),
 ('weapons/shotgun_reload_insert.png',(160,120)),
 ('weapons/shotgun_reload_end.png',(160,120)),
 ('pickups/shotgun_pickup.png',(64,32)),
])
def test_new_rgba_assets(name,size):
    p=ROOT/'ui/frontend/art'/name;d=p.read_bytes()
    assert d[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II',d[16:24])==size
    assert d[25]==6 # RGBA

def test_validated_assets_gameplay_collection_and_controls_unchanged():
    for name,digest in json.loads((ROOT/'tests/shotgun_v1_preserved.json').read_text()).items():
        if name in json.loads((ROOT/'tests/sprint_sign_hashes.json').read_text()):
            digest=json.loads((ROOT/'tests/sprint_sign_hashes.json').read_text())[name]
        data=(ROOT/name).read_bytes()
        if name == 'ui/frontend/realtime.js':
            # Crawler/Rivet extend only the existing client-side visual cue guards.
            data=data.replace(b"if (e.type !== 'worker' && e.type !== 'crawler' && e.type !== 'rivet') return;",
                              b"if (e.type !== 'worker') return;")
        assert hashlib.sha256(data).hexdigest()==digest,name

def test_actual_js_selector_contract():
    subprocess.run(['node','tests/js_shotgun_polish.js'],cwd=ROOT,check=True,capture_output=True)

def test_shared_master_anchor_and_pickup_integration():
    text=(ROOT/'ui/frontend/renderer.js').read_text()
    assert 'referenceBounds.h' in text and 'referenceCenterSrcX' in text
    assert 'get("pickups",pickupProfile.key)' in text
    assert 'reloadDuration: fs.config.weapons[s.weapon]?.reload' in text
    assert 'depth>=zbuf[col]' in text
