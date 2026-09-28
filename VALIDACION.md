# Validación — Fraction Slayer v0.3-alpha2 candidate

Fecha: 2026-09-26. Base físicamente validada: **v0.3-alpha1 — The Laboratory**. Esta validación cubre la implementación nueva de **The Foundry**; no sustituye el playtest real en PC/móvil.

## Automatización ejecutada

- `python -m pytest -q` → **160 passed**.
- `node --check ui/frontend/*.js` → **OK**.
- `node tests/js_laboratory_smoke.js` → **Laboratory JS smoke: OK**.
- `node tests/js_foundry_smoke.js` → **Foundry JS smoke: OK**.
- `python -m compileall -q .` → **OK**.

Streamlit real no pudo ejecutarse en este entorno: `python -m streamlit --version` devuelve `No module named streamlit`.

## Cobertura Foundry

Las regresiones nuevas verifican, entre otras cosas:

- `foundry` registrado con 41/54 enemigos y tipos Furnace Hound/Forge Brute/The Crucible;
- LMG y Rocket Launcher como pickups de campaña;
- cuatro M.A.D. y progresión secuencial hasta MOD III;
- enseñanza explícita de 1/64 antes de evaluación y uso real de entrada manual;
- Control de Mecanizado escrito en español claro, sin `SPEC/PART/ACCEPT` como enunciado principal;
- transición Laboratory→Foundry con persistencia de campaña y piso de HP;
- señal UTCJ Foundry independiente y desbloqueo de El Toro únicamente al llegar a 4/4;
- estado de fases/locks de The Crucible sobreviviendo save/load;
- condición de salida: The Crucible derrotado + Emergency Override;
- contrato frontend para heat cycles, enemigos nuevos, Rocket/El Toro y selector de 8 armas;
- ausencia de preguntas matemáticas dentro del boss arena;
- BFS secuencial: la calibración manual abre Heavy Fabrication, Pressure Regulation abre Forge Assembly y Forge Run abre The Crucible.

## Smoke JS de Foundry

`tests/js_foundry_smoke.js` ejecuta la lógica nueva con un runtime mínimo de Node y comprueba comportamiento, no solo sintaxis. Incluye el ciclo del Furnace Hound y transiciones importantes de The Crucible. El smoke de Laboratory también se mantiene para detectar regresiones en Stalker/K-32.

## Riesgos que requieren playtest físico

1. **Thermal Purge:** claridad visual del warning, especialmente en celular.
2. **LMG:** sensación de control/recoil y legibilidad del HUD con cargadores grandes.
3. **Rocket Launcher:** AOE, autodaño y utilidad sin volver triviales Brutes/Crucible.
4. **Furnace Hound:** telegraph del salto y justicia de la ventana de recuperación.
5. **Forge Brute:** que la armadura frontal se entienda sin explicación externa excesiva.
6. **The Forge Run:** ritmo y posibilidad de avanzar sin necesidad de limpiar todo.
7. **The Crucible:** que quede claro qué locks destruir en cada fase y cuándo atacar el núcleo.
8. **DOOM:** combinación de heat zones + Hounds/Brutes sin volverse frustrante en móvil.
9. **MOD III / M.A.D.:** selector móvil y persistencia tras checkpoint/muerte.
10. **El Toro:** feedback, potencia y claridad de Bull Core si el jugador llega con UTCJ 4/4.

## Nota de diseño pendiente

La candidate no incluye todavía un selector de niveles/revisita para recuperar logos PROJECT U.T.C.J. perdidos. Por tanto, El Toro solo se desbloquea si las tres señales anteriores ya están registradas al encontrar la señal de Foundry. Esto queda deliberadamente fuera del hot path de v0.3-alpha2 para no arriesgar la campaña validada antes del playtest.

Hasta completar el recorrido físico, **v0.3-alpha2 debe considerarse candidate** y **v0.3-alpha1** continúa siendo la versión estable validada.
