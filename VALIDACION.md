# Validación — Fraction Slayer v0.1.1

Fecha de la actualización: 23 de septiembre de 2026.

## Continuidad y alcance

Se continuó sobre los archivos ya modificados, sin reconstruir la v0.1. Antes de la reanudación ya habían pasado las 37 pruebas Python y la regresión general `browser_smoke.py` sobre v0.1.1 (menús, combate, preguntas, M.A.D., puerta, checkpoints, muerte, final, guardar/continuar y móvil emulado). No se repitieron tras la reanudación porque no se modificaron esas reglas.

Se comparó el contenido de los archivos contra `Fraction_Slayer_v0.1(1).zip`: todos los módulos de `game/`, `app.py`, dependencias y configuración de Streamlit permanecen idénticos byte a byte. En `realtime.js` solo se añadieron las llamadas opcionales de vibración, sin cambiar valores o reglas de combate.

## Pruebas pendientes completadas

Entorno: Python 3.12, Streamlit 1.55.0, Chromium Headless 134 y Playwright 1.51.0. Las pruebas levantan Streamlit real y verifican HTTP 200 en `/_stcore/health` antes de abrir la app.

| Comprobación | Resultado |
|---|---|
| Origen flotante exacto, zona muerta, intensidad, diagonales, radio máximo y liberación | Aprobado |
| Joystick + disparar; soltar disparo mantiene movimiento | Aprobado |
| Segundo dedo en zona izquierda no roba el primer joystick | Aprobado |
| Joystick + cámara y captura independiente | Aprobado |
| Joystick + cámara + disparo + selector con cuatro contactos | Aprobado |
| Cambiar arma con dos dedos sin detener movimiento | Aprobado |
| Elegir arma cierra el selector y conserva cámara/disparo/movimiento activos | Aprobado |
| Recargar y pulsar USAR fuera de una estación no cancelan movimiento ni giran cámara | Aprobado |
| Dos dedos sobre disparo: soltar uno no cancela al otro | Aprobado |
| Cancelación del sistema sin entradas atascadas | Aprobado |
| Zona Esquina izquierda ignora toques en la región superior izquierda | Aprobado |
| Tamaño, zona, radio y vibración se guardan y sobreviven a recarga de página | Aprobado |
| Pequeño/Medio/Grande en cinco viewports; botones ≥44 px, sin solaparse | Aprobado |
| Selector dentro del área jugable, incluido 568 × 320 | Aprobado tras ajuste de ancho mínimo |
| Márgenes seguros simulados: izquierda/derecha 44, arriba 12, abajo 21 px | Aprobado |
| Vertical libera contactos y pausa; horizontal recupera layout y movimiento | Aprobado |
| Vibración activada/desactivada y ausencia de API | Aprobado con API simulada |
| PC: WASD, 1/2 mientras se camina, R, arrastre real de ratón, clic, Esc, E y volver del holograma | Aprobado |
| Errores JavaScript en las pruebas completadas | Ninguno |

Viewports: **568 × 320, 667 × 375, 844 × 390, 932 × 430 y 1024 × 768**, cada uno con los tres tamaños de controles. Orientación vertical: **390 × 844**. Los gestos simultáneos se enviaron como contactos táctiles mediante CDP, no como simples clics ni asignaciones a `FS.move`. Se verificó desplazamiento real del jugador durante cambio de arma/disparo.

Los bloques se ejecutaron por etapas: interacción/preferencias, layout/safe areas y orientación; se repitió únicamente el bloque afectado por cada corrección. `--layout-only` y `--orientation-only` permiten reproducir esa validación selectiva. La prueba de PC se ejecutó aparte al corregir el fallback del ratón.

## Errores encontrados y correcciones

1. **Simulador:** el helper de pruebas enviaba a `touchEnd` el contacto que debía seguir activo. Se corrigió para finalizar el ID levantado. El fallo no estaba en el joystick y no requirió cambiar sus reglas.
2. **Selector en pantalla corta:** las etiquetas se envolvían y lo hacían invadir la barra superior. Se fijó un ancho mínimo de 120 px, manteniendo tamaños táctiles y sin solaparlo con los botones.
3. **Espera de orientación en la prueba:** la visibilidad CSS cambiaba antes de procesarse el evento de resize. Se espera la liberación efectiva de los contactos y la pausa, sin alterar el juego.
4. **Ratón dentro del iframe:** el sandbox de Streamlit no concede `allow-pointer-lock`. Se conserva la solicitud cuando es posible y se añadió giro por arrastre derecho; clic izquierdo dispara aun sin captura. No se cambiaron permisos del navegador ni la arquitectura.

## Evidencia y límites

Las capturas nuevas están en `docs/capturas/v011-*.png`; las otras son evidencia histórica de v0.1. El juego se probó en navegador emulado, no en Android/iPhone físicos ni Safari real. Las inserciones de safe areas son valores CSS de prueba: no prueban un notch físico o las barras dinámicas reales del sistema.

La vibración se verificó interceptando la API para comprobar los pulsos solicitados y su desactivación; falta evaluar soporte y sensación física. Los gestos reservados del sistema operativo, límites de contactos del dispositivo, latencia y ergonomía con distintos tamaños de mano requieren prueba real. En pantallas muy cortas, Medio y Grande pueden converger parcialmente de tamaño para seguir cabiendo.

Los tests usan posiciones controladas y recogida de la escopeta para llegar al caso de cambio de arma. No modifican enemigos o balance en los archivos del juego. No se ha hecho un nuevo despliegue en Streamlit Community Cloud ni una nueva prueba de balance.

## Reproducir las pruebas de esta actualización

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium --only-shell
python tests/mobile_controls.py
python tests/pc_controls.py
```

Solo layout y orientación:

```bash
python tests/mobile_controls.py --layout-only
python tests/mobile_controls.py --orientation-only
```

Para repetir voluntariamente la regresión general, siguen disponibles `python -m pytest -q` y `python tests/browser_smoke.py`. No son necesarios para cambiar únicamente documentación.

---

## Registro histórico de v0.1


Fecha: 22 de septiembre de 2026.

## Entorno y resultado

- Python 3.12, Streamlit 1.55.0, pytest 9.0.2.
- Chromium Headless 134 con Playwright 1.51.0 para la integración. Se utilizó esta versión de pruebas porque la descarga de los navegadores más recientes falló en el entorno; no es una restricción del juego ni una dependencia de producción.
- `python -m pytest -q`: **37 pruebas aprobadas**.
- Arranque real con `python -m streamlit run app.py`: correcto.
- `/_stcore/health`: **HTTP 200**, contenido `ok`.
- `streamlit.testing.v1.AppTest`: **0 excepciones** durante el arranque de `app.py`.
- Verificación de sintaxis JavaScript con Node: correcta.
- `python tests/browser_smoke.py`: **aprobado**, sin errores JavaScript de página.

## Cobertura comprobada

### Reglas Python

Parseo exacto de fracciones, decimales, comas y números mixtos; rechazo de entradas inválidas y división entre cero; opciones con una sola respuesta válida; respuestas privadas; mezcla del banco; diferencias reales entre dificultades; reintentos de puertas; mejoras de pistola y escopeta; consumo único de M.A.D.; deduplicación de eventos; protección del progreso educativo frente al snapshot; guardado/restauración; rechazo de datos corruptos; puntuación y rachas; condiciones de fin de misión; conectividad del mapa.

### Navegador con Streamlit real

Menú → nombre → dificultad → introducción; movimiento WASD; disparo y consumo de munición; pausa y continuidad del mundo; recogida de escopeta; respuesta incorrecta y reintento correcto; mejora de escopeta mediante Python; apertura de puerta; daño a enemigos con disparo real; checkpoint; muerte y restauración; MISSION COMPLETE; recarga de página y CONTINUAR desde el navegador.

En viewport móvil **844 × 390** se comprobó el modo DOOM, seis enemigos, movimiento y giro simultáneos mediante dos contactos táctiles independientes, preguntas manuales resueltas con botones del teclado holográfico y pantalla de rotación en **390 × 844**.

Las capturas de menú, gameplay, teclado y misión fueron revisadas visualmente. Se corrigió un aviso temporal que podía tapar el enunciado del holograma. Se incluyen algunas capturas en `docs/capturas/`.

## Alcance y límites de estas pruebas

La integración usa posiciones controladas para alcanzar las estaciones rápidamente y prepara el estado de enemigos para verificar el cierre de misión. El disparo y su daño se prueban antes de esa preparación. **No es una partida completa sin intervención ni una prueba de balance.**

No se ha probado en hardware Android/iPhone físico ni Safari real. Tampoco se ha publicado en una cuenta de Streamlit Community Cloud. El objetivo pendiente es validar esas condiciones y la comodidad táctil en dispositivos reales, especialmente tamaños pequeños, áreas seguras y rendimiento.

## Repetir

Desde la carpeta del proyecto:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m playwright install chromium --only-shell
python tests/browser_smoke.py
```

El script de navegador crea y detiene su servidor automáticamente. Las nuevas capturas y el log se guardan en `test-results/`, excluido de Git.
