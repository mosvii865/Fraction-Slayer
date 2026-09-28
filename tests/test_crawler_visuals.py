from pathlib import Path
import struct,subprocess,zlib
import pytest
ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('pose',['idle','walk_1','walk_2','attack','hurt','death'])
def test_crawler_rgba_common_canvas(pose):
    data=(ROOT/f'ui/frontend/art/sprites/crawler_{pose}.png').read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II',data[16:24])==(80,56)
    assert data[25]==6

def test_crawler_actual_js_selectors_and_cues():
    subprocess.run(['node','tests/js_crawler_smoke.js'],cwd=ROOT,check=True,capture_output=True)

def test_crawler_renderer_uses_full_canvas_and_safe_fallback():
    text=(ROOT/'ui/frontend/renderer.js').read_text()
    assert 'window.FSArt.enemyFrameKey(o.type,' in text
    assert "type:v.type,x:v.deadX" in text
    assert "['worker','crawler','rivet'].includes(o.type)" in text
    assert "if (((o.type==='worker' || o.type==='crawler' || o.type==='rivet') || sprintEnemy) && rasterImg)" in text
    assert 'sw = sh *' in text or 'sw=sh*' in text
    assert 'floorY-sh' in text or 'floorY - sh' in text
