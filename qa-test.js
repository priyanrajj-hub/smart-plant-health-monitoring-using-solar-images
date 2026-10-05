require('dotenv').config();
const http = require('http');

// Simple test to hit the local or direct logic of api/gemini.js
// Since it's a Vercel serverless function, we can import it and mock req/res.

async function runTests() {
    console.log("=== STARTING LOCAL QA DIAGNOSTICS ===");

    // We will dynamically import the handler
    const handler = (await import('./api/gemini.js')).default;

    const mockRes = () => {
        const res = {};
        res.status = (code) => { res.statusCode = code; return res; };
        res.json = (data) => { res.data = data; return res; };
        res.setHeader = () => { };
        return res;
    };

    const scenarios = [
        {
            name: "Building Test (English)",
            body: { entityType: "Building", ndvi: 0.12, temperature: 30, language: "English" }
        },
        {
            name: "Vegetation Test (English)",
            body: { entityType: "Vegetation", ndvi: 0.72, temperature: 25, cropType: "Wheat", language: "English" }
        },
        {
            name: "Farmland Multi-Lang Test (Tamil)",
            body: { entityType: "Vegetation", ndvi: 0.65, temperature: 28, cropType: "Rice", language: "Tamil" }
        },
        {
            name: "Water Body Test (Hindi)",
            body: { entityType: "Water Body", ndvi: -0.3, language: "Hindi" }
        }
    ];

    for (const s of scenarios) {
        console.log(`\nTesting Scenario: ${s.name}...`);
        const req = { method: 'POST', body: s.body };
        const res = mockRes();

        try {
            await handler(req, res);
            if (res.statusCode === 200 && res.data && res.data.report) {
                console.log(`✅ SUCCESS (${res.data.model})`);
                console.log(`   Status:       ${res.data.report.status}`);
                console.log(`   Health Score: ${res.data.report.healthScore}`);
                console.log(`   Summary:      ${res.data.report.summary}`);

                // Assertions
                if (s.body.entityType === 'Building' || s.body.entityType === 'Water Body') {
                    if (res.data.report.status !== 'Non-Vegetation' || res.data.report.healthScore !== 0) {
                        console.error(`❌ FAILED ASSERTION: Expected Non-Vegetation with score 0 for ${s.body.entityType}`);
                    }
                } else {
                    if (res.data.report.status === 'Non-Vegetation') {
                        console.error(`❌ FAILED ASSERTION: Vegetation falsely flagged as Non-Vegetation`);
                    }
                }
            } else {
                console.error(`❌ FAILED HTTP ${res.statusCode}:`, res.data);
            }
        } catch (err) {
            console.error(`❌ CATASTROPHIC ERROR:`, err);
        }
    }
    console.log("\n=== QA DIAGNOSTICS COMPLETE ===");
}

runTests();
