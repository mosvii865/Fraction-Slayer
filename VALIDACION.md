# Validación — Fraction Slayer v0.2-alpha2

Fecha: 2026-09-24. Base exclusiva: el ZIP adjunto `Fraction_Slayer_v0.2-alpha1.1-stable(1)(1).zip`, SHA-256 `3bbb14029255e4a97bc963baf762332d410d9415d6aa5dc5a01c784a5def9ca9`. La estable fue validada físicamente por el usuario; los resultados siguientes corresponden a la nueva alpha2, no a una prueba física nueva.

## Entorno y resultados

Python 3.12, Streamlit 1.55.0, pytest 9.0.2, Playwright 1.51.0, Chromium Headless 134. Los scripts levantan **Streamlit real**, esperan HTTP 200 en `/_stcore/health` y abren su iframe real. No se validó únicamente HTML simulado. Servidor iniciado mediante `python -m streamlit run app.py` con puertos temporales locales.

| Prueba | Resultado |
|---|---|
| `python -m pytest -q` | **101 passed**: 80 anteriores + 21 casos parametrizados de Workshop |
| `python -m compileall -q game ui app.py` | Aprobado |
| `python tests/browser_workshop.py` | CLÁSICO PC y DOOM móvil: recorrido completo aprobado |
| `python tests/browser_workshop_feedback.py` | Aviso de refuerzos visible aunque coincida con desbloqueo del elevador |
| `python tests/browser_startup.py` | Industrial Test PC/móvil × CLÁSICO/DOOM; primer frame, sync, v2/v1 y recuperación del error inyectado |
| `python tests/browser_smoke.py` | Industrial Test CLÁSICO y móvil DOOM aprobados |
| `python tests/browser_smoke.py --doom` | Industrial Test DOOM y móvil DOOM aprobados |
| `python tests/mobile_controls.py` | Multitouch, 5 viewports × 3 tamaños, safe areas y orientación aprobados |
| `python tests/pc_controls.py` | WASD, mouse, clic, E, R, 1/2, Esc aprobados |
| `python tests/browser_engine.py` | Recuperación real de sesión, cooldown, LOS, dormidos, pickups desconocidos y render recuperable aprobados |

No hubo ERROR DE MOTOR espontáneo ni excepción crítica JS durante el recorrido normal. Las suites conservan errores deliberados para probar el diagnóstico: checkpoint null sin guard en memoria, renderer inyectado, saves inválidos y NEED_SESSION. Las preguntas bajo amenaza devuelven intencionalmente AREA NOT SECURE; esos tracebacks Python son esperados.

## Cobertura Workshop

- Nueva Partida de la interfaz elige `workshop`; ambas dificultades producen estado válido, canvas y HUD visibles. La API sin nivel conserva Industrial Test.
- 21 enemigos CLÁSICO, 30 DOOM, encuentros explícitos y dormidos. Se activa la escopeta y segunda oleada durante el primer encuentro, no por haberlo terminado.
- Recorrido por colisión real entre recepción, almacén, Assembly, Calibration, Maintenance, Power Control, almacén del fusible, Generator Hall y elevador. BFS adicional en Python comprueba gates cerrados, consola obligatoria accesible, fusible inaccesible antes de abrir, y elevador inaccesible antes de sus requisitos.
- Terminal incorrecta/correcta y reintento; ambos M.A.D.; puerta .375 → 3/8; cache; formato manual de DOOM mediante teclado holográfico. Pool fijo 2/4/8. Las cinco calibraciones se validan también en Python.
- M.A.D. sin arma compatible: prueba Python confirma que no cambia inventario, aciertos ni consumo; tras obtener un arma compatible sí funciona.
- Fuse es quest_item; ambush se activa una vez y no revive tras CONTINUAR. Instalación por el botón USAR real: consume el fusible, restaura energía y activa Loader sin sumar pregunta/acierto.
- Antes del boss se prueba piso de munición de un solo uso; nueva comprobación al instalar evita depender de respuestas opcionales.
- Checkpoints Calibration, fusible y antes del Loader; muerte real por `hurt()` sin gracia, botón reinicio, HP mínimo/gracia. Python rechaza checkpoint muerto y valida seguridad/progreso.
- Save v2 avanzado: recarga real de página + CONTINUAR conserva fusible, oleada derrotada y mejoras. Fases del Loader y timestamps del 50% sobreviven save/load Python. v2 de Industrial Test sigue cargando; v1 y corruptos se rechazan limpiamente.
- Loader: melee y ground slam causan daño sin gracia; preparación de carga, dirección bloqueada aunque el jugador cambie posición, impacto contra pared, 1.75 s de stun, recuperación y daño trasero mayor que frontal. Se derrota mediante disparos reales en los dos recorridos.
- Evento 50% único y refuerzos después de dos segundos; persistencia y cruce con múltiples impactos entre syncs. Aviso de refuerzos tiene prioridad si coincide con POWER RESTORED.
- Logo UTCJ por disparo, separado de kills y persistente: CLÁSICO encontrado → 1/4; DOOM omitido → ???. Python comprueba restauración también desde checkpoint.
- Elevador exige `power_restored && loader_defeated`; matar Loader sin energía no abre. No exige todos los kills: una ejecución DOOM terminó con 29/30; otras con 30/30 por disparos durante el recorrido.
- Entrada automática al elevador y MISSION COMPLETE con producción 212%, shutdown denied y teaser The Factory. The Factory no es un nivel jugable.

## Alcance del recorrido automatizado

`workshop_driver.js` vive exclusivamente en `tests/`, no se carga en producción. Usa movimiento con colisiones, IA, disparos, recarga, munición y cooldown del juego. Acelera ticks y apunta automáticamente. Durante navegación renueva gracia para aislar progresión de la habilidad del bot; **no modifica HP de enemigos para terminar el recorrido**. Pruebas separadas del Loader usan fixtures y quitan la gracia para medir daño/estados.

Por ello, los tiempos de ~80 segundos simulados de estas ejecuciones **no equivalen a una partida humana de 8–12 minutos**. Tampoco demuestran dificultad o supervivencia sin protección. No se presenta la prueba como balance final. Las suites antiguas usan posiciones/HP controlados y conservan ese alcance declarado.

## Correcciones surgidas al validar

1. **Salida demasiado temprana:** `auto_zone` incluía posiciones fuera de `interaction_distance`. Se observó una serie de rechazos reales de `finish`. El cliente ahora exige también la distancia de interacción antes de iniciar la finalización. El recorrido comprueba la salida automática sin llamar directamente a finish como fallback.
2. **Umbral saltado por sync demorado:** la condición inicialmente exigía HP > 0; varios impactos podían pasar desde arriba del 50% hasta cero en un snapshot. Se acepta también cero para registrar el cruce una vez. Refuerzos conservan demora/aviso; un test cubre el golpe fatal agrupado. El aviso prioritario no queda sustituido por el mensaje de elevador.
3. **Barra/aviso superpuestos en móvil:** inspección visual detectó que el toast cubría la nueva barra del boss. El aviso baja solo mientras hay barra visible; no cambia hit areas de controles.
4. **Prueba antigua suponía nivel predeterminado:** scripts ahora eligen Industrial Test explícitamente. Un handoff de fixture podía coincidir con sync de realtime; la prueba smoke pausa antes de pedir una calibración. No se modificó el bridge para acomodar el test.

No se reescribieron controles, protocolo Streamlit, armas, preguntas, puntuación ni mapa de regresión. Se conservó el guard de checkpoint y el diagnóstico de la estable.

## Pendiente físico / límites

- Jugar sin protección en Android/iPhone: duración, dificultad, tasas de fallo, claridad de rutas, ammo y combate del Loader. Los factores ~1.5×/1.28× son estimaciones declaradas en README, no resultados humanos.
- Safari real: barras dinámicas, safe areas, fullscreen, multitouch durante carga del boss, vibración y rendimiento sostenido. Chromium emulado no sustituye WebKit/dispositivo físico.
- No se publicó en Community Cloud/GitHub; dependencias y estructura de despliegue se conservan. La app se comprobó localmente con Streamlit real.
- Gráficos y efectos son procedurales simples; IA sin navegación global. No se añadieron assets IA, Factory ni armas futuras.

Evidencias nuevas: `docs/validacion-alpha2/`. Historial anterior: `docs/VALIDACION_ALPHA1_STABLE.md`.
