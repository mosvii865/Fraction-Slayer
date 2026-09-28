# Worker Visual v1 — validation candidate

- Primer enemigo de producción basado en la dirección artística aprobada de Fraction Slayer.
- Set 64×80 RGBA: idle, walk_1, walk_2, attack, hurt, death.
- Estado de animación exclusivamente cliente: no modifica saves ni autoridad Python.
- Prioridad visual: DEATH > HURT > ATTACK > WALK > IDLE.
- Worker conserva anclaje al piso y proporción real del canvas.
- Fallback procedural intacto si los assets raster no están disponibles.
- Muerte visual temporal sin alterar reglas de kills/objetivos.
