from pathlib import Path
import struct,subprocess,zlib
import pytest
ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('pose',['idle','walk_1','walk_2','attack','hurt','death'])
def test_rivet_rgba_common_canvas(pose):
    data=(ROOT/f'ui/frontend/art/sprites/rivet_{pose}.png').read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II',data[16:24])==(80,80)
    assert data[25]==6

def test_rivet_actual_js_selectors_and_cues():
    subprocess.run(['node','tests/js_rivet_smoke.js'],cwd=ROOT,check=True,capture_output=True)

def test_rivet_renderer_uses_full_canvas_and_safe_fallback():
    text=(ROOT/'ui/frontend/renderer.js').read_text()
    assert 'window.FSArt.enemyFrameKey(o.type,' in text
    assert "type:v.type,x:v.deadX" in text
    assert "['worker','crawler','rivet'].includes(o.type)" in text
    assert "if (((o.type==='worker' || o.type==='crawler' || o.type==='rivet') || sprintEnemy) && rasterImg)" in text
    assert 'sw = sh *' in text or 'sw=sh*' in text
    assert 'floorY-sh' in text or 'floorY - sh' in text


def test_validated_base_and_gameplay_preserved():
    import hashlib,json
    for name,digest in json.loads((ROOT/'tests/rivet_preserved_base.json').read_text()).items():
        if name in json.loads((ROOT/'tests/sprint_sign_hashes.json').read_text()):
            digest=json.loads((ROOT/'tests/sprint_sign_hashes.json').read_text())[name]
        data=(ROOT/name).read_bytes()
        if name=='ui/frontend/realtime.js':
            old=b"if (e.type !== 'worker' && e.type !== 'crawler') return;"
            new=b"if (e.type !== 'worker' && e.type !== 'crawler' && e.type !== 'rivet') return;"
            assert data.count(new)==3
            data=data.replace(new,old)
        assert hashlib.sha256(data).hexdigest()==digest,name
