// Cloudflare Worker: recibe los updates de Telegram y los publica como
// comentarios en un issue de GitHub por chat. El issue es la conversación
// que atiende la automatización "Soporte Telegram — reportes".
//
// Secretos del Worker:
//   GITHUB_TOKEN             PAT fine-grained con Issues: Read and write
//   TELEGRAM_WEBHOOK_SECRET  el mismo secret_token de setWebhook

const REPO = "JesusQuijada34/packagemaker";
const LABEL = "telegram";
const MARKER = "<!-- telegram-relay -->";

const headers = (env) => ({
  Authorization: `Bearer ${env.GITHUB_TOKEN}`,
  Accept: "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
  "User-Agent": "packagemaker-telegram-relay",
  "Content-Type": "application/json",
});

const repoApi = (path) => `https://api.github.com/repos/${REPO}${path}`;

async function ensureLabel(env) {
  await fetch(repoApi("/labels"), {
    method: "POST",
    headers: headers(env),
    body: JSON.stringify({ name: LABEL, color: "1d76db", description: "Reportes de Telegram" }),
  });
}

async function findIssue(env, title, chatId) {
  const q = encodeURIComponent(`repo:${REPO} label:${LABEL} in:title "chat ${chatId}"`);
  const res = await fetch(`https://api.github.com/search/issues?q=${q}&per_page=20`, {
    headers: headers(env),
  });
  if (!res.ok) return null;
  const data = await res.json();
  return (data.items || []).find((item) => item.title === title) || null;
}

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("ok", { status: 200 });
    }
    const secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
    if (!env.TELEGRAM_WEBHOOK_SECRET || secret !== env.TELEGRAM_WEBHOOK_SECRET) {
      return new Response("forbidden", { status: 403 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("bad json", { status: 400 });
    }

    const msg = update.message;
    if (!msg || !msg.text || (msg.from && msg.from.is_bot)) {
      return new Response("ignored", { status: 200 });
    }

    const chatId = msg.chat.id;
    const title = `[telegram] chat ${chatId}`;
    const who =
      [msg.from?.first_name, msg.from?.last_name].filter(Boolean).join(" ") ||
      msg.from?.username ||
      "usuario";
    const username = msg.from?.username ? ` (@${msg.from.username})` : "";

    try {
      await ensureLabel(env);

      let issue = await findIssue(env, title, chatId);
      if (!issue) {
        const created = await fetch(repoApi("/issues"), {
          method: "POST",
          headers: headers(env),
          body: JSON.stringify({
            title,
            body: `Reportes de Telegram para el chat \`${chatId}\`.\n\nEste issue es la conversación del bot y la bandeja de revisión.`,
            labels: [LABEL],
          }),
        });
        if (!created.ok) {
          return new Response(`issue create failed: ${await created.text()}`, { status: 502 });
        }
        issue = await created.json();
      }

      const body =
        `**Telegram** · chat_id: \`${chatId}\` · ${who}${username} · ${msg.date || ""}\n\n` +
        `${msg.text}\n\n${MARKER}`;
      const commented = await fetch(repoApi(`/issues/${issue.number}/comments`), {
        method: "POST",
        headers: headers(env),
        body: JSON.stringify({ body }),
      });
      if (!commented.ok) {
        return new Response(`comment failed: ${await commented.text()}`, { status: 502 });
      }
      return new Response("ok", { status: 200 });
    } catch (error) {
      return new Response(`relay error: ${error}`, { status: 502 });
    }
  },
};
