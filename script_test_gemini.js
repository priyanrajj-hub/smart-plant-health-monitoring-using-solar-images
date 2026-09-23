require('dotenv').config({ path: '.env.local' });
const { GoogleGenAI } = require('@google/genai');

const runTests = async () => {
    // Determine active API key safely
    const apiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
    if (!apiKey) {
        console.error("No API key available in local environment!");
        return;
    }

    const ai = new GoogleGenAI({ apiKey });

    const places = [
        { name: "Punjab Wheat Field (Healthy)", ndvi: 0.72, desc: "High biomass, adequate moisture" },
        { name: "Maharashtra Sugarcane (Water Stressed)", ndvi: 0.38, desc: "Moderate canopy, rain deficit and high temp" },
        { name: "Kerala Coconut Grove (Disease Risk)", ndvi: 0.55, desc: "High humidity, localized browning" },
        { name: "Rajasthan Millet (Drought Warning)", ndvi: 0.18, desc: "Extremely sparse vegetation, dry" },
        { name: "UP Mustard Farm (Optimal)", ndvi: 0.65, desc: "Stable seasonal growth" }
    ];

    console.log("==========================================");
    console.log("CANOPY AI INSIGHTS: BATCH TESTING 5 PLACES");
    console.log("==========================================\n");

    for (let place of places) {
        console.log(`Analyzing: ${place.name} | Proxy NDVI: ${place.ndvi}`);

        const prompt = `You are the Canopy AI Agricultural Analyst. I just scanned a farm polygon using OSINT proxies. The Mean NDVI is ${place.ndvi.toFixed(3)}. Return your analysis STRICTLY as a JSON object with the following exact keys, and DO NOT wrap it in markdown code blocks:
{
  "summary": "one sentence overview of overall crop canopy health",
  "stress_severity": "Low | Moderate | High | Critical",
  "disease_risk_assessment": "estimated disease risk level based on environmental factors",
  "pest_risk_assessment": "estimated pest pressure level based on environment",
  "nutrient_stress_risk": "estimated nutrient stress risk level",
  "irrigation_recommendation": "estimated water need based on current NDVI",
  "climate_risk_flag": "flag drought/heat-wave/flood risk if current weather data crosses thresholds",
  "confidence_caveat": "AI-estimated reasoning based on telemetry, not direct sensor measurement — requires ground validation"
}`;

        try {
            const response = await ai.models.generateContent({
                model: 'gemini-2.5-flash',
                contents: prompt,
            });

            const rawStr = response.text;
            let cleanStr = rawStr.replace(/^```(json)?/, '').replace(/```$/, '').trim();
            const j = JSON.parse(cleanStr);
            console.log(JSON.stringify(j, null, 2));

        } catch (e) {
            console.error(`[ERROR] Gemini execution failed for ${place.name}:`, e.message);
        }
        console.log("\n------------------------------------------\n");
    }
};

runTests();
