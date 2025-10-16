// api/config.js
export default function handler(req, res) {
  // Devuelve la URL del backend que tu frontend usará para IA
  res.status(200).json({ API_BASE: process.env.API_BASE });
}
