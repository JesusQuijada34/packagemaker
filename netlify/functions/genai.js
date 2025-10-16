// netlify/functions/genai.js
import { GoogleGenerativeAI } from "@google/generative-ai";

export default async function handler(req, res) {
  try {
    if (req.method !== "POST") {
      return res.status(405).json({ error: "Method not allowed" });
    }

    const { prompt, mode } = req.body || {};
    if (!prompt) {
      return res.status(400).json({ error: "Missing prompt" });
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: "Missing GEMINI_API_KEY" });
    }

    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });

    // Prompt extendido y explicativo
    const fullPrompt = `
Eres un sistema experto en ingeniería de software llamado "Influent Package Maker".
Tu función es crear proyectos completos (paquetes) basados en descripciones humanas.
Debes:
1. Interpretar y mejorar la idea del usuario aunque el prompt sea incompleto.
2. Retornar SIEMPRE un bloque de código con JSON que contenga:
   {
     "meta": { "fabricante", "shortName", "version", "title", "description", "colors" },
     "files": [ { "path": "ruta/del/archivo", "content": "contenido" } ]
   }
3. El campo "description" debe ser generado creativamente, técnica y comercialmente.
4. Puedes sugerir colores, interfaces y estructura de carpetas.
5. Si el usuario no da datos, inventa valores realistas.
6. Tu salida siempre debe incluir el JSON dentro de triple backticks.

Prompt del usuario:
${prompt}

Modo: ${mode}
`;

    const result = await model.generateContent(fullPrompt);
    const text = result.response.text();

    const match = text.match(/```json([\s\S]*?)```/);
    const jsonText = match ? match[1].trim() : text;
    const parsed = JSON.parse(jsonText);

    res.status(200).json(parsed);
  } catch (error) {
    console.error("Error en genai.js:", error);
    res.status(500).json({ error: error.message || "AI backend error" });
  }
}
