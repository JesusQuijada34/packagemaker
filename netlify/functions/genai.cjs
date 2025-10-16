// netlify/functions/genai.cjs
'use strict';

const { GoogleGenerativeAI } = require('@google/generative-ai');
const crypto = require('crypto');

/**
 * Extrae bloque THINKING y el bloque JSON (fenced o primer {...} ... } )
 * Devuelve { thinking: string|null, jsonText: string|null, raw: string }
 */
function extractBlocks(raw) {
  if (!raw || typeof raw !== 'string') return { thinking: null, jsonText: null, raw: String(raw) };

  // 1) THINKING markers (opcional)
  const thinkingMatch = raw.match(/---THINKING---([\s\S]*?)---ENDTHINK---/i);
  const thinking = thinkingMatch ? thinkingMatch[1].trim() : null;

  // 2) JSON fenced block
  let jsonMatch = raw.match(/```json([\s\S]*?)```/i) || raw.match(/```([\s\S]*?)```/i);
  let jsonText = jsonMatch ? jsonMatch[1] : null;

  // 3) fallback: first {...} ... last }
  if (!jsonText) {
    const first = raw.indexOf('{');
    const last = raw.lastIndexOf('}');
    if (first !== -1 && last !== -1 && last > first) jsonText = raw.slice(first, last + 1);
  }

  // 4) basic cleanup
  if (jsonText) {
    jsonText = jsonText.replace(/\r\n/g, '\n');            // normalize CRLF
    jsonText = jsonText.replace(/\u00A0/g, ' ');          // non-break space
    jsonText = jsonText.replace(/,\s*([\]}])/g, '$1');    // trailing commas
  }

  return { thinking, jsonText, raw };
}

/** Intenta parsear JSON con varias heurísticas */
function tryParseJSON(t) {
  if (!t) return null;
  try {
    return JSON.parse(t);
  } catch (e) {
    // attempt: escape raw newlines inside quoted strings
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

/** Añade archivos contenedor y LICENSE si faltan */
function ensureDefaults(parsed, folder, hv) {
  parsed.files = parsed.files || [];
  const DEFAULT_FOLDERS = ['app', 'assets', 'config', 'docs', 'source', 'lib'];
  DEFAULT_FOLDERS.forEach((f) => {
    const p = `${folder}/${f}/.${f}-container`;
    if (!parsed.files.some((x) => (x.path || '').toLowerCase() === p.toLowerCase())) {
      parsed.files.push({ path: p, content: `#store (sha256 hash):${f}/.${hv}` });
    }
  });

  if (!parsed.files.some((x) => /license/i.test(x.path || ''))) {
    parsed.files.push({ path: `${folder}/LICENSE`, content: 'MIT License\n\nCopyright (c) ' + new Date().getFullYear() });
  }

  return parsed;
}

exports.handler = async function (event) {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    const prompt = body.prompt || '';
    const mode = body.mode || 'full';
    const incomingFiles = Array.isArray(body.files) ? body.files : [];

    if (!prompt) {
      return { statusCode: 400, body: JSON.stringify({ error: 'Missing prompt' }) };
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return { statusCode: 500, body: JSON.stringify({ error: 'Missing GEMINI_API_KEY in environment' }) };
    }

    // Inicializa cliente
    const ai = new GoogleGenerativeAI(apiKey);
    const model = ai.getGenerativeModel({ model: 'gemini-2.5-flash' });

    // Prompt maestro: obliga THINKING + JSON fenced block, reglas y ejemplo breve
    const systemPrompt = `
Eres "Influent Package Maker", experto en generar paquetes de software en Python (y otros lenguajes).
Debes devolver EXACTAMENTE dos cosas en el texto de salida:
1) Un bloque de pensamiento corto entre marcadores:
---THINKING---
Breve frase (1-2 oraciones) que explique en voz natural lo que vas a generar y por qué.
---ENDTHINK---

2) A CONTINUACIÓN y SOLO a continuación, UN BLOQUE JSON válido dentro de triple backticks:
\`\`\`json
{ "meta": { "fabricante": "...", "shortName": "...", "version":"...", "title":"...", "description":"..." },
  "files":[ {"path":"README.md","content":"..."}, ... ]
}
\`\`\`

REGLAS:
- Escapa los saltos de línea dentro de los valores "content" como \\n.
- Incluye al menos: README.md, <shortName>.py (o .js si el prompt lo sugiere), lib/requirements.txt, details.xml, autorun, autorun.bat, LICENSE.
- Añade contenedores en app/, assets/, config/, docs/, source/, lib/.
- Si el modo = "edit" y se envían incoming files, modifica esos archivos de forma coherente y devuélvelos.
- NO incluyas texto adicional fuera de THINKING y del bloque JSON. Si incluyes ejemplos, que estén dentro del JSON como valores.
- Asegúrate que el JSON sea parseable (no comillas sin escapar, no saltos de línea sin \\n).
`;

    const userBlock = `USER_PROMPT: ${prompt}\nMODE: ${mode}\nEXISTING_FILES: ${JSON.stringify(incomingFiles).slice(0, 2000)}`;

    const requestText = systemPrompt + '\n\n' + userBlock + '\n\nPor favor devuelve la respuesta.';

    // Ejecuta el modelo
    const result = await model.generateContent(requestText, { temperature: 0.6, maxOutputTokens: 2000 });
    const rawText = (result && result.response && typeof result.response.text === 'function') ? result.response.text() : (result.output || result.text || JSON.stringify(result));

    // Extraer thinking y json
    const blocks = extractBlocks(String(rawText));
    let parsed = tryParseJSON(blocks.jsonText);

    // fallback: intentar parsear raw completo
    if (!parsed) parsed = tryParseJSON(blocks.raw);

    // Si aún no parsea, construir fallback razonable
    if (!parsed) {
      parsed = {
        meta: {
          fabricante: 'Default Manufacturer',
          shortName: 'calculator',
          version: '1.0.0',
          title: 'Calculadora Simple',
          description: 'Fallback generado por servidor'
        },
        files: [
          { path: 'calculator.py', content: 'class Calculator:\\n    def add(self,a,b):\\n        return a+b\\n' },
          { path: 'README.md', content: '# Calculadora Simple\\nGenerado por fallback' },
          { path: 'lib/requirements.txt', content: '# Ninguna dependencia' }
        ]
      };
    }

    // Construye folder y hash
    const empresa = (parsed.meta && (parsed.meta.fabricante || parsed.meta.manufacturer || 'default')).toString().trim().toLowerCase().replace(/\s+/g, '-');
    const shortn = (parsed.meta && (parsed.meta.shortName || parsed.meta.short || 'myapp')).toString().trim().toLowerCase();
    const versionVal = (parsed.meta && parsed.meta.version) ? parsed.meta.version : '1.0.0';
    const folder = `${empresa}.${shortn}.v${versionVal}`;
    const hv = crypto.createHash('sha256').update(`${empresa}.${shortn}.v${versionVal}`).digest('hex');

    parsed = ensureDefaults(parsed, folder, hv);

    // normalize file paths
    parsed.files = parsed.files.map((f) => ({ path: (f.path || '').replace(/^\.\//, '').replace(/^\/+/, ''), content: f.content || '' }));

    // Retornar thinking + parsed en body
    return {
      statusCode: 200,
      body: JSON.stringify({ thinking: blocks.thinking || null, parsed })
    };

  } catch (err) {
    console.error('genai error:', err);
    return { statusCode: 500, body: JSON.stringify({ error: err.message || String(err) }) };
  }
};
