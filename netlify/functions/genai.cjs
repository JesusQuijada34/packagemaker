// netlify/functions/genai.js
'use strict';

const crypto = require('crypto');
const fetch = require('node-fetch'); // backup fetch
const { GoogleGenerativeAI } = require('@google/generative-ai');

/**
 * Extract THINKING block and JSON fenced or first {..}..}
 * return { thinking, jsonText, raw }
 */
function extractBlocks(raw) {
  if (!raw || typeof raw !== 'string') return { thinking: null, jsonText: null, raw: String(raw) };

  const thinkingMatch = raw.match(/---THINKING---([\s\S]*?)---ENDTHINK---/i);
  const thinking = thinkingMatch ? thinkingMatch[1].trim() : null;

  let jsonMatch = raw.match(/```json([\s\S]*?)```/i) || raw.match(/```([\s\S]*?)```/i);
  let jsonText = jsonMatch ? jsonMatch[1] : null;

  if (!jsonText) {
    const first = raw.indexOf('{');
    const last = raw.lastIndexOf('}');
    if (first !== -1 && last !== -1 && last > first) jsonText = raw.slice(first, last + 1);
  }

  if (jsonText) {
    jsonText = jsonText.replace(/\r\n/g, '\n')
                       .replace(/\u00A0/g, ' ')
                       .replace(/,\s*([\]}])/g, '$1'); // remove trailing commas
  }

  return { thinking, jsonText, raw };
}

/** Try parsing JSON with heuristics (escape raw CR in quotes) */
function tryParseJSON(t) {
  if (!t) return null;
  try {
    return JSON.parse(t);
  } catch (e) {
    try {
      const safe = t.replace(/"([^"]*)\n([^"]*)"/g, (m, a, b) => {
        return `"${a}\\n${b.replace(/\n/g, '\\n')}"`;
      });
      return JSON.parse(safe);
    } catch (e2) {
      return null;
    }
  }
}

/** Ensure default container files and license/icon presence */
async function ensureDefaults(parsed, folder, hv, opts = {}) {
  parsed.files = parsed.files || [];
  const DEFAULT_FOLDERS = ['app', 'assets', 'config', 'docs', 'source', 'lib'];

  DEFAULT_FOLDERS.forEach((f) => {
    const p = `${folder}/${f}/.${f}-container`;
    if (!parsed.files.some((x) => (x.path || '').toLowerCase() === p.toLowerCase())) {
      parsed.files.push({ path: p, content: `#store (sha256 hash):${f}/.${hv}` });
    }
  });

  // LICENSE: try to fetch from upstream raw if not present
  if (!parsed.files.some((x) => /license/i.test(x.path || ''))) {
    const licenseUrl = opts.licenseRawUrl || 'https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/LICENSE';
    try {
      const r = await fetch(licenseUrl);
      if (r.ok) {
        const text = await r.text();
        parsed.files.push({ path: `${folder}/LICENSE`, content: String(text) });
      } else {
        parsed.files.push({ path: `${folder}/LICENSE`, content: 'MIT License\n\nCopyright (c) ' + new Date().getFullYear() });
      }
    } catch (e) {
      parsed.files.push({ path: `${folder}/LICENSE`, content: 'MIT License\n\nCopyright (c) ' + new Date().getFullYear() });
    }
  }

  // Icon: include ICO from raw URL if not present (as base64)
  if (!parsed.files.some((x) => /icon/i.test(x.path || ''))) {
    const iconUrl = opts.iconRawUrl || 'https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/app/app-icon.ico';
    try {
      const r2 = await fetch(iconUrl);
      if (r2.ok) {
        const buffer = await r2.arrayBuffer();
        const b64 = Buffer.from(buffer).toString('base64');
        parsed.files.push({ path: `${folder}/app-icon.ico`, content: `data:application/octet-stream;base64,${b64}` });
      }
    } catch (e) {
      // ignore icon fetch failure
    }
  }

  return parsed;
}

/** Build fallback minimal package when parsing fails */
function fallbackPackage(meta) {
  const short = (meta.shortName || 'calculator').toString().trim();
  return {
    meta: {
      fabricante: meta.fabricante || 'Default Manufacturer',
      shortName: short,
      version: meta.version || '1.0.0',
      title: meta.title || 'Fallback Package',
      description: meta.description || 'Fallback generated package'
    },
    files: [
      { path: `${short}.py`, content: `#!/usr/bin/env python\n# simple fallback\nprint("Hello from ${short}")\n` },
      { path: 'README.md', content: `# ${short}\n\nPaquete fallback generado por servidor.` },
      { path: 'lib/requirements.txt', content: '# no dependencies\n' }
    ]
  };
}

exports.handler = async function (event) {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    const prompt = body.prompt || '';
    const mode = body.mode || 'full';
    const incomingFiles = Array.isArray(body.files) ? body.files : [];

    if (!prompt) return { statusCode: 400, body: JSON.stringify({ error: 'Missing prompt' }) };

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) return { statusCode: 500, body: JSON.stringify({ error: 'Missing GEMINI_API_KEY in environment' }) };

    // Initialize Gemini client
    const ai = new GoogleGenerativeAI(apiKey);
    const model = ai.getGenerativeModel({ model: 'gemini-2.5-flash' });

    // Construct enforced prompt (THINKING + fenced JSON)
    const systemPrompt = `
Eres "Influent Package Maker", experto en generar paquetes de software.
Salida requerida: PRIMERO un bloque THINKING (1-2 oraciones) entre:
---THINKING---
...texto...
---ENDTHINK---

A CONTINUACIÓN, SOLO un bloque JSON válido, dentro de triple backticks:
\`\`\`json
{
  "meta": {
    "fabricante": "Acme Corp",
    "shortName": "hello",
    "version": "1.0.0",
    "title": "Hello App",
    "description": "Breve descripción"
  },
  "files": [
    {"path":"README.md","content":"..."},
    {"path":"hello.py","content":"..."},
    {"path":"lib/requirements.txt","content":"..."},
    {"path":"details.xml","content":"..."},
    {"path":"autorun","content":"..."},
    {"path":"autorun.bat","content":"..."},
    {"path":"app/app-icon.ico","content":"..."}
  ]
}
\`\`\`

REGLAS IMPORTANTES:
- Escapa saltos de línea como \\n dentro de los valores "content".
- Incluye al menos: README.md, <shortName>.py (o .js si hace falta), lib/requirements.txt, details.xml, autorun (sh), autorun.bat, LICENSE.
- Añade contenedores en app/, assets/, config/, docs/, source/, lib/.
- Si "mode" es "edit", toma incomingFiles y modifica sus contenidos coherentemente.
- NO añadas texto fuera del bloque THINKING y del bloque JSON.
- Asegúrate que el JSON sea parseable estrictamente.
`;

    const userBlock = `USER_PROMPT: ${prompt}\nMODE: ${mode}\nEXISTING_FILES: ${JSON.stringify(incomingFiles).slice(0, 3000)}`;

    const requestText = systemPrompt + '\n\n' + userBlock + '\n\nDevuelve la respuesta.';

    // Call Gemini
    const response = await model.generateContent(requestText, { temperature: 0.6, maxOutputTokens: 2000 });
    const raw = (response && response.response && typeof response.response.text === 'function') ? response.response.text() : (response.output || response.text || JSON.stringify(response));

    const blocks = extractBlocks(String(raw));
    let parsed = tryParseJSON(blocks.jsonText);

    // If not parsed, try parsing raw
    if (!parsed) parsed = tryParseJSON(blocks.raw);

    // If still not parsed, create fallback using minimal meta inference
    if (!parsed) {
      const inferredMeta = {
        fabricante: /fabricante[:=]\s*([^\n]+)/i.exec(prompt)?.[1] || 'Default Manufacturer',
        shortName: /shortname[:=]\s*([^\n]+)/i.exec(prompt)?.[1] || /short name[:=]\s*([^\n]+)/i.exec(prompt)?.[1] || 'calculator',
        version: /version[:=]\s*([^\n]+)/i.exec(prompt)?.[1] || '1.0.0',
        title: /title[:=]\s*([^\n]+)/i.exec(prompt)?.[1] || '',
        description: prompt
      };
      parsed = fallbackPackage(inferredMeta);
    }

    // Compute folder and hash for .storedetail
    const empresa = (parsed.meta && (parsed.meta.fabricante || parsed.meta.manufacturer || 'default')).toString().trim().toLowerCase().replace(/\s+/g, '-');
    const shortn = (parsed.meta && (parsed.meta.shortName || parsed.meta.short || 'myapp')).toString().trim().toLowerCase();
    const versionVal = parsed.meta && parsed.meta.version ? parsed.meta.version : '1.0.0';
    const folder = `${empresa}.${shortn}.v${versionVal}`;
    const storeKey = `${empresa}.${shortn}.${versionVal}`;
    const hv = crypto.createHash('sha256').update(storeKey).digest('hex');

    // Add .storedetail file (sha256 string)
    const storedetailPath = `${folder}/.storedetail`;
    const storedetailContent = hv;
    if (!parsed.files.some((f) => f.path === storedetailPath)) {
      parsed.files.push({ path: storedetailPath, content: storedetailContent });
    }

    // Ensure defaults: license + icon + containers
    parsed = await ensureDefaults(parsed, folder, hv, {
      licenseRawUrl: 'https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/LICENSE',
      iconRawUrl: 'https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/app/app-icon.ico'
    });

    // Normalize file paths and ensure contents are strings
    parsed.files = parsed.files.map((f) => ({
      path: (f.path || '').replace(/^\.\//, '').replace(/^\/+/, ''),
      content: typeof f.content === 'string' ? f.content : String(f.content || '')
    }));

    // Return thinking + parsed package
    return {
      statusCode: 200,
      body: JSON.stringify({ thinking: blocks.thinking || null, parsed })
    };
  } catch (err) {
    console.error('genai error:', err);
    return { statusCode: 500, body: JSON.stringify({ error: err.message || String(err) }) };
  }
};
    
