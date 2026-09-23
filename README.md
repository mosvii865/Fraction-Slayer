# Fraction Slayer — v0.2-alpha1

**Engine preparation for real levels**

FPS retro educativo original, con Python + Streamlit y renderizado Canvas por raycasting. Diseñado para jugar desde el navegador en celular horizontal y PC.

**Diseño y concepto:** Esteban Montaño. **Proyecto académico:** Universidad Tecnológica de Ciudad Juárez.

> La matemática no te impide jugar. Te permite jugar mejor.

## Actualización v0.2-alpha1

Motor preparado para niveles definidos por datos. `industrial_test` sigue siendo el único nivel jugable y conserva geometría, armas, enemigos y balance de CLÁSICO/DOOM. No se construye todavía The Workshop ni Loader.

- Identidad `level_id` y revisión por nivel; save versión **2**, incompatible con saves v0.1/v0.1.1. El error permite empezar una partida nueva. Las preferencias táctiles sí se conservan.
- Progreso por ID para puertas, M.A.D., terminales, objetivos, triggers, oleadas y secretos; puntos de interacción independientes de la posición visual.
- Checkpoints por zona/prerrequisitos y respawn seguro, con HP mínimo, munición mínima y breve gracia solamente al reiniciar.
- Enemigos dormidos y encuentros explícitos por dificultad; búsqueda de última posición vista y capacidades básicas para un futuro Loader.
- Pickups tipados, quest/key inventory, secretos UTCJ separados de kills y salida por objetivos.
- Preguntas configurables por estación, formato manual estricto y recompensas transaccionales.
- Cooldown conservado al cambiar de arma; terminales normales bloqueadas con amenaza cercana visible.
- Recuperación automática de `session_state` desde el save local y bucle de render recuperable ante errores.
- Cambios pequeños de altura/visualViewport conservan los contactos; rotación real, cambios fuertes, pausa o pérdida de foco los liberan.

Contrato y ejemplos: [docs/LEVEL_CONFIG.md](docs/LEVEL_CONFIG.md). Resultados: [VALIDACION.md](VALIDACION.md). Lista exacta de archivos: [CAMBIOS_V0.2-alpha1.md](CAMBIOS_V0.2-alpha1.md).

## Controles móviles conservados de v0.1.1

- **Joystick flotante:** toca la mitad izquierda del área jugable y arrastra. El origen coincide con el primer contacto y no se desplaza mientras mantengas ese dedo. Al soltar, el movimiento se detiene y el círculo se desvanece. Dirección continua, incluidas las ocho direcciones y diagonales, con magnitud analógica; la velocidad máxima original no cambia.
- **Multitouch:** cada `pointerId` tiene un propietario. Movimiento, cámara, disparo y botones no se sobrescriben entre sí. Un segundo toque sobre la zona de movimiento no roba el joystick. Cancelar o soltar un botón solo libera su propio contacto.
- **Selector compacto:** toca **ARMAS** junto al pulgar derecho, o el arma del HUD, y elige PISTOLA/ESCOPETA. Se cierra al elegir y no pausa movimiento, cámara ni disparo. También muestra munición y disponibilidad. No es necesario soltar el joystick.
- **Botones grandes:** DISPARAR, USAR, RECARGAR y ARMAS están separados en el lado derecho. La recarga móvil tiene un botón grande propio; se conserva la barra general del HUD.
- **Preferencias:** Configuración → Pequeño / **Medio** / Grande, zona **Mitad izquierda** / Esquina izquierda, radio máximo del joystick (40–85 px base; 60 predeterminado) y Vibración Sí/No. Se conservan en la misma clave local de configuración. El tamaño también escala el joystick y el selector. En pantallas cortas, los controles se reducen lo necesario para caber sin solaparse.
- **Zona muerta:** 16% del radio efectivo, con mínimo de 7 px. Fuera de ella, la intensidad crece hasta el radio máximo y se limita a uno; alejar más el dedo no aumenta la velocidad. El radio efectivo combina la preferencia, el tamaño de controles y el espacio disponible.
- **Márgenes seguros:** se consideran los cuatro `safe-area-inset`, el viewport visible y los cambios de orientación. Los toques no desplazan ni amplían la vista durante gameplay; los paneles conservan desplazamiento y zoom. Solo una rotación real o un cambio fuerte de tamaño libera contactos; las variaciones pequeñas de altura relayoutan sin cancelar el joystick. En vertical se pausa y aparece ROTATE DEVICE; vuelve a horizontal, pulsa CONTINUAR y vuelve a tocar el joystick.
- **Vibración opcional:** desactivada inicialmente. Pulsos solicitados de 6 ms al disparar, 14 ms al recibir daño y 8 ms al cambiar arma, limitados para evitar acumulación. Si el navegador no admite o no permite vibración, se omite sin errores.

El selector de armas no pausa el juego. **Interactuar con una estación que abre un holograma conserva la pausa educativa de v0.1**; pulsar USAR sin abrir un panel no cancela el joystick. Pausa, muerte, pérdida de foco y aviso de desconexión siguen liberando todos los controles por seguridad.

En PC se mantienen WASD, clic izquierdo, E, R y 1/2. Si el iframe impide capturar el ratón, puedes girar arrastrando con el botón derecho; las flechas también funcionan. No se modifican los permisos del iframe.

Consulta `CHANGELOG.md` para el historial; `CAMBIOS_V0.1.1.md` conserva el registro de la actualización anterior.

## Arranque rápido

Recomendado: **Python 3.12**. Ejecuta los comandos dentro de la carpeta que contiene `app.py`.

```bash
python -m venv .venv
```

Activa el entorno:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Instala y ejecuta:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abre `http://localhost:8501`. No abras `index.html` directamente: las preguntas requieren el proceso Python de Streamlit. No hace falta Node, npm, compilación del frontend, base de datos, API key ni assets externos.

Para probar desde un teléfono en la misma red Wi-Fi:

```bash
python -m streamlit run app.py --server.address 0.0.0.0
```

Abre `http://IP_LOCAL_DE_TU_PC:8501` en el teléfono. Permite el puerto en el firewall de tu PC si es necesario. En Cloud se utiliza directamente la URL HTTPS de la app, sin instalar nada en el celular.

## Qué incluye

- Menú industrial animado, nueva partida con nombre, dos dificultades, continuar, estadísticas, configuración y créditos.
- Mapa de prueba: sala inicial, pasillo, arena, terminal QC, M.A.D., Secure Cache, puerta y fin de turno.
- Raycasting, colisiones, movimiento rápido sin salto, controles de ocho direcciones y giro horizontal.
- Worker-01 cuerpo a cuerpo, Crawler rápido y Rivet con proyectiles esquivables. La IA adquiere objetivos por línea de visión y busca su última posición cuando la pierde.
- Pistola y escopeta de corredera de ocho cartuchos, recarga manual/automática al intentar disparar vacío, munición de reserva y selector de arma.
- Botiquines, armadura, munición y cartuchos. La armadura absorbe hasta la mitad del daño mientras tenga carga.
- HUD con rostro procedural, cinco rangos de daño y estados de daño/concentración/recogida/mejora.
- Hologramas con opción múltiple y teclado interno de enteros, decimales y fracciones; también se admite teclado físico.
- Preguntas de conversión, equivalencia, simplificación, numerador/denominador, tolerancias e instrumentos.
- Puerta con reintentos ilimitados; una mejora real por arma y un solo uso por cada dron M.A.D.; no se consume si no hay mejora válida.
- Tres checkpoints, muerte/reinicio, resumen final, puntuación, guardado local y exportación/importación JSON.
- Sonidos sintetizados originales, sin música ni assets comerciales.

## Primera partida sugerida

1. Inicia en CLÁSICO. El practicante llega a DDI para trabajar en Quality Control y encuentra el caos de The Converter.
2. Explora la sala: la terminal verde entrega munición al calibrarla; la escopeta y la armadura están en el lado sur. No es obligatorio responder para empezar a combatir.
3. Cruza el pasillo hacia la arena. Se guarda el checkpoint antes de entrar si la zona y el respawn están seguros.
4. Usa cobertura contra Rivet. Los tres tipos se distinguen por forma/color y comportamiento.
5. El M.A.D. azul, al norte de la arena, permite elegir una de tus armas y mejorarla al resolver una calibración. Un error no consume el dron. Las estaciones normales exigen que no haya una amenaza cercana con línea de visión.
6. La estación morada al noreste es un Secure Cache opcional: +35 vida y +24 balas, y cuenta como un secreto.
7. Elimina a todos los enemigos; antes del acceso final se registra otro checkpoint.
8. Calibra la puerta ámbar al este y entra a la sala final. Interactúa con FIN DE TURNO para ver MISSION COMPLETE.

## Controles

| Acción | Móvil horizontal | PC |
|---|---|---|
| Moverse | Joystick flotante izquierdo, analógico | WASD |
| Girar | Arrastrar zona derecha sin botones | Mouse capturado si se permite; arrastre con botón derecho o ← / → |
| Disparar | Mantener DISPARAR | Clic izquierdo; Espacio como alternativa |
| Interactuar | USAR, cerca de estación | E |
| Cambiar arma | ARMAS → selector compacto, sin soltar el joystick | 1 pistola / 2 escopeta |
| Recargar | Botón grande RECARGAR a la derecha | R |
| Pausar | Ⅱ, esquina superior | Esc o botón Ⅱ |
| Pantalla completa | ⛶ si el navegador lo admite | ⛶ |

No hay salto ni botón de correr. La velocidad base ya es rápida. El pad, la cámara y el disparo usan punteros independientes para admitir multitouch. Al perder foco, girar a vertical o cambiar de pestaña se pausa el juego. Algunas funciones del navegador, como pantalla completa en iPhone, dependen de Safari y de los permisos del iframe; la vista horizontal funciona sin ellas.

En Configuración puedes ajustar sensibilidad, sonido, minimapa y resolución reducida. El teclado holográfico incluye `/`, signo negativo, borrar y limpiar, además de los dígitos y el punto. No depende del teclado nativo para las respuestas matemáticas. El nombre sí usa un campo de texto normal.

## CLÁSICO y DOOM

| Regla v0.1 | CLÁSICO | DOOM |
|---|---:|---:|
| Enemigos | 3 | 6 |
| Multiplicador velocidad enemiga | 0.75 | 1.12 |
| Daño base por ataque | 8 | 14 |
| Intervalo de ataque | 1.70 s | 1.05 s |
| Cantidad de recursos en mapa | 100% | 55%, redondeada |
| Reserva inicial de pistola | 48 | 24 |
| Reserva al recoger escopeta | 12 | 6 |
| Respuesta manual entre preguntas numéricas | 15% | 55% |
| Denominadores | Hasta 8, luego 16 tras dos aciertos | Hasta 16 |

La vida de cada tipo de enemigo es igual en ambos modos. Las preguntas de teoría usan opciones. La mezcla del generador es aproximadamente 70% conversiones/equivalencias/simplificación, 20% teoría aplicada y 10% identificación de denominador. Son probabilidades por pregunta; una partida pequeña no tiene por qué reproducir esos porcentajes exactamente.

## Arquitectura y responsabilidades

| Archivo / carpeta | Función |
|---|---|
| `app.py` | Arranque de Streamlit, `session_state`, entrega de eventos al motor |
| `game/engine.py` | Nueva partida, preguntas, respuestas, mejoras, checkpoint y finalización |
| `game/conversiones.py` | Parseo seguro y comparación exacta con `fractions.Fraction` |
| `game/preguntas.py` | Generación de preguntas, respuestas privadas y explicaciones |
| `game/dificultad.py` | Balance de dificultades |
| `game/armas.py`, `enemigos.py`, `mejoras.py` | Catálogos y reglas extensibles |
| `game/nivel.py` | Registro y datos de niveles; encuentros explícitos por dificultad |
| `game/world.py` | Condiciones, progreso, seguridad, pickups y recompensas transaccionales |
| `game/estadisticas.py`, `puntuacion.py` | Métricas y cálculo de puntuación |
| `game/save_system.py` | Formato de guardado versionado, validación y restauración |
| `game/reporte.py` | Modelo inicial del futuro reporte de estadías |
| `game/roadmap.py` | Metadatos futuros: niveles, Project U.T.C.J., El Toro y escudos |
| `ui/game_component.py` | Componente bidireccional, servido desde archivos locales |
| `ui/frontend/bridge.js` | Protocolo Streamlit v1, IDs, confirmación y reintento |
| `ui/frontend/game.js` | Menús, HUD, hologramas y almacenamiento del navegador |
| `ui/frontend/realtime.js` | Física, combate, IA, recogidas y telemetría |
| `ui/frontend/controls.js` | Entradas táctiles/PC y bucle de animación |
| `ui/frontend/renderer.js` | Raycasting, sprites procedurales, armas y rostro |
| `ui/frontend/style.css` | Diseño responsive del juego y paneles |
| `tests/` | Pruebas unitarias e integración en navegador |
| `assets/` | Espacios reservados para sprites, armas, HUD, sonido y música |

Python conserva las respuestas correctas hasta la evaluación. JavaScript recibe el enunciado/opciones, presenta la pregunta y envía la respuesta; no decide si es correcta. Python controla progreso educativo, uso de estaciones, mejoras, puntuación y validación del save.

El navegador calcula cada frame: movimiento, colisiones, disparos, daño inmediato, IA y recogidas. Sus parámetros proceden de Python. Envía snapshots cada 10 segundos y en eventos relevantes; cambios de pickups, combate u objetivos/zonas pendientes se agrupan para confirmar progreso sin peticiones por frame. El FPS no hace una petición por frame ni reinicia el Canvas en cada rerun de Streamlit. El tiempo registrado excluye pausa y hologramas.

Los eventos tienen IDs y una caché de respuestas para evitar aplicar dos veces una respuesta retransmitida. Una interrupción de red prolongada presenta un aviso y permite reintentar el mismo evento. Para mantener la sencillez, solo se envía una solicitud a la vez; si pulsas una estación durante una sincronización, aparecerá un aviso para intentar de nuevo.

**Límite de autoridad:** se confía en la telemetría de combate del navegador. Esta versión es un juego académico para un jugador, no un sistema competitivo con antitrampas. Los guardados son editables. La validación comprueba estructura/rangos y no demuestra que el usuario haya jugado legítimamente.

## Guardado y checkpoints

- Un slot en `localStorage` del navegador bajo `fraction-slayer-save`, con esquema `version: 2`. Saves antiguos/incompatibles se rechazan con un mensaje; no se migran automáticamente.
- Contiene `level_id`, revisión, identidad de partida, nombre, dificultad, posición, vida, armadura, enemigos/activación, objetos, inventario, armas, mejoras, progreso por ID y estadísticas; además, una copia del último checkpoint.
- Python mantiene la partida y las estadísticas en `st.session_state` durante la sesión.
- El navegador conserva los saves confirmados por Python. La sincronización automática es cada 10 segundos y también ocurre al pausar, contestar, crear checkpoints y terminar.
- CONTINUAR carga el último snapshot confirmado. REINICIAR CHECKPOINT restaura el mundo, recursos y estadísticas de ese checkpoint; el intento posterior descartado no suma a la puntuación. Se aplica HP mínimo de 50, mínimo total de 12 balas de pistola / 4 cartuchos por arma poseída y 2.5 s de gracia; estos pisos son datos del nivel y no se aplican durante gameplay normal.
- Reiniciar también elimina proyectiles transitorios. No se conserva una recarga en curso.
- Pausa → Configuración / Guardado → EXPORTAR JSON descarga una copia portátil. IMPORTAR JSON la valida en Python y reemplaza el slot si es válida.
- El guardado no utiliza archivos compartidos del servidor ni depende de su disco. No comparte partidas entre usuarios.
- Borrar datos del sitio, usar incógnito, cambiar dominio o cambiar navegador puede eliminar/ocultar el slot. Exporta JSON para transferirlo o respaldarlo. Algunos navegadores bloquean almacenamiento en iframes; se muestra aviso y sigue disponible la exportación durante la sesión.
- Si el servidor pierde `session_state`, el cliente intenta restaurar el slot automáticamente y sincronizar su snapshot actual; muestra “Sesión restaurada”. Una pregunta pendiente se vuelve a emitir con un ID nuevo. Si no existe un save compatible, vuelve al menú con un mensaje claro. Tras recargar la página, CONTINUAR recupera el último save confirmado.

Para persistencia entre dispositivos, `make_save` y `load_save` son el punto de integración de un repositorio remoto por usuario. Una futura versión puede incorporar autenticación y almacenamiento durable sin cambiar el contenido de preguntas ni el renderer. No se ha agregado una base de datos en v0.1.

## Puntuación

`100 × enemigos + 150 × aciertos + 25 × mejor racha + 200 × secretos + bonus de precisión − 20 × errores`, con mínimo cero. El bonus de precisión es hasta 300 puntos. La precisión incluye todas las calibraciones, también teoría aplicada. Las estadísticas mostradas en el menú corresponden al último registro confirmado, no a un historial de múltiples partidas.

## Subir a GitHub

Descomprime el ZIP. Usa **el contenido de `fraction-slayer/` como raíz del repositorio**, de forma que `app.py`, `requirements.txt`, `game/`, `ui/` y `.streamlit/` estén juntos.

Opción desde el navegador: crea un repositorio vacío en GitHub, abre **Add file → Upload files**, arrastra los archivos/carpetas del proyecto y confirma el commit. Comprueba que también se subió `.streamlit/config.toml`; si tu selector oculta carpetas que empiezan con punto, crea esa ruta desde GitHub. No subas `.venv/`, `__pycache__/` ni los resultados temporales de pruebas.

Opción con Git, desde la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Fraction Slayer v0.1.1: controles móviles"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/fraction-slayer.git
git push -u origin main
```

Sustituye `TU_USUARIO` por tu cuenta y crea primero el repositorio vacío. Si ya tienes un repositorio existente, incorpora estos archivos en una rama y conserva su historial.

## Desplegar en Streamlit Community Cloud

1. Entra a [share.streamlit.io](https://share.streamlit.io/) y conecta tu cuenta de GitHub.
2. Elige **Create app** y la opción de desplegar una app existente.
3. Selecciona el repositorio, rama `main` y archivo principal `app.py`.
4. En **Advanced settings**, elige Python **3.12**, la versión utilizada en las pruebas. No necesitas secretos.
5. Elige un subdominio disponible y pulsa **Deploy**.
6. Abre la URL HTTPS en móvil horizontal y crea una partida. Comprueba el disparo, una calibración y CONTINUAR después de recargar.

Cloud instala `requirements.txt`, que fija Streamlit 1.55.0. No instales `requirements-dev.txt` para producción. Las carpetas `ui/frontend/` y `game/` deben estar incluidas en GitHub. El componente se sirve desde el propio Streamlit, sin un segundo servidor ni CDN.

Referencias oficiales: [despliegue](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [dependencias](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies), [componentes bidireccionales](https://docs.streamlit.io/develop/concepts/custom-components/components-v1/intro).

El proyecto se entrega preparado; no se ha creado ni publicado un repositorio o despliegue en tu cuenta.

## Pruebas

Solo reglas Python:

```bash
python -m pip install pytest==9.0.2
python -m pytest -q
```

Integración visual opcional:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium --only-shell
python tests/browser_smoke.py
python tests/mobile_controls.py
python tests/pc_controls.py
python tests/browser_engine.py
```

En Linux sin bibliotecas de navegador, Playwright puede requerir `python -m playwright install-deps chromium`. Esto solo es para el entorno de desarrollo/pruebas, no para Streamlit Cloud.

El script levanta su propio Streamlit temporal, comprueba escritorio y móvil emulado, y guarda capturas en `test-results/`. Emplea posiciones controladas para llegar a cada sistema y una preparación de estado para terminar el mapa; no sustituye una partida completa de balance ni pruebas en un teléfono físico. Se puede usar `CHROME_PATH` para indicar un ejecutable Chromium compatible existente. Consulta `VALIDACION.md` para los resultados de esta entrega.

## Límites de v0.2-alpha1 y siguiente paso

Un mapa de validación y sprites procedurales sencillos; IA sin búsqueda de rutas compleja; no hay música, cinemáticas, lectura gráfica de regla, navegación vertical ni multijugador. La escopeta usa un cono de daño simplificado, y la recarga repone el tubo en una sola animación temporal, sin inserción cartucho por cartucho. Las caras son dibujos geométricos reemplazables.

El banco de teoría es pequeño. Solo hay MOD I real para cada arma, aunque los catálogos admiten cuatro niveles. Las preguntas alcanzan MOD II matemático; no hay un árbol de dificultad adaptativa. Las animaciones de concentración/mejora son muy básicas. El reporte de estadías contiene el modelo y registros mínimos, no un documento exportable.

El juego necesita conexión para consultar Python y guardar confirmaciones. Al perder conexión, los frames pueden continuar hasta detectarse una solicitud pendiente; después se pausa con aviso. No es una PWA offline. Rendimiento y comodidad final deben medirse en Android/iPhone reales. Pantalla completa y captura del mouse dependen del navegador.

**Siguiente paso recomendado:** diseñar el contrato de The Workshop sobre esta base (objetivos, gates, encuentros y estaciones con denominadores 2/4/8), verificar alcanzabilidad y recursos mínimos con tests, y validar en iPhone Safari/Android físicos antes de construir el nivel completo. La máquina de estados y los ataques de Loader siguen pendientes; solo están preparados los campos y primitivas del motor.

Preparado para expandirse con The Workshop, The Factory, The Laboratory, The Foundry y The Converter. Los catálogos reservan armas futuras; el reporte dispone de `project_utcj` para los cuatro logos. El Toro, Bull Core, el desbloqueo 4/4 y los escudos del jefe todavía no se implementan. Un escudo futuro puede reutilizar los eventos de pregunta/respuesta y aplicar un efecto de progreso como hoy lo hace la puerta.
