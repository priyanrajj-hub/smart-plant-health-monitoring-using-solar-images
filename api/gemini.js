// Minimal safe memory cache across invocations (Vercel Node.js Functions)
const requestSpamMap = new Map();

module.exports = async (req, res) => {
    try {
        const apiKey = process.env.GEMINI_API_KEY;

        // Check if API key is missing or invalid
        if (!apiKey || apiKey === '' || (typeof apiKey === 'string' && apiKey.includes('YOUR_API_KEY'))) {
            return res.status(503).json({ error: "API Key missing! Please configure GEMINI_API_KEY in Vercel Deployment Settings." });
        }

        // Basic Edge Rate-Limiting Protection (Max 2 requests per 10s per IP)
        const ip = req.headers['x-forwarded-for'] || 'anonymous';
        const now = Date.now();
        if (requestSpamMap.has(ip)) {
            const hits = requestSpamMap.get(ip);
            if (hits.length >= 2) {
                const oldest = hits[0];
                if (now - oldest < 10000) {
                    return res.status(429).json({ error: "Rate limit exceeded. Please wait 10 seconds." });
                } else {
                    hits.shift();
                }
            }
            hits.push(now);
        } else {
            requestSpamMap.set(ip, [now]);
        }

        // Memory cleanup to prevent small memory expansion
        if (requestSpamMap.size > 200) requestSpamMap.clear();

        const body = req.body;

        // Accept BOTH payload formats: { prompt: "..." } and { contents: [...] }
        let payload;
        if (body && body.contents) {
            // Frontend sends Gemini-native format — pass through directly
            payload = { contents: body.contents };
        } else if (body && body.prompt) {
            // Legacy format — wrap in Gemini structure
            payload = { contents: [{ parts: [{ text: body.prompt }] }] };
        } else {
            return res.status(400).json({ error: "Missing prompt or contents payload" });
        }

        // Use the explicit flash model per user instructions
        const modelUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;

        const response = await fetch(modelUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errBody = await response.text();
            console.error("Gemini upstream exception:", errBody);
            let errMsg = errBody;
            try {
                const parsed = JSON.parse(errBody);
                if (parsed.error && parsed.error.message) errMsg = parsed.error.message;
            } catch (ignore) { }
            return res.status(response.status).json({ error: "Upstream API Error: " + errMsg });
        }

        const data = await response.json();
        return res.status(200).json(data);

    } catch (e) {
        console.error("Critical Proxy Exception:", e);
        return res.status(500).json({ error: "Proxy Exception: " + (e.message || "Unknown error") });
    }
};
