// netlify/functions/genai.cjs
const { GoogleGenerativeAI } = require("@google/generative-ai");
const crypto = require("crypto");

exports.handler = async function (event) {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    const { prompt, mode } = body;

    if (!prompt) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Missing prompt" }),
      };
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: "Missing GEMINI_API_KEY" }),
      };
    }

    // Inicializamos Gemini
    const ai = new GoogleGenerativeAI(apiKey);
    const model = ai.getGenerativeModel({ model: "gemini-2.5-flash" });

    // Prompt maestro para la IA
    const fullPrompt = `
Eres un generador experto de paquetes de software.
Recibe un prompt de usuario y devuelve SIEMPRE un bloque JSON con esta estructura:
{
  "meta": {
    "fabricante": "nombre de fabricante",
    "shortName": "nombre corto",
    "version": "versión",
    "title": "título",
    "description": "descripción"
  },
  "files": [
    {"path": "archivo", "content": "contenido"},
    ...
  ]
}

Crea al menos estos archivos predeterminados:
- README.md
- <shortName>.py
- lib/requirements.txt
- details.xml
- autorun.bat
- autorun (sh)
- LICENSE

Prompt del usuario:
${prompt}
Modo: ${mode || "full"}
`;

    const result = await model.generateContent(fullPrompt);
    const text = result.response.text();

    // Extraemos el JSON del bloque
    const match = text.match(/```json([\s\S]*?)```/);
    const jsonText = match ? match[1].trim() : text;
    let parsed = JSON.parse(jsonText);

    // Generar folder y hash de correlación
    const empresa = (parsed.meta.fabricante || "default").trim().toLowerCase().replace(/\s+/g, "-");
    const nombre = (parsed.meta.shortName || "myapp").trim().toLowerCase();
    const version = parsed.meta.version || "1.0.0";
    const folder = `${empresa}.${nombre}.v${version}`;
    const hv = crypto.createHash("sha256").update(`${empresa}.${nombre}.v${version}`).digest("hex");

    // Aseguramos carpetas predeterminadas
    const DEFAULT_FOLDERS = ["app","assets","config","docs","source","lib"];
    DEFAULT_FOLDERS.forEach(f => {
      parsed.files.push({
        path: `${folder}/${f}/.${f}-container`,
        content: `#store (sha256 hash):${f}/.${hv}`
      });
    });

    // LICENSE predeterminada si no existe
    const hasLicense = parsed.files.some(f => f.path.toLowerCase().includes("license"));
    if (!hasLicense) {
      parsed.files.push({
        path: `${folder}/LICENSE`,
        content: "GNU GENERAL PUBLIC LICENSE Version 3"
      });
    }

    return {
      statusCode: 200,
      body: JSON.stringify(parsed),
    };
  } catch (err) {
    console.error("❌ Error en genai:", err);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
