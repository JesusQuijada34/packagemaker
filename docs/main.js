// main.js - completo

const API_PATH = "/.netlify/functions/genai";
let LAST_FILES = {};
const $ = id => document.getElementById(id);

// helpers
function setStatus(s){ $("status").textContent = "Estado: " + s; }
function showProgress(){ document.querySelector(".progress-wrap").style.display = "block"; updateProgress(0); }
function hideProgress(){ document.querySelector(".progress-wrap").style.display = "none"; updateProgress(0); }
function updateProgress(p){ document.getElementById("progress-bar").style.width = Math.max(0, Math.min(100, p)) + "%"; }

// JSON extraction (robust)
function extractBlocks(text){
  if(!text) return { thinking: null, jsonText: null };
  // find thinking block marker ---THINKING--- ... ---ENDTHINK---
  const thinkMatch = text.match(/---THINKING---([\s\S]*?)---ENDTHINK---/i);
  const thinking = thinkMatch ? thinkMatch[1].trim() : null;
  // find JSON fenced
  let jsonMatch = text.match(/```json([\s\S]*?)```/i);
  if(!jsonMatch) jsonMatch = text.match(/```([\s\S]*?)```/i);
  let jsonText = jsonMatch ? jsonMatch[1] : null;
  if(!jsonText){
    const first = text.indexOf("{"), last = text.lastIndexOf("}");
    if(first !== -1 && last !== -1 && last>first) jsonText = text.slice(first, last+1);
  }
  if(jsonText) jsonText = jsonText.replace(/\r\n/g,"\n").replace(/,\s*([\]}])/g,"$1");
  return { thinking, jsonText };
}

function tryParseJSON(t){
  if(!t) return null;
  try { return JSON.parse(t); } catch(e){
    // attempt to escape internal newlines in quotes
    let s = t.replace(/"([^"]*)\n([^"]*)"/g, (m,a,b)=> `"${a}\\n${b.replace(/\n/g,'\\n')}"`);
    try { return JSON.parse(s); } catch(e2){ return null; }
  }
}

// UI fill meta
function fillMeta(meta){
  if(!meta) return;
  $("inp-fabricante").value = meta.fabricante || meta.manufacturer || meta.empresa || $("inp-fabricante").value;
  $("inp-short").value = meta.shortName || meta.shortname || meta.short || $("inp-short").value;
  $("inp-version").value = meta.version || $("inp-version").value;
  $("inp-title").value = meta.title || meta.titulo || $("inp-title").value;
  const container = $("preview-meta");
  container.innerHTML = `
    <div class="meta">
      <div><strong>Fabricante:</strong> ${meta.fabricante || ""}</div>
      <div><strong>Short name:</strong> ${meta.shortName || ""}</div>
      <div><strong>Versión:</strong> ${meta.version || ""}</div>
      <div style="color:var(--muted);font-size:0.9rem">${meta.description || ""}</div>
    </div>
  `;
}

// progressive render
function renderFilesProgressive(files, folderBase){
  LAST_FILES = {};
  const container = $("preview-files");
  container.innerHTML = "";
  const processed = files.map(f => ({ path: (f.path||"").replace("{folder}", folderBase).replace(/^\/+/,""), content: String(f.content || "") }));
  let i=0; showProgress();
  function step(){
    if(i>=processed.length){ updateProgress(100); hideProgress(); setStatus("Archivos listos"); $("btn-download").style.display = "inline-block"; return; }
    const f = processed[i];
    LAST_FILES[f.path] = f.content;
    const div = document.createElement("div");
    div.className = "file-card";
    div.innerHTML = `<div class="file-path">${f.path}</div><textarea class="file-edit" data-path="${f.path}">${f.content}</textarea>`;
    container.appendChild(div);
    const ta = div.querySelector(".file-edit");
    ta.addEventListener("input", ()=>{ LAST_FILES[ta.dataset.path] = ta.value; });
    i++;
    updateProgress(Math.round((i/processed.length)*90));
    setTimeout(step, 120);
  }
  step();
}

// download
async function downloadZIP(){
  const zip = new JSZip();
  document.querySelectorAll(".file-edit").forEach(ta => LAST_FILES[ta.dataset.path] = ta.value);
  for(const p in LAST_FILES) zip.file(p, LAST_FILES[p]);
  const folder = Object.keys(LAST_FILES)[0]?.split("/")[0] || "package";
  const blob = await zip.generateAsync({type:"blob"});
  saveAs(blob, `${folder}.iflapp`);
  setStatus(`ZIP generado: ${folder}.iflapp`);
}

// API key handling for GitHub Pages
async function getApiKeyOrThrow(){
  const isGithub = location.hostname.includes("github.io");
  if(!isGithub) return null;
  const cached = localStorage.getItem("gemini_api_key");
  if(cached) return cached;
  const ok = confirm("Estás en GitHub Pages. ¿Deseas ingresar tu API Key de Gemini (se guardará localmente)?");
  if(!ok) throw new Error("API Key required");
  const k = prompt("Introduce tu API key de Gemini:");
  if(!k) throw new Error("API Key required");
  localStorage.setItem("gemini_api_key", k.trim());
  return k.trim();
}

// call AI: Netlify backend preferred; fallback direct to Google API if on GitHub
async function callGenAI(prompt, mode="full", files=[]){
  const isGithub = location.hostname.includes("github.io");
  setStatus("Invocando IA...");
  if(isGithub){
    const key = await getApiKeyOrThrow();
    setStatus("Pensando...");
    // call Google Generative REST endpoint for text (v1beta2 or v1 depending)
    const endpoint = `https://generativelanguage.googleapis.com/v1beta2/models/gemini-2.5-flash:generateText?key=${encodeURIComponent(key)}`;
    const body = { prompt: { text: prompt }, temperature: 0.7, candidate_count: 1, max_output_tokens: 2000 };
    const r = await fetch(endpoint, { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(body) });
    const data = await r.json();
    const raw = data?.candidates?.[0]?.output || data?.candidates?.[0]?.content || JSON.stringify(data);
    return { rawText: typeof raw === "string" ? raw : (raw[0]?.text || JSON.stringify(raw)) };
  } else {
    // Netlify function
    const r = await fetch(API_PATH, { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify({ prompt, mode, files }) });
    const text = await r.text();
    return { rawText: text };
  }
}

// UI actions & thinking flow
async function generateHandler(fast=false){
  const fabricante = $("inp-fabricante").value.trim();
  const shortName = $("inp-short").value.trim();
  const version = $("inp-version").value.trim();
  const title = $("inp-title").value.trim();
  const desc = $("inp-prompt").value.trim();

  // prompt: enforce structure and two-block output
  const instruction = `
---THINKING---
Por favor, escribe una frase corta (1-2 oraciones) explicando en voz natural qué vas a generar ahora y por qué (coherencia). No uses más texto.
---ENDTHINK---

Ahora genera SOLO UN BLOQUE JSON válido, dentro de triple backticks \`\`\`json ... \`\`\`, y sin nada antes o después del bloque JSON.
El JSON debe tener esta forma exacta:
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
- Genera al menos: README.md, <shortName>.py, lib/requirements.txt, details.xml, autorun, autorun.bat, LICENSE.
- Añade contenedores en app/, assets/, config/, docs/, source/, lib/ con un archivo .<name>-container que contenga "#store (sha256 hash):<name>/.<hash>".
- No incluyas explicaciones fuera del bloque JSON; el bloque THINKING se permite antes.
- Si el prompt es vago, infiere sensible defaults.
- Asegúrate de que JSON parsee sin errores.
`;

  const userPrompt = `Fabricante: ${fabricante || "Default Manufacturer"}
ShortName: ${shortName || "calculator"}
Version: ${version || "1.0.0"}
Title: ${title || "Aplicación"}
Description: ${desc || "Aplicación generada por IA"}
Mode: ${fast ? "fast" : "full"}
`;

  const fullPrompt = instruction + "\n\nUSER:\n" + userPrompt;

  try {
    showProgress(); updateProgress(10);
    setStatus("Pensando...");
    // call AI
    const res = await callGenAI(fullPrompt, fast ? "fast":"full");
    const raw = res.rawText;
    // display thinking part early if present
    const blocks = extractBlocks(raw);
    if(blocks.thinking){
      $("ai-output").textContent = blocks.thinking;
      setStatus("Pensando: " + (blocks.thinking.length > 80 ? blocks.thinking.slice(0,80)+"..." : blocks.thinking));
    } else {
      $("ai-output").textContent = "Pensando...";
    }
    updateProgress(30);
    // parse JSON
    const parsed = tryParseJSON(blocks.jsonText || raw);
    if(!parsed){
      // As fallback try to extract from entire raw
      const fallback = tryParseJSON(raw);
      if(fallback) parsed = fallback;
    }
    if(!parsed){
      // final fallback minimal package
      setStatus("IA devolvió respuesta no válida, usando fallback.");
      const fallbackPackage = {
        meta: { fabricante: fabricante || "Default Manufacturer", shortName: shortName || "calculator", version: version || "1.0.0", title: title || "Calculadora Simple", description: desc || "Fallback" },
        files: [
          { path: (shortName||"calculator") + ".py", content: "class Calculator:\\n    def add(self,a,b):\\n        return a+b\\n" },
          { path: "README.md", content: "# Fallback package\\nGenerado por fallback." },
          { path: "lib/requirements.txt", content: "# none" }
        ]
      };
      fillMeta(fallbackPackage.meta);
      renderFilesProgressive(fallbackPackage.files, `${(fallbackPackage.meta.fabricante||"default").toLowerCase().replace(/\s+/g,"-")}.${(fallbackPackage.meta.shortName||"calculator").toLowerCase()}.v${fallbackPackage.meta.version}`);
      $("ai-output").textContent = JSON.stringify(fallbackPackage, null, 2);
      hideProgress(); return;
    }

    // success path
    fillMeta(parsed.meta || {});
    updateProgress(60);
    // compute folder
    const empresa = (parsed.meta.fabricante || $("inp-fabricante").value || "default").toString().trim().toLowerCase().replace(/\s+/g,"-");
    const nombre = (parsed.meta.shortName || $("inp-short").value || "myapp").toString().trim().toLowerCase();
    const versionVal = parsed.meta.version || $("inp-version").value || "1.0.0";
    const folder = `${empresa}.${nombre}.v${versionVal}`;
    renderFilesProgressive(parsed.files || [], folder);
    $("ai-output").textContent = JSON.stringify(parsed, null, 2);
    updateProgress(100);
    hideProgress();
    setStatus("Generación completada");
  } catch(err){
    console.error(err);
    hideProgress();
    setStatus("Error: " + (err.message || err));
    $("ai-output").textContent = "Error: " + (err.message || JSON.stringify(err));
  }
}

// wire events
$("btn-generate").addEventListener("click", ()=> generateHandler(false));
$("btn-fast").addEventListener("click", ()=> generateHandler(true));
$("btn-download").addEventListener("click", downloadZIP);
$("btn-clear").addEventListener("click", ()=>{ $("preview-files").innerHTML=""; $("ai-output").textContent=""; LAST_FILES={}; setStatus("limpio"); });

// edit (send current files to edit mode)
$("btn-edit").addEventListener("click", async ()=>{
  const files = [];
  document.querySelectorAll(".file-edit").forEach(ta => files.push({ path: ta.dataset.path, content: ta.value }));
  try {
    setStatus("Solicitando edición a IA...");
    // reuse generateHandler flow but send 'edit' mode prompt
    const promptParts = [];
    files.forEach(f => promptParts.push(`FILE: ${f.path}\nCONTENT:\\n${f.content}\n---END_FILE---`));
    const combined = "EDIT MODE\n" + promptParts.join("\n") + "\nINSTRUCTION: Please modify files according to user's prompt: " + ($("inp-prompt").value || "");
    // call AI via same pipeline
    showProgress(); updateProgress(10);
    const res = await callGenAI(combined, "edit", files);
    const raw = res.rawText;
    const blocks = extractBlocks(raw);
    const parsed = tryParseJSON(blocks.jsonText || raw) || tryParseJSON(raw);
    if(parsed && Array.isArray(parsed.files)){
      parsed.files.forEach(f => {
        const ta = document.querySelector(`textarea[data-path="${f.path}"]`);
        if(ta) { ta.value = f.content; LAST_FILES[f.path] = f.content; }
      });
      $("ai-output").textContent = JSON.stringify(parsed, null, 2);
      setStatus("Edición completada.");
    } else {
      throw new Error("Respuesta de edición inválida");
    }
    hideProgress();
  } catch(err){
    console.error(err);
    hideProgress();
    setStatus("Error: " + (err.message || err));
  }
});

// logout visibility: show only on GitHub Pages (not on Netlify)
function setupLogoutVisibility(){
  const isNetlify = location.hostname.endsWith("netlify.app") || location.hostname.includes("vercel") || location.hostname === "localhost";
  const btn = $("btnLogout");
  if(!isNetlify){
    btn.style.display = "inline-block";
  } else {
    btn.style.display = "none";
  }
}
$("btnLogout").addEventListener("click", ()=>{ localStorage.removeItem("gemini_api_key"); alert("API key eliminada localmente"); location.reload(); });

setupLogoutVisibility();

// auto-run via ?in?appid=Entorno or ?appid=Entorno
function getQueryAppId(){
  const q = location.search || "";
  const clean = q.replace(/^\?in\?/,"?");
  const params = new URLSearchParams(clean);
  return params.get("appid");
}
window.addEventListener("load", ()=>{
  const appid = getQueryAppId();
  if(appid){
    $("inp-fabricante").value = "Environment";
    $("inp-short").value = appid;
    $("inp-title").value = appid;
    setTimeout(()=> $("btn-generate").click(), 600);
  }
});
