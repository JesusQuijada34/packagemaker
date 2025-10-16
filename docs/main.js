// main.js - frontend logic: detection de entorno, UI, progreso, parseo seguro, descarga ZIP

const API_PATH = '/.netlify/functions/genai'; // endpoint Netlify
let LAST_FILES = {}; // path -> content

const $ = id => document.getElementById(id);

// UI helpers
function setStatus(text){ $('status').textContent = 'Estado: ' + text; }
function showProgress(){ document.getElementById('progress-wrap').style.display = 'block'; updateProgress(0); }
function hideProgress(){ document.getElementById('progress-wrap').style.display = 'none'; updateProgress(0); }
function updateProgress(p){ document.getElementById('progress-bar').style.width = Math.max(0,Math.min(100,p)) + '%'; }

// robust extractor like server: returns { thinking, jsonText, raw }
function extractBlocksClient(raw){
  if(!raw || typeof raw !== 'string') return { thinking:null, jsonText:null, raw: String(raw) };
  const thinkingMatch = raw.match(/---THINKING---([\s\S]*?)---ENDTHINK---/i);
  const thinking = thinkingMatch ? thinkingMatch[1].trim() : null;
  let jsonMatch = raw.match(/```json([\s\S]*?)```/i) || raw.match(/```([\s\S]*?)```/i);
  let jsonText = jsonMatch ? jsonMatch[1] : null;
  if(!jsonText){
    const first = raw.indexOf('{'), last = raw.lastIndexOf('}');
    if(first !== -1 && last !== -1 && last>first) jsonText = raw.slice(first, last+1);
  }
  if(jsonText) jsonText = jsonText.replace(/\r\n/g, '\n').replace(/,\s*([\]}])/g, '$1');
  return { thinking, jsonText, raw };
}

function tryParseJSON(t){
  if(!t) return null;
  try { return JSON.parse(t); }
  catch(e){
    try {
      const safe = t.replace(/"([^"]*)\n([^"]*)"/g, (m,a,b)=> `"${a}\\n${b.replace(/\n/g,'\\n')}"`);
      return JSON.parse(safe);
    } catch(e2){
      return null;
    }
  }
}

function fillMeta(meta){
  if(!meta) return;
  $('inp-fabricante').value = meta.fabricante || meta.manufacturer || $('inp-fabricante').value;
  $('inp-short').value = meta.shortName || meta.shortname || $('inp-short').value;
  $('inp-version').value = meta.version || $('inp-version').value;
  $('inp-title').value = meta.title || $('inp-title').value;
  const container = $('preview-meta');
  container.innerHTML = `<div class="meta">
    <div><strong>Fabricante:</strong> ${meta.fabricante || ''}</div>
    <div><strong>Short name:</strong> ${meta.shortName || ''}</div>
    <div><strong>Versión:</strong> ${meta.version || ''}</div>
    <div style="color:var(--muted);font-size:.9rem">${meta.description || ''}</div>
  </div>`;
}

function renderFilesProgressive(files, folderBase){
  LAST_FILES = {};
  const container = $('preview-files');
  container.innerHTML = '';
  const processed = files.map(f => ({ path: (f.path||'').replace('{folder}', folderBase).replace(/^\/+/,''), content: String(f.content || '') }));
  let i = 0;
  showProgress();
  function step(){
    if(i >= processed.length){
      updateProgress(100);
      hideProgress();
      $('btn-download').style.display = 'inline-block';
      setStatus('Archivos listos');
      return;
    }
    const f = processed[i];
    LAST_FILES[f.path] = f.content;
    const div = document.createElement('div');
    div.className = 'file-card';
    div.innerHTML = `<div class="file-path">${f.path}</div><textarea class="file-edit" data-path="${f.path}">${f.content}</textarea>`;
    container.appendChild(div);
    const ta = div.querySelector('.file-edit');
    ta.addEventListener('input', ()=> { LAST_FILES[ta.dataset.path] = ta.value; });
    i++;
    updateProgress(Math.round((i / processed.length) * 90));
    setTimeout(step, 110);
  }
  step();
}

async function downloadZIP(){
  const zip = new JSZip();
  document.querySelectorAll('.file-edit').forEach(ta => LAST_FILES[ta.dataset.path] = ta.value);
  for(const p in LAST_FILES) zip.file(p, LAST_FILES[p]);
  const folder = Object.keys(LAST_FILES)[0]?.split('/')[0] || 'package';
  const blob = await zip.generateAsync({ type: 'blob' });
  saveAs(blob, `${folder}.iflapp`);
  setStatus(`ZIP generado: ${folder}.iflapp`);
}

// env detection: GitHub Pages => client must ask key; Netlify => use server function
function isGitHubPages(){
  return location.hostname.includes('github.io');
}

// show/hide logout: visible only on GitHub pages
function setupLogoutVisibility(){
  const isNetlify = location.hostname.endsWith('netlify.app') || location.hostname === 'localhost';
  const btn = $('btnLogout');
  if(isNetlify) btn.style.display = 'none';
  else btn.style.display = 'inline-block';
}
$('btnLogout').addEventListener('click', ()=>{ localStorage.removeItem('gemini_api_key'); alert('API key local eliminada'); location.reload(); });
setupLogoutVisibility();

// get API key from localStorage or prompt (GitHub Pages only)
async function getLocalApiKey(){
  const cached = localStorage.getItem('gemini_api_key');
  if(cached) return cached;
  const ask = confirm('Estás en GitHub Pages. ¿Quieres ingresar tu API Key de Gemini (se guardará localmente)?');
  if(!ask) throw new Error('API key required');
  const key = prompt('Introduce tu API Key de Gemini (Google AI Studio):');
  if(!key) throw new Error('API key required');
  localStorage.setItem('gemini_api_key', key.trim());
  return key.trim();
}

// call AI: uses serverless function on Netlify or direct REST on GitHub Pages
async function callAI(prompt, mode = 'full', files = []){
  setStatus('Invocando IA...');
  if(isGitHubPages()){
    const key = await getLocalApiKey();
    setStatus('Pensando (cliente)...');
    // Google Generative REST endpoint (v1beta2/v1beta depending on availability). Using v1beta2 generateText pattern.
    const endpoint = `https://generativelanguage.googleapis.com/v1beta2/models/gemini-2.5-flash:generateText?key=${encodeURIComponent(key)}`;
    const body = {
      prompt: { text: prompt },
      temperature: 0.6,
      candidate_count: 1,
      max_output_tokens: 1600
    };
    const r = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if(!r.ok) throw new Error('Error desde API cliente: ' + r.statusText);
    const data = await r.json();
    // extract text: different shapes possible, try common fields
    const text = data?.candidates?.[0]?.output || data?.candidates?.[0]?.content || data?.output || JSON.stringify(data);
    return String(text);
  } else {
    // Netlify function
    const r = await fetch(API_PATH, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt, mode, files }) });
    if(!r.ok) {
      const t = await r.text();
      throw new Error('Server error: ' + (t || r.status));
    }
    const json = await r.json();
    // the server returns { thinking, parsed } serialized
    // Convert to a string representation similar to client flow: put THINKING markers then fenced JSON
    const thinking = json.thinking || null;
    const parsed = json.parsed || null;
    if (thinking && parsed) {
      // ensure JSON string has escaped \n in content values (server already did best-effort)
      const rendered = (thinking ? `---THINKING---\n${thinking}\n---ENDTHINK---\n\n` : '') + '```json\n' + JSON.stringify(parsed, null, 2) + '\n```\n';
      return rendered;
    }
    // fallback: if server returned error field
    if (json.error) throw new Error(json.error);
    return JSON.stringify(json);
  }
}

// main generate flow with thinking UI, progress, parsing robust y render progresivo
async function generateHandler(fast = false){
  const fabricante = $('inp-fabricante').value.trim();
  const shortName = $('inp-short').value.trim();
  const version = $('inp-version').value.trim();
  const title = $('inp-title').value.trim();
  const desc = $('inp-prompt').value.trim();

  const instruction = `
---THINKING---
Por favor, escribe una breve frase (1-2 oraciones) explicando qué vas a generar y por qué.
---ENDTHINK---

Ahora devuelve SOLO un bloque JSON válido (dentro de triple backticks ```json ... ```), con esta forma:
{
  "meta": {
    "fabricante": "...",
    "shortName": "...",
    "version": "...",
    "title": "...",
    "description": "..."
  },
  "files": [
    { "path": "README.md", "content": "..." },
    { "path": "<shortName>.py", "content": "..." },
    ...
  ]
}

REGLAS:
- Escapa saltos de línea con \\n dentro de los valores "content".
- Incluye archivos básicos: README.md, <shortName>.py (o .js si procede), lib/requirements.txt, details.xml, autorun, autorun.bat, LICENSE.
- Añade contenedores en app/, assets/, config/, docs/, source/, lib/ (.{name}-container).
- Asegura JSON parseable.
`;

  const userPrompt = `Fabricante: ${fabricante || 'Default Manufacturer'}
ShortName: ${shortName || 'calculator'}
Version: ${version || '1.0.0'}
Title: ${title || ''}
Description: ${desc || ''}
Mode: ${fast ? 'fast' : 'full'}`;

  const fullPrompt = instruction + '\n\nUSER:\n' + userPrompt;

  try {
    showProgress(); updateProgress(10);
    setStatus('Pensando...');
    const raw = await callAI(fullPrompt, fast ? 'fast' : 'full');

    // extract client blocks
    const blocks = extractBlocksClient(String(raw));
    if(blocks.thinking){
      $('ai-output').textContent = blocks.thinking;
      setStatus('Pensando: ' + (blocks.thinking.length > 120 ? blocks.thinking.slice(0,120)+'...' : blocks.thinking));
    } else {
      $('ai-output').textContent = 'Pensando...';
    }
    updateProgress(30);

    // parse JSON
    let parsed = tryParseJSON(blocks.jsonText || blocks.raw);
    if(!parsed){
      // try RAW full parse
      parsed = tryParseJSON(blocks.raw);
    }
    if(!parsed){
      // fallback small package
      setStatus('La IA devolvió JSON inválido; aplicando fallback.');
      const fallback = {
        meta: { fabricante: fabricante || 'Default Manufacturer', shortName: shortName || 'calculator', version: version || '1.0.0', title: title || 'Fallback', description: desc || '' },
        files: [
          { path: (shortName||'calculator') + '.py', content: 'class Calculator:\\n    def add(self,a,b):\\n        return a+b\\n' },
          { path: 'README.md', content: '# Fallback package\\nGenerado por fallback' },
          { path: 'lib/requirements.txt', content: '# none' }
        ]
      };
      fillMeta(fallback.meta);
      renderFilesProgressive(fallback.files || [], `${(fallback.meta.fabricante||'default').toLowerCase().replace(/\s+/g,'-')}.${(fallback.meta.shortName||'calculator').toLowerCase()}.v${fallback.meta.version}`);
      $('ai-output').textContent = JSON.stringify(fallback, null, 2);
      hideProgress();
      return;
    }

    // success path
    fillMeta(parsed.meta || {});
    updateProgress(60);
    const empresa = (parsed.meta.fabricante || $('inp-fabricante').value || 'default').toString().trim().toLowerCase().replace(/\s+/g,'-');
    const nombre = (parsed.meta.shortName || $('inp-short').value || 'myapp').toString().trim().toLowerCase();
    const versionVal = parsed.meta.version || $('inp-version').value || '1.0.0';
    const folder = `${empresa}.${nombre}.v${versionVal}`;
    renderFilesProgressive(parsed.files || [], folder);
    $('ai-output').textContent = JSON.stringify(parsed, null, 2);
    updateProgress(100);
    hideProgress();
    setStatus('Generación completada');
  } catch (err) {
    console.error(err);
    hideProgress();
    setStatus('Error: ' + (err.message || err));
    $('ai-output').textContent = 'Error: ' + (err.message || JSON.stringify(err));
  }
}

// edit current files
$('btn-edit').addEventListener('click', async ()=> {
  const files = [];
  document.querySelectorAll('.file-edit').forEach(ta => files.push({ path: ta.dataset.path, content: ta.value }));
  const desc = $('inp-prompt').value.trim() || 'Edit request';
  setStatus('Solicitando edición a IA...');
  try {
    // reuse generate flow with edit mode: send existing files as part of prompt via callAI in server or client
    const editPrompt = `EDIT FILES\nDescription: ${desc}\nFILES: ${JSON.stringify(files).slice(0,4000)}\nPlease return JSON with same structure {"meta":...,"files":[...]} and edited contents.`;
    // call AI
    const raw = await (isGitHubPages() ? (async ()=> { const key = await getLocalApiKey(); return fetch(`https://generativelanguage.googleapis.com/v1beta2/models/gemini-2.5-flash:generateText?key=${encodeURIComponent(key)}`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ prompt:{ text: editPrompt }, temperature:0.6, candidate_count:1 }) }).then(r=>r.json()).then(d=> d?.candidates?.[0]?.output || JSON.stringify(d)) })() : (async ()=> { const r = await fetch(API_PATH, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ prompt: editPrompt, mode: 'edit', files }) }); const j = await r.json(); return (j.thinking ? `---THINKING---\n${j.thinking}\n---ENDTHINK---\n\n` : '') + '```json\n' + JSON.stringify(j.parsed || {}, null, 2) + '\n```'; })());
    const blocks = extractBlocksClient(String(raw));
    const parsed = tryParseJSON(blocks.jsonText || blocks.raw) || null;
    if(parsed && Array.isArray(parsed.files)){
      parsed.files.forEach(f=>{
        const ta = document.querySelector(`textarea[data-path="${f.path}"]`);
        if(ta){ ta.value = f.content; LAST_FILES[f.path] = f.content; }
      });
      $('ai-output').textContent = JSON.stringify(parsed, null, 2);
      setStatus('Edición completada.');
    } else throw new Error('Respuesta de edición inválida');
  } catch(err){
    console.error(err); setStatus('Error: ' + (err.message || err)); $('ai-output').textContent = 'Error: ' + (err.message || JSON.stringify(err));
  }
});

// wire generate & fast & download & clear
$('btn-generate').addEventListener('click', ()=> generateHandler(false));
$('btn-fast').addEventListener('click', ()=> generateHandler(true));
$('btn-clear').addEventListener('click', ()=> { $('preview-files').innerHTML=''; $('ai-output').textContent=''; LAST_FILES={}; setStatus('limpio'); $('btn-download').style.display='none'; });
$('btn-download').addEventListener('click', downloadZIP);

// logout button
$('btnLogout').addEventListener('click', ()=> { localStorage.removeItem('gemini_api_key'); alert('API key local eliminada'); location.reload(); });

// auto-run via query param ?in?appid=Entorno or ?appid=Entorno
function getQueryAppId(){
  const q = location.search || '';
  const clean = q.replace(/^\?in\?/,'?');
  const params = new URLSearchParams(clean);
  return params.get('appid');
}

window.addEventListener('load', ()=> {
  const appid = getQueryAppId();
  if(appid){
    $('inp-fabricante').value = 'Environment';
    $('inp-short').value = appid;
    $('inp-title').value = appid;
    setTimeout(()=> $('btn-generate').click(), 700);
  }
});
