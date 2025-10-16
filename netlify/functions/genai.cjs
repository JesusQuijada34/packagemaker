// netlify/functions/genai.cjs
const { GoogleGenerativeAI } = require("@google/generative-ai");

exports.handler = async function (event) {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    const { prompt } = body;

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

    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });

    const fullPrompt = `
Eres un generador experto de paquetes de software.
Debes devolver SIEMPRE un bloque JSON con esta estructura:
{
  "meta": { "fabricante", "shortName", "version", "title", "description" },
  "files": [{ "path": "...", "content": "..." }]
}
Prompt del usuario:
${prompt}
`;

    const result = await model.generateContent(fullPrompt);
    const text = result.response.text();

    const match = text.match(/```json([\s\S]*?)```/);
    const jsonText = match ? match[1].trim() : text;
    const parsed = JSON.parse(jsonText);

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
