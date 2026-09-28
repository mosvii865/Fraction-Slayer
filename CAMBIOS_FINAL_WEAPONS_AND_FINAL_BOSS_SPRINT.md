# Final Weapons + Final Boss Visual Sprint — candidata

Base exclusiva: `Fraction_Slayer_v0.3-alpha2-visual-delivery-sprint-candidate.zip`.
Salida: `Fraction_Slayer_v0.3-alpha2-final-weapons-and-final-boss-sprint-candidate.zip`.

## Completado

| Arma existente | Identidad visual | Frames en `ui/frontend/art/weapons/` |
|---|---|---|
| Sawed-Off | DDI TWIN-BREACH | sawed_off, sawed_off_fire, sawed_off_break_open, sawed_off_reload_insert, sawed_off_close |
| Assault Rifle | DDI LINE DRIVER | assault, assault_fire, assault_reload_start, assault_reload_swap, assault_reload_end |
| Sniper Rifle | DDI PRECISION CALIBRATOR | sniper, sniper_fire, sniper_bolt_back, sniper_bolt_forward, sniper_reload |
| LMG | DDI CONTINUOUS FEED DRIVER | lmg, lmg_fire, lmg_reload_start, lmg_reload_box, lmg_reload_end |
| Rocket Launcher | DDI DEMOLITION SYSTEM | rocket, rocket_fire, rocket_reload_open, rocket_reload_insert, rocket_reload_close |

Todos son PNG RGBA de 160×120. Se añadieron cinco pickups independientes de perfil, PNG RGBA 64×40, en `ui/frontend/art/pickups/`: `sawed_off_pickup.png`, `assault_pickup.png`, `sniper_pickup.png`, `lmg_pickup.png`, `rocket_pickup.png`. No son el viewmodel reducido.

El jefe real pendiente era **The Crucible**, id `crucible`, de Foundry. Se integraron `boss_idle.png`, `boss_walk_1.png`, `boss_walk_2.png`, `boss_attack.png`, `boss_hurt.png`, `boss_death.png` en `ui/frontend/art/sprites/`, todos RGBA 128×128. Diseño de guardián pesado con núcleo térmico, acero y energía residual. No se creó otra entidad ni se renombró su lógica. Sus fases, bloqueos térmicos y barra existentes se conservan.

## Integración exclusivamente visual

- `ui/frontend/art.js`: manifiesto, perfiles, selector `weaponFrameKey`, recargas por proporción del temporizador real, observador efímero del disparo para el ciclo de cerrojo Sniper y perfiles de Crucible/pickups.
- `ui/frontend/renderer.js`: consulta del observador visual, fallback a idle de la familia y render de pickups con profundidad/línea de suelo. Un marcador temporal del objeto dibujado distingue armas de cajas de munición: las cajas conservan su aspecto previo.
- Cada familia usa **idle como referencia maestra**, un canvas compartido y un factor de escala común. Ninguna pose se escala por su bounding box individual. Los frames conservan articulación y desplazamientos naturales.
- Recarga tiene prioridad sobre disparo/cerrojo. Los estados se derivan del temporizador existente. Cambiar arma, recargar, morir o sustituir el estado de partida limpia el observador cliente. No entra al save ni escribe munición.
- Los flashes están incorporados al frame de disparo. La rama procedural permanece oculta cuando se dibuja el arma rasterizada, evitando doble flash.
- Crucible reutiliza el observador visual del sprint anterior: muerte > daño > ataque > movimiento > idle. Las variantes de energía mantienen señalización visual de sus fases. La caída se muestra brevemente como los otros sets existentes.
- Se conservan fallbacks procedurales si un PNG falla al cargar; todos los assets de esta entrega cargaron correctamente en las pruebas.

## Preservación

Comparación byte a byte contra el ZIP base: **solo dos archivos anteriores cambiaron: art.js y renderer.js; ninguno se eliminó**. Todos los archivos de `game/`, los scripts de IA/gameplay, bridge, controles, HUD, mapas, saves, preguntas y assets anteriores permanecen idénticos. `tests/final_preserved.json` contiene hashes comprobados automáticamente. Pistola, DDI Breach Pump, Worker, Crawler, Rivet, ocho sets del sprint anterior y signage no se regeneraron.

No cambiaron daño, cadencia, munición, velocidad, dificultad, IA, hitboxes, campaña, M.A.D. ni triggers/recompensas de recogida.

## Archivos nuevos de soporte

- 36 PNG de producción: 25 viewmodels + 5 pickups + 6 Crucible.
- `tests/test_final_visuals.py`, `tests/js_final_visuals.js`, `tests/browser_final_visuals.py`, `tests/final_preserved.json`.
- `tools/prepare_final_art.py`, `tools/prepare_final_boss.py`: preparación offline, no se ejecutan al iniciar el juego.
- `docs/final-sources/`: hojas originales y prompts de generación de esta entrega; no sustituyen assets previos.
- `docs/final_weapons_preview.png`, `docs/final_boss_preview.png`, `docs/final_ingame_preview.png`, metadatos de normalización y evidencia de pruebas.

## Validación ejecutada

- `python -m pytest -q`: **290 passed**.
- `python -m compileall -q app.py game ui tests tools`: correcto.
- `node --check`: 19 JS de frontend y tests; correcto.
- Todos los scripts `tests/js_*.js`: correctos, incluidos Laboratory/Foundry, arte, Shotgun, Crawler, Rivet y sprint visual disponibles.
- `python tests/browser_final_visuals.py`: Streamlit REAL + Chromium, desktop 1280×720 CLÁSICO y móvil landscape 900×405 DOOM. Cinco armas: recogida con función real, primer sync, disparo, cerrojo Sniper, recarga con duración y munición reales, etapas dibujadas, escala constante y cambio a Pistola/vuelta. Crucible real: seis poses mediante fixtures visuales, escala/anclaje constantes. Sin excepciones de página ni ERROR DE MOTOR.
- `python tests/browser_visual_sprint.py`: ocho sets anteriores × seis frames × dos viewports; escenas en Workshop, Factory, Laboratory y Foundry, ticks de combate y carteles; PASS.
- `python tests/browser_shotgun_polish.py`: pickup, fire/pump_back/pump_forward, tres etapas reload, munición conservada, cambio de arma/nueva partida; PASS en ambos viewports.
- `python tests/browser_rivet.py` y `python tests/browser_crawler.py`: seis estados, combate, daño/muerte, escala/anclaje; PASS en escritorio y móvil.

Las pruebas de navegador usan posiciones controladas y cues visuales para observar cada pose, no un recorrido completo de campaña. Para capturas deterministas se congeló únicamente el reloj de presentación de la fixture de Crucible. La fixture de armas desactiva amenazas tras el sync; no modifica código de producción. Un primer intento de prueba se rechazó correctamente por usar gracia fuera del rango permitido: se corrigió la fixture, no el validador del juego.

## Pendientes y límites

- Candidata lista para playtest físico; no se ha probado en un Android/iPhone real ni Safari físico en este sprint.
- No se completó nuevamente toda la campaña ni una pelea completa contra Crucible. Sus seis estados y render se verificaron; fases y gameplay quedan preservados por igualdad de código.
- Arte de una vista frontal/primera persona, sin sprites direccionales adicionales. Validar a juicio del usuario tamaño aparente, legibilidad de pickups a distancia y fluidez percibida en dispositivo físico.
- Sniper usa un frame específico de recarga y dos de cerrojo, conforme al alcance; los otros cuatro sets usan tres etapas de recarga. Animaciones visuales no añaden tiempo real a las acciones.
- No se implementó ningún nivel, arma jugable ni enemigo nuevo: se sustituyó únicamente su presentación.

## Ejecución

Las instrucciones y dependencias del README original siguen vigentes:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Para reproducir los tests de navegador:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/browser_final_visuals.py
```

Los generadores offline requieren Pillow, NumPy y SciPy; no son dependencias adicionales de ejecución del juego.
