# Cambios exactos — v0.2-alpha1 frente a v0.1.1

## Modificados

- `CHANGELOG.md`
- `README.md`
- `VALIDACION.md`
- `game/engine.py`
- `game/mejoras.py`
- `game/nivel.py`
- `game/preguntas.py`
- `game/save_system.py`
- `tests/browser_smoke.py`
- `tests/test_rules.py`
- `ui/frontend/controls.js`
- `ui/frontend/game.js`
- `ui/frontend/index.html`
- `ui/frontend/realtime.js`
- `ui/frontend/renderer.js`

## Nuevos

- `CAMBIOS_V0.2-alpha1.md`
- `docs/LEVEL_CONFIG.md`
- `docs/capturas/v02-hologram.png`
- `docs/capturas/v02-menu.png`
- `docs/capturas/v02-mission.png`
- `docs/capturas/v02-mobile.png`
- `game/world.py`
- `tests/browser_engine.py`
- `tests/test_engine_levels.py`

## Alcance

Se eliminaron límites de mapa y HP fijos, listas recortadas de enemigos, flags globales de estación, checkpoints por coordenadas en código, clamps especiales para la puerta, salida universal por todos los enemigos muertos, fallback de munición para pickups desconocidos, reset de cooldown al cambiar arma y cancelación indiscriminada por resize.

`app.py`, dependencias, CSS, bridge, catálogos de armas/enemigos/dificultad, conversiones exactas, scoring, estadísticas y configuración de Streamlit se conservan. La geometría de industrial_test, posiciones y cantidades de sus encuentros/recursos no cambian. Las nuevas reglas de seguridad y correcciones explícitamente solicitadas sí modifican cuándo se permite interactuar/guardar y cómo se restaura un checkpoint.

Las únicas nuevas dependencias usadas durante el trabajo son herramientas locales de formateo: no se añaden a requirements ni se necesitan para ejecutar el proyecto.
