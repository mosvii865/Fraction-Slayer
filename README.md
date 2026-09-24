# Fraction Slayer v0.2-alpha2 — The Workshop

Primer nivel de campaña completo sobre **v0.2-alpha1.1-stable**. Python + Streamlit conservan preguntas, reglas, recompensas, progreso y guardados; Canvas/JavaScript llevan el FPS en tiempo real. No requiere instalar nada en el celular.

**Diseño y concepto:** Esteban Montaño. **Proyecto académico:** Universidad Tecnológica de Ciudad Juárez.

> La matemática no te impide jugar. Te permite jugar mejor.

## Jugar

**NUEVA PARTIDA → nombre → LEVEL 01 — THE WORKSHOP → CLÁSICO / DOOM.** Workshop es el destino predeterminado de la interfaz. El selector también ofrece **Industrial Test — regresión**, conservado con su mapa y balance anteriores. La API Python sin `level_id` mantiene ese nivel antiguo para compatibilidad.

Misión: **RESTORE POWER AND REACH THE ELEVATOR**. Eres un estudiante de UTCJ en su primer día de estadías en DDI, Quality Control. Primero combate y exploración; solo la puerta del fusible exige una conversión. Las otras cuatro calibraciones dan ventajas opcionales.

| Zona | Contenido |
|---|---|
| Reception / Inspection Bay | Inicio tranquilo, pistola 12 + 24; dos Workers al avanzar |
| Tool Storage | +6 balas, +10 HP, terminal opcional 1/2 = .50 → +12 balas |
| Assembly Floor | Dos oleadas; escopeta durante el combate, 8 + 12 cartuchos |
| Calibration Room | M.A.D. #1 visible, 3/4 = .75, MOD I de pistola o escopeta |
| Maintenance Tunnels | +25 armadura, +8 cartuchos; alcoba con M.A.D. #2 y emblema UTCJ |
| Power Control | Puerta obligatoria .375 = 3/8; fusible; emboscada; Secure Cache 5/8 = .625 → +12 cartuchos |
| Generator Hall | Instalar fusible sin pregunta; suministro mínimo; energía y Loader MK-I |
| Exit Elevator | Se abre con energía restaurada **y** Loader derrotado; estadísticas y teaser de The Factory |

Ruta: Reception → Assembly → Calibration → Maintenance → Power Control; vuelve por Maintenance hacia Generator Hall. Tool Storage y la alcoba de servicio son ramales opcionales. El HUD nombra la zona y el objetivo; un rombo ámbar señala el destino en el minimapa. No es una ruta automática.

El segundo M.A.D. pide **7/8 = .875** y mejora el arma pendiente. Si no hay una compatible, informa y sigue disponible; un fallo matemático no consume estaciones. Dispara al emblema oculto: **PROJECT U.T.C.J. 1/4 — SIGNAL REGISTERED**. Si lo omites, el resumen dice **UTCJ: ???**. No cuenta como enemigo ni kill.

## Loader MK-I

250 HP en ambos modos; melee, carga corta con dirección fijada y aviso, ground slam con aviso y recuperación. Chocar contra sólidos lo aturde **1.75 s**. Su núcleo trasero recibe **×1.65** daño; el frontal también permite derrotarlo. Color rojo durante preparación y azul al aturdirse; barra de vida y sonidos sintetizados.

Al cruzar el 50% se registra un evento único. Primero hay alerta y sonido; **dos segundos de juego después** se activan dos Crawlers, más un Rivet en DOOM. Si varios impactos llegan juntos por latencia, el evento no se pierde aunque incluyan el golpe final. El elevador no exige eliminar estos refuerzos ni otros enemigos opcionales.

## CLÁSICO / DOOM

| Workshop | CLÁSICO | DOOM |
|---|---:|---:|
| Worker / Crawler / Rivet / Loader | 11 / 5 / 4 / 1 | 14 / 9 / 6 / 1 |
| Total | 21 | 30 |
| Vida del Loader | 250 | 250 |
| Velocidad / daño base / intervalo | .75 / 8 / 1.70 s | 1.12 / 14 / 1.05 s |
| Preguntas | Cinco de opción múltiple | Terminal y puerta con opciones; M.A.D./cache manuales |
| Denominadores | 2, 4, 8 | 2, 4, 8 |

La pistola comienza con 12 cargadas + 24 de reserva y la escopeta con 8 + 12 en ambos modos. DOOM añade encuentros concretos, posiciones, agresividad y preparación de carga más corta, no más HP. Los recursos de Workshop son explícitos; no heredan el escalado global de Industrial Test. Hay proporcionalmente menos recursos por enemigo en DOOM.

Después de despejar Generator Hall se asegura una vez un total mínimo de **24 balas y 12 cartuchos**, por arma poseída. Instalar el fusible vuelve a comprobar ese piso una sola vez al iniciar el boss. No se rellena cada frame ni al abrir el menú, y no depende de acertar preguntas opcionales.

La economía apunta a ~1.5× CLÁSICO y ~1.28× DOOM bajo una estimación simplificada (65% impactos, 40 de daño medio por cartucho, sin MOD/rear/múltiples blancos; incluye terminal/cache y excluye aportes variables de los pisos de emergencia). **No es balance medido en jugadores.** Objetivo de duración inicial: 8–12 minutos, todavía pendiente de validación humana.

## Ejecución local exacta

Recomendado Python 3.12. Descomprime el ZIP y entra en `fraction-slayer/`:

```bash
python -m venv .venv
```

Windows PowerShell: `.venv\Scripts\Activate.ps1`. macOS/Linux: `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abre `http://localhost:8501`. No abras `ui/frontend/index.html` directamente: el componente necesita Python/Streamlit. No hay Node/npm, build del frontend, API keys, base de datos ni CDN necesarios para jugar.

Teléfono en la misma Wi-Fi:

```bash
python -m streamlit run app.py --server.address 0.0.0.0
```

Abre `http://IP_LOCAL_DE_TU_PC:8501` y permite el puerto en el firewall si corresponde. En Community Cloud basta su URL HTTPS y el móvil horizontal.

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

## Guardado y checkpoints

Un slot local, exportable/importable en Configuración. **SAVE_VERSION = 2** se conserva: los saves de `industrial_test` de la estable siguen cargando; v1, revisiones incompatibles o datos corruptos se rechazan con un mensaje y permiten partida nueva. Workshop tiene su propio `level_id`, revisión y progreso; nunca mezcla checkpoints de niveles distintos.

Se guardan inventario/fusible, objetivos, estaciones por ID, oleadas y tiempos de triggers, estado/fase del Loader, secretos, mejoras y estadísticas. Los cuatro checkpoints son Reception, Calibration tras Assembly, fusible recuperado tras la emboscada y antes del Loader. Se rechazan checkpoints muertos o inseguros; al reiniciar hay mínimo 50 HP, munición y 2.5 s de gracia. Se restaura el progreso del checkpoint, no los eventos posteriores a él.

Python usa `session_state`; el navegador conserva `fraction-slayer-save` y las preferencias. Una sesión de Streamlit perdida intenta restauración limitada desde ese slot. No depende del disco efímero de Community Cloud. Borrar datos del navegador o cambiar de dispositivo requiere importar el JSON exportado. Nueva Partida reemplaza el único slot.

## Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Arranque Streamlit y entrega de eventos, sin cambios |
| `game/workshop.py` | Grid, zonas, encuentros, estaciones, objetivos, gates y recursos del nuevo nivel |
| `game/nivel.py` | Registro de niveles y composición por dificultad |
| `game/engine.py`, `world.py` | Reglas autoritativas, transacciones, instalación del fusible, checkpoints y eventos |
| `game/preguntas.py`, `conversiones.py` | Validación educativa existente, sin cambios |
| `game/save_system.py` | Save v2, fases del boss y tiempos de eventos opcionales |
| `ui/frontend/loader.js` | Ataques y feedback del Loader; no decide recompensas ni progreso |
| `ui/frontend/realtime.js` | Combate, movimiento y sincronización |
| `ui/frontend/game.js`, `renderer.js` | Menús/hologramas, mapa, sprites procedurales y HUD |
| `ui/frontend/controls.js`, `bridge.js` | Controles/diagnóstico y protocolo Streamlit, sin cambios |
| `tests/test_workshop.py`, `browser_workshop.py`, `workshop_driver.js` | Reglas, gates y recorrido de Workshop contra Streamlit real |

Se mantiene el límite original de confianza: combate y posiciones del cliente son telemetría de un juego de un jugador; no hay antitrampas competitivo. Python decide las respuestas, recompensas, estaciones, oleadas, scoring y validación del save.

Se conserva **ERROR DE MOTOR**, `COPIAR ERROR`, stack/etapa/contexto y `DEBUG_ENGINE_ERRORS=true` en `controls.js`. Los errores no se ocultan. Python registra eventos y excepciones sin imprimir saves ni respuestas; sync exitoso como máximo cada 30 segundos por sesión.

## Subir a GitHub

Descomprime el ZIP. Usa **el contenido de `fraction-slayer/` como raíz del repositorio**, de forma que `app.py`, `requirements.txt`, `game/`, `ui/` y `.streamlit/` estén juntos.

Opción desde el navegador: crea un repositorio vacío en GitHub, abre **Add file → Upload files**, arrastra los archivos/carpetas del proyecto y confirma el commit. Comprueba que también se subió `.streamlit/config.toml`; si tu selector oculta carpetas que empiezan con punto, crea esa ruta desde GitHub. No subas `.venv/`, `__pycache__/` ni los resultados temporales de pruebas.

Opción con Git, desde la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Fraction Slayer v0.2-alpha2: The Workshop"
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

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m playwright install chromium --only-shell
python tests/browser_workshop.py
python tests/browser_workshop_feedback.py
python tests/browser_startup.py
python tests/browser_smoke.py
python tests/browser_smoke.py --doom
python tests/mobile_controls.py
python tests/pc_controls.py
python tests/browser_engine.py
```

Cada script de navegador levanta y termina su propia instancia **real** de Streamlit y genera evidencias en `test-results/`. En Linux pueden hacer falta dependencias del sistema: `python -m playwright install-deps chromium`. Es desarrollo, no un requisito para el servidor Cloud. `CHROME_PATH` permite un Chromium compatible instalado.

El recorrido Workshop usa colisiones, disparos, munición, recarga y RPC reales, con navegación acelerada y gracia renovada solo desde el test. Prueba funcionalidad, no balance sin protección. Los ataques del Loader se comprueban por separado sin gracia. Las suites anteriores siguen usando Industrial Test explícitamente. Resultados, fallos corregidos y alcance: **VALIDACION.md** y **CAMBIOS_V0.2-alpha2.md**.

## Límites y siguiente paso

Sprites geométricos, IA sin pathfinding global, sin música/assets finales, sin navegación vertical. El núcleo trasero es angular, no una hitbox 3D. Se omite el terminal opcional de teoría para mantener cinco calibraciones. No se implementan Factory, niveles posteriores, El Toro ni emblemas 2/4–4/4. El reporte de estadías conserva su modelo y registros mínimos.

Falta jugar Workshop sin protección en Android/iPhone físicos para medir dificultad, duración 8–12 minutos, FPS, claridad de orientación y ergonomía del boss. Los controles tienen regresiones Chromium emuladas; Safari físico y sus barras/notch/haptics necesitan prueba real. No se ha publicado en una cuenta de Cloud/GitHub.

**Siguiente paso:** playtest físico de esta alpha, registrar tiempo, muertes, munición al entrar al Loader y preguntas utilizadas; ajustar datos de encuentros/recursos antes de añadir The Factory.
