# Validación — Fraction Slayer v0.1

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
