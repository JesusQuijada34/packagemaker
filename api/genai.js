import { GoogleGenAI } from "@google/genai";

// Inicializa el cliente Gemini con la API key desde Vercel
const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY
});

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end("Method Not Allowed");

  const { prompt, mode, files } = req.body;

  // Construir prompts enciclopédicos según el modo
  let fullPrompt = "";

  if (mode === "full") {
    fullPrompt = `
Eres un asistente experto en generación de paquetes de software. 
Tu objetivo es generar proyectos completos listos para descargar en ZIP.
Incluso si el prompt del usuario es vago o confuso, debes inferir todos los detalles.
Debes generar:
- Carpetas: app, assets, config, docs, source, lib
- Archivos obligatorios: README.md, main.py, lib/requirements.txt, details.xml, autorun, LICENSE
- Meta: empresa, short name, versión, título completo, colores coherentes (primario, secundario, fondo)
- Headers en archivos, README con pasos básicos, main.py funcional, autorun para Linux/Windows
- Mantener buenas prácticas y consistencia

Responde **siempre en JSON válido** dentro de un bloque de código.
Prompt usuario: ${prompt}
`;
  } else if (mode === "edit") {
    fullPrompt = `
Eres un editor experto de paquetes de software. Modifica archivos existentes según el prompt del usuario.
Debes:
- Mantener la estructura de carpetas
- Preservar headers, hashes y licencias
- Ajustar colores, títulos, versiones si el prompt lo indica
- Mantener coherencia y buenas prácticas
- Responder en JSON válido dentro de un bloque de código
Prompt del usuario: ${prompt}
Archivos actuales: ${JSON.stringify(files)}
`;
  } else { // suggest
    fullPrompt = `
Sugiere campos: empresa, short name, versión, título completo y paleta de colores coherente a partir de:
${prompt}
Aunque el prompt sea confuso, genera resultados coherentes y claros.
Responde siempre en JSON válido dentro de un bloque de código.
`;
  }

  try {
    // Llamada a Gemini usando @google/genai
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: fullPrompt,
      temperature: 0.7,
      maxOutputTokens: 2000
    });

    // La respuesta se encuentra en response.text
    const jsonText = response?.text || "{}";

    res.status(200).json(JSON.parse(jsonText));
  } catch (e) {
    console.error("Error Gemini:", e);
    res.status(500).json({ error: e.message });
  }
}
