export default function handler(req, res) {
  res.status(200).json({ 
    API_BASE: process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}/api/genai` : "http://localhost:3000/api/genai" 
  });
}
