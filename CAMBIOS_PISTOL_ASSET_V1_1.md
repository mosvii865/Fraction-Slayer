# Pistol Asset v1.1 — integración de estados

- `pistol_reload.png` ya participa realmente en el renderer.
- Estado visual de pistola: idle / fire / reload.
- Reload tiene prioridad sobre fire para evitar parpadeos al recargar inmediatamente después de disparar.
- La familia de pistola usa `pistol.png` como frame de referencia para escala y anclaje.
- Los alpha bounds siguen optimizando el dibujo, pero ya no reescalan cada pose de forma independiente.
- Se documentó la dirección artística oficial y el estándar de assets de armas.
- No se modificó combate, daño, munición, IA, matemáticas, campaña ni guardados.
