# DDI Breach Pump v1.1 — Polish Candidate

Base exclusiva: `Fraction_Slayer_v0.3-alpha2-shotgun-v1-candidate(1).zip`, adjunta por el usuario y validada físicamente. Esta entrega es una micro-iteración visual y queda pendiente de la aprobación física de sus dos cambios.

## Problema y causa

La recarga mostraba `shotgun_reload.png` durante todo `FS.reloading`. Aunque el disparo y la corredera funcionaban correctamente, la mano y el cartucho quedaban inmóviles durante el temporizador completo. El objeto recogible de shotgun aún caía al dibujo procedural antiguo del renderer.

## Cambios

Solo se modificaron dos archivos de runtime existentes:

- `ui/frontend/art.js`: registra las tres poses de recarga y el pickup; añade un selector **puro** de fase visual y metadatos de pickup.
- `ui/frontend/renderer.js`: comunica la duración de recarga que ya existe al selector; mantiene fallback a `shotgun.png` si falta una pose; dibuja el pickup con proporción natural, apoyo de suelo, recorte y z-buffer.

### Assets nuevos

| Archivo | Formato |
|---|---|
| `ui/frontend/art/weapons/shotgun_reload_start.png` | 160×120, PNG RGBA transparente |
| `ui/frontend/art/weapons/shotgun_reload_insert.png` | 160×120, PNG RGBA transparente |
| `ui/frontend/art/weapons/shotgun_reload_end.png` | 160×120, PNG RGBA transparente |
| `ui/frontend/art/pickups/shotgun_pickup.png` | 64×32, PNG RGBA transparente |

El start muestra la mano aproximándose al puerto; insert muestra el cartucho parcialmente dentro y la mano empujándolo; end retira la mano y recupera la postura de combate. El pickup es un perfil lateral independiente, no el viewmodel encogido: conserva acero, corredera, bandas amarillas, empuñadura industrial y un pequeño detalle cyan.

Se conservaron **byte por byte** `shotgun.png`, `shotgun_fire.png`, `shotgun_pump_back.png`, `shotgun_pump_forward.png`, el antiguo `shotgun_reload.png`, toda la pistola y Worker v1. El antiguo reload queda como fallback de compatibilidad para llamadas sin metadatos de duración; el renderer normal usa la nueva secuencia.

## Estado visual y tiempos

No se añadieron variables a FS, Python ni al save. La fase se deriva de:

`elapsed = config.weapons.shotgun.reload - FS.reloading`

- Preparación: primeros 100 ms, o 20% si la recarga fuese muy corta.
- Inserción: 160 ms; retirada/aproximación: 120 ms. Se alternan mientras queda tiempo.
- Cierre: últimos 100 ms, o 20% en una recarga muy corta.
- Al terminar el temporizador: vuelve al selector normal/idle inmediatamente.

Las inserciones intermedias son exclusivamente cosméticas: **no representan entregas individuales de munición**. La munición sigue transfiriéndose con la lógica original al terminar la recarga.

La recarga domina tanto fire como pump. Fuera de recarga se preservó exactamente la secuencia validada: primero el breve fire, después pump_back y pump_forward. El reloj de pump ya comienza junto con el disparo; no se le dio precedencia incondicional sobre ese primer flash, porque eso ocultaría el frame fire que el usuario pidió conservar.

El selector no retiene estado: cambiar de arma, reiniciar, cargar o iniciar nivel utiliza los mismos resets existentes de `reloading`/`pumpAnim`. No puede quedar un contador visual adicional congelado. Pausar congela el temporizador de gameplay existente y, por tanto, también la representación.

## Escala y anclaje

`shotgun.png` continúa como referencia maestra. Se mantiene la fórmula existente basada en `referenceBounds`, no en el alpha bounding box de cada pose. Los bounds de cada frame solo delimitan el rectángulo que se dibuja; **no deciden el zoom ni recentran la imagen**.

Los tres renders de origen se normalizaron con la misma transformación de canvas completo (151×113, desplazamiento 0,4 dentro de 160×120). No hubo ajuste individual de escala por alpha. Los gestos contienen desplazamientos de mano/arma dibujados, no un zoom del renderer. Chromium comprobó que la escala aplicada a todas las poses fue idéntica.

El pickup usa bounds explícitos [2,15,60,17], proporción 60:17 y altura visual 0.16. Su base coincide con `H/2 + H/(2*depth)`, el suelo que ya usa este renderer. Una sombra de contacto sutil ayuda a leer el apoyo. Se conservan la prueba de profundidad contra paredes y el clipping de pantalla; el sprite no se anima.

## Gameplay preservado

**No se modificaron gameplay, daño, cadencia, recarga real, munición, pickup radius, desbloqueo, colisiones, mapas, enemigos, IA, matemáticas, M.A.D., campaña, checkpoints, controles ni guardado.** No se cambió SAVE_VERSION.

`tests/shotgun_v1_preserved.json` contiene hashes de los archivos del ZIP original de `game/` y frontend salvo los dos módulos visuales editados. La regresión verifica esos bytes, incluidos `realtime.js` (recarga/recogida/cambio de arma), `game.js`, bridge, controles, CSS y assets ya validados. La comparación del ZIP completo encontró únicamente `art.js` y `renderer.js` modificados entre los archivos existentes. El resto de cambios son archivos nuevos.

## Tests ejecutados

- `python -m pytest -q`: **174 passed** (167 existentes + 7 nuevos).
- `python -m compileall -q app.py game ui tests`: PASS.
- `node --check`: PASS en los 15 JavaScript de frontend y tests.
- `node tests/js_art_smoke.js`: PASS, sin editar el test existente.
- `node tests/js_shotgun_polish.js`: PASS: start/insert/end, prioridad de recarga, selector puro, duración variable, retorno idle y fire/pump sin regresión.
- `node tests/js_laboratory_smoke.js`: PASS.
- `node tests/js_foundry_smoke.js`: PASS.
- `python tests/browser_shotgun_polish.py`: PASS, Chromium real conectado a una instancia real de `python -m streamlit run app.py`; escritorio 1280×720 y móvil táctil emulado 900×405.

### Validación de navegador

En ambos viewports:

1. Se renderizó el pickup nuevo antes de recogerlo, en Workshop.
2. Se usó la función de recogida existente: arma con 8 cargados y 12 de reserva; el sync real fue aceptado por Python.
3. Se disparó con ratón o botón táctil y se registraron draws reales de fire, pump_back, pump_forward e idle.
4. Se inició recarga con R o el botón táctil. Los draws reales pasaron por start, insert, end e idle, con escala constante.
5. Munición antes/después: **7+12 → 8+11**, mismo total. Sin cartuchos creados por la animación.
6. Se interrumpió y alternó Pistola ↔ Shotgun rápidamente: sin reload/pump retenidos.
7. Se simuló muerte y se pulsó REINICIAR CHECKPOINT: contadores limpios. Una nueva partida por RPC también reinició correctamente.
8. Ninguna excepción JS de página ni ERROR DE MOTOR.

Las posiciones de observación/recogida se prepararon como fixtures; no se afirma haber recorrido de nuevo los cuatro niveles de punta a punta. Las capturas individuales de cada pose usan el temporizador fijado para inspección, mientras que la prueba de secuencia observó el temporizador real. Una primera corrida utilizó una gracia de fixture demasiado alta, rechazada por la validación original; se corrigió el fixture al límite del nivel, no el juego, y se repitió exigiendo sync aceptado.

Resultados y capturas: `docs/shotgun-v1.1-validation/`. Previews adicionales: `docs/shotgun_reload_v1_1_preview.png` y `docs/shotgun_pickup_v1_1_preview.png`.

## Producción de los assets

Se utilizó la herramienta integrada de imágenes para las cuatro variantes, con transparencia, tomando los PNG originales y la lámina DDI adjunta como referencias. Después se realizó la normalización de formato/tamaño necesaria para el juego, sin modificar los originales.

Prompts de trabajo (restricciones comunes: un asset, sin etiquetas, fondo transparente, misma identidad industrial, sin rediseño):

- **Start:** editar el reload de referencia; conservar arma, orientación, escala y composición; quitar el cartucho del puerto y acercar la mano enguantada desde abajo/izquierda, preparándose para cargar.
- **Insert:** editar el reload de referencia; conservar arma y composición; desplazar cartucho rojo/latón y dedos hacia el puerto hasta dejar el cartucho parcialmente insertado.
- **End:** partir de idle; conservar escala/orientación; mano secundaria retirándose, sin cartucho visible, composición próxima a idle.
- **Pickup:** perfil lateral de DDI Breach Pump completo, sin manos/brazos ni fondo; cañón robusto, corredera negra estriada con bandas amarillas, receptor de acero y pequeño detalle DDI/cyan; no viewmodel reducido ni arma militar genérica.

## Pendiente

La aceptación artística y la sensación de ritmo finales requieren el playtest físico del usuario. No se probó Safari/iPhone físico ni Android físico en esta iteración; sí Chromium con emulación táctil. La animación es deliberadamente retro, de tres poses con repetición visual, no una simulación mecánica de cartuchos individuales. No se expandió el contenido ni se alteró la dirección visual ya validada.
