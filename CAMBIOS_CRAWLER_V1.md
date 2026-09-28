# Fraction Slayer v0.3-alpha2 — Crawler v1 candidate

Integración exclusivamente visual del **CRAWLER v1 / DDI C-01**, fase 1 industrial/robótico. No se rediseñó el enemigo ni se generaron variantes nuevas.

## Fuente de verdad

Base: `Fraction_Slayer_v0.3-alpha2-shotgun-v1.1-polish-reload-hotfix-candidate(1).zip`.
SHA-256: `8a947e23a1c23110d606c635d70460033c43d9e929fec7e41b1d0cc801a4b69b`.

Referencia aprobada: `crawler_v1_concept_sheet(2).png`, conservada en `docs/crawler_v1_approved_reference.png`.
SHA-256: `5668353d8048e08659a6ea5a9c4b0305051fd1a4100fc602cc1dc727c7a79006`.

## Sprites y extracción

Se extrajeron las seis poses originales; se retiraron fondo, rótulos y sombra de la hoja. Se conservaron chasis, pinzas, placas, patas y detalles amarillo/cyan.

Ruta: `ui/frontend/art/sprites/`:
- `crawler_idle.png`
- `crawler_walk_1.png`
- `crawler_walk_2.png`
- `crawler_attack.png`
- `crawler_hurt.png`
- `crawler_death.png`

PNG RGBA transparentes de **80×56**. Reducción común de 0.15 con vecino más cercano, traslaciones para alinear el apoyo; no se ajusta escala a bounding boxes individuales. Un píxel de variación del contacto en hurt representa el desbalance de esa pose. El colapso conserva su menor altura dentro del mismo canvas.

`tools/extract_crawler_v1.py` reproduce la extracción (solo herramienta offline; requiere Pillow/numpy/scipy). No se añadieron dependencias al juego. `docs/crawler_v1_preview.png` muestra el set ampliado.

## Integración mínima

Archivos de producción modificados:
- `ui/frontend/art.js`: manifiesto y perfil Crawler; selector existente con prioridad death > hurt > attack > move > idle.
- `ui/frontend/realtime.js`: únicamente tres condiciones de las funciones de señales visuales permiten también Crawler. No cambia ninguna operación de combate, movimiento o recarga.
- `ui/frontend/renderer.js`: selección de poses, cadáver visual temporal, proporción 80:56, altura visual de canvas .68 y anclaje al suelo. Continúa la oclusión por profundidad existente y el fallback procedural si falta un asset.

Las señales son client-side en `FS.enemyVisuals`; no se serializan. El reset existente limpia el set al restaurar/iniciar. El cadáver dura los mismos 1.15 s del mecanismo de Worker; no crea entidades de gameplay ni kills extra.

**Gameplay intacto:** comparación binaria con la base confirma sin cambios todo Python, mapas, IA salvo los tres filtros visuales indicados, controles, campaña, guardado, M.A.D. y todos los assets anteriores. Pistola, Worker, shotgun idle/fire/pump/reload y pickup conservan sus bytes. No se modificaron daño, HP, velocidad, cadencia, munición, radios ni spawns.

## Tests y archivos de validación

Añadidos:
- `tests/test_crawler_visuals.py`
- `tests/js_crawler_smoke.js`
- `tests/browser_crawler.py`

Actualizado `tests/test_shotgun_polish.py`: conserva los hashes originales; antes de comparar realtime.js normaliza **únicamente** las tres condiciones visuales nuevas a las originales. Así no se permite ocultar cambios de gameplay actualizando un digest completo.

Ejecutados:
- `python -m pytest -q`: **185 passed**.
- `python -m compileall -q app.py game ui tests tools`: correcto.
- `node --check`: todos los JS de frontend y tests, **16 archivos**.
- Smoke JS: arte, Crawler, shotgun, Laboratory y Foundry: correctos.
- `python tests/browser_crawler.py`: Streamlit real + Chromium; escritorio 1280×720 CLÁSICO y móvil emulado 900×405 DOOM. Se dibujan las seis poses, con igual altura proyectada y mismo anclaje; movimiento/ataque por tick real, daño al jugador, hurt y muerte por disparos reales; reset sin cadáver residual. Sin pageerror ni ERROR DE MOTOR.
- `python tests/browser_shotgun_polish.py`: Streamlit real, escritorio/móvil; pickup, fire, pump_back, pump_forward, tres etapas de recarga, conservación de munición, cambios rápidos y reinicio: correctos.

Resultados: `docs/crawler_v1_browser_results.json`, `docs/crawler_v1_shotgun_regression_results.json`. Captura revisada: `docs/crawler_v1_ingame_preview.png`.

## Alcance y límites

Las pruebas del Crawler usan posiciones y señales controladas para observar cada pose; el combate ejecuta las funciones reales. No son un recorrido completo de los cuatro niveles ni un playtest de balance. No se probaron dispositivos físicos ni Safari en esta iteración. Queda validar en celular físico la legibilidad y cadencia visual durante encuentros reales.

El arte aprobado es de una sola orientación; esta candidata conserva el billboard existente y no inventa vistas laterales/traseras. El detalle DDI pierde lectura a 80×56, pero la silueta, herramientas, placas y colores permanecen. No hay fases 2/3.

## Otros archivos nuevos

Este documento, seis PNG, herramienta offline, referencia aprobada, preview del set, captura y dos JSON de resultados. README, versiones de save y requisitos originales no se alteran. Ejecución habitual: `pip install -r requirements.txt` y `python -m streamlit run app.py`.
