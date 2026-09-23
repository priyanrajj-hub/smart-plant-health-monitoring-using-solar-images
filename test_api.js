const places = [
    { name: 'Punjab Wheat Field (Healthy)', ndvi: 0.72 },
    { name: 'Maharashtra Sugarcane (Water Stressed)', ndvi: 0.38 },
    { name: 'Kerala Coconut Grove (Disease Risk)', ndvi: 0.55 },
    { name: 'Rajasthan Millet (Drought Warning)', ndvi: 0.18 },
    { name: 'UP Mustard Farm (Optimal)', ndvi: 0.65 }
];
(async () => {
    for (let p of places) {
        console.log('===', p.name, '|| NDVIProxy:', p.ndvi, '===');
        try {
            const res = await fetch('https://smart-plant-health-monitoring-using-solar-images.vercel.app/api/gemini', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: `You are the Canopy AI Agricultural Analyst. I just scanned a farm polygon using OSINT proxies. The Mean NDVI is ${p.ndvi}. Return your analysis STRICTLY as a JSON object with the following exact keys, and DO NOT wrap it in markdown code blocks: { \"summary\": \"overview...\", \"stress_severity\": \"...\", \"disease_risk_assessment\": \"...\", \"pest_risk_assessment\": \"...\", \"nutrient_stress_risk\": \"...\", \"irrigation_recommendation\": \"...\", \"climate_risk_flag\": \"...\", \"confidence_caveat\": \"...\" }`
                        }]
                    }]
                })
            });
            const data = await res.status;
            if (res.ok) {
                const json = await res.json();
                console.log(JSON.stringify(JSON.parse(json.text), null, 2));
            } else {
                const text = await res.text();
                console.log(`Failed! HTTP ${data}: ${text}`);
            }
        } catch (e) { console.error('Error:', e.message); }
        console.log('\n\n');
    }
})();
