const RAW_ICON_URL = "https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/app/app-icon.ico";
const DEFAULT_FOLDERS = ["app","assets","config","docs","source","lib"];

function getversion() {
  const d = new Date();
  return `${d.getFullYear().toString().slice(-2)}.${(d.getMonth()+1)}-${d.getHours()}.${d.getMinutes()}`;
}
async function sha256(str) {
  const buf = new TextEncoder().encode(str);
  const hash = await window.crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash)).map(b=>b.toString(16).padStart(2,"0")).join("");
}

// ========== CREAR Y VERIFICAR PROYECTO ==========
let lastZip = null, lastFiles = null;

document.getElementById("create-form").onsubmit = async function(e){
  e.preventDefault();
  document.getElementById("btn-download").style.display = "none";
  document.getElementById("preview-files").textContent = "";
  document.getElementById("create-status").textContent = "Generando estructura...";
  let empresa = this.empresa.value.trim().toLowerCase().replace(/ /g,"-") || "influent";
  let nombre = this.nombre.value.trim().toLowerCase() || "mycoolapp";
  let version = this.version.value.trim();
  version = version ? `${version}-${getversion()}-danenone` : `1-${getversion()}-danenone`;
  let titulo = this.titulo.value.trim() || nombre.toUpperCase();
  let folder_name = `${empresa}.${nombre}.v${version}`;
  let hv = await sha256(`${empresa}.${nombre}.v${version}`);

  // Estructura
  const files = {};
  DEFAULT_FOLDERS.forEach(f=>{
    files[`${folder_name}/${f}/.${f}-container`] = `#store (sha256 hash):${f}/.${hv}`;
  });
  files[`${folder_name}/LICENSE`] = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007 ...";
  files[`${folder_name}/README.md`] = `# ${empresa} ${titulo}\nProyecto generado con Influent Package Maker Web.`;
  files[`${folder_name}/${nombre}.py`] = `#!/usr/bin/env python\n# publisher: ${empresa}\n# name: ${nombre}\n# version: IO-${version}\n`;
  files[`${folder_name}/autorun.bat`] = `REM\npip install -r lib/requirements.txt\npython ${nombre}.py\n`;
  files[`${folder_name}/autorun`] = `#!/usr/bin/env sh\npip install -r "./lib/requirements.txt"\nclear\n/usr/bin/python3 "./${nombre}.py"\n`;
  files[`${folder_name}/details.xml`] = `<app>
  <publisher>${empresa}</publisher>
  <app>${nombre}</app>
  <name>${titulo}</name>
  <version>v${version}</version>
  <with>${navigator.platform}</with>
  <danenone>${getversion()}</danenone>
  <correlationid>${hv}</correlationid>
  <rate>Todas las edades</rate>
</app>`;
  files[`${folder_name}/lib/requirements.txt`] = "# Dependencias del paquete\n";

  // Icono RAW .ico
  let iconBlob=null;
  try {
    let iconResp = await fetch(RAW_ICON_URL);
    if(iconResp.ok) iconBlob = await iconResp.blob();
  }catch(e){iconBlob=null;}
  if(iconBlob) files[`${folder_name}/app/app-icon.ico`] = iconBlob;

  // Previsualización (verificación antes de descarga)
  let html = `<b>Carpetas y archivos generados:</b><ul>`;
  Object.keys(files).forEach(f=>{
    let ext = f.split('.').pop();
    html += `<li>${f} ${ext==="ico"?"<span style='color:#0366d6;'>(icono RAW)</span>":""}</li>`;
  });
  html += `</ul><hr><b>Contenido de archivos (muestra):</b>`;
  Object.keys(files).forEach(f=>{
    if(typeof files[f] === "string" && f.endsWith(".py") || f.endsWith(".bat") || f.endsWith(".sh") || f.endsWith(".md") || f.endsWith(".xml")){
      html += `<details><summary>${f}</summary><pre style="white-space:pre-wrap;font-size:.96em;background:#fff;">${files[f]}</pre></details>`;
    }
  });
  document.getElementById("preview-files").innerHTML = html;
  document.getElementById("create-status").textContent = `✅ Verifica la estructura antes de descargar. SHA256: ${hv}`;
  document.getElementById("btn-download").style.display = "inline-block";
  lastFiles = files;
};

document.getElementById("btn-download").onclick = async function(){
  if(!lastFiles) return;
  document.getElementById("create-status").textContent = "Empaquetando ZIP...";
  const zip = new JSZip();
  for(const f in lastFiles){
    if(typeof lastFiles[f]==="string") zip.file(f, lastFiles[f]);
    else zip.file(f, lastFiles[f]); // Blob (icono)
  }
  let folder_name = Object.keys(lastFiles)[0].split("/")[0];
  zip.generateAsync({type:"blob"}).then(blob=>{
    saveAs(blob, `${folder_name}.iflapp`);
    document.getElementById("create-status").textContent = `ZIP descargado: ${folder_name}.iflapp`;
  });
};

// ========== INSTALAR / EXPLORAR ZIP ==========
document.getElementById("zipfile").onchange = function(e){
  const file = e.target.files[0];
  if(!file)return;
  document.getElementById("install-status").textContent = "Leyendo ZIP...";
  JSZip.loadAsync(file).then(async zip=>{
    let details = `<b>Contenido de "${file.name}"</b><ul>`;
    let xmlContent = "", iconUrl = "";
    for(const fname of Object.keys(zip.files)){
      details += `<li>${fname}${fname.endsWith(".ico")?" <span style='color:#0366d6;'>(icono)</span>":""}</li>`;
      if(fname.endsWith("details.xml")) xmlContent = await zip.file(fname).async("text");
      if(fname.endsWith("app-icon.ico")) iconUrl = URL.createObjectURL(await zip.file(fname).async("blob"));
    }
    details += "</ul>";
    if(xmlContent) details += "<hr><b>Details.xml:</b><pre style='white-space:pre-wrap;font-size:.96em;background:#fff;'>" + xmlContent + "</pre>";
    if(iconUrl) details += `<hr><b>Icono:</b><br><img src="${iconUrl}" style="width:38px;height:38px;border-radius:4px;border:1px solid #e1e4e8;">`;
    document.getElementById("zip-details").innerHTML = details;
    document.getElementById("install-status").textContent = "ZIP leído correctamente.";
  }).catch(()=>{
    document.getElementById("install-status").textContent = "Error: El archivo no es un ZIP válido.";
    document.getElementById("zip-details").textContent = "";
  });
};
