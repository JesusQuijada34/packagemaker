// netlify/functions/genai.js
import { GoogleGenerativeAI } from "@google/generative-ai";

export default async (req, res) => {
  try {
    // Netlify no parsea automáticamente el body
    const body = req.body ? JSON.parse(req.body) : {};
    const { prompt } = body;

    if (!prompt) {
      return res.status(400).json({ error: "Missing prompt" });
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: "Missing GEMINI_API_KEY" });
    }

    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });

    const fullPrompt = `
Eres un generador avanzado de paquetes de software ("Influent Package Maker").
Debes generar SIEMPRE un bloque de código JSON que contenga:
{
  "meta": { "fabricante", "shortName", "version", "title", "description", "colors" },
  "files": [ { "path": "...", "content": "..." } ]
}
Prompt del usuario:
${prompt}
`;

    const result = await model.generateContent(fullPrompt);
    const text = result.response.text();

    const match = text.match(/```json([\s\S]*?)```/);
    const jsonText = match ? match[1].trim() : text;
    const parsed = JSON.parse(jsonText);

    return res.status(200).json(parsed);
  } catch (error) {
    console.error("Error en función genai:", error);
    return res.status(500).json({ error: error.message || "AI backend error" });
  }
};
