# Controlar PackageMaker sin abrir el navegador

Tres herramientas de terminal. Ninguna abre ventana ni carga la interfaz web.

## 1. Ver si hubo push a `main`

```bash
python scripts/watch_main.py --once          # una consulta
python scripts/watch_main.py                 # vigilando, cada 60 s
python scripts/watch_main.py --items         # añade issues y PRs abiertos
```

Avisa cuando aparece un commit nuevo o cuando cambia el estado del CI. Cada
consulta son unos pocos KB contra la API de GitHub, así que puedes dejarlo
corriendo horas sin que el PC se resienta.

## 2. Hablar con OpenHands

```bash
export OH_CONVERSATION_ID=<id>            # opcional si sólo hay una abierta

python scripts/oh_chat.py status          # estado del sandbox y del agente
python scripts/oh_chat.py read --last 5   # últimas respuestas
python scripts/oh_chat.py say "continua con la fase 2.3"
python scripts/oh_chat.py say "revisa los tests" --wait 30
python scripts/oh_chat.py new "revisa la cola de bugs.md" --repo JesusQuijada34/packagemaker
```

Necesita `OPENHANDS_API_KEY` en el entorno. La clave de sesión del sandbox la
pide el script a la API y nunca se imprime.

## 3. Reaccionar solo a los pushes

```bash
python scripts/watch_and_act.py                                  # sólo avisar
python scripts/watch_and_act.py --run-tests                      # valida cada push
python scripts/watch_and_act.py --ask "continua con bugs.md"     # delega el trabajo
```

Cada commit dispara las acciones una sola vez; el SHA se guarda en
`.openhands/watch_and_act.json`, así que reiniciar el script no repite trabajo.

## Dejarlo en segundo plano

```bash
nohup python scripts/watch_and_act.py --run-tests > watch.log 2>&1 &
tail -f watch.log
```

Para Windows, el equivalente en PowerShell:

```powershell
Start-Process python -ArgumentList "scripts/watch_and_act.py","--run-tests" -RedirectStandardOutput watch.log
Get-Content watch.log -Wait
```

## Tests

```bash
QT_QPA_PLATFORM=offscreen python -m pytest tests/test_watch_main.py tests/test_oh_chat.py tests/test_watch_and_act.py -q
```
