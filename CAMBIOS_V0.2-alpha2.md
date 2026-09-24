# Fraction Slayer v0.2-alpha2 — The Workshop

Base: v0.2-alpha1.1-stable adjunta y validada físicamente por el usuario. No se reconstruyó el juego ni se modificaron sus controles/bridge. `industrial_test()` conserva exactamente sus datos; las opciones nuevas tienen valores por defecto compatibles.

## Entrega

- Workshop es el nivel de campaña predeterminado de la UI; Industrial Test permanece seleccionable.
- Ocho zonas principales y dos anexos, 21 enemigos CLÁSICO / 30 DOOM en grupos/oleadas, escopeta durante Assembly.
- Cinco calibraciones fijas, solo denominadores 2/4/8: terminal 1/2, M.A.D. #1 3/4, puerta .375 → 3/8, cache 5/8, M.A.D. #2 7/8. M.A.D./cache manuales en DOOM. No se añade la teoría opcional.
- Fusible quest_item, emboscada persistente, instalación sin pregunta, energía y suministro mínimo de emergencia. Cuatro checkpoints seguros.
- Loader 250 HP: melee, telegraph/carga, impacto/stun 1.75 s, ground slam, recuperación, núcleo trasero ×1.65 y aviso/refuerzos al 50%.
- UTCJ 1/4 por disparo, sin kill, persistencia y ??? si se omite. Salida por energía + Loader, estadísticas y teaser Factory.
- Render procedural propio, zona/objetivo en HUD, destino en minimapa y barra del Loader. Sin imágenes IA.

## Extensiones mínimas

`game/world.py` añade predicados de pickup, final, umbral HP y tiempo desde trigger; registra tiempos opcionales. `game/engine.py` aplica loadout por nivel e instalación transaccional, copia campos opcionales del Loader y rechaza checkpoints con HP cero. `save_system.py` valida esos campos sin cambiar SAVE_VERSION 2. El código de ataques está aislado en `loader.js` y solo se invoca para ese tipo.

Se conservan `app.py`, `requirements.txt`, `requirements-dev.txt`, `game/armas.py`, `game/enemigos.py`, `game/preguntas.py`, `game/conversiones.py`, `game/dificultad.py`, scoring, `ui/frontend/controls.js` y `ui/frontend/bridge.js`. Catálogo Loader definido por Workshop, sin cambiar otros tipos. La munición de Workshop es explícita y no altera Industrial Test.

## Errores corregidos durante esta alpha

- Salida automática iniciaba `finish` fuera del radio permitido: ahora comprueba `interaction_distance` además de zona y objetivos en `realtime.js`.
- El umbral del 50% podía perderse si un snapshot agrupaba hasta el golpe fatal: condición inclusiva de cero y flag monotónico, con test de latencia. El aviso de refuerzos tiene prioridad sobre el aviso simultáneo de elevador.
- Toast ocultaba barra del boss en móvil: separación CSS solo mientras se muestra esa barra.
- Pruebas anteriores dependían del destino predeterminado y una tenía una carrera al solicitar preguntas entre syncs. Selección explícita de Industrial Test y pausa del fixture antes de interactuar; ningún parche del bridge.

## Validación

101 tests Python aprobados; Streamlit real + Chromium para ambos recorridos Workshop, regresión Industrial Test en ambos modos, save v1/v2, sesión, PC y multitouch/safe areas. Tests nuevos: reglas de Workshop, recorridos reales y prioridad de feedback. Evidencias y alcance en VALIDACION.md.

La ruta automatizada usa gracia de test y ticks acelerados, con disparos/colisiones/munición reales. No certifica balance ni duración de 8–12 minutos. Esos puntos, rendimiento y Safari/haptics físicos siguen pendientes. Próximo paso: playtest físico y ajuste de datos, antes de The Factory.

## Archivos modificados respecto del ZIP estable

- `CHANGELOG.md`
- `README.md`
- `VALIDACION.md`
- `docs/LEVEL_CONFIG.md`
- `game/engine.py`
- `game/nivel.py`
- `game/roadmap.py`
- `game/save_system.py`
- `game/world.py`
- `tests/browser_engine.py`
- `tests/browser_smoke.py`
- `tests/browser_startup.py`
- `tests/mobile_controls.py`
- `tests/pc_controls.py`
- `ui/frontend/game.js`
- `ui/frontend/index.html`
- `ui/frontend/realtime.js`
- `ui/frontend/renderer.js`
- `ui/frontend/style.css`

## Archivos añadidos

- `docs/VALIDACION_ALPHA1_STABLE.md`
- `game/workshop.py`
- `tests/browser_workshop.py`
- `tests/browser_workshop_feedback.py`
- `tests/test_workshop.py`
- `tests/workshop_driver.js`
- `ui/frontend/loader.js`
- `CAMBIOS_V0.2-alpha2.md`
- `docs/validacion-alpha2/`: capturas y resultados de esta ejecución.
