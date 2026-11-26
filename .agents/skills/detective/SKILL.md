---
name: detective
description: Investigación sistemática de causa raíz para bugs de Influent Package Maker. Úsala cuando haya que reproducir un fallo, separar síntomas de causas, encontrar el punto exacto que lo provoca y verificar la corrección con evidencia.
---

# Detective

## Objetivo

Llegar a la causa raíz con evidencia, no con intuición. Un bug no está
entendido hasta que puedes explicar la cadena causal completa y demostrarla con
una prueba que falla antes del arreglo y pasa después.

## Método

1. **Define el síntoma.** Qué se esperaba, qué pasó, en qué plataforma y con
   qué versión. Si el reporte es vago, pide los datos mínimos: pasos, versión,
   SO, salida exacta y captura.
2. **Reproduce.** Busca el caso más pequeño que dispare el fallo. Guarda el
   comando exacto y la salida. Si no puedes reproducirlo, dilo y documenta qué
   falta; no inventes una causa.
3. **Recoge evidencia.** Stack trace, logs, `git log`, `git blame`,
   `git log -S '<cadena>'`, `git bisect`, pruebas existentes y las rutas de
   código que participan. Comprueba si el fallo apareció con un cambio reciente.
4. **Formula hipótesis.** Escríbelas antes de tocar código. Prueba una cada
   vez. Distingue correlación de causalidad: que algo cambie a la vez no
   significa que lo cause.
5. **Aísla la causa.** Reduce el caso, añade instrumentación temporal o
   compara una versión buena con una mala. Si hay varias causas, sepáralas.
6. **Escribe la prueba primero.** Una prueba que falle con el código actual y
   que describa el comportamiento correcto. Después aplica la corrección
   mínima.
7. **Verifica.** La prueba nueva pasa, la suite completa pasa y `pyflakes` /
   `py_compile` quedan limpios. Revisa efectos secundarios y casos límite.
8. **Documenta.** Deja el caso en `bugs.md` o en el issue con: síntoma,
   reproducción, evidencia, causa raíz, solución, pruebas y riesgo residual.

## Comandos útiles en este repositorio

```bash
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q
QT_QPA_PLATFORM=offscreen python -m pytest tests/test_x.py -q -k patron
python -m pyflakes $(git ls-files '*.py')
python -m py_compile $(git ls-files '*.py')
git log --oneline -20
git log -S 'texto que cambió' --oneline
git blame -L 100,160 lib/modulo.py
git bisect start && git bisect bad && git bisect good <sha>
python -X faulthandler -m modulo 2>&1 | tail -80
```

## Reglas

- No cambies código hasta poder explicar la causa.
- No tapes el síntoma: arregla la causa, no el mensaje de error.
- No des por buena una corrección sin una prueba que falle antes.
- Comprueba si el mismo patrón está en otros módulos.
- Si el fallo es intermitente, busca condiciones de carrera, orden de
  inicialización, estado global y diferencias de plataforma.
- Si te bloqueas, documenta las hipótesis descartadas y pide el dato que falta.
- Mantén la corrección pequeña y reversible; no mezcles refactors.

## Plantilla de caso

```
ID:
Síntoma:
Reproducción:
Evidencia:
Hipótesis probadas:
Causa raíz:
Solución:
Pruebas:
Riesgo residual:
```
