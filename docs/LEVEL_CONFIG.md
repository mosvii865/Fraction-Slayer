# Contrato de niveles — v0.2-alpha1

`game/nivel.py` registra niveles en `LEVELS`. Cada entrada es un diccionario o una función sin argumentos que devuelve un diccionario. `level_config(difficulty, level_id)` devuelve una copia independiente, resuelve el encuentro de la dificultad y deriva `width`/`height` del grid. `industrial_test` es el único nivel jugable incluido. Los niveles artificiales de `tests/test_engine_levels.py` son fixtures, no contenido nuevo.

## Datos del nivel

| Campo | Contrato |
|---|---|
| `id`, `revision`, `name` | Identidad estable, revisión de compatibilidad y nombre visible |
| `grid` | Matriz rectangular: 0 suelo, 1 muro, 2 pilar, 3 puerta; cada puerta tiene una celda registrada |
| `enemy_types` | Catálogo por tipo: `hp`, `speed`, `range`, `color`, `name`; extensiones `radius`, `vision`, `search_seconds`, `rear_multiplier`, `rear_angle`, `charge_speed`, `stun_seconds` |
| `encounters` | Listas explícitas por `clasico` y `doom`; no se recorta una lista común por cantidad |
| `items` | Pickups con `id`, `type`, `x`, `y`, `amount` y datos específicos del tipo |
| `stations` | Entidades independientes con contrato descrito abajo |
| `doors` | `id`, `cell: [x, y]`; la celda debe ser 3 |
| `checkpoints` | `id`, `order`, `zone: [x1,y1,x2,y2]`, `prerequisites`, `respawn_position: {x,y}`, `respawn_angle` |
| `objectives` | `id`, `condition` opcional; sin condición se activa mediante recompensa/evento |
| `triggers` | `id`, `condition`, `actions`; cada trigger se ejecuta una sola vez por partida/checkpoint |
| `waves` | `id`, `groups`, `rewards` opcional; `ensure_ammo` garantiza un piso antes de activarse |
| `secrets` | `id`, `kind`; logos: `kind: utcj`, `on_shot: True`, `x`, `y` |
| `exit` | `station`, `condition`; no existe una regla global de matar a todos |
| `player_config` | `max_hp`, `max_armor` |
| `respawn_rules` | `min_hp`, `grace` en segundos, `ammo` como mínimos totales por arma |

Los IDs son únicos **dentro de cada colección** y se guardan en mapas separados. Al cambiar entidades, grid o reglas incompatibles de un nivel publicado, incrementa su `revision`. Un save no se migra silenciosamente a otro nivel/revisión.

## Estaciones y preguntas

Ejemplo de datos para una futura puerta; no registra ni construye The Workshop:

```python
{
    "id": "tool_storage_terminal",
    "kind": "door",                    # terminal / door / mad / cache / exit
    "x": 8.5, "y": 2.5,              # posición visual; puede estar empotrada
    "interaction_point": {"x": 7.5, "y": 3.5},  # suelo accesible
    "interaction_distance": 1.9,
    "label": "TOOL STORAGE",
    "door_id": "power_door",
    "prerequisites": {"objective": "fuse_collected"},
    "allow_in_combat": False,
    "question": {
        "categories_allowed": ["to_decimal"],
        "denominators_allowed": [2, 4, 8],
        "multiple_choice_allowed": True,
        "manual_allowed": False,
        "difficulty_override": "clasico",
        # Alternativa opcional: fixed_question
    },
    "reward": [{"type": "door", "id": "power_door"}],
}
```

Pregunta fija opcional dentro de `question`:

```python
"fixed_question": {
    "prompt": "Convierte 1/2″ a decimal.",
    "answer": "0.5", "category": "to_decimal",
    "mode": "choice", "choices": ["0.5", "0.25", "0.75", "0.125"],
    "explanation": "1 ÷ 2 = 0.5",
    "expected_format": "decimal",
}
```

Las respuestas fijas y generadas permanecen en Python. El frontend recibe la pregunta pública, no `fixed_question`. Categorías: `to_decimal`, `to_fraction`, `equivalence`, `simplify`, `theory`, `special`. Formatos: `decimal`, `fraction`, `integer`, `text`. Las fracciones deben estar reducidas por defecto (`require_reduced`). La equivalencia generada pide decimal; una fija puede declarar el formato esperado. Teoría usa opción múltiple: todavía no existe teclado alfanumérico táctil.

Si se limita un pool a `[2,4,8]`, ni los enunciados fraccionales ni los distractores numéricos introducen pasos de 1/16. `industrial_test` conserva su progresión matemática hasta MOD II. El futuro Workshop debe declarar explícitamente `[2,4,8]` en sus estaciones normales.

## Condiciones y acciones

Una condición vacía `{}` es verdadera. Se combinan con `all` y `any`:

```python
{"all": [{"objective": "power_restored"}, {"objective": "loader_defeated"}]}
```

Predicados: `objective`, `door_open`, `station_used`, `trigger`, `wave`, `secret`, `item`, `group_defeated`, `zone`, `event`. Los primeros consultan progreso por ID; `item` consulta quest/key inventory; `group_defeated` exige un grupo existente con todos sus integrantes muertos (un grupo dormido no cuenta como derrotado). `event` compara un evento exacto: al resolver una estación se emite `station:<id>`. La API Python `advance(state, level, event=...)` permite futuros eventos adicionales.

Una oleada:

```python
"waves": [{
    "id": "loader_encounter", "groups": ["loader_group"],
    "rewards": [{"type": "ensure_ammo", "minimum": {"pistol": 24, "shotgun": 8}}],
}],
"triggers": [{
    "id": "wake_loader", "condition": {"objective": "fuse_installed"},
    "actions": [{"type": "activate_wave", "id": "loader_encounter"}],
}]
```

`activate_group` activa un grupo directamente. Otras acciones utilizan el mismo dispatch transaccional de recompensas. Antes de publicar encuentros grandes obligatorios, declara una fuente mínima garantizada (`ensure_ammo` de la oleada o recurso previo accesible) y verifica alcanzabilidad. No hay un encuentro Loader implementado en esta alpha.

Recompensas: los tipos de pickup, `upgrade` (`mod: 1` disponible), `door`, `objective`, `secret`, `consume_item` (`item_id`, `bag`, `amount`) y `ensure_ammo`. Toda la lista se aplica a una copia; solo se confirma si todas las operaciones y la validación final son válidas. Un error conserva pregunta, acierto pendiente, estación e inventario. El dron solo muestra armas que todavía admiten MOD I.

## Pickups

Dispatch explícito:

| `type` | Datos adicionales |
|---|---|
| `ammo` | `weapon`, `amount` |
| `health`, `armor` | `amount` |
| `weapon` | `weapon` |
| `quest_item` | `item_id`, por ejemplo `main_power_fuse` |
| `key_item` | `item_id` |
| `secret_item` | `secret_id` registrado |

Los pickups de quest/key se confirman en Python; la recogida visual no bloquea el frame. Un tipo desconocido no se marca recogido ni se convierte en munición. No introduce una excepción que rompa la animación.

## Estado, sincronización y seguridad

`progress` contiene mapas `stations`, `doors`, `objectives`, `triggers`, `waves`, `secrets`, además de `utcj_found` y `complete`. `inventory` separa `quest_items` y `key_items`. Los logos son secretos, nunca enemigos ni kills. El resumen incluye `utcj_display: "???"` hasta encontrar uno.

Python resuelve progreso, oleadas, checkpoints y recompensas. El cliente aporta movimiento/combate y no puede sobrescribir progreso educativo, mejoras ni activar enemigos por snapshot. La respuesta de un sync en marcha se fusiona mediante deltas de recursos y campos autoritativos: no rebobina la posición mientras el jugador camina.

Checkpoint: comprueba zona, orden, prerrequisitos y seguridad tanto en el jugador como en el respawn. Rechaza enemigos activos a menos de 2 unidades, o con LOS dentro de 6 unidades / alcance hostil inmediato si es mayor. El cliente reintenta como máximo cada 3 segundos. Reiniciar coloca al jugador en el respawn configurado, con piso de HP/munición y gracia; guardar/sincronizar normalmente no cura.

Terminal normal: rechaza enemigos vivos activos visibles a menos de 6 unidades, distancia a la que el enemigo adquiere persecución. Dormidos, enemigos detrás de paredes o fuera del radio no bloquean. `allow_in_combat` permite la excepción futura de The Converter.

IA: persigue, busca última posición conocida, intenta desplazamiento lateral si está bloqueada y abandona al expirar la búsqueda. Los datos permiten radio, orientación, carga, detección `charge_blocked`, aturdimiento y multiplicador angular trasero. La lógica de cuándo iniciar una carga y el combate completo de Loader quedan pendientes. No hay navegación global ni pathfinding garantizado.

## Validar un nivel futuro

1. IDs, colecciones y referencias coherentes; posiciones dentro del grid.
2. Recorrido con todas las puertas cerradas y acceso al punto de interacción de cada puerta usando solo gates anteriores.
3. Checkpoints con respawn en suelo abierto, prerrequisitos y lugares seguros.
4. Encuentros explícitos por dificultad, dormidos/grupos/oleadas y fuente mínima de munición.
5. Pool matemático de cada estación y recompensas válidas con el inventario posible.
6. Salida con objetivos explícitos. Para Workshop: `power_restored` **y** `loader_defeated`.
7. Pruebas de guardar/cargar en cada etapa, muerte y recuperación de sesión.

Los tests artificiales cubren contratos, no sustituyen la validación del layout real ni su balance. No se incluye un editor ni un validador exhaustivo de esquemas de contenido.
