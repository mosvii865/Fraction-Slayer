# Fraction Slayer v0.2-alpha3 — candidate2 hotfix

Base: `v0.2-alpha3` candidate. No content from The Laboratory was added.

## Correcciones de alta prioridad

- **Persistencia al reiniciar checkpoint:** armas desbloqueadas, MODs M.A.D. y señales PROJECT U.T.C.J. ya conseguidas no se pierden al morir después de un checkpoint anterior.
- **M.A.D. / UTCJ anti-duplicación:** al restaurar checkpoint también se conserva el consumo de drones M.A.D. y el estado local de logos UTCJ ya registrados, evitando reutilizarlos tras morir.
- **Restart con snapshot:** los botones `REINICIAR CHECKPOINT` sincronizan primero el snapshot realtime para no perder una adquisición hecha justo antes de morir.
- **Ruta principal de Factory:** la enemy rush de Central Manufacturing Floor no inicia hasta haber obtenido **Assault Rifle + Sawed-Off**, por lo que Production Line B ya no puede saltarse como progreso principal.
- **Lab Transit:** nueva compuerta física `lab_transit_gate`; permanece cerrada hasta `production_controls_disabled && foreman_defeated` y evita usar la salida final como corredor de escape durante Foreman.

## Correcciones de progresión / UX

- `factory_foreman` cubre ambos Production Controls, de modo que el checkpoint previo al boss puede registrarse sin depender del orden A/B.
- La navegación apunta primero a Production Control A y luego a B en vez de señalar solo el centro de la arena.
- M.A.D. #2 (Catwalk Service) queda oculto en minimapa hasta ser usado.
- El support del Foreman requiere que el boss siga vivo; el comportamiento histórico del Loader ante sync tardío se conserva.
- Validación de campaña endurecida: `completed_levels` debe referir niveles registrados y `campaign.utcj_found` solo admite señales UTCJ declaradas por niveles registrados.

## Revisión de Factory

`factory.revision` sube de **1 → 2** porque cambió geometría/progresión (compuerta de Lab Transit y prerequisitos de rush). Saves creados con la candidate alpha3 anterior de Factory se rechazan limpiamente por revisión incompatible; saves de Workshop/alpha2 siguen usando su revisión propia.

## Decisiones conscientes tras auditoría

- No se aplicó multiplicador artificial de “perdigones” a Industrial Nodes: las escopetas del motor hacen **cleave multiobjetivo**, no múltiples impactos acumulados sobre un solo blanco. Multiplicar `cfg.damage` por 3/4 haría que Sawed-Off destruyera nodos de 55 HP de forma desproporcionada.
- Sentinel conserva por ahora su implementación actual (torreta fija con burst); el arco de giro limitado queda para balance/pulido después del playtest físico.
- Object Conveyors siguen fuera de alcance de esta candidate; conveyors afectan al jugador usando la colisión normal.
- No se tocaron todavía caps de munición ni MOD II–IV.

## Validación local disponible

- Suite Python completa: **126 passed**.
- `python -m compileall`: sin errores.
- `node --check` sobre scripts frontend modificados: sin errores.
- Streamlit real / Chromium no se pudo ejecutar en este entorno porque `streamlit` no está instalado. Esta build sigue siendo **candidate** hasta el playtest físico del usuario.
