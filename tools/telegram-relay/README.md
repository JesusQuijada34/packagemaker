# Bot de soporte por Telegram

Flujo:

```
Telegram → Worker → comentario en el issue [telegram] chat <id>
        → automatización "Soporte Telegram — reportes"
        → respuesta por Telegram + comentarios en el issue
        → el bot de mantenimiento revisa la etiqueta needs-review
```

## Requisitos

- Cuenta gratuita de Cloudflare.
- Bot de Telegram creado con @BotFather (token).
- PAT fine-grained de GitHub con `Issues: Read and write` sobre el repositorio.

## Configuración

1. En Cloudflare, crea un Worker (Workers & Pages → Create → Worker) y pega
   `worker.js`.
2. Añade estos secretos al Worker:
   - `GITHUB_TOKEN`: el PAT fine-grained.
   - `TELEGRAM_WEBHOOK_SECRET`: una cadena aleatoria larga.
3. Anota la URL pública del Worker (`https://<nombre>.<subdominio>.workers.dev`).
4. Registra el webhook de Telegram:

   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<WORKER_URL>&secret_token=<TELEGRAM_WEBHOOK_SECRET>&allowed_updates=%5B%22message%22%5D"
   ```

5. En OpenHands, añade los secretos:
   - `TELEGRAM_BOT_TOKEN`: el token del bot (lo usa el agente para responder).
   - `TELEGRAM_OWNER_CHAT_ID`: tu `chat_id`. El bot te lo dice en el primer
     mensaje; solo ese chat puede autorizar un push.
6. Escribe al bot. El Worker crea el issue `[telegram] chat <id>` y comenta el
   mensaje; la automatización responde por Telegram y deja el rastro en el issue.

## Notas

- El Worker no necesita el token del bot: solo el PAT y el secreto del webhook.
- El marcador `<!-- telegram-relay -->` es lo que dispara la automatización. No
  lo incluyas en otros comentarios.
- `.github/workflows/telegram-relay.yml` es un plan B si algún día habilitas
  GitHub Actions. Ahora mismo Actions está deshabilitado o con runs en cola en
  este repositorio, así que el Worker es el camino recomendado.
