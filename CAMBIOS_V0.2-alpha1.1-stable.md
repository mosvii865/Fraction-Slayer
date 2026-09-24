# Archivos y alcance — v0.2-alpha1.1-stable

Base: ZIP candidate adjunto. El guard `current?.order ?? -1` y el test Python correspondiente ya estaban presentes. No se reaplicaron. La lógica de realtime es idéntica al quitar las marcas `FS.debugStage`; se verificó por comparación de texto. El save, datos del nivel, catálogo, balance, app.py y arquitectura no cambiaron.

## Archivos modificados frente a candidate

- `CHANGELOG.md`
- `README.md`
- `VALIDACION.md`
- `game/engine.py`
- `tests/browser_smoke.py`
- `ui/frontend/bridge.js`
- `ui/frontend/controls.js`
- `ui/frontend/game.js`
- `ui/frontend/index.html`
- `ui/frontend/realtime.js`
- `ui/frontend/renderer.js`
- `ui/frontend/style.css`

## Nuevos

- `docs/validacion-stable/controlled-null-first-error.json`
- `docs/validacion-stable/engine-results.txt`
- `docs/validacion-stable/pc-results.txt`
- `docs/validacion-stable/stable-clasico-pc.png`
- `docs/validacion-stable/stable-doom-mobile.png`
- `docs/validacion-stable/startup-results.json`
- `tests/browser_startup.py`
- `CAMBIOS_V0.2-alpha1.1-stable.md`

## Líneas y significado

- Candidata: `ui/frontend/realtime.js:428` obtiene `current`; línea 429 contiene el guard existente.
- Stable: líneas 433–435 hacen la misma selección, después de incorporar marcas de etapa. La línea 434 conserva el fallback.
- La excepción reproducida al retirar el guard fue `TypeError: Cannot read properties of undefined (reading 'order')`, etapa `CHECKPOINT_UPDATE`, con `checkpoint=null` inyectado explícitamente.
- No hubo crash espontáneo durante Nueva Partida: el backend inicia con `inicio`. Por tanto, no se atribuye sin evidencia el incidente remoto original a null.
- `game/engine.py`: solo logging limitado y contexto de excepción; reglas conservadas.
- `controls.js`, `bridge.js`, `renderer.js`, `style.css`: diagnóstico, contexto, etapas y panel copiable. `game.js`/`index.html`: etiqueta de versión.
- `tests/browser_startup.py`: nueva regresión real Streamlit/Chromium. `browser_smoke.py`: opción `--doom` para repetir el recorrido en ese modo.
- Documentación/capturas: resultados y límites; no son assets nuevos de gameplay.

No hubo otro fallo reproducible que requiriera hotfix de gameplay o arquitectura.
