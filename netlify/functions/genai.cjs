'use strict';

const crypto = require('crypto');
const fetch = require('node-fetch');
const { GoogleGenerativeAI } = require('@google/generative-ai');

/**
 * Helpers
 */
function sanitizeRawString(s) {
  if (s == null) return '';
  // convert Buffer-like to string safely
  s = String(s);
  // normalize CRLF
  return s.replace(/\r\n/g, '\n');
}

// If model returned JSON where file.content contains literal "\n" characters
// convert them to real newlines for the produced files.
function interpretEscapedNewlines(s) {
  if (s == null) return '';
  return String(s).replace(/\\n/g, '\n').replace(/\r\n/g, '\n');
}

function extractJsonBlock(raw) {
  if (!raw) return null;
  // prioritized fenced json block
  let m = raw.match(/```json([\s\S]*?)```/i) || raw.match(/```([\s\S]*?)```/i);
  if (m && m[1]) return m[1].trim();
  // fallback: first {...}..}
  const first = raw.indexOf('{');
  const last = raw.lastIndexOf('}');
  if (first !== -1 && last !== -1 && last > first) return raw.slice(first, last + 1);
  return null;
}

function tryParseWithHeuristics(text) {
  if (!text) return null;
  try { return JSON.parse(text); } catch (e) {
    // try to replace unescaped newlines inside strings by \n (best-effort)
    try {
      const safe = text.replace(/\r\n/g, '\n').replace(/\n(?=[^{}]*?":)/g, '\\n');
      return JSON.parse(safe);
    } catch (e2) {
      return null;
    }
  }
}

async function fetchRawText(url) {
  try {
    const r = await fetch(url);
    if (!r.ok) return null;
    return await r.text();
  } catch {
    return null;
  }
}

async function fetchRawBase64(url) {
  try {
    const r = await fetch(url);
    if (!r.ok) return null;
    const arr = await r.arrayBuffer();
    return Buffer.from(arr).toString('base64');
  } catch {
    return null;
  }
}

/**
 * Build canonical package structure (ensures missing pieces)
 */
async function normalizePackage(parsed, metaOverrides = {}) {
  parsed = parsed || {};
  parsed.meta = parsed.meta || {};

  // apply any overrides from client (fabricante/short/version/title)
  for (const k of ['fabricante','shortName','version','title','description']) {
    if (metaOverrides[k]) parsed.meta[k] = metaOverrides[k];
  }

  // defaults
  parsed.meta.fabricante = parsed.meta.fabricante || 'Default Manufacturer';
  parsed.meta.shortName = parsed.meta.shortName || 'myapp';
  parsed.meta.version = parsed.meta.version || '1.0.0';
  parsed.meta.title = parsed.meta.title || parsed.meta.shortName;
  parsed.meta.description = parsed.meta.description || parsed.meta.title;

  // sanitize names used in folder
  const empresa = parsed.meta.fabricante.toString().trim().toLowerCase().replace(/\s+/g,'-');
  const shortn = parsed.meta.shortName.toString().trim().toLowerCase().replace(/\s+/g,'-');
  const version = parsed.meta.version.toString().trim();
  const folder = `${empresa}.${shortn}.v${version}`;

  parsed.files = Array.isArray(parsed.files) ? parsed.files.slice() : [];

  // ensure main script file
  const mainScriptName = `${parsed.meta.shortName}.py`;
  if (!parsed.files.some(f => f.path === `${folder}/${mainScriptName}` || f.path === mainScriptName)) {
    const content = `#!/usr/bin/env python
# publisher: ${parsed.meta.fabricante}
# name: ${parsed.meta.shortName}
# version: ${parsed.meta.version}

def main():
    print("Hello from ${parsed.meta.title}")

if __name__ == "__main__":
    main()
`;
    parsed.files.push({ path: `${folder}/${mainScriptName}`, content });
  }

  // ensure README
  if (!parsed.files.some(f => /README\.md$/i.test(f.path))) {
    parsed.files.push({ path: `${folder}/README.md`, content: `# ${parsed.meta.title}\n\nPaquete generado con Influent Package Maker.\n` });
  }

  // ensure requirements
  if (!parsed.files.some(f => /lib\/requirements\.txt$/i.test(f.path))) {
    parsed.files.push({ path: `${folder}/lib/requirements.txt`, content: "# Dependencias del paquete\n" });
  }

  // autorun (sh)
  if (!parsed.files.some(f => f.path === `${folder}/autorun`)) {
    const autorunSh = `#!/usr/bin/env sh
echo "Iniciando ${parsed.meta.shortName}..."
pip install -r "./lib/requirements.txt" || true
clear
python3 "./${parsed.meta.shortName}.py"
`;
    parsed.files.push({ path: `${folder}/autorun`, content: autorunSh });
  }

  // autorun.bat
  if (!parsed.files.some(f => f.path === `${folder}/autorun.bat`)) {
    const autorunBat = `@echo off
echo Iniciando ${parsed.meta.shortName}...
where python3 >nul 2>nul && set PYTHON_CMD=python3 || set PYTHON_CMD=python
%PYTHON_CMD% ${parsed.meta.shortName}.py
pause
`;
    parsed.files.push({ path: `${folder}/autorun.bat`, content: autorunBat });
  }

  // details.xml (mirror create_details_xml)
  if (!parsed.files.some(f => f.path === `${folder}/details.xml`)) {
    const detailsXml = `<?xml version="1.0" encoding="UTF-8"?>
<app>
  <publisher>${parsed.meta.fabricante}</publisher>
  <app>${parsed.meta.shortName}</app>
  <name>${parsed.meta.title}</name>
  <version>v${parsed.meta.version}</version>
  <with>web</with>
  <danenone>${getVersionStamp()}</danenone>
  <correlationid>${crypto.createHash('sha256').update(`${empresa}.${shortn}.v${version}`).digest('hex')}</correlationid>
  <rate>Todas las edades</rate>
</app>
`;
    parsed.files.push({ path: `${folder}/details.xml`, content: detailsXml });
  }

  // containers for default folders (app,assets,config,docs,source,lib)
  const DEFAULT_FOLDERS = ['app','assets','config','docs','source','lib'];
  const hv = crypto.createHash('sha256').update(`${empresa}.${shortn}.${version}`).digest('hex');

  for (const f of DEFAULT_FOLDERS) {
    const p = `${folder}/${f}/.${f}-container`;
    if (!parsed.files.some(x => x.path === p)) {
      parsed.files.push({ path: p, content: `#store (sha256 hash):${f}/.${hv}` });
    }
  }

  // .storedetail (content similar to your script)
  const storeDetailPath = `${folder}/.storedetail`;
  if (!parsed.files.some(x => x.path === storeDetailPath)) {
    parsed.files.push({ path: storeDetailPath, content: `#aiFlatr Store APP DETAIL | Correlation Engine for Influent OS\n#store key protection id:\n${hv}` });
  }

  // LICENSE: try to fetch raw from repository if not provided
  if (!parsed.files.some(x => /\/LICENSE$/.test(x.path) || /^LICENSE$/i.test(x.path))) {
    const licenseRawUrl = 'https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/LICENSE';
    const licText = await fetchRawText(licenseRawUrl);
    parsed.files.push({ path: `${folder}/LICENSE`, content: licText || `MIT License\nCopyright (c) ${new Date().getFullYear()}` });
  }

  // ICON: fetch raw icon and attach as base64 data URI (frontend should decode)
  if (!parsed.files.some(x => /app-icon\.ico$/i.test(x.path) || /app\/app-icon\.ico$/i.test(x.path))) {
    const iconRawUrl = 'https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/app/app-icon.ico';
    const b64 = await fetchRawBase64(iconRawUrl);
    if (b64) {
      parsed.files.push({ path: `${folder}/app/app-icon.ico`, content: `data:application/octet-stream;base64,${b64}` });
    }
  }

  // final normalization: interpret escaped newlines in all contents and ensure path is clean
  parsed.files = parsed.files.map(f => ({
    path: String(f.path).replace(/^\.\//, '').replace(/^\/+/, ''),
    content: interpretEscapedNewlines(sanitizeRawString(f.content))
  }));

  // attach computed folder (useful for frontend)
  parsed._folderName = folder;
  parsed._sha256 = hv;

  return parsed;
}

function getVersionStamp(){
  const d = new Date();
  return `${d.getFullYear().toString().slice(-2)}.${d.getMonth()+1}-${d.getHours()}.${String(d.getMinutes()).padStart(2,"0")}`;
}

/**
 * Handler
 */
exports.handler = async function(event) {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    const prompt = (body.prompt || '').toString();
    const mode = (body.mode || 'full').toString();
    const metaOverrides = body.meta || {};

    if (!prompt || !prompt.trim()) {
      return { statusCode: 400, body: JSON.stringify({ error: 'Missing prompt' }) };
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return { statusCode: 500, body: JSON.stringify({ error: 'Missing GEMINI_API_KEY in environment' }) };
    }

    // init client
    const ai = new GoogleGenerativeAI(apiKey);
    const model = ai.getGenerativeModel({ model: 'gemini-2.5-flash' });

    // Build the strict system prompt (concise, enforces JSON)
    const systemInstructions = `
Eres "Influent Package Maker". Responde EXCLUSIVAMENTE con UN bloque JSON (sin texto adicional),
o con un bloque de código fenced ```json ... ``` que contenga el JSON. No escribas explicaciones fuera del JSON.

JSON requerido (ejemplo):
{
  "meta": {
    "fabricante":"Acme Corp",
    "shortName":"hello",
    "version":"1.0.0",
    "title":"Hello",
    "description":"Breve"
  },
  "files":[
    {"path":"README.md","content":"..."},
    {"path":"hello.py","content":"..."}
  ]
}

Reglas:
- Escapa si usas literales \\n en el prompt: el servidor convertirá \\n a saltos de línea.
- Asegura README, main script (shortName.py), lib/requirements.txt, details.xml, autorun, autorun.bat, LICENSE, contenedores en app/,assets/,config/,docs/,source/,lib/.
- No añadas campos binarios crudos fuera de base64 (si incluyes icono, úsalo como data URI base64).
- Si algo falta, devuelve lo que sí puedas y el servidor rellenará lo restante.
`;

    const userPrompt = `${systemInstructions}\nUSUARIO:\n${prompt}\nMODO:${mode}`;

    // call model
    const result = await model.generateContent(userPrompt, { temperature: 0.5, maxOutputTokens: 1800 });

    // Try to extract text string from response
    let rawText = '';
    try {
      // API surface: result.response.text() or result.output...
      rawText = (result && result.response && typeof result.response.text === 'function')
                ? await result.response.text()
                : (result.output && result.output[0] && (result.output[0].content || result.output[0].text)) || JSON.stringify(result);
    } catch (e) {
      rawText = JSON.stringify(result);
    }

    // Extract JSON block and parse
    const jsonBlock = extractJsonBlock(rawText);
    let parsed = tryParseWithHeuristics(jsonBlock) || tryParseWithHeuristics(rawText);

    // If parsing failed, fallback to a minimal package using meta overrides
    if (!parsed) {
      parsed = {
        meta: {
          fabricante: metaOverrides.fabricante || 'Default Manufacturer',
          shortName: metaOverrides.shortName || 'fallback',
          version: metaOverrides.version || '1.0.0',
          title: metaOverrides.title || (metaOverrides.shortName || 'Fallback'),
          description: metaOverrides.description || prompt.slice(0,200)
        },
        files: [
          { path: 'README.md', content: `# ${metaOverrides.title || 'Fallback'}\n\nPaquete fallback generado automáticamente.\n` },
          { path: `${metaOverrides.shortName || 'fallback'}.py`, content: `print("Fallback package")\n` },
          { path: 'lib/requirements.txt', content: "# no dependencies\n" }
        ]
      };
    }

    // Normalize and fill missing files according to packagemaker.py pattern
    const normalized = await normalizePackage(parsed, {
      fabricante: metaOverrides.fabricante,
      shortName: metaOverrides.shortName,
      version: metaOverrides.version,
      title: metaOverrides.title,
      description: metaOverrides.description
    });

    // Return only the parsed package (no verbose)
    return {
      statusCode: 200,
      body: JSON.stringify({ parsed: normalized })
    };
  } catch (err) {
    console.error('genai error:', err && err.stack ? err.stack : err);
    return { statusCode: 500, body: JSON.stringify({ error: String(err) }) };
  }
};
    
