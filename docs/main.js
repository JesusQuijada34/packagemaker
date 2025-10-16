// main.js - frontend logic
const API_PATH = "/.netlify/functions/genai"; // Netlify function entrypoint
let LAST_FILES = {}; // path -> content

// helpers
function el(id){ return document.getElementById(id); }
function setStatus(s){ el("status").textContent = "Estado: " + s; }

// safe JSON parsing and extraction
function extractJSONFromText(text){
  // Try to find ```json ... ```
  const codeJson = /```json([\s\S]*?)```/i.exec(text);
  if(codeJson) text = codeJson[1];

  // If not, try triple backticks generic
  const codeBlock = /```([\s\S]*?)```/.exec(text);
  if(codeBlock) text = codeBlock[1];

  // Finally try to find first { ... } block
  const first = text.indexOf('{');
  const last = text.lastIndexOf('}');
  if(first !== -1 && last !== -1 && last > first){
    text = text.slice(first, last + 1);
  }

  // Try parsing, with some sanitizations
  try { return JSON.parse(text); }
  catch(e){
    // Heuristics: remove trailing commas, replace unescaped line breaks inside quotes
    let t = text.replace(/,\s*}/g, '}').replace(/,\s*]/g, ']');
    // Fix common unescaped newlines in strings: replace "line\nsomething" raw newlines with \n (best-effort)
    // This is risky but helps in many Gemini outputs
    t = t.replace(/"([^"]*)\n([^"]*)"/g, (m, a, b) => {
      return `"${a}\\n${b.replace(/\n/g,'\\n')}"`;
    });
    try { return JSON.parse(t); }
    catch(e2){
      console.warn("JSON parse failed:", e2);
      return null;
    }
  }
}

// render meta UI
function fillMeta(meta){
  if(!meta) return;
  el("inp-fabricante").value = meta.fabricante || meta.manufacturer || meta.empresa || "";
  el("inp-short").value = meta.shortName || meta.shortname || meta.short || "";
  el("inp-version").value = meta.version || "1.0.0";
  el("inp-title").value = meta.title || meta.titulo || "";
  // show structured meta block
  const container = el("preview-meta");
  container.innerHTML = `
    <div class="meta">
      <div><strong>Fabricante:</strong> ${meta.fabricante || meta.manufacturer || ""}</div>
      <div><strong>Short name:</strong> ${meta.shortName || meta.short || ""}</div>
      <div><strong>Versión:</strong> ${meta.version || ""}</div>
      <div><strong>Título:</strong> ${meta.title || ""}</div>
      <div style="color:var(--muted);font-size:0.9rem">${meta.description || ""}</div>
    </div>
  `;
}

// render files progressively (simulated streaming)
function renderFilesProgressive(files, folderBase){
  LAST_FILES = {};
  const container = el("preview-files");
  container.innerHTML = "";
  // Ensure folderBase present in file paths by replacing {folder} tokens if present
  for(const f of files) {
    const p = (f.path || "").replace("{folder}", folderBase);
    LAST_FILES[p] = ""; // fill later
  }

  // render incrementally with small delay to show progress
  let i = 0;
  function step(){
    if(i >= files.length) {
      setStatus("Archivos listos");
      // make download button visible
      return;
    }
    const f = files[i];
    const path = (f.path || "").replace("{folder}", folderBase);
    const content = String(f.content || "");
    LAST_FILES[path] = content;
    const div = document.createElement("div");
    div.className = "file-card";
    div.innerHTML = `
      <div class="file-path">${path}</div>
      <textarea class="file-edit" data-path="${path}">${content}</textarea>
    `;
    container.appendChild(div);

    // wire textarea update
    const ta = div.querySelector(".file-edit");
    ta.addEventListener("input", ()=>{ LAST_FILES[ta.dataset.path] = ta.value; });

    i++;
    // schedule next file (fast)
    setTimeout(step, 120);
    setStatus(`Generando archivos... (${i}/${files.length})`);
  }
  step();
}

// download zip
async function downloadZIP(){
  const zip = new JSZip();
  // update LAST_FILES from UI (ensure edits are captured)
  document.querySelectorAll(".file-edit").forEach(ta=>{
    LAST_FILES[ta.dataset.path] = ta.value;
  });
  for(const p in LAST_FILES){
    zip.file(p, LAST_FILES[p]);
  }
  const folderName = Object.keys(LAST_FILES)[0]?.split("/")[0] || "package";
  const blob = await zip.generateAsync({type:"blob"});
  saveAs(blob, `${folderName}.iflapp`);
  setStatus(`ZIP generado: ${folderName}.iflapp`);
}

// call backend and handle results
async function callGenAI(prompt, mode="full"){
  setStatus("Contactando IA...");
  try{
    const res = await fetch(API_PATH, {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify({ prompt, mode })
    });

    const text = await res.text();
    // Try to parse as JSON response first (Netlify function might return JSON directly)
    let parsed = null;
    try { parsed = JSON.parse(text); }
    catch(e){
      // Not pure JSON: try extract JSON from text block
      parsed = extractJSONFromText(text);
    }

    if(!parsed){
      throw new Error("La IA devolvió JSON inválido.");
    }

    // normalize meta keys
    parsed.meta = parsed.meta || {};
    parsed.files = parsed.files || [];

    // ensure default meta values if missing
    if(!parsed.meta.fabricante && el("inp-fabricante").value) parsed.meta.fabricante = el("inp-fabricante").value;
    if(!parsed.meta.shortName && el("inp-short").value) parsed.meta.shortName = el("inp-short").value;
    if(!parsed.meta.version && el("inp-version").value) parsed.meta.version = el("inp-version").value;
    if(!parsed.meta.title && el("inp-title").value) parsed.meta.title = el("inp-title").value;

    // compute folder name (match previous convention)
    const empresa = (parsed.meta.fabricante || "default").toString().trim().toLowerCase().replace(/\s+/g,"-");
    const nombre = (parsed.meta.shortName || "myapp").toString().trim().toLowerCase();
    const version = parsed.meta.version || "1.0.0";
    const folder = `${empresa}.${nombre}.v${version}`;

    // Fill meta inputs and preview
    fillMeta(parsed.meta);

    // Render files progressively
    renderFilesProgressive(parsed.files, folder);

    // show raw JSON on ai-output
    el("ai-output").textContent = JSON.stringify(parsed, null, 2);

    setStatus("Respuesta IA procesada.");
  } catch(err){
    console.error(err);
    setStatus("Error: " + err.message);
    el("ai-output").textContent = "Error: " + err.message;
  }
}

// event wiring
el("btn-generate").addEventListener("click", async ()=>{
  const fabricante = el("inp-fabricante").value;
  const shortName = el("inp-short").value;
  const version = el("inp-version").value;
  const title = el("inp-title").value;
  const desc = el("inp-prompt").value;

  const prompt = `Fabricante: ${fabricante}\nShortName: ${shortName}\nVersion: ${version}\nTitle: ${title}\nDescription: ${desc}`;
  await callGenAI(prompt, "full");
});

el("btn-edit").addEventListener("click", async ()=>{
  // collect current files to send for edit
  const filesToSend = [];
  document.querySelectorAll(".file-edit").forEach(ta=>{
    filesToSend.push({ path: ta.dataset.path, content: ta.value });
  });
  const desc = el("inp-prompt").value || "Mejorar según prompt";
  const payloadPrompt = `EDIT REQUEST:\nDescription: ${desc}\nUse current files to modify.`;
  setStatus("Solicitando edición a IA...");
  try{
    const res = await fetch(API_PATH, {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify({ prompt: payloadPrompt, mode: "edit", files: filesToSend })
    });
    const text = await res.text();
    let parsed = null;
    try { parsed = JSON.parse(text); } catch(e){ parsed = extractJSONFromText(text); }
    if(parsed && Array.isArray(parsed.files)){
      // update UI files
      parsed.files.forEach(f=>{
        const ta = document.querySelector(`textarea[data-path="${f.path}"]`);
        if(ta) ta.value = f.content;
        LAST_FILES[f.path] = f.content;
      });
      el("ai-output").textContent = JSON.stringify(parsed, null, 2);
      setStatus("Edición completada.");
    } else {
      throw new Error("Respuesta de edición inválida.");
    }
  } catch(err){
    console.error(err); setStatus("Error: "+err.message);
    el("ai-output").textContent = "Error: "+err.message;
  }
});

el("btn-download").addEventListener("click", downloadZIP);
el("btn-clear").addEventListener("click", ()=>{ el("ai-output").textContent = ""; el("preview-files").innerHTML = ""; LAST_FILES = {}; setStatus("limpio"); });

/* Initialize UI */
setStatus("listo");
