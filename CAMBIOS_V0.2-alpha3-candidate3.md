# Fraction Slayer v0.2-alpha3-candidate3 — Playtest Feedback

Build de seguimiento sobre `v0.2-alpha3-candidate2` a partir del primer playtest físico en PC.

## Feedback incorporado

- Workshop deja de repetir siempre las mismas calibraciones: las cinco estaciones matemáticas usan pools de tres variantes y evitan repetir inmediatamente una pregunta de la misma estación durante la sesión.
- Las variantes de Workshop mantienen exclusivamente denominadores 2/4/8; CLÁSICO usa opción múltiple y DOOM mantiene entrada manual en M.A.D./cache.
- La pregunta de tolerancia de Factory fue rediseñada por motivos pedagógicos. Ya no usa el enunciado críptico `SPEC / PART / ACCEPT` ni introduce 1/32. Ahora explica primero el rango permitido en español claro y solo después, en la explicación, presenta la notación industrial `0.500″ ± 0.0625″`.
- Se actualizó también la pregunta genérica de tolerancias para evitar depender de jerga no enseñada.
- Foreman MK-II muestra avisos centrales, grandes y no bloqueantes en español al activar/desactivar el escudo y al destruir nodos.
- La barra del Foreman indica `PROTEGIDO · NODOS ACTIVOS X/2` o `VULNERABLE` en lugar de estados crípticos en inglés.
- El HUD de munición muestra cargador como `actual/capacidad` y etiqueta la reserva por arma (`RESERVA RIFLE`, `RESERVA CORREDERA`, etc.).
- Recargar ahora informa claramente `RECARGANDO <ARMA>`, `CARGADOR COMPLETO` o `SIN MUNICIÓN EN RESERVA` según corresponda.

## Seguridad educativa

Las respuestas de los pools fijos siguen siendo server-only; `fixed_question` y `fixed_questions` se eliminan del `config` enviado al frontend.

## Tests

- 129 tests Python pasan.
- `python -m compileall` pasa.
- Todos los JavaScript de `ui/frontend` pasan `node --check`.
- No se pudo ejecutar Streamlit real en este entorno porque la dependencia no está instalada; esta build sigue siendo candidata hasta el siguiente playtest físico.
