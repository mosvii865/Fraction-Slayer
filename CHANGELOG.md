# Changelog

## v0.2-alpha1 — Engine preparation for real levels

- Level ID, revisión y SAVE_VERSION 2; rechazo seguro de saves incompatibles.
- Nivel, encuentros, checkpoints, estaciones, objetivos y salida definidos por datos.
- Puertas y M.A.D. independientes; interaction points para terminales empotradas.
- Respawn con piso de recursos y gracia; checkpoints inseguros rechazados y reintentos con backoff.
- Enemigos dormidos, grupos, triggers y oleadas persistentes; munición mínima configurable por oleada.
- Pickups tipados, quest/key items y secretos UTCJ separados de enemigos.
- Preguntas por estación, validación de formato y recompensas atómicas; respuestas fijas privadas.
- Cooldown resistente al cambio de arma y terminales bloqueadas ante amenaza cercana visible.
- Búsqueda tras perder LOS y primitivas de radio, facing, carga bloqueada, stun y daño trasero.
- Minimap derivado del grid, render recuperable y recuperación automática de sesión Streamlit.
- Pequeños cambios de visualViewport conservan multitouch; controles v0.1.1 mantenidos.
- Regresiones Python y navegador; industrial_test conservado. No incluye The Workshop ni Loader completo.

## v0.1.1 — 2026-09-23

- Floating joystick: origen en el contacto, zona muerta y magnitud analógica.
- Improved multitouch: propietario independiente por pointerId, captura y cancelación aislada.
- Larger mobile controls: áreas generosas para disparar, usar, recargar y elegir arma.
- Weapon switching while moving: selector compacto sin pausar.
- Control size settings: Pequeño / Medio / Grande; zona y radio configurables.
- Safe-area improvements: cuatro márgenes seguros y adaptación al viewport/orientación.
- Optional vibration feedback: pulsos cortos, desactivados por defecto.
- Fallback de ratón por arrastre derecho cuando el iframe no permite captura.
- Pruebas táctiles, de tamaños y de controles PC; reglas/contenido/guardado de v0.1 conservados.

## v0.1 — 2026-09-22

- Primer prototipo jugable con mapa industrial, dos dificultades, armas, enemigos, preguntas Python, M.A.D., checkpoints y guardado.
