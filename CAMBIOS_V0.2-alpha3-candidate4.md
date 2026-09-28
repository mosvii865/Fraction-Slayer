# Fraction Slayer v0.2-alpha3-candidate4 — Mobile M.A.D. hotfix

Base: `v0.2-alpha3-candidate3`.

## Bug corregido

En controles táctiles, `INTERACTUAR` ejecutaba su acción en `pointerdown`. Los M.A.D. abren su selector de arma de forma síncrona, por lo que el mismo dedo seguía físicamente presionado mientras `freeze()` liberaba el pointer capture y el overlay nuevo aparecía. En algunos navegadores móviles el `pointerup`/click de compatibilidad podía terminar dirigido al modal recién creado, cerrándolo o activando accidentalmente un control. El síntoma era que el selector M.A.D. se cerraba inmediatamente salvo que el jugador tocara muy rápido.

## Hotfix

- `INTERACTUAR` ahora se activa en `pointerup`, no en `pointerdown`.
- `DISPARAR` conserva activación inmediata en `pointerdown`.
- Reload y selector de armas conservan su comportamiento anterior.
- La activación por teclado/accesibilidad (`click` con `detail=0`) se mantiene.
- Se añadió una regresión de contrato para impedir que `INTERACTUAR` vuelva accidentalmente a activarse en `pointerdown`.

No se modificaron reglas de M.A.D., preguntas, campaña, Factory ni balance.
