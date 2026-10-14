// Vercel Serverless Function: POST /api/assistant
// Multilingual Plant Health AI Assistant powered by Google Gemini

const MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3-flash-preview",
    "gemini-3.5-flash"
];

const LANG_NAMES = {
    'en': 'English',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'bn': 'Bengali',
    'gu': 'Gujarati',
    'pa': 'Punjabi'
};

async function askGemini(prompt, userLang, telemetryContext) {
    const key = process.env.GEMINI_API_KEY;
    if (!key) return null;

    const langName = LANG_NAMES[userLang] || userLang || "English";
    const systemPrompt = `You are AGRI-JARVIS, an expert multilingual AI voice & agronomic intelligence assistant for the Canopy Smart Plant Health Monitoring platform.
Your task:
1. Speak warmly, clearly and concisely in ${langName} (unless user writes in another language).
2. Help farmers, agronomists, and researchers monitor crop vegetation, solar-induced chlorophyll / NDVI health, weather, soil moisture, and pest risks.
3. Keep answers under 3 sentences so it can be spoken smoothly via Text-to-Speech (TTS).
4. If current field context is given, cite the telemetry values (NDVI, temperature, moisture, health status).
Current Field Telemetry Context:
${telemetryContext ? JSON.stringify(telemetryContext) : "No active parcel polygon selected yet. Guide the user to draw a polygon or search a farmland."}`;

    for (const model of MODELS) {
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), 12000);
        try {
            const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(key)}`;
            const r = await fetch(url, {
                method: "POST",
                signal: ctrl.signal,
                headers: { "Content-Type": "application/json", "x-goog-api-key": key },
                body: JSON.stringify({
                    systemInstruction: { parts: [{ text: systemPrompt }] },
                    contents: [{ role: "user", parts: [{ text: prompt }] }],
                    generationConfig: { temperature: 0.3 }
                })
            });
            clearTimeout(timer);
            if (!r.ok) continue;
            const data = await r.json();
            const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
            if (text && text.trim()) {
                return { text: text.trim(), model };
            }
        } catch (_) {
            clearTimeout(timer);
        }
    }
    return null;
}

export default async function handler(req, res) {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        let body = req.body;
        if (typeof body === 'string') {
            try { body = JSON.parse(body); } catch (_) { body = {}; }
        }
        const userMessage = (body.message || '').trim();
        const userLang = body.lang || 'en';
        const telemetry = body.telemetry || null;
        const lower = userMessage.toLowerCase();

        let actions = [];

        // Check for quick navigation commands
        if (lower.includes("zoom in") || lower.includes("அருகில்") || lower.includes("अंदर") || lower.includes("பெரிதாக்கு")) {
            actions.push({ type: "zoom_map", level: 1 });
        } else if (lower.includes("zoom out") || lower.includes("வெளியே") || lower.includes("बाहर") || lower.includes("சிறிதாக்கு")) {
            actions.push({ type: "zoom_map", level: -1 });
        } else if (lower.includes("high risk") || lower.includes("खतरा") || lower.includes("ஆபத்து")) {
            actions.push({ type: "filter_by_risk", level: "High" });
        } else if (lower.includes("globe") || lower.includes("world") || lower.includes("பூமி") || lower.includes("ग़्लोब")) {
            actions.push({ type: "reset_globe" });
        }

        // Call Gemini for intelligent natural response
        let aiResult = null;
        if (userMessage) {
            aiResult = await askGemini(userMessage, userLang, telemetry);
        }

        let response_text = "";
        if (aiResult && aiResult.text) {
            response_text = aiResult.text;
        } else {
            // High quality localized fallbacks if network fails
            if (userLang === 'ta') {
                response_text = `வணக்கம்! நான் AGRI-JARVIS. தாவர ஆரோக்கியம் மற்றும் செயற்கைக்கோள் NDVI பகுப்பாய்வு கண்காணிக்க தயாராக உள்ளேன்.`;
            } else if (userLang === 'hi') {
                response_text = `नमस्ते! मैं AGRI-JARVIS हूँ। आपकी फसलों के स्वास्थ्य और NDVI निगरानी के लिए तैयार हूँ।`;
            } else if (userLang === 'te') {
                response_text = `నమస్కారం! నేను AGRI-JARVIS. పంట ఆరోగ్యం మరియు NDVI పర్యవేక్షణకు సిద్ధంగా ఉన్నాను.`;
            } else {
                response_text = `Hello! I am AGRI-JARVIS, your multilingual plant health AI assistant. I am monitoring live NDVI, vegetation canopy, and soil moisture telemetry.`;
            }
        }

        return res.status(200).json({
            text: response_text,
            actions: actions,
            model: aiResult ? aiResult.model : "fallback",
            lang: userLang
        });
    } catch (error) {
        return res.status(500).json({ error: 'Failed to process request', details: error.message });
    }
}
