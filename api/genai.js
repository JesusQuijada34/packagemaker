import OpenAI from "openai";

const client = new OpenAI({ apiKey: process.env.GEMINI_API_KEY });

export default async function handler(req, res) {
  if(req.method !== "POST") return res.status(405).end("Method Not Allowed");

  const { prompt, mode, files } = req.body;

  // Prompts extendidos tipo enciclopedia
  let fullPrompt = "";
  if(mode === "full"){
    fullPrompt = `
Eres un asistente experto en generación de paquetes. Crea todos los archivos y carpetas, genera meta info (empresa, nombre, version, titulo) y colores coherentes. Devuelve **JSON válido** en bloque. Prompt usuario: ${prompt}
`;
  } else if(mode === "edit"){
    fullPrompt = `
Eres un editor experto de paquetes. Modifica los archivos existentes según la descripción de usuario, preservando headers y hashes. Devuelve JSON válido. Prompt: ${prompt}
`;
  } else { // suggest
    fullPrompt = `
Sugiere campos: empresa, nombre, version, titulo y paleta de colores a partir de: ${prompt}. Devuelve JSON válido.
`;
  }

  try{
    const g = await client.responses.create({
      model: "gemini-1",
      input: fullPrompt
    });
    const jsonText = g.output_text || "{}";
    res.status(200).json(JSON.parse(jsonText));
  } catch(e){
    res.status(500).json({error:e.message});
  }
}
