# Fraction Slayer v0.3-alpha2 — Visual Delivery Sprint Candidate

Base exclusiva: `Fraction_Slayer_v0.3-alpha2-rivet-v1-candidate(1).zip` adjunta. No se reconstruyó el proyecto. SHA-256 y comparación de archivos en `docs/sprint-base-comparison.json`.

## Entregado

**Ocho familias completas, 48 sprites nuevos e integrados.** Cada familia contiene idle, walk_1, walk_2, attack, hurt y death; seis imágenes distintas, PNG RGBA transparentes.

| Enemigo | Prefijo de archivos | Canvas |
|---|---|---|
| Sentinel v1 | sentinel | 80×64 |
| Corrupted Gunner v1 | gunner | 80×80 |
| Stalker v1 | stalker | 80×80 |
| Specimen K-32 | specimen_k32 | 112×112 |
| Furnace Hound v1 | furnace_hound | 96×64 |
| Forge Brute | forge_brute | 112×112 |
| Loader MK-I | loader | 112×96 |
| Foreman MK-II | foreman_mk2 | 112×112 |

Ruta común: `ui/frontend/art/sprites/<prefijo>_<estado>.png`. Los ids de gameplay `k32` y `foreman` permanecen intactos; solo sus perfiles gráficos usan los prefijos largos.

Diseños industriales: Sentinel con base articulada y proyector de remaches; Gunner técnico con alimentación neumática; Stalker unidad de sondas de laboratorio; K-32 aparato experimental de contención; Hound máquina de horno; Brute prensa hidráulica; Loader montacargas bípedo; Foreman maquinaria de supervisión.

## Producción y normalización

Se usó la herramienta integrada image_gen, una hoja de seis poses por familia. No se modificaron ni regeneraron los assets validados. Prompts exactos: `docs/sprint-generation-prompts.json`; fuentes: `docs/sprint-sources/`.

Preparación reproducible: `tools/prepare_sprint_art.py` (Pillow/numpy/scipy, solo offline, no nuevas dependencias del juego). Se separan personajes conectados antes del recorte para no arrastrar fragmentos del cuadro vecino. Cada familia usa **una sola escala**, canvas común, centro de celda común y traslación al apoyo. No se amplía una pose por su bounding box individual. El cadáver conserva menor altura dentro del mismo canvas. Se normaliza por reflexión la orientación de walk_2 en Stalker y Hound; se mantienen las herramientas asimétricas de los otros diseños.

Preview: `docs/visual_delivery_sprint_preview.png`. Escalas y límites fuente: `docs/sprint-normalization.json`.

## Integración y estabilidad

Solo dos módulos de producción JS cambian:
- `ui/frontend/art.js`: manifiesto/perfiles, observador exclusivamente visual y efectos de estado.
- `ui/frontend/renderer.js`: consumo de los perfiles nuevos, cadáver temporal, proporción de canvas y marcadores de peligro.

El observador lee posición, HP, cooldown y modos **sin escribir en el enemigo ni en FS.state**. Sus datos viven en FS.enemyVisuals, cuyo reset ya existía. Orden death > hurt > attack > move > idle. El cadáver dura 1.15 s y no se renueva cada frame. Enemigos dormidos no reciben estado visual. Los pasos disponibles se usan solo cuando hay desplazamiento real: no se obliga a caminar al Sentinel ni se altera su velocidad.

Se conservan los avisos especiales:
- Loader: preparación de carga naranja, aturdimiento/ángulo trasero verde.
- Foreman: protección cyan; texto del HUD y nodos originales intactos.
- Stalker: transparencia durante camuflaje y aviso al revelarse.
- K-32: sobrecarga rosa y exposición verde.
- Hound y Brute: aviso naranja durante preparación peligrosa.

Los marcadores se dibujan con la misma oclusión por profundidad. No alteran colisiones ni daño. Si falta una imagen nueva, se utiliza la variante anterior específica del estado, incluida la representación procedural. Crucible permanece como estaba.

**Preservado byte por byte:** Python, realtime.js, loader.js, foreman.js, laboratory.js, foundry.js, controles, bridge, preguntas, mapas, campaña, guardado, M.A.D., armas y todos los assets anteriores excepto los seis carteles solicitados. Worker, Crawler, Rivet, Pistola y DDI Breach Pump mantienen sus PNG y su lógica.

## Señalética corregida

La superposición estaba en los PNG originales (por ejemplo QUALITY y CONTROL ya se tocaban). Se sustituyeron seis PNG en `ui/frontend/art/props/`: sign_qc, sign_tools, sign_assembly, sign_power, sign_exit y sign_generator.

Ahora usan 256×128, tipografía con márgenes y dos líneas separadas, proporción 2:1 y estética industrial. No se cambiaron posiciones, tamaños de mundo, mapa, HUD ni sistema de interacción. QUALITY CONTROL, TOOL STORAGE y ASSEMBLY FLOOR se comprobaron también dentro del renderer real.

## Armas, pickups y pendientes

- **Armas nuevas completadas: ninguna.** Sawed-Off, Assault Rifle, Sniper, LMG y Rocket Launcher conservan su presentación anterior. Se priorizaron las ocho familias enemigas y la señalética; faltan sus sets idle/fire/reload.
- **Pickups nuevos completados: ninguno.** Se conserva el pickup validado de shotgun y los restantes anteriores. Pendientes los pickups coherentes con los futuros viewmodels.
- Props secundarios: sin cambios fuera de los seis carteles.
- No se añadieron nuevos enemigos jugables, niveles, variantes futuras ni contenido de progresión.

## Pruebas ejecutadas

- `python -m pytest -q`: **251 passed**.
- `python -m compileall -q app.py game ui tests tools`: correcto.
- `node --check` en frontend y tests: **18 JS**, correcto.
- Smoke JS de arte, sprint, Rivet, Crawler, shotgun, Laboratory y Foundry: correctos.
- `python tests/browser_visual_sprint.py`: **Streamlit real + Chromium**. Escenas controladas en Workshop, Factory, Laboratory y Foundry; CLÁSICO/escritorio 1280×720 y DOOM/móvil emulado 900×405. 8 familias × 6 poses × 2 viewports, altura/anclaje constantes, ticks/disparos reales, señalética visible, sin pageerror ni ERROR DE MOTOR.
- `python tests/browser_rivet.py`: correcto, ambos viewports.
- `python tests/browser_crawler.py`: correcto, ambos viewports.
- `python tests/browser_shotgun_polish.py`: correcto, ambos viewports; pickup, fire, ambos pumps, recarga, cambio de arma, munición y reset.

Los casos del sprint usan ubicaciones/estados preparados para mostrar cada pose; el segmento de combate corre funciones reales con tiempo de gracia para proteger la fixture. No son recorridos completos de campaña ni pruebas de dificultad o tiempo de juego. No se afirma validación física ni Safari.

Pruebas nuevas: `tests/test_visual_sprint.py`, `tests/js_sprint_smoke.js`, `tests/browser_visual_sprint.py`, `tests/sprint_preserved.json`, `tests/sprint_sign_hashes.json`.

Se conservan los tests previos; se actualizan tres comprobaciones de presentación en `test_crawler_visuals.py`, `test_rivet_visuals.py` y `test_shotgun_polish.py`. Los hashes históricos siguen guardados; solo se permiten explícitamente los seis PNG de carteles nuevos. El manifiesto nuevo verifica el resto de producción contra la base exacta.

## Límites y siguiente validación

Es una candidata visual, pendiente de aprobación artística y juego físico en PC/móvil. Las fuentes tienen una orientación principal y dos pasos; no hay rotaciones direccionales completas. Los cambios de postura proceden de poses generadas y pueden requerir refinamiento manual tras playtest, sobre todo los jefes. Los marcadores gráficos de vulnerabilidad deben revisarse durante combates completos. La prueba automatizada no mide rendimiento sostenido en celulares de gama baja.

Siguiente paso recomendado: validar el lote enemigo en combate físico y después completar viewmodels/pickups en una iteración separada, sin alterar balance.

## Ejecución y entrega

Se mantiene `requirements.txt`: `pip install -r requirements.txt` y `python -m streamlit run app.py`. El ZIP incluye todo el proyecto ejecutable, tests, fuentes, previews y resultados. No es un parche.
