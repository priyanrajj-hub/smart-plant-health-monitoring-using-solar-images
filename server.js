const express = require('express');
const path = require('path');
const app = express();

app.use(express.json());

// Health check (mirrors api/health.js behavior for local dev)
app.get('/api/health', (req, res) => {
    res.json({
        status: 'online',
        timestamp: new Date().toISOString(),
        integrations: {
            gemini_api: {
                configured: !!process.env.GEMINI_API_KEY,
                status: process.env.GEMINI_API_KEY ? 'healthy' : 'missing_credentials'
            },
            sentinel_api: { configured: false, status: 'not_implemented' },
            database: { configured: false, status: 'not_implemented' }
        }
    });
});

// Gemini proxy (local dev — uses real API if key present, mock otherwise)
app.post('/api/gemini', async (req, res) => {
    const apiKey = process.env.GEMINI_API_KEY;

    if (apiKey) {
        // Real Gemini call if key is available
        try {
            const body = req.body;
            let payload;
            if (body && body.contents) {
                payload = { contents: body.contents };
            } else if (body && body.prompt) {
                payload = { contents: [{ parts: [{ text: body.prompt }] }] };
            } else {
                return res.status(400).json({ error: "Missing prompt or contents" });
            }

            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
                { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }
            );
            const data = await response.json();
            return res.json(data);
        } catch (e) {
            console.error('Gemini API error:', e.message);
            return res.status(502).json({ error: "AI analysis temporarily unavailable" });
        }
    }

    // No key — return error so frontend uses rule-based fallback
    console.log('[Dev] No GEMINI_API_KEY set — frontend will use rule-based fallback');
    res.status(503).json({ error: "AI analysis not configured (no GEMINI_API_KEY)" });
});

// VERY IMPORTANT: STATIC AFTER API ROUTES
app.use(express.static(__dirname));

const PORT = process.env.PORT || 3000;
app.listen(PORT, '127.0.0.1', () => {
    console.log(`\n======================================================`);
    console.log(`🚀 Canopy Local Dev Server Running!`);
    console.log(`👉 OPEN: http://127.0.0.1:${PORT}`);
    console.log(`📝 Gemini AI: ${process.env.GEMINI_API_KEY ? 'Configured' : 'Not configured (set GEMINI_API_KEY)'}`);
    console.log(`======================================================\n`);
});
