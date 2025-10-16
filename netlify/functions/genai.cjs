const { GoogleGenerativeAI } = require("@google/generative-ai");
const crypto = require("crypto");

function cleanJSON(text) {
  try {
    const match = text.match(/```json([\s\S]*?)```/);
    let jsonText = match ? match[1].trim() : text;
    jsonText = jsonText.replace(/\\n/g, "\\n").replace(/\r/g, "");
    return JSON.parse(jsonText);
  } catch {
    return null;
  }
}

exports.handler = async function(event) {
  try {
    const { prompt, mode } = JSON.parse(event.body);
    const apiKey = process.env.GEMINI_API_KEY;
    const ai = new GoogleGenerativeAI(apiKey);
    const model = ai.getGenerativeModel({ model: "gemini-2.5-flash" });

    const systemPrompt = `
Eres un generador experto de paquetes de software.
Tu salida DEBE ser estrictamente un bloque JSON en formato correcto, como este:
${prompt}

Incluye archivos predeterminados (README.md, LICENSE, autorun, autorun.bat, details.xml, lib/requirements.txt)
Usa nombres coherentes y genera contenido válido.
`;

    const result = await model.generateContent(systemPrompt);
    let parsed = cleanJSON(result.response.text());
    if (!parsed) {
      parsed = { meta: { title: "Error", description: "Respuesta inválida" }, files: [] };
    }

    const empresa = parsed.meta.fabricante?.toLowerCase().replace(/\s+/g, "-") || "default";
    const nombre = parsed.meta.shortName?.toLowerCase() || "app";
    const version = parsed.meta.version || "1.0.0";
    const hv = crypto.createHash("sha256").update(`${empresa}.${nombre}.v${version}`).digest("hex");

    const folders = ["app","assets","config","docs","source","lib"];
    folders.forEach(f => {
      parsed.files.push({
        path: `${empresa}.${nombre}.v${version}/${f}/.${f}-container`,
        content: `#store (sha256 hash):${f}/.${hv}`
      });
    });

    return { statusCode: 200, body: JSON.stringify(parsed) };
  } catch (e) {
    return { statusCode: 500, body: JSON.stringify({ error: e.message }) };
  }
};
