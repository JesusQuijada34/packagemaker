// netlify/functions/genai.cjs
const { GoogleGenerativeAI } = require("@google/generative-ai");
const crypto = require("crypto");

function safeExtractJSON(text){
  // try several heuristics to extract JSON block
  if(!text || typeof text !== "string") return null;
  let candidate = null;
  const m1 = /```json([\s\S]*?)```/i.exec(text);
  if(m1) candidate = m1[1];
  else {
    const m2 = /```([\s\S]*?)```/.exec(text);
    if(m2) candidate = m2[1];
    else {
      const first = text.indexOf('{'), last = text.lastIndexOf('}');
      if(first !== -1 && last !== -1 && last>first) candidate = text.slice(first, last+1);
    }
  }
  if(!candidate) return null;

  // cleaning heuristics
  // remove leading/trailing non-json
  candidate = candidate.trim();
  // replace windows CRLF
  candidate = candidate.replace(/\r\n/g, "\n");
  // remove trailing commas before } or ]
  candidate = candidate.replace(/,\s*([\]}])/g, "$1");

  // Try parse directly
  try { return JSON.parse(candidate); }
  catch(e){
    // escape newlines inside double quotes (best-effort)
    try {
      let t = candidate.replace(/\\n/g, "\\n"); // normalize
      // replace unescaped newlines inside quotes -> \n
      t = t.replace(/"([^"]*)\n([^"]*)"/g, (m,a,b)=> `"${a}\\n${b.replace(/\n/g,'\\n')}"`);
      t = t.replace(/\t/g, "\\t");
      // last resort: remove control chars
      t = t.replace(/[\x00-\x1F]+/g, " ");
      return JSON.parse(t);
    } catch(err2){
      console.warn("safeExtractJSON failed parse", err2);
      return null;
    }
  }
}

// Add default containers and LICENSE if missing
function ensureDefaultFiles(parsed, folder, hv){
  const DEFAULT_FOLDERS = ["app","assets","config","docs","source","lib"];
  parsed.files = parsed.files || [];
  // ensure container files (use folder prefixed paths)
  DEFAULT_FOLDERS.forEach(f=>{
    const p = `${folder}/${f}/.${f}-container`;
    if(!parsed.files.some(x => (x.path||"").toLowerCase() === p.toLowerCase())){
      parsed.files.push({ path: p, content: `#store (sha256 hash):${f}/.${hv}` });
    }
  });
  // ensure license
  if(!parsed.files.some(x => /license/i.test(x.path||""))){
    parsed.files.push({ path: `${folder}/LICENSE`, content: "GNU GENERAL PUBLIC LICENSE Version 3" });
  }
  return parsed;
}

exports.handler = async function(event){
  try{
    const body = event.body ? JSON.parse(event.body) : {};
    const prompt = body.prompt || "";
    const mode = body.mode || "full";
    const incomingFiles = body.files || [];

    if(!prompt) return { statusCode:400, body: JSON.stringify({ error:"Missing prompt" }) };

    const apiKey = process.env.GEMINI_API_KEY;
    if(!apiKey) return { statusCode:500, body: JSON.stringify({ error:"Missing GEMINI_API_KEY" }) };

    const ai = new GoogleGenerativeAI(apiKey);
    const model = ai.getGenerativeModel({ model: "gemini-2.5-flash" });

    // Build extended prompt (doctrina + examples)
    let system = `
Eres "Influent Package Maker", asistente experto en generar paquetes de software en Python.
Tu tarea: a partir de una descripción humana (prompt) devolver SIEMPRE un bloque JSON válido (dentro de triple backticks o no) con la estructura:
{
 "meta": { "fabricante","shortName","version","title","description" },
 "files": [ {"path":"...","content":"..."} ]
}
Debes generar al menos: README.md, <shortName>.py, lib/requirements.txt, details.xml, autorun, autorun.bat, LICENSE.
Si el prompt es confuso, inferir valores razonables. Evita comentarios adicionales fuera del bloque JSON.
Incluye ejemplos claros en README y headers en los archivos principales.
`;

    // user content includes prompt and optionally files for edit mode
    let userContent = `PROMPT USER: ${prompt}\nMODE: ${mode}`;
    if(mode === "edit" && Array.isArray(incomingFiles) && incomingFiles.length){
      userContent += `\nEXISTING_FILES: ${JSON.stringify(incomingFiles).slice(0,5000)}`; // truncated
    }

    const requestText = system + "\n\n" + userContent + "\n\nReturn JSON now.";

    // call model
    const response = await model.generateContent(requestText, { temperature: 0.7, maxOutputTokens: 2000 }).catch(err=>{
      throw err;
    });

    const rawText = (response && response.response && typeof response.response.text === "function")
      ? response.response.text()
      : (response.output || response.text || "");

    // Extract JSON robustly
    let parsed = safeExtractJSON(rawText);

    if(!parsed){
      // if extraction failed, create a safe default
      parsed = {
        meta: {
          fabricante: "Default Manufacturer",
          shortName: "calculator",
          version: "1.0.0",
          title: "Calculadora Simple",
          description: "Una calculadora"
        },
        files: [
          { path: "calculator.py", content: "class Calculator:\\n    def add(self,a,b):\\n        return a+b\\n" },
          { path: "README.md", content: "# Calculadora Simple\\n\\nGenerado por IA (fallback)\\n" },
          { path: "lib/requirements.txt", content: "# Ninguna dependencia\\n" }
        ]
      };
    }

    // compute folder name and hash
    const empresa = (parsed.meta && (parsed.meta.fabricante || parsed.meta.manufacturer || "default")).toString().trim().toLowerCase().replace(/\s+/g,"-");
    const shortn = (parsed.meta && (parsed.meta.shortName || parsed.meta.short || "myapp")).toString().trim().toLowerCase();
    const version = (parsed.meta && parsed.meta.version) || "1.0.0";
    const folder = `${empresa}.${shortn}.v${version}`;
    const hv = crypto.createHash("sha256").update(`${empresa}.${shortn}.v${version}`).digest("hex");

    // add default containers & LICENSE if needed
    parsed = ensureDefaultFiles(parsed, folder, hv);

    // ensure all relative file paths replace leading slashes
    parsed.files = parsed.files.map(f=>{
      let p = (f.path || "").replace(/^\.\//, "").replace(/^\/+/, "");
      // if path contains {folder} keep it to frontend; also add folder prefix for top-level ones that are not already foldered
      if(!p.startsWith(folder) && !/\{folder\}/.test(p) && !p.includes("/")) {
        // top-level file: keep as is (frontend will put folder when rendering). But for containers we already used ${folder}/...
      }
      return { path: p, content: f.content || "" };
    });

    return { statusCode:200, body: JSON.stringify(parsed) };

  } catch(err){
    console.error("genai error:", err);
    return { statusCode:500, body: JSON.stringify({ error: err.message || String(err) }) };
  }
};
