from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REALTIME = (ROOT / "ui/frontend/realtime.js").read_text(encoding="utf-8")


def test_reload_guard_uses_positive_countdown_not_truthiness():
    assert "if (!FS.playing || FS.reloading > 0) return;" in REALTIME
    assert "if (!FS.playing || FS.reloading) return;" not in REALTIME


def test_reload_countdown_is_clamped_to_zero():
    assert "FS.reloading = Math.max(0, FS.reloading - dt);" in REALTIME
    assert "if (FS.reloading === 0)" in REALTIME


def test_reload_completion_still_transfers_loaded_and_reserve_ammo():
    assert "need = FS.config.weapons[s.weapon].capacity - w.loaded" in REALTIME
    assert "n = Math.min(need, w.reserve);" in REALTIME
    assert "w.loaded += n;" in REALTIME
    assert "w.reserve -= n;" in REALTIME
