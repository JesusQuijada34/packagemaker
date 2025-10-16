const { GoogleGenerativeAI } = require("@google/generative-ai");
const mime = require("mime");
const fetch = require("node-fetch");

exports.handler = async (event) => {
  try {
    const { prompt, mode } = JSON.parse(event.body || "{}");

    if (!process.env.GEMINI_API_KEY) {
      return { statusCode: 401, body: JSON.stringify({ error: "No API Key" }) };
    }

    const ai = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = ai.getGenerativeModel({ model: "gemini-2.5-flash" });

    // PROMPT DOCTRINAL (para respuestas coherentes y limpias)
    const doctrinePrompt = `
Eres un generador de paquetes Python estructurados.

Tu misión:
- Analiza la descripción del usuario y genera un proyecto Python funcional y ordenado.
- Devuelve SOLO un JSON válido (sin texto fuera de bloques).
- Los campos deben ser:
{
  "meta": {
    "fabricante": "nombre de la empresa o desarrollador",
    "shortName": "nombre_corto",
    "version": "1.0.0",
    "title": "Título descriptivo",
    "description": "Breve explicación"
  },
  "files": [
    {"path": "{shortName}.py", "content": "código Python"},
    {"path": "README.md", "content": "documentación Markdown"},
    {"path": "lib/requirements.txt", "content": "dependencias"}
  ]
}

- Si el usuario no da muchos detalles, genera un ejemplo simple y legible.
- No uses explicaciones adicionales ni comentarios fuera del JSON.
`;

    const fullPrompt = `${doctrinePrompt}\n\nDescripción del usuario:\n${prompt}`;

    const response = await model.generateContent(fullPrompt);
    const text = response.response.text();

    // Limpieza y parseo seguro del JSON
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("Respuesta sin JSON válido");

    const parsed = JSON.parse(jsonMatch[0]);

    // Generar logotipo con modelo de imagen
    const imageModel = ai.getGenerativeModel({ model: "gemini-2.5-flash-image" });
    const imageResponse = await imageModel.generateContent([
      {
        role: "user",
        parts: [{ text: `Crea un logotipo para una app llamada "${parsed.meta.title}" con el estilo moderno, profesional, minimalista.` }],
      },
    ]);

    let logoBase64 = "";
    const inlineData = imageResponse.response.candidates?.[0]?.content?.parts?.[0]?.inlineData;
    if (inlineData?.data) {
      logoBase64 = inlineData.data;
      parsed.files.push({
        path: "assets/product_logo.png",
        content: logoBase64,
        isBinary: true,
      });
    }

    return {
      statusCode: 200,
      body: JSON.stringify(parsed),
    };
  } catch (err) {
    console.error("Error IA:", err);
    return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
  }
};
