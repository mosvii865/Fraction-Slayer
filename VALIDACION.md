# Validación — Fraction Slayer v0.2-alpha3

Fecha de construcción: 2026-09-25. Base: **v0.2-alpha2**, previamente validada físicamente por el usuario en CLÁSICO y DOOM. Esta validación corresponde a la implementación nueva de The Factory y persistencia de campaña.

## Resultado automatizado disponible

- `PYTHONPATH=. python -m pytest -q` → **116 passed**.
- `node --check ui/frontend/*.js` → **OK**.
- `python -m compileall -q game ui app.py` → **OK**.

No hubo fallos de sintaxis Python/JavaScript en estas comprobaciones.

## Cobertura Python de Factory

`tests/test_factory.py` cubre, entre otros:

- registro de `factory` y conteos 30/42;
- presencia de Sentinel, Gunner y Foreman;
- conveyors y boss nodes dentro del mapa;
- armas Assault/Sawed-Off y 3 M.A.D.;
- pool matemático restringido a 2/4/8/16;
- rush de tres waves monotónicas sin duplicación;
- Production Controls y desbloqueo condicionado del Lab Transit;
- Foreman protegido/nodos persistentes en save;
- UTCJ Factory independiente;
- transición Workshop→Factory;
- conservación de armas, MOD, HP, armor, ammo y UTCJ;
- eliminación de quest items/local state en transición;
- pisos de HP/ammo y preservación de recursos por encima de esos pisos;
- contador UTCJ 1/4 → 2/4 entre niveles;
- recuperación de Pump mediante Emergency Armory;
- final objetivo-driven sin requerir todos los enemigos muertos.

Los tests existentes de Workshop, motor, reglas y saves también siguen pasando.

## Save/campaña

SAVE_VERSION pasa a **3**. El loader acepta v2 y lo migra al bloque de campaña. v1 permanece incompatible. Se valida campaña, armas, estado del Foreman, nodos, waves, secretos y checkpoint antes de aceptar un slot.

## Validación de navegador/Streamlit

**No ejecutada en este entorno de construcción.** Playwright está disponible, pero las navegaciones a `localhost` y `file://` son bloqueadas con `ERR_BLOCKED_BY_ADMINISTRATOR`. Streamlit tampoco está instalado localmente y no hay red para instalar dependencias.

Por eso no se declara validado físicamente todavía:

- transición real Workshop → Factory desde UI;
- rendimiento sostenido móvil;
- multitouch sobre conveyors;
- ritmo real de Assault/Sawed-Off;
- balance del rush;
- comportamiento completo del Foreman con jugador humano;
- duración 10–14 min;
- Streamlit Community Cloud.

## Checklist recomendada para playtest físico

1. Completar Workshop y pulsar **CONTINUAR CAMPAÑA**.
2. Confirmar armas/M.A.D./UTCJ/HP/armor/ammo transferidos y fusible eliminado.
3. Obtener Assault Rifle durante Line A.
4. Probar Tooling, Quality y AREA NOT SECURE.
5. Probar conveyors con movimiento + cámara + disparo simultáneo.
6. Combatir Sentinel y Corrupted Gunner.
7. Obtener Sawed-Off.
8. Encontrar/no encontrar UTCJ Factory y verificar 1/4 o 2/4.
9. Probar los tres M.A.D., incluido caso sin modificación compatible.
10. Guardar/cargar a mitad de Factory.
11. Completar las tres waves y verificar que no reaparezcan tras CONTINUAR.
12. Resolver ambos Production Controls.
13. Foreman: burst, ram, slam, support, dos Protected Modes y nodos.
14. Confirmar que no se abre Lab Transit antes de controles + Foreman.
15. Completar Factory en CLÁSICO y DOOM.
16. Confirmar teaser de The Laboratory sin nivel jugable.
17. Repetir un smoke de `industrial_test` y Workshop para regresión.

Hasta terminar ese recorrido, **v0.2-alpha3 debe tratarse como candidata de playtest**, no como nueva estable física.

## Candidate2 — auditoría/hotfix posterior

Tras una auditoría adicional de persistencia, geometría y progresión de Factory se creó `v0.2-alpha3-candidate2`.

Validación disponible en el entorno de construcción:

- 126 tests Python aprobados.
- compilación Python y sintaxis JS aprobadas.
- regresiones añadidas para persistencia permanente tras restart, snapshot previo a restart, prerequisitos de la rush, compuerta Lab Transit, checkpoint pre-Foreman, IDs UTCJ/campaign y Foreman support.

No fue posible levantar Streamlit real en este entorno; la candidate2 requiere playtest físico antes de promover alpha3 a estable.


## Candidate3 — feedback del primer playtest físico PC

El usuario completó Workshop y Factory en PC sobre candidate2. El flujo principal y el Foreman fueron jugables; el combate del miniboss se consideró dinámico y divertido. El playtest detectó tres problemas de UX/pedagogía: calibraciones repetitivas en Workshop, una pregunta de tolerancia demasiado críptica/adelantada y poca claridad visual sobre escudo/nodos del Foreman y reservas de munición por arma.

Candidate3 corrige esos puntos sin alterar la progresión principal de Factory. La validación local de esta build es: 129 tests Python, `compileall` y `node --check` sobre todos los JS. Falta repetir el recorrido físico PC y realizar el playtest móvil/DOOM.
