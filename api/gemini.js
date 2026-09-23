// Vercel serverless function: POST /api/gemini
// Needs env var GEMINI_API_KEY (Vercel > Project > Settings > Environment Variables).
const MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"];

const SCHEMA = {
    type: "OBJECT",
    properties: {
        healthScore: { type: "INTEGER" },
        status: { type: "STRING", enum: ["Healthy", "Watch", "Stressed", "Critical"] },
        summary: { type: "STRING" },
        confidence: { type: "STRING", enum: ["Low", "Medium", "High"] },
        risks: { type: "ARRAY", items: { type: "STRING" } },
        recommendations: { type: "ARRAY", items: { type: "STRING" } },
        nextChecks: { type: "ARRAY", items: { type: "STRING" } },
    },
    required: ["healthScore", "status", "summary", "confidence", "risks", "recommendations", "nextChecks"],
};

const SYSTEM = `You are an agronomy remote-sensing analyst for the Canopy vegetation-health dashboard.
Use ONLY the numbers provided. NDVI is an RGB/OSINT proxy, not a lab measurement: say so when it drives the conclusion.
If a value is null, say it is missing instead of guessing. Be specific to the crop and the weather values.
summary: max 3 sentences. risks, recommendations, nextChecks: 2-4 short items each.`;

async function callModel(model, key, prompt) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 20000);
    try {
        const r = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,
            {
                method: "POST",
                signal: ctrl.signal,
                headers: { "Content-Type": "application/json", "x-goog-api-key": key },
                body: JSON.stringify({
                    systemInstruction: { parts: [{ text: SYSTEM }] },
                    contents: [{ role: "user", parts: [{ text: prompt }] }],
                    generationConfig: {
                        temperature: 0.3,
                        responseMimeType: "application/json",
                        responseSchema: SCHEMA,
                    },
                }),
            }
        );
        const body = await r.json().catch(() => ({}));
        if (!r.ok) throw Object.assign(new Error(body?.error?.message || `HTTP ${r.status}`), { status: r.status });
        const text = body?.candidates?.[0]?.content?.parts?.map((p) => p.text || "").join("") || "";
        if (!text) throw new Error("Empty model response");
        return JSON.parse(text.replace(/```json|```/g, "").trim());
    } finally {
        clearTimeout(timer);
    }
}

export default async function handler(req, res) {
    res.setHeader("Cache-Control", "no-store");
    if (req.method !== "POST") return res.status(405).json({ error: "Use POST" });

    const key = process.env.GEMINI_API_KEY;
    if (!key) {
        return res.status(503).json({
            error: "GEMINI_API_KEY is not set on the server",
            fix: "Vercel > Settings > Environment Variables > add GEMINI_API_KEY, then redeploy",
        });
    }

    let p = req.body;
    if (typeof p === "string") { try { p = JSON.parse(p); } catch { p = null; } }
    if (!p || typeof p !== "object") return res.status(400).json({ error: "Body must be a JSON parcel object" });

    const prompt = `Analyse this parcel and return the JSON report.\n${JSON.stringify(p, null, 2)}`;
    const errors = [];
    for (const model of MODELS) {
        try {
            const report = await callModel(model, key, prompt);
            return res.status(200).json({ ok: true, model, report });
        } catch (e) {
            errors.push({ model, status: e.status || 0, message: String(e.message).slice(0, 300) });
            if (e.status === 400 || e.status === 403) break; // bad key / bad request: other models will fail too
        }
    }
    return res.status(502).json({ ok: false, error: "All Gemini models failed", details: errors });
}
