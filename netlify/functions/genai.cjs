// netlify/functions/genai.cjs
const { GoogleGenerativeAI } = require("@google/generative-ai");
const crypto = require("crypto");

function safeExtractBlocks(text){
  if(!text || typeof text !== "string") return { thinking:null, jsonText:null };
  const think = (text.match(/---THINKING---([\s\S]*?)---ENDTHINK---/i) || [])[1] || null;
  let jsonMatch = text.match(/```json([\s\S]*?)```/i) || text.match(/```([\s\S]*?)```/i);
  let jsonText = jsonMatch ? jsonMatch[1] : null;
  if(!jsonText){
    const first = text.indexOf("{"), last = text.lastIndexOf("}");
    if(first!==-1 && last!==-1 && last>first) jsonText = text.slice(first, last+1);
  }
  if(jsonText) jsonText = jsonText.replace(/\r\n/g,"\n").replace(/,\s*([\]}])/g,"$1");
  return { thinking: think ? think.trim() : null, jsonText };
}

function tryParse(t){
  if(!t) return null;
  try { return JSON.parse(t); } catch(e){}
  try {
    const safe = t.replace(/"([^"]*)\n([^"]*)"/g, (m,a,b)=> `"${a}\\n${b.replace(/\n/g,'\\n')}"`);
    return JSON.parse(safe);
  } catch(e) { return null; }
}

function ensureDefaults(parsed, folder, hv){
  parsed.files = parsed.files || [];
  const DEFAULT_FOLDERS = ["app","assets","config","docs","source","lib"];
  DEFAULT_FOLDERS.forEach(f=>{
    const p = `${folder}/${f}/.${f}-container`;
    if(!parsed.files.some(x => (x.path||"").toLowerCase() === p.toLowerCase())){
      parsed.files.push({ path: p, content: `#store (sha256 hash):${f}/.${hv}`});
    }
  });
  if(!parsed.files.some(x=>/license/i.test(x.path||""))){
    parsed.files.push({ path: `${folder}/LICENSE`, content: "GNU GENERAL PUBLIC LICENSE Version 3" });
  }
  return parsed;
}

exports.handler = async function(event){
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    const prompt = body.prompt || "";
    const mode = body.mode || "full";
    const incomingFiles = body.files || [];

    if(!prompt) return { statusCode:400, body: JSON.stringify({ error:"Missing prompt" }) };

    const apiKey = process.env.GEMINI_API_KEY;
    if(!apiKey) return { statusCode:500, body: JSON.stringify({ error:"Missing GEMINI_API_KEY" }) };

    const ai = new GoogleGenerativeAI(apiKey);
    const model = ai.getGenerativeModel({ model: "gemini-2.5-flash" });

    // Build an enforced prompt: THINKING block + strict JSON block requirement
    const system = `
Eres "Influent Package Maker", asistente experto en generar paquetes (Python). Sigue estas instrucciones al pie de la letra.

1) Primero genera una breve nota de "pensando" (1-2 oraciones) que explique en voz natural lo que vas a generar. Colócala SOLO entre los marcadores:
---THINKING---
tu texto aquí
---ENDTHINK---

2) Luego, genera EXCLUSIVAMENTE un bloque JSON válido y completo dentro de triple backticks \`\`\`json ... \`\`\`. No pongas texto fuera de la sección THINKING y del bloque JSON.

3) El JSON debe tener esta forma EXACTA:
{ "meta": { "fabricante","shortName","version","title","description" }, "files": [ { "path":"...", "content":"..." }, ... ] }

4) REGLAS importantes:
- Escapa saltos de línea con \\n dentro de los valores "content".
- Genera por lo menos: README.md, <shortName>.py, lib/requirements.txt, details.xml, autorun, autorun.bat, LICENSE.
- Añade contenedores en app/, assets/, config/, docs/, source/, lib/ (archivo .<name>-container con contenido "#store (sha256 hash):<name>/.<hash>").
- Si modo == "edit", edita y devuelve los archivos basados en incomingFiles.
- No agregues texto ni comentarios fuera del bloque THINKING y del bloque JSON.
- Asegúrate que el JSON sea estrictamente parseable.
`;

    const user = `USER_PROMPT: ${prompt}\nMODE: ${mode}\nEXISTING_FILES: ${JSON.stringify(incomingFiles).slice(0,4000)}`;

    const requestText = system + "\n\n" + user + "\n\nAhora devuelve la respuesta.";

    const response = await model.generateContent(requestText, { temperature: 0.65, maxOutputTokens: 2000 });
    const raw = (response && response.response && typeof response.response.text === "function") ? response.response.text() : JSON.stringify(response);

    const blocks = safeExtractBlocks(raw) || safeExtractBlocks(String(raw));
    let parsed = tryParse(blocks.jsonText) || null;
    // final fallback: attempt parsing entire raw
    if(!parsed) parsed = tryParse(raw);

    if(!parsed){
      // fallback minimal package
      parsed = {
        meta: { fabricante: "Default Manufacturer", shortName: "calculator", version: "1.0.0", title: "Calculadora Simple", description: "Fallback" },
        files: [
          { path: "calculator.py", content: "class Calculator:\\n    def add(self,a,b):\\n        return a+b\\n" },
          { path: "README.md", content: "# Calculadora Simple\\nGenerado (fallback)" },
          { path: "lib/requirements.txt", content: "# Ninguna dependencia" }
        ]
      };
    }

    // compute folder & hash and ensure defaults
    const empresa = (parsed.meta && (parsed.meta.fabricante || parsed.meta.manufacturer || "default")).toString().trim().toLowerCase().replace(/\s+/g,"-");
    const shortn = (parsed.meta && (parsed.meta.shortName || parsed.meta.short || "myapp")).toString().trim().toLowerCase();
    const versionVal = parsed.meta && parsed.meta.version ? parsed.meta.version : "1.0.0";
    const folder = `${empresa}.${shortn}.v${versionVal}`;
    const hv = crypto.createHash("sha256").update(`${empresa}.${shortn}.v${versionVal}`).digest("hex");

    parsed = ensureDefaults(parsed, folder, hv);

    // normalize paths
    parsed.files = parsed.files.map(f => ({ path: (f.path||"").replace(/^\.\//,"").replace(/^\/+/,""), content: (f.content||"") }));

    // Return both thinking (if present) and full parsed JSON in body as JSON (so frontend can read thinking quickly)
    return { statusCode:200, body: JSON.stringify({ thinking: blocks.thinking || null, parsed }) };

  } catch(err){
    console.error("genai error:", err);
    return { statusCode:500, body: JSON.stringify({ error: err.message || String(err) }) };
  }
};
