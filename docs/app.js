const btnGenerar = document.getElementById("btn-generar");
const btnLimpiar = document.getElementById("btn-limpiar");
const jsonOutput = document.getElementById("json-output");
const statusEl = document.getElementById("status");
const thinkingEl = document.getElementById("thinking");
const thinkingText = document.getElementById("thinking-text");
const previewFiles = document.getElementById("preview-files");
const btnDownload = document.getElementById("btn-download");

let API_URL = "/.netlify/functions/genai";

// Detectar GitHub Pages → pedir API key manual
if (location.hostname.includes("github.io")) {
  const storedKey = localStorage.getItem("GEMINI_API_KEY");
  if (!storedKey) {
    const key = prompt("Introduce tu clave de API de Gemini (Google AI Studio):");
    if (key) localStorage.setItem("GEMINI_API_KEY", key);
  }
  API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + localStorage.getItem("GEMINI_API_KEY");
}

function showThinking(msg = "Pensando...") {
  thinkingText.textContent = msg;
  thinkingEl.classList.remove("hidden");
}
function hideThinking() {
  thinkingEl.classList.add("hidden");
}

btnGenerar.onclick = async () => {
  const fabricante = document.getElementById("inp-fabricante").value;
  const shortName = document.getElementById("inp-short").value;
  const version = document.getElementById("inp-version").value;
  const title = document.getElementById("inp-titulo").value;
  const descripcion = document.getElementById("inp-descripcion").value;

  if (!descripcion.trim()) return alert("Por favor escribe una descripción del proyecto.");

  statusEl.textContent = "Enviando solicitud a IA...";
  showThinking("Analizando descripción...");

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: descripcion,
        mode: "full",
        meta: { fabricante, shortName, version, title }
      })
    });

    const data = await res.json();
    hideThinking();

    if (data.error) {
      statusEl.textContent = "❌ " + data.error;
      return;
    }

    if (data.thinking) {
      thinkingText.textContent = data.thinking;
      thinkingEl.classList.remove("hidden");
      setTimeout(() => thinkingEl.classList.add("hidden"), 4000);
    }

    const parsed = data.parsed || {};
    jsonOutput.textContent = JSON.stringify(parsed, null, 2);
    statusEl.textContent = "✅ Paquete generado por IA.";
    renderFiles(parsed.files);
  } catch (err) {
    hideThinking();
    statusEl.textContent = "❌ Error: " + err.message;
  }
};

btnLimpiar.onclick = () => {
  jsonOutput.textContent = "";
  previewFiles.innerHTML = "";
  statusEl.textContent = "";
  btnDownload.classList.add("hidden");
};

function renderFiles(files = []) {
  previewFiles.innerHTML = "";
  const zip = new JSZip();

  files.forEach((f) => {
    const div = document.createElement("div");
    div.innerHTML = `<strong>${f.path}</strong>`;
    const pre = document.createElement("textarea");
    pre.className = "preview";
    pre.value = f.content;
    div.appendChild(pre);
    previewFiles.appendChild(div);
    zip.file(f.path, f.content);
  });

  btnDownload.classList.remove("hidden");
  btnDownload.onclick = async () => {
    const blob = await zip.generateAsync({ type: "blob" });
    saveAs(blob, "package.iflapp");
  };
}
