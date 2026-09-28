# Fraction Slayer v0.3-alpha1 — The Laboratory

Base: **v0.2-alpha3-candidate4**, validada físicamente por el usuario en PC/móvil. Esta entrega añade Level 03 sin reconstruir Workshop ni Factory.

## Contenido nuevo

- Nuevo `level_id="laboratory"` con nueve zonas: Lab Transit, Precision Metrology, Ballistics Testing Range, Containment Wing A, Specimen Observation, Cryogenic Wing B, Restricted Archives, Core Analysis y Specimen Vault.
- CLÁSICO: 37 enemigos. DOOM: 49 enemigos.
- Nueva arma **Sniper Rifle** (5/15 al recogerla), selector móvil/PC 5 y representación procedural.
- Nuevo enemigo **Stalker** con ciclo STALK → REVEAL → LUNGE → RECOVERY. Nunca inflige daño durante STALK.
- Nuevo boss **SPECIMEN K-32** con HUNTING → OVERLOAD → EXHAUSTED, daño reducido en sobrecarga y 1.5× daño recibido durante la ventana vulnerable.
- Tres Containment Nodes con progreso 33% / 66% / 100% y acceso sellado a Specimen Vault hasta completar los tres.
- Tercer PROJECT U.T.C.J. independiente; al alcanzar 3/4 muestra `ENCRYPTED PAYLOAD: 75%`.
- Tres M.A.D. de laboratorio y desbloqueo de **MOD II**. Las mejoras son secuenciales y persisten como progreso de campaña.
- Terminales narrativas opcionales en Restricted Archives y Core Analysis.
- Teaser final de **LEVEL 04 — THE FOUNDRY**; Foundry aún no está implementado.

## Diseño educativo

Laboratory formaliza el patrón **enseñar → practicar → aplicar → combinar**.

- Introduce 1/32 explicando primero que `1/16 ÷ 2 = 1/32 = .03125`.
- Usa fracción→decimal, decimal→fracción y equivalencias con denominadores hasta 32; no introduce 1/64.
- Introduce números mixtos con lenguaje claro antes de evaluarlos: por ejemplo `1 3/8 = 1 + .375 = 1.375`.
- Añade formato de respuesta `mixed` y validación de fracciones propias/reducidas en entradas como `1 5/8`.
- No usa notación industrial críptica como enunciado principal. El vocabulario nuevo se explica antes de preguntar.
- Las matemáticas normales siguen bloqueadas durante combate cercano (`AREA NOT SECURE`). K-32 no incluye preguntas matemáticas durante la pelea.

## Campaña, armas y guardado

- Factory ahora enlaza a Laboratory mediante `next_level="laboratory"`.
- `SAVE_VERSION = 4`; se aceptan saves v2/v3 válidos y los saves nuevos se emiten como v4.
- La validación de armas admite hasta MOD II y respeta la capacidad modificada del cargador.
- Persisten armas, MODs, UTCJ, HP/armor/ammo y campaña; se eliminan objetos/flags locales al cambiar de nivel.
- Stalker y K-32 guardan sus estados realtime relevantes para save/load y recuperación de sesión.
- Se conserva la protección de restart/checkpoint para armas, M.A.D. consumidos y señales UTCJ.

## Correcciones descubiertas durante implementación

- Los M.A.D. genéricos usados por tests/contratos solo exigen arma mejorable cuando su reward contiene realmente `upgrade`/`upgrade_next`.
- El Specimen Vault tiene dos accesos físicos y ambos quedan ahora sellados hasta Containment 100%, evitando bypass por Archives/Wing B.
- Los terminales `install` pueden definir feedback/panel narrativo propio; Workshop conserva su mensaje anterior y Core Analysis deja de mostrar texto específico del Loader.
- Se eliminó una validación duplicada de capacidad en `save_system.py`.

## Validación local

- `PYTHONPATH=. python -m pytest -q` → **148 passed**.
- `node --check ui/frontend/*.js` → **OK**.
- `node tests/js_laboratory_smoke.js` → **Laboratory JS smoke: OK**.
- `python -m compileall -q .` → **OK**.
- Smoke backend completo de Laboratory → **MISSION COMPLETE**.
- Streamlit real/browser físico del nuevo nivel: **pendiente**, porque Streamlit no está instalado en este entorno.

Esta build debe tratarse como **candidate** hasta que el usuario complete el playtest físico de Laboratory.
