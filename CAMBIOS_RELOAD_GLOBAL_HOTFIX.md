# Reload global hotfix

## Problema reportado en playtest
El HUD podía mostrar munición de reserva disponible, pero después de una recarga anterior el juego podía rechazar nuevas recargas en cualquier arma.

## Causa raíz
`FS.reloading` es un contador en segundos. Al finalizar se restaba `dt` y podía quedar ligeramente negativo. En JavaScript, un número negativo sigue siendo `truthy`, mientras que `reload()` usaba `if (FS.reloading) return;`. El resultado era un bloqueo permanente de recargas posteriores aunque `reserve > 0`.

## Corrección
- La entrada de recarga ahora solo se bloquea cuando `FS.reloading > 0`.
- El contador se clampa explícitamente a `0` con `Math.max(0, ...)`.
- La transferencia de reserva a cargador se ejecuta cuando el contador llega exactamente a `0`.

No se modificaron capacidades, reservas, daño, cadencia, animaciones de la DDI Breach Pump, M.A.D., campaña, saves ni balance.
