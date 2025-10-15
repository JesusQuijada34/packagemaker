// TODO-EN-UNO PWA Influent Package Maker, crystal-glow + IA UI
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
document.querySelectorAll("nav button").forEach(btn=>{
  btn.onclick = ()=>{
    document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));
    document.getElementById("tab-"+btn.dataset.tab).classList.add("active");
    document.getElementById("status").textContent = btn.textContent;
  };
});
document.getElementById("platform").textContent = navigator.platform + " / " + navigator.userAgent;
// Crear Proyecto
function renderCreateTab() {
  const html = `
    <form id="create-form">
      <fieldset>
        <legend>Datos del Proyecto</legend>
        <label>Fabricante:<input name="empresa" required placeholder="Ejemplo: influent"></label>
        <label>Nombre interno:<input name="nombre" required placeholder="Ejemplo: mycoolapp"></label>
        <label>Versión:<input name="version" required placeholder="Ejemplo: 1.0"></label>
        <label>Título completo:<input name="titulo" required placeholder="Ejemplo: MyCoolApp"></label>
      </fieldset>
      <button type="submit" class="btn success">Crear Proyecto</button>
      <div id="create-status"></div>
    </form>
    <div>TELEGRAM: <a href="https://t.me/JesusQuijada34/" target="_blank">@JesusQuijada34</a></div>
  `;
  document.getElementById("tab-create").innerHTML = html;
  document.getElementById("create-form").onsubmit = async function(e) {
    e.preventDefault();
    const empresa = this.empresa.value.trim().toLowerCase().replace(/ /g,"-") || "influent";
    const nombre = this.nombre.value.trim().toLowerCase() || "mycoolapp";
    let version = this.version.value.trim();
    version = version ? `${version}-${getversion()}-danenone` : `1-${getversion()}-danenone`;
    const titulo = this.titulo.value || nombre.toUpperCase();
    const folder_name = `${empresa}.${nombre}.v${version}`;
    const hv = await sha256(`${empresa}.${nombre}.v${version}`);
    window.currentProject = {empresa, nombre, version, titulo, folder_name, hv};
    document.getElementById("create-status").innerHTML =
      `✅ Paquete creado en: ${folder_name}/<br>🔐 Protegido con sha256: ${hv}`;
    document.getElementById("status").textContent = "Proyecto creado!";
  };
}
renderCreateTab();
// Construir Paquete (ZIP)
function renderBuildTab() {
  const html = `
    <form id="build-form">
      <fieldset>
        <legend>Construir Paquete</legend>
        <label>Fabricante:<input name="empresa" required></label>
        <label>Nombre interno:<input name="nombre" required></label>
        <label>Versión:<input name="version" required></label>
        <label>Tipo:
          <select name="tipo">
            <option value="1">.iflapp NORMAL</option>
            <option value="2">.iflappb BUNDLE</option>
          </select>
        </label>
      </fieldset>
      <button type="submit" class="btn default">Construir paquete</button>
      <div id="build-status"></div>
    </form>
  `;
  document.getElementById("tab-build").innerHTML = html;
  document.getElementById("build-form").onsubmit = async function(e) {
    e.preventDefault();
    const empresa = this.empresa.value.trim().toLowerCase() || "influent";
    const nombre = this.nombre.value.trim().toLowerCase() || "mycoolapp";
    const version = this.version.value.trim() || "1";
    const tipo = this.tipo.value;
    const zip = new JSZip();
    const folder = `${empresa}.${nombre}.v${version}`;
    DEFAULT_FOLDERS.forEach(f=>zip.folder(`${folder}/${f}/`).file(`.${f}-container`,`#store (sha256 hash):${f}/.`));
    zip.file(`${folder}/LICENSE`,`GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007 ...`);
    zip.file(`${folder}/README.md`,`# ${empresa} ${nombre}\nPaquete generado con Influent Package Maker PWA.`);
    zip.file(`${folder}/${nombre}.py`,`#!/usr/bin/env python\n# ...\n# publisher: ${empresa}\n# name: ${nombre}\n# version: IO-${version}\n`);
    zip.file(`${folder}/autorun.bat`,`REM ...\npip install -r lib/requirements.txt\npython ${nombre}.py\n`);
    zip.file(`${folder}/autorun`,`#!/usr/bin/env sh\npip install -r "./lib/requirements.txt"\nclear\n/usr/bin/python3 "./${nombre}.py"\n`);
    zip.file(`${folder}/details.xml`,`<app>
  <publisher>${empresa}</publisher>
  <app>${nombre}</app>
  <name>${nombre}</name>
  <version>v${version}</version>
  <with>${navigator.platform}</with>
  <danenone>${getversion()}</danenone>
  <correlationid>${await sha256(folder)}</correlationid>
  <rate>Todas las edades</rate>
</app>`);
    zip.file(`${folder}/lib/requirements.txt`,`# Dependencias del paquete\n`);
    document.getElementById("build-status").textContent = "Empaquetando...";
    zip.generateAsync({type:"blob"}).then(blob=>{
      saveAs(blob, `${folder}${tipo==="1"?".iflapp":".iflappb"}`);
      document.getElementById("build-status").textContent = `Paquete construido: ${folder}${tipo==="1"?".iflapp":".iflappb"}`;
      document.getElementById("status").textContent = "Paquete descargado!";
    });
  };
}
renderBuildTab();
// Gestor de Proyectos (simulación memoria)
function renderManagerTab() {
  const html = `
    <div class="split">
      <div>
        <h3>Proyectos locales</h3>
        <ul id="projects-list"></ul>
      </div>
      <div>
        <h3>Apps instaladas</h3>
        <ul id="apps-list"></ul>
      </div>
    </div>
    <div>
      <button id="btn-refresh" class="btn info">Refrescar listas</button>
      <button id="btn-install" class="btn success">Instalar paquete</button>
      <button id="btn-uninstall" class="btn danger">Desinstalar paquete</button>
    </div>
    <div id="manager-status"></div>
  `;
  document.getElementById("tab-manager").innerHTML = html;
  let projects = window.projects || [];
  let apps = window.apps || [];
  function renderLists() {
    document.getElementById("projects-list").innerHTML = projects.map((p,i)=>
      `<li data-idx="${i}">${p.empresa} ${p.titulo} | ${p.version}</li>`).join("");
    document.getElementById("apps-list").innerHTML = apps.map((a,i)=>
      `<li data-idx="${i}">${a.empresa} ${a.titulo} | ${a.version}</li>`).join("");
  }
  renderLists();
  document.getElementById("btn-refresh").onclick = () => {
    renderLists();
    document.getElementById("manager-status").textContent = "Listas refrescadas!";
  };
  document.getElementById("btn-install").onclick = () => {
    if(window.currentProject) {
      apps.push({...window.currentProject});
      window.apps = apps;
      renderLists();
      document.getElementById("manager-status").textContent = "App instalada!";
    } else {
      document.getElementById("manager-status").textContent = "No hay proyecto para instalar.";
    }
  };
  document.getElementById("btn-uninstall").onclick = () => {
    if(apps.length>0) {
      apps.pop();
      window.apps = apps;
      renderLists();
      document.getElementById("manager-status").textContent = "App desinstalada!";
    } else {
      document.getElementById("manager-status").textContent = "No hay apps para desinstalar.";
    }
  };
}
renderManagerTab();
// About
function renderAboutTab() {
  document.getElementById("tab-about").innerHTML = `
    <b>Influent Package Suite Todo en Uno</b><br>
    Creador, empaquetador e instalador de proyectos Influent (.iflapp, .iflappb) para terminal y sistema.<br><br>
    <b>Funciones:</b>
    <ul>
      <li>Interfaz adaptable y moderna</li>
      <li>Gestor visual de proyectos y apps instaladas</li>
      <li>Instalación/Desinstalación fácil</li>
      <li>Construcción de paquetes protegidos</li>
      <li>Accesos directos y menú inicio en Windows</li>
      <li>Soporte para iconos y detalles personalizados</li>
      <li>Ejecuta scripts .py (simulado)</li>
      <li>Paneles ajustables y organización por pestañas</li>
    </ul>
    <b>Desarrollador:</b> <a href="https://t.me/JesusQuijada34/" target="_blank">Jesus Quijada (@JesusQuijada34)</a><br>
    <b>Colaborador:</b> <a href="https://t.me/MkelCT/" target="_blank">MkelCT18 (@MkelCT)</a><br>
    <b>GitHub:</b> <a href="https://github.com/jesusquijada34/packagemaker/" target="_blank">packagemaker</a><br>
  `;
}
renderAboutTab();
// Service Worker
if('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}
window.runCommand = function(cmd) {
  if(cmd === "build") renderBuildTab();
  if(cmd === "create") renderCreateTab();
  if(cmd === "manager") renderManagerTab();
  if(cmd === "about") renderAboutTab();
  }
