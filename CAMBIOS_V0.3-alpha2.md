# Fraction Slayer v0.3-alpha2 — The Foundry

## Nuevo Level 04

- 10 zonas nuevas y ruta semilineal con tres compuertas físicas anti-bypass.
- 41 enemigos CLÁSICO / 54 DOOM.
- Thermal Purge como hazard ambiental telegrafiado.
- The Forge Run como secuencia de avance bajo presión.
- Teaser final de **LEVEL 05 — THE CONVERTER**, sin implementar Level 05.

## Progresión educativa

- Introducción explícita de `1/64 = .015625` a partir de `1/32 ÷ 2`.
- Pools variados con equivalencias y simplificación.
- Entrada manual para fracción↔decimal y números mixtos.
- Control de mecanizado planteado en español claro; la notación industrial aparece solo como explicación posterior.
- No hay matemáticas durante The Crucible.

## Arsenal

- **LMG** con cargador grande, alta cadencia y MOD I/II/III.
- **Rocket Launcher** con proyectiles realtime, AOE y autodaño cercano; MOD I/II/III.
- **MOD III** habilitado para arsenal compatible.
- **El Toro** se desbloquea únicamente al registrar PROJECT U.T.C.J. 4/4; usa Bull Core, no acepta M.A.D. y llega en configuración final.

## Enemigos

- **Furnace Hound**: TRACK → HEAT UP → LEAP → RECOVERY.
- **Forge Brute**: armadura frontal, vulnerabilidad lateral/trasera, ataque pesado y Ground Shock.
- **The Crucible**: PRESSURE → EXPOSED → MELTDOWN → EXPOSED → CRITICAL, con 3 Pressure Locks + 2 Emergency Locks.

## Campaña y guardado

- Laboratory enlaza ahora a Foundry mediante `next_level='foundry'`.
- SAVE_VERSION permanece en 4.
- Persistencia de campaña y protección de restart/checkpoint se conservan.
- Validación de guardado ampliada para estados realtime de enemigos y boss de Foundry.
- El menú de revisita de niveles para recuperar señales UTCJ faltantes queda pendiente; no se simula ni se promete en esta candidate.

## Validación automatizada

- 160 tests Python.
- Sintaxis de todos los JavaScript validada con Node.
- Smoke JS de Laboratory y Foundry.
- `compileall` correcto.
- Regresión BFS de gates pedagógicos/finales.
