async function callAI(prompt, fast = false) {
  const response = await fetch("/.netlify/functions/genai", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, mode: fast ? "fast" : "full" })
  });
  return await response.json();
}

function updatePreview(obj) {
  const preview = document.getElementById("preview");
  preview.innerHTML = "";

  if (!obj || !obj.files) return;

  obj.files.forEach(f => {
    const div = document.createElement("div");
    div.innerHTML = `<strong>${f.path}</strong>\n<pre>${f.content}</pre>`;
    preview.appendChild(div);
  });
}

function autoFill(meta) {
  if (!meta) return;
  for (const key in meta) {
    const el = document.getElementById(key);
    if (el && !el.value) el.value = meta[key];
  }
}

document.getElementById("btnGenerate").onclick = async () => {
  const fabricante = fabricante.value.trim() || "Default Manufacturer";
  const shortName = shortName.value.trim() || "MyApp";
  const version = version.value.trim() || "1.0.0";
  const title = title.value.trim() || "Aplicación";
  const description = description.value.trim() || "Descripción predeterminada";
  const userPrompt = `
Fabricante: ${fabricante}
Nombre corto: ${shortName}
Versión: ${version}
Título: ${title}
Descripción: ${description}
`;

  status.textContent = "Generando paquete con IA...";
  const result = await callAI(userPrompt, false);
  updatePreview(result);
  autoFill(result.meta);
  status.textContent = "✅ Generación completada";
  btnDownload.style.display = "inline-block";
};

document.getElementById("btnFast").onclick = async () => {
  const desc = description.value.trim() || "Paquete vacío";
  status.textContent = "Modo rápido...";
  const result = await callAI(desc, true);
  updatePreview(result);
  autoFill(result.meta);
  status.textContent = "✅ Paquete rápido listo";
  btnDownload.style.display = "inline-block";
};
