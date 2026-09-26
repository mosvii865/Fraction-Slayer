# Fraction Slayer v0.2-alpha3 — The Factory

Segundo nivel de campaña construido sobre **v0.2-alpha2 — The Workshop**, la última base validada físicamente por el usuario. Python/Streamlit conserva reglas educativas, progreso, recompensas, campaña y guardados; Canvas/JavaScript lleva el FPS en tiempo real.

**Diseño y concepto:** Esteban Montaño. **Proyecto académico:** Universidad Tecnológica de Ciudad Juárez.

> La matemática no te impide jugar. Te permite jugar mejor.

## Estado de esta versión

**Candidate3 de playtest:** incorpora el primer feedback físico de PC sobre candidate2: variedad de calibraciones en Workshop, rediseño pedagógico de tolerancias, instrucciones centrales del Foreman y HUD/recarga de munición más explícitos. Factory mantiene `revision=2`; aún requiere validación física adicional antes de considerarse estable.

- `industrial_test` se conserva como nivel de regresión.
- `workshop` sigue siendo Level 01 y ahora enlaza directamente con Factory al completar la misión.
- `factory` es Level 02, con nueve zonas, conveyors, Assault Rifle, Sawed-Off, Sentinel, Corrupted Gunner, rush de tres oleadas y Foreman MK-II.
- The Laboratory **no está implementado**; solo aparece como teaser al terminar Factory.
- La campaña conserva armas, MOD I de M.A.D., PROJECT U.T.C.J., HP, armadura y munición entre niveles. Los objetos/flags locales no migran.

## Flujo de campaña

**NUEVA PARTIDA → LEVEL 01 — THE WORKSHOP → CLÁSICO / DOOM.** Al completar Workshop aparece **CONTINUAR CAMPAÑA →**. La transición a Factory conserva el arsenal y aplica un resupply mínimo sin quitar recursos ganados:

- HP: `max(HP actual, 60)`.
- Armadura: se conserva dentro del máximo del nuevo nivel.
- Reserva mínima si el arma existe: pistola 24, Pump 10, Assault 36 y Sawed-Off 8.
- Si una reserva ya es mayor, no se reduce.
- Se eliminan fusibles, quest items, enemigos, triggers, puertas, checkpoints y progreso local del nivel anterior.

PROJECT U.T.C.J. usa señales independientes. Encontrar solo el logo de Factory muestra **1/4**; encontrar Workshop + Factory muestra **2/4**. El orden no importa.

## Level 01 — The Workshop

Se conserva el contenido validado de alpha2: Reception, Tool Storage, Assembly Floor, Calibration Room, Maintenance Tunnels, Power Control, Generator Hall y Exit Elevator; Pump Shotgun, dos M.A.D., UTCJ, fusible, energía y Loader MK-I. La salida exige `power_restored && loader_defeated` y ya puede transferir la campaña hacia Factory.

## Level 02 — The Factory

Objetivo: **REACTIVATE PRODUCTION CONTROL AND REACH LAB TRANSIT**.

| Zona | Contenido principal |
|---|---|
| Freight Elevator / Receiving | Entrada desde Workshop; 2 Workers + Rivet tras avanzar |
| Production Line A | Primeros conveyors; Assault Rifle durante el combate |
| Tooling Bay | Terminal 5/16 = .3125 y DDI Emergency Armory |
| Quality Control | Tolerancia industrial y M.A.D. #1 |
| Conveyor Network | Sentinel, cobertura y conveyor rápido |
| Production Line B | Sawed-Off y debut de Corrupted Gunner |
| Maintenance Catwalks | Exploración, M.A.D. #2 y PROJECT U.T.C.J. Factory |
| Central Manufacturing Floor | Rush de tres oleadas, controles de producción y M.A.D. #3 |
| Lab Transit | Salida tras Production Controls + Foreman MK-II |

CLÁSICO contiene **30 enemigos** y DOOM **42**, con composición/posiciones adicionales en vez de inflar simplemente el HP de los jefes.

### Matemáticas de Factory

Factory conserva denominadores 2/4/8 e introduce **1/16**:

`1/16=.0625`, `3/16=.1875`, `5/16=.3125`, `7/16=.4375`, `9/16=.5625`, `11/16=.6875`, `13/16=.8125`, `15/16=.9375`.

Hay conversión fracción↔decimal, equivalencia, simplificación sencilla y aplicación industrial. Ejemplos fijos del nivel incluyen:

- Tooling: `5/16" = .3125`.
- Quality tolerance: `SPEC .500" ± .03125" / PART .53125" → ACCEPT`.
- M.A.D. #1: `7/16" = .4375`.
- Production Control A: `.6875" = 11/16`.
- Production Control B: `13/16" = .8125`.

Las calibraciones normales siguen bloqueadas cuando hay una amenaza cercana relevante: **AREA NOT SECURE**. No hay preguntas matemáticas durante Foreman MK-II.

### Assault Rifle y Sawed-Off

- **Assault Rifle:** 30 de cargador, alta cadencia, media distancia; MOD I **Compensator**.
- **Sawed-Off:** 2 cartuchos, daño alto a corta distancia; MOD I **Magnum Load**.

M.A.D. #1/#2/#3 comparten el sistema existente y no se consumen si no existe una modificación compatible.

### DDI Emergency Armory

Tooling Bay incluye una recuperación no matemática de la Pump Shotgun si el jugador llegó a Factory sin ella. No entrega armas futuras.

### Conveyors

Los belts aplican empuje mediante el mismo movimiento con colisiones del jugador. Factory usa belts normales y uno rápido. El empuje no elimina el control y no atraviesa sólidos. El diseño evita usar conveyors como muerte instantánea inevitable.

### Sentinel y Corrupted Gunner

- **Sentinel:** fijo/semiestático, burst fire, línea de visión, cooldown y cobertura.
- **Corrupted Gunner:** móvil, ráfagas, búsqueda y strafe/reposicionamiento.

Ambos comparten el estado de IA persistente ya usado por el motor y no son bullet sponges.

## Rush y Production Controls

Central Manufacturing Floor activa tres oleadas monotónicas:

1. Workers + Crawlers.
2. Rivet + Sentinel + presión adicional.
3. Corrupted Gunner + Crawlers + Workers.

Cada wave queda registrada en `progress.waves`; save/load o CONTINUAR no vuelve a disparar una wave ya completada. Al limpiar el rush aparecen los dos controles matemáticos. Activar ambos fija `production_controls_disabled`.

## Foreman MK-II

Miniboss propio de Factory, separado de Loader.

- HP base: **360** en la configuración actual.
- Burst Fire.
- Short Ram.
- Area Slam.
- Support Deployment al caer por debajo del 50%.
- Dos ciclos de **PROTECTED MODE** aproximadamente al 67% y 34%.
- Durante protección el daño al Foreman se bloquea y aparecen dos **Industrial Nodes**.
- Destruir ambos nodos devuelve **EXPOSED MODE**.

La salida solo se habilita con:

`production_controls_disabled && foreman_defeated`

No exige eliminar todos los enemigos opcionales del mapa.

## Controles

| Acción | Móvil horizontal | PC |
|---|---|---|
| Moverse | Joystick flotante izquierdo | WASD |
| Girar | Arrastrar zona derecha | Mouse / arrastre derecho / ← → |
| Disparar | Mantener DISPARAR | Clic izquierdo / Espacio |
| Interactuar | USAR | E |
| Recargar | RECARGAR | R |
| Cambiar arma | ARMAS sin soltar joystick | 1 Pistola · 2 Pump · 3 Assault · 4 Sawed-Off |
| Pausa | Ⅱ | Esc |

No hay salto ni botón de sprint. Multitouch y safe areas de alpha2 se conservan.

## Guardado

**SAVE_VERSION = 3.**

- Saves v3 guardan campaña + estado local.
- Saves v2 válidos se migran añadiendo el bloque de campaña sin alterar su nivel actual.
- Saves v1, corruptos o revisiones incompatibles se rechazan limpiamente.
- La campaña guarda `current_level`, `completed_levels`, `utcj_found` y estadísticas globales.
- El estado del nivel sigue guardando enemigos, checkpoints, estaciones, waves, secretos, inventario y objetivos.
- El Foreman persiste con modo, escudo, ciclos, HP de nodos, cooldown y support deployment.

El slot continúa siendo local/exportable. Una pérdida de `session_state` usa la recuperación de sesión existente.

## Ejecución local

Python 3.12 recomendado:

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abre `http://localhost:8501`. Para teléfono en la misma red puede usarse `--server.address 0.0.0.0`. En Streamlit Community Cloud usa el contenido de `fraction-slayer/` como raíz del repositorio.

## Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `game/workshop.py` | Level 01 validado y transición hacia Factory |
| `game/factory.py` | Level 02: mapa, encuentros, estaciones, conveyors, rush, Foreman |
| `game/nivel.py` | Registro `industrial_test`, `workshop`, `factory` |
| `game/engine.py` | campaña, transición, resupply y transacciones autoritativas |
| `game/save_system.py` | SAVE_VERSION 3 y migración v2 |
| `game/armas.py`, `mejoras.py` | Assault/Sawed-Off y sus MOD I |
| `game/world.py` | UTCJ de campaña, armory/rewards y progreso monotónico |
| `ui/frontend/foreman.js` | ataques/fases realtime del Foreman |
| `ui/frontend/realtime.js` | combate, conveyors, Sentinel/Gunner, nodes, HUD |
| `ui/frontend/renderer.js` | representación procedural de Factory y armas nuevas |
| `tests/test_factory.py` | regresiones de Factory/campaña |

Se mantiene **ERROR DE MOTOR**, `COPIAR ERROR` y el diagnóstico introducido en la estable.

## Validación de esta entrega

En el entorno de construcción de alpha3:

- `python -m pytest -q`: **126 passed**.
- `node --check ui/frontend/*.js`: **OK**.
- `python -m compileall`: **OK**.
- El navegador/Streamlit real no pudo ejecutarse en este entorno porque la navegación local está bloqueada por política y Streamlit no está instalado.

Por tanto alpha3 debe considerarse **candidate hasta el playtest físico del usuario**, igual que se hizo con las versiones anteriores. Ver `VALIDACION.md`, `CAMBIOS_V0.2-alpha3.md`, `CAMBIOS_V0.2-alpha3-candidate2.md` y `CAMBIOS_V0.2-alpha3-candidate3.md`.
