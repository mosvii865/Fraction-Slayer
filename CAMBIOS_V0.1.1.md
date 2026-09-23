# Archivos de Fraction Slayer v0.1.1

Comparación contra el ZIP v0.1 recuperado para esta tarea.

## Modificados

- `README.md`
- `VALIDACION.md`
- `tests/browser_smoke.py`
- `ui/frontend/bridge.js`
- `ui/frontend/controls.js`
- `ui/frontend/game.js`
- `ui/frontend/index.html`
- `ui/frontend/realtime.js`
- `ui/frontend/renderer.js`
- `ui/frontend/style.css`

## Añadidos

- `CAMBIOS_V0.1.1.md`
- `CHANGELOG.md`
- `docs/capturas/v011-568x320.png`
- `docs/capturas/v011-desktop.png`
- `docs/capturas/v011-multitouch-selector.png`
- `docs/capturas/v011-safe-areas.png`
- `tests/mobile_controls.py`
- `tests/pc_controls.py`

## Conservados

No se eliminó ningún archivo. Todos los módulos `game/`, `app.py`, `requirements.txt`, `requirements-dev.txt` y `.streamlit/config.toml` se conservan byte a byte. `realtime.js` añade únicamente tres llamadas opcionales de feedback háptico. `renderer.js` solo toma la altura real del HUD para respetar el margen inferior. No hay cambios de mapa, balance, contenido educativo, puntuación ni esquema de guardado.
