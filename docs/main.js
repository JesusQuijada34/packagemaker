// main.js - UI + env detection + caching API key + progressive render + download ZIP

const API_PATH = "/.netlify/functions/genai"; // Netlify function
let LAST_FILES = {}; // path -> content

const $ = id => document.getElementById(id);

// status helper
function setStatus(txt){ $("status").textContent = "Estado: " + txt; }

// Extract JSON robustly from AI text
function extractJSON(text){
  if(!text || typeof text !== "string") return null;
  // 1) JSON fenced block
  let match = text.match(/```json([\s\S]*?)```/i);
  if(!match) match = text.match(/```([\s\S]*?)```/i);
  let candidate = match ? match[1] : text;
  // 2) try to find first {...} range
  const first = candidate.indexOf("{"), last = candidate.lastIndexOf("}");
  if(first !== -1 && last !== -1 && last > first) candidate = candidate.slice(first, last+1);
  // 3) Normalize line endings & common issues
  candidate = candidate.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  candidate = candidate.replace(/,\s*([\]}])/g, "$1"); // trailing commas
  // 4) Attempt parse, if fails try minor fixes
  try { return JSON.parse(candidate); }
  catch(e){
    // Replace unescaped newlines inside quotes (attempt)
    const t = candidate.replace(/"([^"]*)\n([^"]*)"/g, (m,a,b) => `"${a}\\n${b.replace(/\n/g,'\\n')}"`);
    try { return JSON.parse(t); } catch(e2){ return null; }
  }
}

// Fill meta fields and preview meta
function fillMeta(meta) {
  if(!meta) return;
  $("inp-fabricante").value = meta.fabricante || meta.manufacturer || meta.empresa || "";
  $("inp-short").value = meta.shortName || meta.shortname || meta.short || "";
  $("inp-version").value = meta.version || "";
  $("inp-title").value = meta.title || meta.titulo || "";
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

// Render files progressively
function renderFilesProgressive(files, folderBase){
  LAST_FILES = {};
  const container = $("preview-files");
  container.innerHTML = "";
  const filesProcessed = [];

  files.forEach(f => {
    const path = (f.path||"").replace("{folder}", folderBase).replace(/^\/+/, "");
    filesProcessed.push({ path, content: String(f.content || "") });
  });

  let i=0;
  function step(){
    if(i >= filesProcessed.length){ setStatus("Archivos listos"); $("btn-download").style.display = "inline-block"; return; }
    const f = filesProcessed[i];
    LAST_FILES[f.path] = f.content;
    const div = document.createElement("div");
    div.className = "file-card";
    div.innerHTML = `<div class="file-path">${f.path}</div><textarea class="file-edit" data-path="${f.path}">${f.content}</textarea>`;
    container.appendChild(div);
    const ta = div.querySelector(".file-edit");
    ta.addEventListener("input", ()=>{ LAST_FILES[ta.dataset.path] = ta.value; });
    i++;
    setStatus(`Generando archivos... (${i}/${filesProcessed.length})`);
    setTimeout(step, 100);
  }
  step();
}

// Download zip
async function downloadZIP(){
  const zip = new JSZip();
  // gather current edits
  document.querySelectorAll(".file-edit").forEach(ta => { LAST_FILES[ta.dataset.path] = ta.value; });
  for(const p in LAST_FILES) zip.file(p, LAST_FILES[p]);
  const folderName = Object.keys(LAST_FILES)[0]?.split("/")[0] || "package";
  const blob = await zip.generateAsync({type:"blob"});
  saveAs(blob, `${folderName}.iflapp`);
  setStatus(`ZIP generado: ${folderName}.iflapp`);
}

// Detect appid in querystring: supports ?in?appid=Entorno or ?appid=Entorno
function getQueryAppId(){
  const q = location.search || "";
  // support both ?in?appid=Entorno (literal) and normal ?appid=Entorno
  const qClean = q.replace(/^\?in\?/,"?");
  const params = new URLSearchParams(qClean);
  return params.get("appid");
}

// Environment detection & API key handling
async function getApiKeyOrUseBackend(){
  const isGithub = location.hostname.includes("github.io");
  if(!isGithub) return null; // use Netlify backend
  const cached = localStorage.getItem("gemini_api_key");
  if(cached) return cached;
  const ask = confirm("Parece que estás en GitHub Pages. ¿Deseas ingresar tu API Key de Gemini (se guardará localmente)?");
  if(!ask) throw new Error("No API key provided");
  const key = prompt("Introduce tu API key de Gemini (se guardará en su navegador):");
  if(!key) throw new Error("API key missing");
  localStorage.setItem("gemini_api_key", key.trim());
  return key.trim();
}

// Call AI: uses Netlify backend when available, otherwise direct Gemini with key (GitHub Pages)
async function callGenAI(prompt, mode="full", files=[]){
  const isGithub = location.hostname.includes("github.io");
  setStatus("Invocando IA...");
  if(isGithub){
    // direct call to Google Generative Language REST (requires API key)
    const key = await getApiKeyOrUseBackend();
    const endpoint = `https://generativelanguage.googleapis.com/v1beta2/models/gemini-2.5-flash:generateText?key=${encodeURIComponent(key)}`;
    // body shaped for text-bison-like endpoints
    const body = {
      prompt: { text: prompt },
      temperature: 0.7,
      candidate_count: 1,
      max_output_tokens: 2000
    };
    const r = await fetch(endpoint, { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(body) });
    const data = await r.json();
    const raw = data?.candidates?.[0]?.output || data?.candidates?.[0]?.content || JSON.stringify(data);
    const parsed = extractJSON(typeof raw === "string" ? raw : (raw[0]?.text || JSON.stringify(raw)));
    return parsed || { error: "No parseable JSON", raw };
  } else {
    // use Netlify function
    const r = await fetch(API_PATH, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ prompt, mode, files }) });
    const text = await r.text();
    try { return JSON.parse(text); } catch(e){ return extractJSON(text); }
  }
}

// Event wiring
$("btn-generate").addEventListener("click", async ()=>{
  const fabricante = $("inp-fabricante").value.trim() || "";
  const shortName = $("inp-short").value.trim() || "";
  const version = $("inp-version").value.trim() || "";
  const title = $("inp-title").value.trim() || "";
  const desc = $("inp-prompt").value.trim() || "";

  const prompt = `
Eres "Influent Package Maker", asistente enciclopédico para generar paquetes.
Usuario envía:
fabricante: ${fabricante}
shortName: ${shortName}
version: ${version}
title: ${title}
description: ${desc}

Devuelve SIEMPRE un JSON con:
{ "meta": { "fabricante","shortName","version","title","description" }, "files":[ {"path":"...","content":"..."}, ... ] }
Incluye archivos base: README.md, <shortName>.py, lib/requirements.txt, details.xml, autorun, autorun.bat, LICENSE, y contenedores en app/, assets/, config/, docs/, source/, lib/.
Escapa correctamente newlines y usa JSON válido.
`;

  try {
    const result = await callGenAI(prompt, "full");
    if(result?.error) throw new Error(result.error || "AI error");
    result.meta = result.meta || {};
    // fill fields
    fillMeta(result.meta);
    // compute folder name
    const empresa = (result.meta.fabricante || $("inp-fabricante").value || "default").toString().trim().toLowerCase().replace(/\s+/g,"-");
    const nombre = (result.meta.shortName || $("inp-short").value || "myapp").toString().trim().toLowerCase();
    const versionVal = result.meta.version || $("inp-version").value || "1.0.0";
    const folder = `${empresa}.${nombre}.v${versionVal}`;
    // render files progressively
    renderFilesProgressive(result.files || [], folder);
    $("ai-output").textContent = JSON.stringify(result, null, 2);
    setStatus("Listo");
  } catch(err){
    console.error(err);
    setStatus("Error: " + (err.message || err));
    $("ai-output").textContent = "Error: " + (err.message || JSON.stringify(err));
  }
});

$("btn-fast").addEventListener("click", async ()=>{
  const desc = $("inp-prompt").value.trim() || "Paquete rápido";
  setStatus("Modo rápido...");
  try {
    const result = await callGenAI(desc, "fast");
    if(result?.error) throw new Error(result.error || "AI error");
    fillMeta(result.meta || {});
    const empresa = (result.meta?.fabricante || "default").toString().trim().toLowerCase().replace(/\s+/g,"-");
    const nombre = (result.meta?.shortName || "quick").toString().trim().toLowerCase();
    const folder = `${empresa}.${nombre}.v${result.meta?.version || "1.0.0"}`;
    renderFilesProgressive(result.files || [], folder);
    $("ai-output").textContent = JSON.stringify(result, null, 2);
    setStatus("Listo (rápido)");
  } catch(err){ setStatus("Error: "+err.message); $("ai-output").textContent = "Error: "+err.message; }
});

$("btn-edit").addEventListener("click", async ()=>{
  // gather current files to send
  const files = [];
  document.querySelectorAll(".file-edit").forEach(ta => files.push({ path: ta.dataset.path, content: ta.value }));
  const desc = $("inp-prompt").value.trim() || "Edit files request";
  setStatus("Solicitando edición a IA...");
  try {
    const result = await callGenAI(`EDIT: ${desc}`, "edit", files);
    if(result?.files && Array.isArray(result.files)){
      // update editor areas if matches
      result.files.forEach(f=>{
        const ta = document.querySelector(`textarea[data-path="${f.path}"]`);
        if(ta) ta.value = f.content;
        LAST_FILES[f.path] = f.content;
      });
      $("ai-output").textContent = JSON.stringify(result, null, 2);
      setStatus("Edición completada.");
    } else throw new Error("Respuesta de edición inválida");
  } catch(err){ setStatus("Error: "+err.message); $("ai-output").textContent = "Error: "+err.message; }
});

$("btn-clear").addEventListener("click", ()=>{ $("preview-files").innerHTML = ""; $("ai-output").textContent = ""; LAST_FILES = {}; setStatus("limpio"); });
$("btn-download").addEventListener("click", downloadZIP);

// handle logout / cache clear
$("btnLogout").addEventListener("click", ()=>{ localStorage.removeItem("gemini_api_key"); alert("API key local eliminada"); location.reload(); });

// On load: check query param appid and auto-fill/auto-run if present
window.addEventListener("load", ()=>{
  const appid = getQueryAppId();
  if(appid){
    // autopopulate fabrica and shortName from appid
    $("inp-fabricante").value = "Environment";
    $("inp-short").value = appid;
    $("inp-title").value = appid;
    // auto trigger generation after small delay
    setTimeout(()=> $("btn-generate").click(), 800);
  }
});
