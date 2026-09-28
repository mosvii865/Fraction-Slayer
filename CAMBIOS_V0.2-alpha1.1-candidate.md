# Fraction Slayer v0.2-alpha1.1-candidate

Build candidata creada a partir del ZIP oficial `v0.2-alpha1` para que Work pueda validar el hotfix descrito por Claude/Gemini sin reconstruir una rama paralela.

## Cambios

- `ui/frontend/realtime.js`: protege la selección del siguiente checkpoint cuando `find(...)` no devuelve coincidencia, usando `current?.order ?? -1`.
- `tests/test_engine_levels.py`: añade una regresión mínima que documenta el estado previo al primer checkpoint y comprueba que el guard exista en el frontend.
- `ui/frontend/index.html`: identifica esta copia como `v0.2-alpha1.1-candidate`.

## Importante

Esta build **no está declarada estable**. En el ZIP original `GameEngine` inicia una nueva partida con el primer checkpoint (`cp["id"]`), por lo que el hotfix de checkpoint nulo debe ser validado por Work contra Streamlit real y no debe asumirse como causa definitiva del `ERROR DE MOTOR`.
