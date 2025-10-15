// Estilo GitHub, iconos y assets desde RAW GitHub, flujo simple y serio

const DEFAULT_FOLDERS = ["app","assets","config","docs","source","lib"];

function getversion() {
  const d = new Date();
  return `${d.getFullYear().toString().slice(-2)}.${(d.getMonth()+1)}-${d.getHours()}.${d.getMinutes()}`;
}
async function sha256(str) {
  const buf = new TextEncoder().encode(str);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash)).map(b=>b.toString(16).padStart(2,"0")).join("");
}

// Mostrar plataforma
document.getElementById("platform").textContent = navigator.platform;

// Crear y descargar proyecto ZIP
document.getElementById("create-form").onsubmit = async function(e) {
  e.preventDefault();
  const empresa = this.empresa.value.trim().toLowerCase().replace(/ /g,"-") || "influent";
  const nombre = this.nombre.value.trim().toLowerCase() || "mycoolapp";
  let version = this.version.value.trim();
  version = version ? `${version}-${getversion()}-danenone` : `1-${getversion()}-danenone`;
  const titulo = this.titulo.value || nombre.toUpperCase();
  const folder_name = `${empresa}.${nombre}.v${version}`;
  const hv = await sha256(`${empresa}.${nombre}.v${version}`);

  // Crear ZIP
  const zip = new JSZip();
  DEFAULT_FOLDERS.forEach(f=>zip.folder(`${folder_name}/${f}/`).file(`.${f}-container`,`#store (sha256 hash):${f}/.`));
  zip.file(`${folder_name}/LICENSE`,`GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007 ...`);
  zip.file(`${folder_name}/README.md`,`# ${empresa} ${titulo}\nPaquete generado con Influent Package Maker.\n`);
  zip.file(`${folder_name}/${nombre}.py`,`#!/usr/bin/env python\n# publisher: ${empresa}\n# name: ${nombre}\n# version: IO-${version}\n`);
  zip.file(`${folder_name}/autorun.bat`,`REM\npip install -r lib/requirements.txt\npython ${nombre}.py\n`);
  zip.file(`${folder_name}/autorun`,`#!/usr/bin/env sh\npip install -r "./lib/requirements.txt"\nclear\n/usr/bin/python3 "./${nombre}.py"\n`);
  zip.file(`${folder_name}/details.xml`,`<app>
  <publisher>${empresa}</publisher>
  <app>${nombre}</app>
  <name>${titulo}</name>
  <version>v${version}</version>
  <with>${navigator.platform}</with>
  <danenone>${getversion()}</danenone>
  <correlationid>${hv}</correlationid>
  <rate>Todas las edades</rate>
</app>`);
  zip.file(`${folder_name}/lib/requirements.txt`,`# Dependencias del paquete\n`);
  // Icono desde RAW github
  try {
    const iconUrl = "https://raw.githubusercontent.com/JesusQuijada34/packagemaker/main/assets/product_logo.png";
    const iconResp = await fetch(iconUrl);
    if (iconResp.ok) {
      const iconBlob = await iconResp.blob();
      zip.file(`${folder_name}/app/app-icon.png`, iconBlob);
    }
  } catch(e){/*ignorar error de icono*/}

  document.getElementById("create-status").textContent = "Empaquetando proyecto...";
  zip.generateAsync({type:"blob"}).then(blob=>{
    saveAs(blob, `${folder_name}.iflapp`);
    document.getElementById("create-status").innerHTML =
      `✅ Proyecto compilado y descargado:<br>${folder_name}.iflapp<br>🔐 SHA256: ${hv}`;
    document.getElementById("create-form").reset();
  });
};

// Instalar y explorar ZIP
document.getElementById("install-form").packagefile.onchange = function(e) {
  const file = e.target.files[0];
  if (!file) return;
  document.getElementById("install-status").textContent = "Procesando paquete ZIP...";
  JSZip.loadAsync(file).then(async zip => {
    let details = `<b>Contenido de "${file.name}"</b><ul>`;
    let xmlContent = "";
    let iconUrl = "";
    for (const fname of Object.keys(zip.files)) {
      details += `<li>${fname}</li>`;
      // Buscar details.xml y app-icon
      if(fname.endsWith("details.xml")) {
        xmlContent = await zip.file(fname).async("text");
      }
      if(fname.endsWith("app-icon.png") || fname.endsWith("app-icon.ico")) {
        iconUrl = URL.createObjectURL(await zip.file(fname).async("blob"));
      }
    }
    details += "</ul>";
    if (xmlContent) {
      details += "<hr><b>Detalles del paquete:</b><br>";
      details += `<pre style="white-space:pre-wrap">${xmlContent}</pre>`;
    }
    if (iconUrl) {
      details += `<hr><b>Icono del paquete:</b><br><img src="${iconUrl}" alt="icon" style="width:64px;height:64px;border-radius:6px;border:1px solid #e1e4e8;">`;
    }
    document.getElementById("zip-details").innerHTML = details;
    document.getElementById("install-status").textContent = "Paquete cargado.";
  }).catch(()=>{
    document.getElementById("install-status").textContent = "Error: El archivo no es un ZIP válido o está dañado.";
    document.getElementById("zip-details").textContent = "";
  });
};

// Service Worker para PWA básico
if('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
                             }
