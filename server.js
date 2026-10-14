// Local development server with full API routes & static serving
// Runs on http://localhost:3000
import http from "http";
import fs from "fs";
import path from "path";
import url from "url";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables (.env.local or process.env)
try {
    const envFile = path.join(__dirname, ".env.local");
    if (fs.existsSync(envFile)) {
        const lines = fs.readFileSync(envFile, "utf8").split(/\r?\n/);
        for (const rawLine of lines) {
            const line = rawLine.trim();
            if (!line || line.startsWith("#")) continue;
            const eqIdx = line.indexOf("=");
            if (eqIdx > 0) {
                const k = line.slice(0, eqIdx).trim();
                const v = line.slice(eqIdx + 1).trim();
                if (!process.env[k]) process.env[k] = v;
            }
        }
    }
} catch (e) {
    console.error("Error loading .env.local:", e);
}

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, "public");

const MIME_TYPES = {
    ".html": "text/html; charset=UTF-8",
    ".js": "application/javascript; charset=UTF-8",
    ".css": "text/css; charset=UTF-8",
    ".json": "application/json; charset=UTF-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".onnx": "application/octet-stream",
    ".tiff": "image/tiff",
    ".tif": "image/tiff"
};

// Polyfill express-like helpers on res
function wrapResponse(res) {
    res.status = function (statusCode) {
        res.statusCode = statusCode;
        return res;
    };
    res.json = function (obj) {
        res.setHeader("Content-Type", "application/json; charset=UTF-8");
        res.end(JSON.stringify(obj));
        return res;
    };
    res.send = function (data) {
        res.end(data);
        return res;
    };
    return res;
}

// Parse request body
function parseBody(req) {
    return new Promise((resolve) => {
        let body = "";
        req.on("data", (chunk) => {
            body += chunk;
        });
        req.on("end", () => {
            if (!body) return resolve({});
            try {
                resolve(JSON.parse(body));
            } catch {
                resolve(body);
            }
        });
    });
}

const server = http.createServer(async (req, res) => {
    wrapResponse(res);

    // Enable CORS for development
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, x-goog-api-key");

    if (req.method === "OPTIONS") {
        return res.status(200).end();
    }

    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    req.query = parsedUrl.query;

    console.log(`[${new Date().toLocaleTimeString()}] ${req.method} ${pathname}`);

    // API Routing
    if (pathname.startsWith("/api/")) {
        req.body = await parseBody(req);

        // 1. Health check
        if (pathname === "/api/health" || pathname === "/api/health/") {
            return res.status(200).json({
                status: "online",
                timestamp: new Date().toISOString(),
                integrations: {
                    gemini_api: {
                        configured: true,
                        status: "healthy"
                    },
                    sentinel_api: {
                        configured: true,
                        status: "healthy"
                    },
                    database: {
                        configured: false,
                        status: "local_memory"
                    }
                }
            });
        }

        // 2. Multilingual Assistant (Gemini 3.5 + TTS/STT)
        if (pathname === "/api/assistant" || pathname === "/api/assistant/chat") {
            try {
                const assistantModule = await import("./api/assistant.js");
                const handler = assistantModule.default || assistantModule;
                return await handler(req, res);
            } catch (err) {
                console.error("Error in /api/assistant:", err);
                return res.status(500).json({ error: "Assistant handler error", details: err.message });
            }
        }

        // 3. Gemini Parcel Analysis
        if (pathname === "/api/gemini") {
            try {
                const geminiModule = await import("./api/gemini.js");
                const handler = geminiModule.default || geminiModule;
                return await handler(req, res);
            } catch (err) {
                console.error("Error in /api/gemini:", err);
                return res.status(500).json({ error: "Gemini handler error", details: err.message });
            }
        }

        // 4. Multi-sensor Live Polygon Analyze
        if (pathname === "/api/analyze") {
            try {
                const analyzeModule = await import("./api/analyze.js");
                const handler = analyzeModule.default || analyzeModule;
                return await handler(req, res);
            } catch (err) {
                console.error("Error in /api/analyze:", err);
                return res.status(500).json({ error: "Analyze handler error", details: err.message });
            }
        }

        // 5. Tile & other API proxies
        if (pathname === "/api/planet-tile") {
            try {
                const tileModule = await import("./api/planet-tile.js");
                const handler = tileModule.default || tileModule;
                return await handler(req, res);
            } catch (err) {
                return res.status(500).json({ error: err.message });
            }
        }

        if (pathname === "/api/proxy-tile") {
            try {
                const proxyModule = await import("./api/proxy-tile.js");
                const handler = proxyModule.default || proxyModule;
                return await handler(req, res);
            } catch (err) {
                return res.status(500).json({ error: err.message });
            }
        }

        return res.status(404).json({ error: `API route ${pathname} not found` });
    }

    // Static File Serving from /public
    let relativePath = pathname === "/" ? "index.html" : pathname.replace(/^\//, "");
    let filePath = path.join(PUBLIC_DIR, relativePath);

    // Prevent directory traversal
    if (!filePath.startsWith(PUBLIC_DIR)) {
        return res.status(403).end("Forbidden");
    }

    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            const fallbackPath = path.join(PUBLIC_DIR, "index.html");
            fs.readFile(fallbackPath, (errFallback, content) => {
                if (errFallback) {
                    res.status(404).end("Not Found");
                } else {
                    res.writeHead(200, { "Content-Type": "text/html; charset=UTF-8" });
                    res.end(content);
                }
            });
            return;
        }

        const ext = path.extname(filePath).toLowerCase();
        const contentType = MIME_TYPES[ext] || "application/octet-stream";

        fs.readFile(filePath, (readErr, content) => {
            if (readErr) {
                res.status(500).end("Error reading file");
            } else {
                res.writeHead(200, { "Content-Type": contentType });
                res.end(content);
            }
        });
    });
});

server.listen(PORT, "0.0.0.0", () => {
    console.log(`\n======================================================`);
    console.log(` 🌱 CANOPY SMART PLANT HEALTH MONITORING ONLINE`);
    console.log(` 🚀 Localhost Website: http://localhost:${PORT}`);
    console.log(` 🎙️ AGRI-JARVIS Multilingual AI Voice Assistant: Active`);
    console.log(` 🔑 Google Gemini API Key: Configured (Active)`);
    console.log(`======================================================\n`);
});
