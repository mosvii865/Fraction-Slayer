# Fraction Slayer v0.3-alpha2 — The Foundry

FPS retro educativo construido con **Streamlit + Python + HTML5 Canvas/JavaScript**. Python conserva reglas educativas, campaña, progreso, recompensas y guardados; JavaScript/Canvas lleva render, movimiento, disparos, touch/multitouch e IA realtime.

**Diseño y concepto:** Esteban Montaño. **Proyecto académico:** Universidad Tecnológica de Ciudad Juárez.

> La matemática no te impide jugar. Te permite jugar mejor.

## Estado actual

La base físicamente validada es **v0.3-alpha1 — The Laboratory**. Esta entrega añade **Level 04 — The Foundry** y se mantiene como **candidate** hasta un playtest real en PC/móvil.

Niveles disponibles en campaña:

1. **The Workshop** — 1/2, 1/4, 1/8; Pump Shotgun; Loader MK-I; UTCJ 1.
2. **The Factory** — +1/16; Assault Rifle + Sawed-Off; conveyors; Foreman MK-II; UTCJ 2.
3. **The Laboratory** — +1/32 y números mixtos; Sniper Rifle; Stalker; Specimen K-32; UTCJ 3.
4. **The Foundry** — +1/64 e input manual; LMG + Rocket Launcher; Furnace Hound, Forge Brute y The Crucible; UTCJ 4/4 y El Toro.

`industrial_test` se conserva como nivel de regresión. **The Converter todavía no está implementado**; aparece únicamente como teaser al terminar Foundry.

## Filosofía educativa

Fraction Slayer es primero un FPS y después un juego educativo. Las matemáticas aparecen en terminales, M.A.D., caches, puertas y objetivos; no bloquean cada combate.

Regla pedagógica oficial:

> Si una pregunta necesita vocabulario o notación nueva para entenderse, el juego debe enseñarlos antes de evaluarlos.

Foundry mantiene **enseñar → practicar → aplicar → combinar**. Primero explica que `1/32 ÷ 2 = 1/64 = .015625`; después practica 1/64 y finalmente introduce entrada manual. Los ejercicios de Control de Calidad describen el rango permitido y la pieza en español claro antes de mostrar una notación industrial equivalente.

Las preguntas normales no se abren con amenazas cercanas (`AREA NOT SECURE`). No hay matemáticas durante The Crucible.

## Level 04 — The Foundry

Objetivo: cortar la alimentación energética del Converter atravesando una fundición en sobrecarga.

| Zona | Contenido |
|---|---|
| Foundry Descent | Entrada desde Laboratory y primera presión de combate |
| Thermal Processing | Enseñanza de 1/64 + debut de Thermal Purge |
| Heavy Fabrication | LMG obtenida durante combate |
| Slag Processing | Debut del Furnace Hound |
| Pressure Regulation | Control de mecanizado en español claro |
| Forge Assembly | Rocket Launcher durante el encuentro |
| Forge Pits | Debut del Forge Brute |
| Project U.T.C.J. Chamber | Señal final y posible desbloqueo de El Toro |
| The Forge Run | Avance bajo presión con hazards y unidades pesadas |
| The Crucible | Boss-installation con locks, ventanas de daño y meltdown |

CLÁSICO contiene **41 enemigos** y DOOM **54**, incluyendo The Crucible. La dificultad sube mediante composiciones, hazards y comportamiento, no solo HP.

### Thermal Purge

Foundry introduce zonas térmicas con advertencia visible antes de activarse. No son muerte instantánea: castigan quedarse en la zona marcada y obligan a reposicionarse durante combate. En The Forge Run y The Crucible se combinan con mayor presión enemiga.

### LMG

Arma de control sostenido: 60 balas iniciales en cargador, cadencia alta, dispersión mayor y recarga larga.

- MOD I — **Recoil Dampener**.
- MOD II — **Heavy Box**.
- MOD III — **Feed Optimizer**.

### Rocket Launcher

Arma explosiva de alto daño y munición escasa. Usa proyectil realtime, daño de área y riesgo de autodaño a corta distancia.

- MOD I — **Stabilized Rocket**.
- MOD II — **Expanded Blast**.
- MOD III — **Demolition Chamber**.

### MOD III

Los cuatro M.A.D. de Foundry permiten avanzar secuencialmente hasta MOD III. No saltan niveles y no se consumen si no existe un arma elegible.

### Furnace Hound

Ciclo realtime:

`TRACK → HEAT UP → LEAP → RECOVERY`

El salto se anuncia antes de hacer daño; tras fallar o completar la embestida existe una ventana de recuperación.

### Forge Brute

Unidad pesada con armadura frontal. El daño frontal se reduce y los laterales/espalda son más vulnerables. Puede presionar a media distancia y usar Ground Shock a corta distancia, sin depender de HP desproporcionado.

### PROJECT U.T.C.J. / El Toro

La señal de Foundry es independiente, igual que las anteriores. Si el jugador llega a **4/4**, el payload alcanza 100% y se autoriza **EL TORO**: arma secreta de daño extremo, muy lenta, munición Bull Core escasa y sin M.A.D.

Esta candidate **no implementa todavía un menú para revisitar niveles completados**. Si faltan señales anteriores, El Toro no se desbloquea en esa campaña al encontrar solamente la de Foundry.

### The Crucible

Boss con identidad distinta a Loader, Foreman y K-32:

1. **PRESSURE** — núcleo protegido; destruir 3 Pressure Locks.
2. **CORE EXPOSED** — ventana temporal de daño.
3. **MELTDOWN** — núcleo protegido; destruir 2 Emergency Locks y sobrevivir a mayor presión.
4. **CORE EXPOSED II** — segunda ventana de daño.
5. **CRITICAL** — núcleo permanentemente expuesto con purgas térmicas activas.

No utiliza preguntas matemáticas durante el enfrentamiento.

## Campaña persistente

Entre niveles se conservan armas, MODs, PROJECT U.T.C.J., estadísticas globales y recursos con pisos de seguridad. Quest items, enemigos, triggers, puertas y checkpoints siguen siendo locales al nivel.

Foundry añade tres compuertas físicas para evitar bypass pedagógico sin volver el mapa un pasillo: calibración manual 1/64 → Heavy Fabrication, Control de Mecanizado → Forge Assembly y The Forge Run → The Crucible.

## Controles

| Acción | Móvil horizontal | PC |
|---|---|---|
| Moverse | Joystick flotante | WASD |
| Girar | Arrastrar zona derecha | Mouse / ← → |
| Disparar | DISPARAR | Clic izquierdo / Espacio |
| Interactuar | USAR | E |
| Recargar | RECARGAR | R |
| Cambiar arma | ARMAS | 1–8 |
| Pausa | Ⅱ | Esc |

El hotfix móvil de M.A.D. se conserva: **USAR** se confirma en `pointerup`; DISPARAR sigue siendo inmediato.

## Guardado

**SAVE_VERSION = 4.** La forma del guardado no cambió: Foundry agrega validación de fases/cooldowns de Furnace Hound, Forge Brute y The Crucible, además de MOD III. Las campañas v2/v3 válidas siguen migrando/cargando mediante el sistema existente.

## Ejecución local

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Validación de esta candidate

- `python -m pytest -q` → **160 passed**.
- `node --check ui/frontend/*.js` → **OK**.
- `node tests/js_laboratory_smoke.js` → **OK**.
- `node tests/js_foundry_smoke.js` → **OK**.
- `python -m compileall -q .` → **OK**.
- BFS de ruta comprueba las tres compuertas físicas de Foundry → **OK**.

Streamlit real no está disponible en este entorno (`No module named streamlit`), por lo que Foundry sigue siendo candidate hasta el playtest físico.

Ver `CAMBIOS_V0.3-alpha2.md` y `VALIDACION.md`.
