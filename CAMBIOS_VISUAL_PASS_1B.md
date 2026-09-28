# Fraction Slayer — Visual Upgrade Pass 1A/1B

Base funcional: **v0.3-alpha2 — The Foundry candidate**.

Este pase no cambia combate, matemáticas, campaña, guardados, hitboxes ni reglas de progresión.

## 1A — infraestructura visual
- Nuevo `ui/frontend/art.js` con manifiesto y precarga de arte raster opcional.
- Si un PNG tarda en cargar o falta, el renderer conserva automáticamente el sprite procedural anterior.
- El raycaster puede usar texturas de pared por nivel sin reemplazar la arquitectura Canvas/JS.
- Soporte de props decorativos billboard sin colisión ni estado persistente.
- Soporte de armas raster en primera persona con fallback procedural.

## 1B — The Workshop
- Texturas propias para muro, panel industrial y puerta.
- Sprites renovados para Worker, Crawler, Rivet y Loader MK-I (incluye warning/stun/rear).
- Arte propio para Pistol y Pump Shotgun.
- Arte renovado para terminal, M.A.D., power install y exit.
- Biblioteca de props: crates, barriles, tool chest, lockers, extintores, gabinetes eléctricos, tuberías, pallets, workbench y carteles de zona.
- 20 props colocados en Workshop, pegados a paredes y sin colisión para preservar rutas de combate validadas.
- HUD recibe un pass industrial ligero, sin mover controles ni touch targets.

## Principio de compatibilidad
Un fallo visual nunca debe producir `ERROR DE MOTOR`: el arte nuevo es progresivo y opcional; la representación procedural anterior sigue siendo el fallback de seguridad.
