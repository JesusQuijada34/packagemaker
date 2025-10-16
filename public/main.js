document.getElementById("packageForm").addEventListener("submit", async (e) => {
  e.preventDefault(); // ← esto evita que la página se recargue

  const manufacturer = document.getElementById("manufacturer").value;
  const shortName = document.getElementById("shortName").value;
  const version = document.getElementById("version").value;
  const title = document.getElementById("title").value;
  const description = document.getElementById("description").value;

  const prompt = `
Fabricante: ${manufacturer}
Nombre corto: ${shortName}
Versión: ${version}
Título: ${title}
Descripción: ${description}
`;

  const resultArea = document.getElementById("resultArea");
  resultArea.textContent = "Generando con IA... ⏳";

  try {
    const res = await fetch("/.netlify/functions/genai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Error ${res.status}: ${text}`);
    }

    const data = await res.json();
    resultArea.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    resultArea.textContent = `❌ Error: ${err.message}`;
  }
});
