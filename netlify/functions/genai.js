/**
 * Netlify Function: genai.js
 * Integración con API de Gemini para generar paquetes .iflapp
 * Replicar la funcionalidad de packagemaker.py en el backend
 */

const https = require('https');

// Configuración
const GEMINI_API_KEY = process.env.OPENAI_API_KEY; // Usando la variable de entorno disponible
const GEMINI_API_URL = 'https://api.openai.com/v1/chat/completions';

/**
 * Función para obtener la marca de tiempo de versión
 */
function getVersionStamp() {
  const now = new Date();
  const year = now.getFullYear().toString().slice(-2);
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const hour = String(now.getHours()).padStart(2, '0');
  const minute = String(now.getMinutes()).padStart(2, '0');
  return `${year}.${month}-${hour}.${minute}`;
}

/**
 * Función para calcular SHA256 (simplificado para Node.js)
 */
function sha256(str) {
  const crypto = require('crypto');
  return crypto.createHash('sha256').update(str).digest('hex');
}

/**
 * Llamar a la API de Gemini para generar contenido
 */
async function callGeminiAPI(prompt) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'gpt-4-mini', // Usando gpt-4-mini compatible con la API
      messages: [
        {
          role: 'system',
          content: `Eres un asistente experto en crear aplicaciones Python profesionales. 
          Cuando el usuario describe una aplicación, debes generar:
          1. Un script Python completo y funcional
          2. Un archivo README.md bien estructurado
          3. Un archivo requirements.txt con las dependencias necesarias
          
          Responde SIEMPRE en formato JSON válido con esta estructura:
          {
            "python_code": "...",
            "readme": "...",
            "requirements": "..."
          }`
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 2000
    });

    const options = {
      hostname: 'api.openai.com',
      port: 443,
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length,
        'Authorization': `Bearer ${GEMINI_API_KEY}`
      }
    };

    const req = https.request(options, (res) => {
      let responseData = '';

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        try {
          const parsed = JSON.parse(responseData);
          if (parsed.choices && parsed.choices[0] && parsed.choices[0].message) {
            const content = parsed.choices[0].message.content;
            // Intentar extraer JSON de la respuesta
            const jsonMatch = content.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
              resolve(JSON.parse(jsonMatch[0]));
            } else {
              resolve({
                python_code: content,
                readme: 'Generado con IA',
                requirements: ''
              });
            }
          } else {
            reject(new Error('Respuesta inesperada de Gemini'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', (e) => {
      reject(e);
    });

    req.write(data);
    req.end();
  });
}

/**
 * Generar estructura de paquete .iflapp
 */
async function generatePackageStructure(fabricante, shortName, version, titulo, aiContent) {
  const folder = `${fabricante}.${shortName}.v${version}`;
  const hash = sha256(`${fabricante}.${shortName}.v${version}`);
  const versionStamp = getVersionStamp();

  const files = {
    [`${folder}/LICENSE`]: `MIT License\n\nCopyright (c) ${new Date().getFullYear()} ${fabricante}\n\nPermission is hereby granted...`,
    [`${folder}/README.md`]: aiContent.readme || `# ${titulo}\n\nGenerado con Influent Package Maker.`,
    [`${folder}/${shortName}.py`]: aiContent.python_code || `#!/usr/bin/env python3\nprint("Hello from ${titulo}!")`,
    [`${folder}/lib/requirements.txt`]: aiContent.requirements || 'PyQt5>=5.15.4\n',
    [`${folder}/details.xml`]: `<?xml version="1.0" encoding="UTF-8"?>
<app>
  <publisher>${fabricante}</publisher>
  <app>${shortName}</app>
  <name>${titulo}</name>
  <version>v${version}</version>
  <platform>web</platform>
  <danenone>${versionStamp}</danenone>
  <correlationid>${hash}</correlationid>
  <rate>EVERYONE</rate>
</app>`,
    [`${folder}/.storedetail`]: `${hash}`,
    [`${folder}/autorun.bat`]: `@echo off\necho Iniciando ${shortName}...\npip install -r lib/requirements.txt\npython ${shortName}.py\npause`,
    [`${folder}/autorun`]: `#!/bin/sh\npip install -r "./lib/requirements.txt"\npython3 "./${shortName}.py"`,
  };

  // Crear archivos de contenedor para carpetas
  const DEFAULT_FOLDERS = ['app', 'assets', 'config', 'docs', 'source'];
  DEFAULT_FOLDERS.forEach((f) => {
    files[`${folder}/${f}/.${f}-container`] = `#store (sha256 hash):${f}/.${hash}`;
  });

  return files;
}

/**
 * Handler principal de Netlify
 */
exports.handler = async (event, context) => {
  // Validar método HTTP
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Método no permitido' })
    };
  }

  try {
    const body = JSON.parse(event.body);
    const { fabricante, shortName, version, titulo, descripcion } = body;

    // Validar campos requeridos
    if (!fabricante || !shortName || !version || !titulo || !descripcion) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Campos requeridos faltantes' })
      };
    }

    // Llamar a Gemini para generar contenido
    const aiContent = await callGeminiAPI(
      `Crea una aplicación Python llamada "${titulo}" con la siguiente descripción: ${descripcion}`
    );

    // Generar estructura de paquete
    const files = await generatePackageStructure(fabricante, shortName, version, titulo, aiContent);

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        success: true,
        folder: `${fabricante}.${shortName}.v${version}`,
        files: files,
        message: 'Paquete generado exitosamente con IA'
      })
    };
  } catch (error) {
    console.error('Error en genai:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Error al generar paquete',
        details: error.message
      })
    };
  }
};

