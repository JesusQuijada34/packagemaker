'use strict';

const crypto = require('crypto');
const fetch = require('node-fetch');
const { GoogleGenerativeAI } = require('@google/generative-ai');

/* --- Bloques de utilidad --- */

function extractBlocks(raw) {
  if (!raw || typeof raw !== 'string') return { thinking: null, jsonText: null, raw: String(raw) };
  const thinking = (raw.match(/---THINKING---([\s\S]*?)---ENDTHINK---/i) || [])[1]?.trim() || null;
  let jsonText = (raw.match(/```json([\s\S]*?)```/i) || raw.match(/```([\s\S]*?)```/i) || [])[1];
  if (!jsonText) {
    const first = raw.indexOf('{');
    const last = raw.lastIndexOf('}');
    if (first !== -1 && last !== -1) jsonText = raw.slice(first, last + 1);
  }
  return { thinking, jsonText, raw };
}

function tryParseJSON(t) {
  if (!t) return null;
  try {
    return JSON.parse(t);
  } catch {
    try {
      const safe = t.replace(/"([^"]*)\n([^"]*)"/g, (_, a, b) => `"${a}\\n${b}"`);
      return JSON.parse(safe);
    } catch {
      return null;
    }
  }
}

async function ensureDefaults(parsed, folder, hv) {
  parsed.files = parsed.files || [];
  const folders = ['app', 'assets', 'config', 'docs', 'source', 'lib'];

  folders.forEach(f => {
    const path = `${folder}/${f}/.${f}-container`;
    if (!parsed.files.some(x => x.path === path))
      parsed.files.push({ path, content: `#store (sha256 hash):${f}/.${hv}` });
  });

  // LICENSE RAW
  if (!parsed.files.some(x => /license/i.test(x.path))) {
    const url = 'https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/LICENSE';
    const res = await fetch(url).catch(() => null);
    const text = res?.ok ? await res.text() : 'MIT License\nCopyright (c) Influent Labs';
    parsed.files.push({ path: `${folder}/LICENSE`, content: text });
  }

  // ICON RAW
  if (!parsed.files.some(x => /icon/i.test(x.path))) {
    const url = 'https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/app/app-icon.ico';
    const r2 = await fetch(url).catch(() => null);
    if (r2?.ok) {
      const b64 = Buffer.from(await r2.arrayBuffer()).toString('base64');
      parsed.files.push({ path: `${folder}/app-icon.ico`, content: `data:image/x-icon;base64,${b64}` });
    }
  }
  return parsed;
}

/* --- Controlador principal --- */

exports.handler = async (event) => {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    const prompt = body.prompt || '';
    const mode = body.mode || 'full';
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) return { statusCode: 500, body: JSON.stringify({ error: 'Falta GEMINI_API_KEY.' }) };
    if (!prompt.trim()) return { statusCode: 400, body: JSON.stringify({ error: 'Falta prompt del usuario.' }) };

    const ai = new GoogleGenerativeAI(apiKey);
    const model = ai.getGenerativeModel({ model: 'gemini-2.5-flash' });

    /* --------------------------------------------------------------
       📘 DOCTRINA INTERNA — ENTRENAMIENTO DEL MODELO
       --------------------------------------------------------------
       Este modelo actúa como un generador de software autónomo.
       Su misión es producir proyectos de software completos,
       en formato JSON bien formado, desde descripciones humanas.

       📖 Filosofía:
       - No improvises texto fuera del bloque JSON.
       - Usa THINKING breve (2 frases máx.) para reflexión interna.
       - Sé técnico, coherente, ordenado y profesional.
       - Corrige automáticamente inconsistencias del usuario.
       - Todo lo que entregues debe tener valor de ingeniería real.

       📦 Estructura final JSON:
       {
         "meta": {
           "fabricante": "string",
           "shortName": "string",
           "version": "string",
           "title": "string",
           "description": "string"
         },
         "files": [
           {"path": "README.md", "content": "..."},
           {"path": "{shortName}.py", "content": "..."},
           {"path": "lib/requirements.txt", "content": "..."},
           {"path": "details.xml", "content": "..."},
           {"path": "autorun", "content": "..."},
           {"path": "autorun.bat", "content": "..."},
           {"path": "LICENSE", "content": "..."}
         ]
       }

       ⚙️ Ejemplo de details.xml:
       <app>
         <publisher>Acme</publisher>
         <app>calculator</app>
         <version>1.0.0</version>
         <title>Calculadora</title>
         <description>Una calculadora con operaciones básicas</description>
       </app>

       ⚙️ Ejemplo de autorun.bat:
       @echo off
       echo Iniciando aplicación...
       python {shortName}.py
       pause

       ⚙️ Ejemplo de autorun (sh):
       #!/bin/bash
       echo "Iniciando..."
       python3 {shortName}.py

       🧠 Técnicas:
       - Escapa saltos de línea como \\n en todos los contenidos.
       - Elimina comas colgantes.
       - No incluyas texto fuera del bloque JSON.
       - Si el usuario pide una app tipo "editor", genera código Python o JS acorde.
       - No devuelvas HTML, solo código fuente y archivos.
       - Si no sabes algo, genera un esqueleto técnico básico coherente.

       🧩 Ejemplo de entrada y salida:
       Entrada:
         "Quiero una app de notas local sencilla."
       Salida:
         ---THINKING---
         Crear estructura simple con almacenamiento local.
         ---ENDTHINK---
         ```json
         {
           "meta": {...},
           "files": [...]
         }
         ```

       -------------------------------------------------------------- */

    const fullPrompt = `
---INSTRUCCIONES---
${prompt}
---MODO---
${mode}
---FIN---
Devuelve un bloque THINKING y un bloque JSON según las reglas.
`;

    const result = await model.generateContent(fullPrompt, { temperature: 0.5, maxOutputTokens: 2048 });
    const raw = result?.response?.text?.() || JSON.stringify(result);
    const blocks = extractBlocks(raw);
    let parsed = tryParseJSON(blocks.jsonText) || tryParseJSON(blocks.raw);

    if (!parsed) {
      parsed = {
        meta: { fabricante: 'Default Manufacturer', shortName: 'fallback', version: '1.0.0', title: 'Fallback', description: prompt },
        files: [{ path: 'README.md', content: '# Fallback\\n\\nNo se pudo analizar JSON correctamente.' }]
      };
    }

    const fabricante = (parsed.meta.fabricante || 'default').toLowerCase().replace(/\s+/g, '-');
    const shortName = (parsed.meta.shortName || 'myapp').toLowerCase();
    const version = parsed.meta.version || '1.0.0';
    const folder = `${fabricante}.${shortName}.v${version}`;
    const hv = crypto.createHash('sha256').update(`${fabricante}.${shortName}.${version}`).digest('hex');

    // .storedetail
    parsed.files.push({ path: `${folder}/.storedetail`, content: hv });

    // Licencia, ícono y contenedores
    parsed = await ensureDefaults(parsed, folder, hv);

    parsed.files = parsed.files.map(f => ({
      path: f.path.trim(),
      content: String(f.content || '')
    }));

    return {
      statusCode: 200,
      body: JSON.stringify({ thinking: blocks.thinking || null, parsed })
    };
  } catch (err) {
    console.error('Error genai:', err);
    return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
  }
};
