# Fraction Slayer — Estándar de assets de armas v1

Este estándar empieza con la pistola industrial y sirve como contrato para los siguientes viewmodels.

## Canvas y formato

- PNG RGBA con transparencia.
- Canvas de referencia actual: **160 × 120 px** para la familia de pistola.
- Todos los estados de una misma arma deben compartir exactamente el mismo canvas y sistema de coordenadas.
- No se debe recortar cada estado a tamaños distintos antes de integrarlo.

## Estados mínimos

- `<weapon>.png` — idle.
- `<weapon>_fire.png` — disparo/recoil visual.
- `<weapon>_reload.png` — recarga.

Estados adicionales pueden añadirse cuando la animación lo justifique, pero deben conservar el mismo canvas y anclaje.

## Regla de anclaje

El renderer puede usar alpha bounds para evitar procesar píxeles transparentes, **pero no debe recalcular la escala ni centrar cada frame de forma independiente**. La escala y el anclaje se obtienen del frame de referencia (idle) y se aplican a todos los estados mediante las coordenadas compartidas del canvas.

Esto evita que un frame de recarga más corto o ancho parezca crecer, encogerse o saltar en pantalla.

## Estado de la pistola

Prioridad visual actual:

1. Reload, si `FS.reloading > 0`.
2. Fire, si `FS.shotFlash > 0`.
3. Idle.

La recarga tiene prioridad porque puede comenzar mientras todavía existe un remanente muy corto de `shotFlash`.

## Producción futura

Antes de considerar terminado un nuevo viewmodel se debe comprobar en PC y móvil:

- posición estable entre frames;
- tamaño consistente;
- mano/antebrazo sin saltos;
- lectura clara del arma;
- muzzle flash legible;
- recarga visible;
- ausencia de clipping molesto con HUD o bordes.
