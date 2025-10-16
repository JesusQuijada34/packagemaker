/**************************************************************************
 * Influent Package Maker — Cliente Web con IA (Gemini 2.5 Flash + Image)
 * Modo Manual + Modo Inteligente
 * Autor: Jesús Quijada
 * -----------------------------------------------
 * Esta parte inicial maneja configuración general,
 * utilidades de hashing, sanitización y preparación del entorno.
 **************************************************************************/

const API_BASE = "/.netlify/functions/genai"; // punto de acceso backend IA

// Estado global
let LAST_FILES = {};
let IS_AI_MODE = false;

// Elementos del DOM
const statusEl = document.getElementById("status");
const previewEl = document.getElementById("preview-files");
const aiBtn = document.getElementById("btn-ai-generate");
const manualBtn = document.getElementById("btn-manual-generate");
const modeSwitch = document.getElementById("ai-switch");
const progressBar = document.getElementById("progress");

// Utilidad: obtener marca de versión
function getVersionStamp() {
  const d = new Date();
  return `${d.getFullYear().toString().slice(-2)}.${d.getMonth() + 1}-${d.getHours()}.${String(
    d.getMinutes()
  ).padStart(2, "0")}`;
}

// Hash SHA256 → string hexadecimal
async function sha256hex(msg) {
  const buf = new TextEncoder().encode(msg);
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

// Sanitiza contenido de archivos (básico)
function sanitizeContent(s) {
  if (!s) return s;
  return s
    .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, "")
    .replace(/<iframe[\s\S]*?>[\s\S]*?<\/iframe>/gi, "")
    .replace(/javascript:/gi, "");
}

// Aplicar progreso animado
function setProgress(percent, text = "") {
  progressBar.style.width = `${percent}%`;
  progressBar.textContent = text || `${percent}%`;
}

// Limpieza de interfaz
function clearPreview() {
  previewEl.innerHTML = "";
  LAST_FILES = {};
  setProgress(0);
  statusEl.textContent = "";
}

// Renderización de archivos en vista previa
function renderFiles(files, folderName) {
  previewEl.innerHTML = "";
  LAST_FILES = {};
  files.forEach((f) => {
    const path = (f.path || "").replace("{folder}", folderName);
    const content = sanitizeContent(String(f.content || ""));
    LAST_FILES[path] = content;
    const div = document.createElement("div");
    div.className = "file-entry";
    div.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
        <strong>${path}</strong>
        <span style="color:#6c757d;font-size:0.9rem">${path.split(".").pop()}</span>
      </div>
      <textarea class="file-edit" data-path="${path}">${content}</textarea>
    `;
    previewEl.appendChild(div);
  });

  // botón de descarga ZIP
  const btnWrap = document.createElement("div");
  btnWrap.style.marginTop = "10px";
  btnWrap.innerHTML = `<button id="btn-download" class="btn btn-primary">📦 Descargar paquete (.zip)</button>`;
  previewEl.appendChild(btnWrap);

  document.getElementById("btn-download").onclick = async () => {
    document.querySelectorAll(".file-edit").forEach((el) => {
      LAST_FILES[el.dataset.path] = el.value;
    });
    await generateZip(folderName);
  };
}

// Generar y descargar ZIP limpio
async function generateZip(folderBase) {
  const zip = new JSZip();

  for (const p in LAST_FILES) {
    const val = LAST_FILES[p];
    if (typeof val === "string") {
      zip.file(p, val);
    } else if (val instanceof Blob) {
      zip.file(p, val);
    }
  }

  const blob = await zip.generateAsync({ type: "blob" });
  saveAs(blob, `${folderBase}.zip`);
  statusEl.textContent = `✅ Paquete generado: ${folderBase}.zip`;
  setProgress(100, "Completado");
    }
/**************************************************************************
 * Parte 2 — Modo Manual
 * Genera la estructura base del paquete (idéntica al script packagemaker.py)
 * Incluye copia del ícono raw y LICENSE remoto.
 **************************************************************************/

async function generateManual() {
  clearPreview();
  IS_AI_MODE = false;
  setProgress(10, "Preparando estructura…");

  // Obtener campos
  const fabricante = document.getElementById("inp-fabricante").value.trim() || "influent-labs";
  const shortName = document.getElementById("inp-shortname").value.trim() || "myapp";
  const version = document.getElementById("inp-version").value.trim() || "1.0";
  const title = document.getElementById("inp-title").value.trim() || shortName.toUpperCase();
  const description = document.getElementById("inp-desc").value.trim() || "Aplicación generada con Influent Package Maker.";

  const folder = `${fabricante}.${shortName}.v${version}`;
  const hv = await sha256hex(`${fabricante}.${shortName}.v${version}`);

  const DEFAULT_FOLDERS = ["app", "assets", "config", "docs", "source", "lib"];
  const files = [];

  // Crear carpetas principales con su archivo .container
  DEFAULT_FOLDERS.forEach((f) => {
    files.push({
      path: `${folder}/${f}/.${f}-container`,
      content: `#store (sha256 hash):${f}/.${hv}`,
    });
  });

  setProgress(30, "Estructura base creada…");

  // Obtener LICENSE desde GitHub raw
  let license = "Licencia desconocida";
  try {
    const res = await fetch("https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/LICENSE");
    if (res.ok) license = await res.text();
  } catch (e) {
    console.warn("No se pudo obtener LICENSE remoto:", e);
  }

  // Obtener ícono raw (se añadirá en assets/product_logo.png)
  let iconBlob = null;
  try {
    const iconRes = await fetch("https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/app/app-icon.ico");
    if (iconRes.ok) iconBlob = await iconRes.blob();
  } catch (e) {
    console.warn("No se pudo obtener el ícono remoto:", e);
  }

  // Archivos base del paquete
  files.push({
    path: `${folder}/LICENSE`,
    content: license,
  });

  files.push({
    path: `${folder}/README.md`,
    content: `# ${title}\n\n${description}\n\nFabricante: ${fabricante}\nVersión: ${version}\n\nGenerado con Influent Package Maker.`,
  });

  files.push({
    path: `${folder}/${shortName}.py`,
    content: `#!/usr/bin/env python3
# publisher: ${fabricante}
# name: ${shortName}
# version: ${version}
print("Hello from ${title}!")`,
  });

  files.push({
    path: `${folder}/autorun.bat`,
    content: `@echo off
echo Iniciando ${shortName}...
pip install -r lib/requirements.txt
python ${shortName}.py
pause`,
  });

  files.push({
    path: `${folder}/autorun`,
    content: `#!/usr/bin/env sh
pip install -r "./lib/requirements.txt"
clear
python3 "./${shortName}.py"`,
  });

  files.push({
    path: `${folder}/lib/requirements.txt`,
    content: "# Dependencias del paquete\n",
  });

  // Archivo de detalles XML
  files.push({
    path: `${folder}/details.xml`,
    content: `<?xml version="1.0" encoding="UTF-8"?>
<app>
  <publisher>${fabricante}</publisher>
  <app>${shortName}</app>
  <name>${title}</name>
  <version>${version}</version>
  <desc>${description}</desc>
  <with>${navigator.platform}</with>
  <stamp>${getVersionStamp()}</stamp>
</app>`,
  });

  // Archivo de seguridad .storedetail
  files.push({
    path: `${folder}/.storedetail`,
    content: `# Package Hash ${hv}\n# Created at ${new Date().toISOString()}`,
  });

  // Añadir ícono como binario si existe
  if (iconBlob) {
    files.push({
      path: `${folder}/assets/product_logo.png`,
      content: iconBlob,
      isBinary: true,
    });
  }

  setProgress(80, "Verificando integridad…");

  // Validar que todos los archivos esenciales existen
  const essentialPaths = ["LICENSE", `${shortName}.py`, "README.md", "details.xml"];
  const missing = essentialPaths.filter((e) => !files.some((f) => f.path.endsWith(e)));
  if (missing.length) {
    statusEl.textContent = `⚠️ Faltan archivos esenciales: ${missing.join(", ")}`;
    return;
  }

  // Renderizar
  renderFiles(files, folder);
  statusEl.textContent = "✅ Estructura manual generada correctamente. Puedes editar y descargar.";
  setProgress(100, "Completado");
}

// Evento del botón manual
manualBtn.addEventListener("click", generateManual);
