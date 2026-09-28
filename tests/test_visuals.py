from pathlib import Path
import struct
from game.workshop import workshop

ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT / 'ui' / 'frontend'

def png_size(path: Path):
    data = path.read_bytes()[:24]
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    return struct.unpack('>II', data[16:24])

def test_visual_manifest_loaded_before_renderer():
    html = (FRONT / 'index.html').read_text(encoding='utf-8')
    assert '<script src="art.js"></script>' in html
    assert html.index('art.js') < html.index('renderer.js')
    art = (FRONT / 'art.js').read_text(encoding='utf-8')
    assert 'zero-failure fallbacks' in art
    assert 'workshop_wall' in art

def test_workshop_visual_assets_exist_and_are_valid_pngs():
    expected = [
        'art/sprites/worker.png','art/sprites/crawler.png','art/sprites/rivet.png',
        'art/sprites/loader.png','art/sprites/mad.png','art/sprites/terminal.png',
        'art/weapons/pistol.png','art/weapons/shotgun.png',
        'art/textures/workshop_wall.png','art/textures/workshop_panel.png','art/textures/workshop_door.png',
        'art/props/crate.png','art/props/tool_chest.png','art/props/sign_assembly.png',
    ]
    for rel in expected:
        p = FRONT / rel
        assert p.exists(), rel
        w,h = png_size(p)
        assert w > 0 and h > 0

def test_workshop_has_visual_only_props_without_changing_grid_contract():
    level = workshop()
    assert level['revision'] == 1
    assert len(level['props']) >= 18
    ids = [p['id'] for p in level['props']]
    assert len(ids) == len(set(ids))
    assert all({'id','art','x','y'} <= set(p) for p in level['props'])
    # Props are not stations/items and therefore cannot affect saves or objectives.
    station_ids = {s['id'] for s in level['stations']}
    item_ids = {i['id'] for i in level['items']}
    assert not (set(ids) & station_ids)
    assert not (set(ids) & item_ids)

def test_renderer_keeps_procedural_fallbacks():
    js = (FRONT / 'renderer.js').read_text(encoding='utf-8')
    assert 'window.FSArt?.get("sprites", visual)' in js
    assert '|| sprite(fallbackVisual)' in js
    assert 'workshop_door' in js
    assert 'fs.config.level.props || []' in js

def test_pistol_viewmodel_has_idle_fire_reload_state_machine_and_shared_reference_anchor():
    art = (FRONT / 'art.js').read_text(encoding='utf-8')
    renderer = (FRONT / 'renderer.js').read_text(encoding='utf-8')
    for key in ['pistol.png', 'pistol_fire.png', 'pistol_reload.png']:
        p = FRONT / 'art' / 'weapons' / key
        assert p.exists(), key
        assert png_size(p) == (160, 120)
    assert 'weaponFrameKey' in art
    assert 'reload: "pistol_reload"' in art
    assert 'reference: "pistol"' in art
    assert 'reloading: fs.reloading' in renderer
    assert 'referenceBounds' in renderer
    assert 'Scale comes from the REFERENCE frame' in renderer


def test_worker_v1_sprite_set_is_consistent_and_renderer_uses_client_only_states():
    names = [
        'worker_idle.png','worker_walk_1.png','worker_walk_2.png',
        'worker_attack.png','worker_hurt.png','worker_death.png',
    ]
    for name in names:
        path = FRONT / 'art' / 'sprites' / name
        assert path.exists(), name
        assert png_size(path) == (64, 80), name
        # Production frames should be real art, not the tiny placeholder sprites.
        assert path.stat().st_size > 1500, name
    art = (FRONT / 'art.js').read_text(encoding='utf-8')
    renderer = (FRONT / 'renderer.js').read_text(encoding='utf-8')
    realtime = (FRONT / 'realtime.js').read_text(encoding='utf-8')
    game = (FRONT / 'game.js').read_text(encoding='utf-8')
    for key in ['worker_idle','worker_walk_1','worker_walk_2','worker_attack','worker_hurt','worker_death']:
        assert key in art
    assert 'enemyFrameKey' in art
    assert 'deadWorkerObjects' in renderer
    assert 'sw=sh*(rw/Math.max(1,rh))' in renderer
    assert 'enemyVisuals: {}' in game
    assert 'Client-only animation state' in game
    assert 'markEnemyVisualHit' in realtime
    assert 'markEnemyVisualAttack' in realtime


def test_ddi_breach_pump_sprite_set_and_visual_cycle_are_consistent():
    names = [
        'shotgun.png','shotgun_fire.png','shotgun_pump_back.png',
        'shotgun_pump_forward.png','shotgun_reload.png',
    ]
    for name in names:
        path = FRONT / 'art' / 'weapons' / name
        assert path.exists(), name
        assert png_size(path) == (160, 120), name
        assert path.stat().st_size > 5000, name
    art = (FRONT / 'art.js').read_text(encoding='utf-8')
    renderer = (FRONT / 'renderer.js').read_text(encoding='utf-8')
    realtime = (FRONT / 'realtime.js').read_text(encoding='utf-8')
    game = (FRONT / 'game.js').read_text(encoding='utf-8')
    for key in ['shotgun_fire','shotgun_pump_back','shotgun_pump_forward','shotgun_reload']:
        assert key in art
    assert 'reference: "shotgun"' in art
    assert 'pumpAnim: fs.pumpAnim' in renderer
    assert 'if (s.weapon === "shotgun") FS.pumpAnim = 0.36' in realtime
    assert 'FS.pumpAnim = Math.max(0' in realtime
    assert 'pumpAnim: 0' in game
    # The authored fire frame already contains its own muzzle flash, so the
    # renderer must not add the old procedural flash on top of it.
    assert 'if (fs.shotFlash > 0 && !profile?.fire)' in renderer
