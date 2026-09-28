# Visual Pass 2 — Retro FPS Presentation

## Objetivo

Mejorar la presentación visual de Fraction Slayer v0.3-alpha2 hacia un lenguaje de retro-FPS de los 90, inspirado en la lectura visual de la época sin copiar assets ni interfaces de DOOM.

## Cambios seguros

- Corregido el anclaje vertical de sprites: ahora la base se proyecta sobre la línea de suelo en lugar de centrar el sprite en `H/2`.
- Corregido el muestreo de sprites para respetar `naturalWidth` y `naturalHeight`, evitando asumir 48x64 para assets como los carteles 64x32.
- Añadido un plano de suelo en perspectiva de bajo costo con bloques pixelados y sombreado por distancia.
- Añadidas líneas/accentos discretos de panel, suciedad y moldura para dar más volumen a las paredes.
- Ajustado el fondo del mundo hacia una paleta más oscura y cálida de retro-FPS industrial.
- Actualizado el tratamiento visual de HUD, topbar, botones, overlay y scanlines hacia una estética industrial/90s más contundente.
- Conservado Canvas 2D, raycaster, z-buffer, assets existentes, fallback procedural, controles y lógica de juego.

## No modificado

- Combate
- Matemáticas
- IA
- Colisiones
- Progresión
- Save system
- Niveles
- Touch hit areas
- APIs del motor

## Validación

- `node --check ui/frontend/renderer.js` — OK
- `PYTHONPATH=. pytest -q tests/test_visuals.py` — 4 passed

La validación de navegador/Streamlit no pudo ejecutarse en este entorno porque Streamlit no está instalado.
