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