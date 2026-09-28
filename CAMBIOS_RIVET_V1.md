# Fraction Slayer — Rivet v1 candidate

Integración visual de **RIVET v1 / DDI R-02**, fase 1 técnico DDI / ensamble industrial.

## Base y referencia

Se utilizó exclusivamente `Fraction_Slayer_v0.3-alpha2-crawler-v1-candidate.zip`, entregada en la iteración anterior y validada por el usuario, con el hotfix global de recarga incluido. No se reconstruyeron niveles ni sistemas.

Los sprites se extrajeron directamente de la hoja aprobada adjunta `image(20260927-220539).png`, incluida como `docs/rivet_v1_approved_reference.png`. No se regeneró ni rediseñó el personaje. Los SHA-256 y archivos modificados se registran en `docs/rivet_v1_provenance.json`.

## Assets

En `ui/frontend/art/sprites/`:
- `rivet_idle.png`
- `rivet_walk_1.png`
- `rivet_walk_2.png`
- `rivet_attack.png`
- `rivet_hurt.png`
- `rivet_death.png`

PNG RGBA transparentes de **80×80**. Se amplió el ancho recomendado de 64 a 80 para contener la remachadora disparando y el cuerpo caído sin recortar ni reducir esas poses individualmente. La altura del canvas sigue el estándar de 80 píxeles del Worker. Todas las poses tienen una reducción común 0.19, con vecino más cercano y traslación vertical al plano de apoyo. No hay autoajuste de escala por bounding box.

Se eliminaron fondo, rótulos y líneas de suelo de presentación. Se conservan casco, visor, arnés, credencial, herramienta, colores y poses originales. El destello de ataque está extraído de la hoja. El pequeño humo de presentación sobre el cadáver no se convierte en un nuevo efecto.

`tools/extract_rivet_v1.py` permite repetir el proceso offline con Pillow, numpy y scipy; estas bibliotecas no se añadieron a los requisitos del juego. Preview en `docs/rivet_v1_preview.png`.

## Integración mínima

Archivos de producción modificados:
- `ui/frontend/art.js`: seis entradas y perfil Rivet. Reutiliza death > hurt > attack > move > idle.
- `ui/frontend/realtime.js`: solo se amplían tres filtros de las señales visuales para aceptar `rivet`. Ninguna operación de IA, daño, movimiento, proyectiles, cooldown o recarga cambia.
- `ui/frontend/renderer.js`: incluye Rivet en la selección de poses, cadáver temporal y cálculo proporcional del canvas completo. Conserva altura de mundo 1, línea de suelo, oclusión y fallback original.

Las señales continúan en `FS.enemyVisuals`, fuera del save. Muerte visible durante los mismos 1.15 segundos del mecanismo existente. El reset existente borra las señales. No se crean entidades de gameplay ni kills adicionales.

**Gameplay intacto:** comparación binaria contra el ZIP base; todo Python, mapas, campaña, M.A.D., saves, controles y assets anteriores permanecen idénticos. Crawler, Worker, Pistola y DDI Breach Pump no cambian. No cambian HP, daño, velocidad, frecuencias, hitboxes, munición ni spawns.

## Tests

Nuevos: `tests/test_rivet_visuals.py`, `tests/js_rivet_smoke.js`, `tests/browser_rivet.py`, `tests/rivet_preserved_base.json`.

Actualizados: `tests/test_crawler_visuals.py` admite la lista ampliada de tipos; `tests/test_shotgun_polish.py` normaliza exclusivamente los tres filtros visuales antes de verificar el hash original. Se conservan las comprobaciones anteriores. El nuevo manifiesto protege 81 archivos de la base, incluidos todos los assets previos y la lógica; realtime solo admite las tres ampliaciones exactas.

Resultados:
- `python -m pytest -q`: **194 passed**.
- `python -m compileall -q app.py game ui tests tools`: correcto.
- `node --check`: **17 JS**, correcto.
- Smoke JS de arte, Rivet, Crawler, shotgun, Laboratory y Foundry: correctos.
- `python tests/browser_rivet.py`: **Streamlit real + Chromium**, Workshop CLÁSICO/escritorio 1280×720 y DOOM/móvil emulado 900×405. Se dibujan los seis estados, con idéntica altura de canvas proyectada y anclaje. Worker y Crawler se renderizan simultáneamente. Proyectil real, daño al jugador, hurt, muerte por disparos y limpieza al iniciar partida: correctos. Sin errores de página ni ERROR DE MOTOR.
- `python tests/browser_crawler.py`: regresión completa del set Crawler en ambos viewports, correcta.
- `python tests/browser_shotgun_polish.py`: pickup, disparo, ambos pumps, tres etapas de recarga, munición, cambios rápidos y reset: correctos en ambos viewports.

La primera invocación de pytest se realizó desde la carpeta superior y falló por no encontrar `game`; se corrigió el directorio de ejecución, sin parchear imports ni código del juego.

Resultados JSON en `docs/rivet_v1_browser_results.json`, `docs/rivet_v1_crawler_regression.json` y `docs/rivet_v1_shotgun_regression.json`. Capturas revisadas en `docs/rivet_v1_ingame_preview.png` y `docs/rivet_v1_mobile_preview.png`.

## Alcance de la validación

El navegador usa posiciones y señales controladas para revisar poses; el combate ejecuta tick/disparo/proyectiles reales sin cambiar configuraciones. Para comprobar marcha en una sala pequeña, el test fuerza temporalmente pérdida de línea de visión y última posición conocida; restaura la función inmediatamente. Esto es una fixture del test, no un cambio de IA del juego.

No se completó de nuevo toda la campaña ni se realizó playtest de balance. Falta validar Rivet físicamente en PC/celular; no se probó Safari. La hoja solo contiene una orientación, por lo que se conserva el billboard existente. No se inventaron vistas traseras, variantes Factory/Foundry ni fases futuras. La superposición previa de textos de señalización queda fuera de esta integración.

## Entrega

ZIP completo con código, requisitos, seis sprites, tests, referencia, previews, evidencia y este documento. Ejecución sin cambios: `pip install -r requirements.txt` y `python -m streamlit run app.py`.
