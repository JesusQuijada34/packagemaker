// api/genai.js
import fetch from "node-fetch";

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "Método no permitido" });

  const { prompt, mode, files } = req.body;

  try {
    // Llamada a la API de Gemini
    const response = await fetch("https://api.gemini.com/v1/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${process.env.GEMINI_API_KEY}`
      },
      body: JSON.stringify({
        prompt,
        mode,
        files
      })
    });

    const data = await response.json();

    // Transformar respuesta de Gemini a formato de tu frontend
    const generatedFiles = [
      {
        path: "{folder}/README.md",
        content: `# Proyecto generado\nPrompt: ${prompt}\nRespuesta Gemini:\n${data.output || "..." }`
      },
      {
        path: "{folder}/main.py",
        content: `#!/usr/bin/env python\nprint("Hola desde la app generada por Gemini")`
      }
    ];

    const meta = {
      empresa: "influent",
      nombre: "demo",
      version: "1.0",
      titulo: "Demo App",
      colores: { primario: "#0366d6", secundario: "#2ea44f", fondo: "#f4f6f8" }
    };

    res.status(200).json({ meta, files: generatedFiles });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error llamando a la API Gemini" });
  }
}
