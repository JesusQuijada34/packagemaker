let pyodide = null;
async function initPyodide() { pyodide = await loadPyodide(); }
initPyodide();

async function sha256Hex(str){
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,'0')).join('');
}

function getVersionTimestamp(){
  const now = new Date();
  return `${String(now.getFullYear()).slice(-2)}.${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getHours()).padStart(2,'0')}.${String(now.getMinutes()).padStart(2,'0')}`;
}

async function fetchRawText(url){
  const res = await fetch(url);
  return await res.text();
}

async function fetchRawBlob(url){
  const res = await fetch(url);
  return await res.blob();
}

document.getElementById('btnGenerate').addEventListener('click', async ()=>{
  const empresa = (document.getElementById('inputEmpresa').value.trim().toLowerCase().replace(/\s+/g,'-'))||'influent';
  const nombre = document.getElementById('inputNombre').value.trim().toLowerCase()||'mycoolapp';
  let versionInput = document.getElementById('inputVersion').value.trim();
  const titulo = document.getElementById('inputTitulo').value.trim()||nombre;
  const tipo = document.getElementById('selectTipo').value;

  const timestamp = getVersionTimestamp();
  const version = versionInput?`${versionInput}-${timestamp}-danenone`:`${timestamp}-danenone`;
  const folderName = `${empresa}.${nombre}.v${version}`;
  const fullName = `${empresa}.${nombre}.v${version}`;
  const hash = await sha256Hex(fullName);

  const zip = new JSZip();

  // carpetas por defecto
  const DEFAULT_FOLDERS = ["app","assets","config","docs","source","lib"];
  DEFAULT_FOLDERS.forEach(sub=>{
    zip.folder(`${folderName}/${sub}`);
    zip.file(`${folderName}/${sub}/.${sub}-container`, `#store hash:${hash}`);
  });

  // .storedetail
  zip.file(`${folderName}/.storedetail`, `#store detail\n${hash}`);

  // LICENSE
  const licenseText = await fetchRawText('https://raw.githubusercontent.com/JesusQuijada34/packagemaker/refs/heads/main/LICENSE');
  zip.file(`${folderName}/LICENSE`, licenseText);

  // icono
  const iconBlob = await fetchRawBlob('https://raw.githubusercontent.com/JesusQuijada34/packagemaker/refs/heads/main/app/app-icon.ico');
  zip.file(`${folderName}/app/app-icon.ico`, iconBlob);

  // autorun
  zip.file(`${folderName}/autorun.bat`, `@echo off\npython ${nombre}.py`);
  zip.file(`${folderName}/autorun`, `#!/usr/bin/env sh\npython3 ${nombre}.py`);

  // script principal
  zip.file(`${folderName}/${nombre}.py`, `print("Hola desde ${nombre}")`);

  // requirements.txt
  zip.file(`${folderName}/lib/requirements.txt`, "# Dependencias si aplica\n");

  // README.md
  zip.file(`${folderName}/README.md`, `# ${empresa} - ${titulo}\n\nPaquete generado con PackageMaker Web.`);

  // details.xml
  const xmlParts = [
    `<app>`,
    `  <publisher>${empresa.charAt(0).toUpperCase()+empresa.slice(1)}</publisher>`,
    `  <app>${nombre}</app>`,
    `  <name>${titulo}</name>`,
    `  <version>v${version}</version>`,
    `  <with>${navigator.platform}</with>`,
    `  <danenone>${timestamp}</danenone>`,
    `  <correlationid>${hash}</correlationid>`,
    `  <rate>Todas las edades</rate>`,
    `</app>`
  ];
  zip.file(`${folderName}/details.xml`, xmlParts.join("\n"));

  // generar ZIP
  const blob = await zip.generateAsync({type:'blob', compression:"DEFLATE"});
  const ext = tipo==='bundled'?'.iflappb':'.iflapp';
  saveAs(blob, `${folderName}${ext}`);

  document.getElementById('status').textContent = `Paquete generado: ${folderName}${ext}`;
});

// ejecutar Python
document.getElementById('btnRunPython').addEventListener('click', async ()=>{
  if(!pyodide){ document.getElementById('pyOutput').textContent='Pyodide no cargado aún.'; return; }
  const nombre = document.getElementById('inputNombre').value.trim().toLowerCase()||'mycoolapp';
  const code = `print("Ejecutando script: ${nombre}.py")`;
  try{
    const output = await pyodide.runPythonAsync(code);
    document.getElementById('pyOutput').textContent = output;
  }catch(e){ document.getElementById('pyOutput').textContent = e;}
});
    
