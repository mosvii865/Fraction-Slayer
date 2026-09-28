# Worker v1 — Validación visual controlada

Esta build existe para validar **un solo enemigo de producción** antes de acelerar el resto del bestiario.

## Qué cambió

- Worker usa seis sprites de producción 64×80 RGBA: idle, walk_1, walk_2, attack, hurt y death.
- Los seis estados comparten canvas, centro y línea de pies.
- El estado visual es **solo cliente** (`FS.enemyVisuals`) y nunca se guarda en campaña ni cambia IA/HP/daño.
- El renderer conserva el anclaje al piso y usa la proporción real 64:80 del Worker.
- Si un PNG no carga, Worker vuelve al arte procedural anterior.
- La muerte permanece ~1.15 s solo como feedback visual; el enemigo ya está muerto para gameplay desde HP=0.

## Prueba PC

1. Inicia Workshop en CLÁSICO.
2. Observa un Worker quieto: los pies deben coincidir con el piso y no flotar.
3. Haz que te persiga: WALK_1/WALK_2 deben alternar sin que cambie su tamaño aparente.
4. Acércate para que ataque: debe verse ATTACK antes/durante el golpe sin crecer ni saltar.
5. Dispárale sin matarlo: HURT debe aparecer brevemente.
6. Elimínalo: DEATH debe quedar en el piso alrededor de un segundo y luego desaparecer.
7. Gira la cámara y cambia distancia durante la secuencia. El sprite no debe deformarse ni despegarse del suelo.

## Prueba móvil

Repite los pasos anteriores en horizontal. Además comprueba:

- legibilidad del casco, chaleco y herramienta;
- que la silueta siga siendo clara a distancia;
- que atacar/disparar/touch no produzca cierres o stutter;
- que el Worker no tape controles por un escalado incorrecto.

## Criterio de aprobación

Si idle → walk → attack → hurt → death se ve estable en PC y móvil, el pipeline de enemigos queda aprobado para producir Crawler, Rivet y Loader con el mismo estándar.
