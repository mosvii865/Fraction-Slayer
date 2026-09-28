# Fraction Slayer v0.2-alpha3 — The Factory

## Fuente de verdad

Construida exclusivamente sobre **v0.2-alpha2 — The Workshop**, base previamente validada físicamente por el usuario. `industrial_test` y Workshop se conservan.

## Campaña persistente

- SAVE_VERSION 3 con migración segura desde v2.
- Armas, MOD I, PROJECT U.T.C.J., HP, armor y ammo sobreviven Workshop→Factory.
- Transition Resupply eleva solo los recursos por debajo del mínimo; nunca reduce recursos altos.
- Quest items, enemigos, triggers, puertas, checkpoints y progreso local se reinician por nivel.
- `current_level`, niveles completados, UTCJ global y estadísticas globales quedan en `campaign`.
- Workshop ahora ofrece transición directa a Factory tras Mission Complete.

## The Factory

Nuevo `game/factory.py` con grid 56×34 y nueve áreas principales: Receiving, Production Line A, Tooling Bay, Quality Control, Conveyor Network, Production Line B, Maintenance Catwalks, Central Manufacturing Floor y Lab Transit.

CLÁSICO: 30 enemigos. DOOM: 42.

### Armas

- Assault Rifle: 30 de cargador, alta cadencia, MOD I Compensator.
- Sawed-Off: 2 cartuchos, corta distancia, MOD I Magnum Load.
- DDI Emergency Armory puede recuperar Pump Shotgun perdida anteriormente.

### Matemáticas

Factory añade denominador 16 y mantiene 2/4/8. Incluye Tooling 5/16, tolerancia QC, tres M.A.D. y dos Production Controls. AREA NOT SECURE sigue bloqueando calibraciones bajo amenaza.

### Conveyors

Tres belts definidos por datos. Empujan mediante las colisiones normales del motor para conservar control y no atravesar sólidos.

### Enemigos nuevos

- Sentinel: ranged semi-estático con burst/cooldown.
- Corrupted Gunner: ranged móvil con strafe y búsqueda.
- Foreman MK-II: miniboss con Burst Fire, Short Ram, Area Slam, support y dos ciclos Protected/Exposed mediante Industrial Nodes.

### Clímax

Central Manufacturing Floor usa rush de tres waves persistentes. Después se activan Production Control A/B. Foreman aparece al entrar al núcleo tras desactivar ambos controles. Lab Transit exige `production_controls_disabled && foreman_defeated`, no todos los kills.

### U.T.C.J.

El secreto de Factory se registra como señal independiente. Los cuatro futuros logos se pueden recoger en cualquier orden; la UI muestra cantidad total encontrada sobre 4.

## Frontend

- Nuevo `ui/frontend/foreman.js`.
- Realtime soporta conveyors, Sentinel/Gunner, Assault/Sawed-Off, Industrial Nodes y barra Foreman.
- Selector móvil/teclas PC soporta cuatro armas (1/2/3/4).
- Mission Complete de Workshop puede continuar campaña y muestra transferencia de inventario.
- Renderer añade formas procedurales para contenido Factory; no se generaron assets IA.

## Pruebas

- Nuevo `tests/test_factory.py` con campaña, resupply, UTCJ, waves, armas, M.A.D., armory, controls, Foreman y salida.
- Tests existentes actualizados para SAVE_VERSION 3 y migración v2.
- Resultado final: **116 tests Python aprobados**.
- `node --check` aprobado en todos los JS del frontend.
- `compileall` Python aprobado.

## Limitación de esta ejecución

No fue posible levantar Streamlit ni navegar Chromium/Playwright localmente por restricciones del entorno. La build requiere playtest físico/Community Cloud antes de considerarse estable, especialmente para balance, duración, conveyors, multitouch y Foreman.
