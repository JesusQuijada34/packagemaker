const API_BASE = "/api/genai"; // backend Vercel con GEMINI_API_KEY

let LAST_FILES = {};

async function callBackendAI(prompt, mode, files) {
  const res = await fetch(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, mode, files })
  });
  if (!res.ok) throw new Error("Backend IA error: " + res.status);
  return res.json();
}

function sanitizeContent(s) {
  if (!s) return s;
  return s.replace(/<\s*script[\s\S]*?>[\s\S]*?<\/\s*script\s*>/gi, "")
          .replace(/<\s*iframe[\s\S]*?>[\s\S]*?<\/\s*iframe\s*>/gi, "")
          .replace(/javascript:/gi, "");
}

function applyGradient(meta){
  if(!meta?.colores) return;
  const c1 = meta.colores.primario || "#0366d6";
  const c2 = meta.colores.secundario || "#2ea44f";
  const bg = meta.colores.fondo || "#f4f6f8";
  document.documentElement.style.setProperty('--gradient-from', c1);
  document.documentElement.style.setProperty('--gradient-to', c2);
  document.documentElement.style.setProperty('--bg', bg);
}

function renderFiles(filesArray, folderName){
  LAST_FILES = {};
  const preview = document.getElementById("preview-files");
  preview.innerHTML = "";
  filesArray.forEach(f=>{
    const path = f.path.replace("{folder}", folderName);
    const content = sanitizeContent(f.content || "");
    LAST_FILES[path] = content;
    const div = document.createElement("div");
    div.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <strong>${path}</strong>
        <span class="muted">${path.split('.').pop()}</span>
      </div>
      <textarea class="file-edit" data-path="${path}">${content}</textarea>
    `;
    preview.appendChild(div);
  });
}

async function generate() {
  const prompt = document.getElementById("ai-prompt").value;
  if(!prompt) { alert("Escribe un prompt de IA"); return; }

  document.getElementById("status").textContent = "🤖 Generando con IA...";

  const empresa = document.getElementById("inp-empresa").value;
  const nombre = document.getElementById("inp-nombre").value;
  const version = document.getElementById("inp-version").value;
  const titulo = document.getElementById("inp-titulo").value;

  try{
    const parsed = await callBackendAI(prompt, "full", []);
    const folder = `${parsed.meta.empresa}.${parsed.meta.nombre}.v${parsed.meta.version}`;
    renderFiles(parsed.files, folder);
    applyGradient(parsed.meta);
    document.getElementById("status").textContent = "✅ Paquete generado por IA.";
    document.getElementById("ai-output").innerHTML = `<pre>${JSON.stringify(parsed,null,2)}</pre>`;
  } catch(e){
    document.getElementById("status").textContent = "Error IA: "+e.message;
  }
}

document.getElementById("btn-ai-run").addEventListener("click", generate);

document.getElementById("btn-download-zip").addEventListener("click", async ()=>{
  const zip = new JSZip();
  const folderName = Object.keys(LAST_FILES)[0]?.split("/")[0] || "project";
  Object.keys(LAST_FILES).forEach(p=> zip.file(p, LAST_FILES[p]));
  const blob = await zip.generateAsync({type:"blob"});
  saveAs(blob, `${folderName}.iflapp`);
  document.getElementById("status").textContent = `✅ ZIP generado: ${folderName}.iflapp`;
});
