import re
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update the AI Prompt so it doesn't output "Unavailable"
old_prompt = """{
  "summary": "one sentence overview of overall crop canopy health",
  "stress_severity": "Low | Moderate | High | Critical",
  "disease_risk_assessment": "estimated disease risk level based on environmental factors (e.g., fungal risk under high humidity) - Do not act as a diagnosis",
  "pest_risk_assessment": "estimated pest pressure level based on environment - Do not act as a diagnosis",
  "nutrient_stress_risk": "estimated nutrient stress risk level - Do not predict exact NPK values from NDVI alone",
  "irrigation_recommendation": "estimated water need based on current NDVI, rainfall deficit, and temperature",
  "climate_risk_flag": "flag drought/heat-wave/flood risk if current weather data crosses thresholds",
  "confidence_caveat": "AI-estimated reasoning based on telemetry, not direct sensor measurement — requires ground validation"
}"""

new_prompt = """{
  "summary": "one sentence overview of overall crop canopy health based on NDVI",
  "stress_severity": "Low | Moderate | High | Critical",
  "disease_risk_assessment": "ESTIMATE disease risk (Low/Moderate/High) derived from humidity/temp. DO NOT return 'Unavailable'.",
  "pest_risk_assessment": "ESTIMATE pest pressure (Low/Moderate/High) based on weather. DO NOT return 'Unavailable'.",
  "nutrient_stress_risk": "ESTIMATE nutrient risk (Low/Moderate/High) based on NDVI. DO NOT return 'Unavailable'.",
  "irrigation_recommendation": "recommendation based on current NDVI and rainfall deficit",
  "climate_risk_flag": "flag drought/heat-wave/flood risk if applicable",
  "confidence_caveat": "AI-estimated reasoning based on telemetry, not direct sensor measurement \u2014 requires ground validation"
}"""
c = c.replace(old_prompt, new_prompt)

# 2. Add an explicit error message instead of fake fallback text
old_fallback = """                            // Use the locally computed ndvi (never null at this point)
                            const safeNdvi = ndvi.toFixed(3);

                            // Determine health status from real computed values
                            let healthVerdict = "stable and within seasonal norms";
                            if (ndvi >= 0.6) healthVerdict = "vigorous with strong chlorophyll activity";
                            else if (ndvi >= 0.4) healthVerdict = "moderate with adequate vegetation cover";
                            else if (ndvi >= 0.2) healthVerdict = "showing signs of stress — sparse canopy detected";
                            else healthVerdict = "critically low — possible bare soil or severe degradation";

                            const sourceStr = isTimeout ? "Fallback logic — timeout" : "Fallback logic — AI service error";

                            insight = `AI insight unavailable. Showing rule-based data only: Computed NDVI of ${safeNdvi} indicates vegetation health is ${healthVerdict}. ` +
                                `<em style="font-size:11px; color:#8a7a63;">[Source: ${sourceStr}]</em>`;"""

new_fallback = """                            insight = `<div style="text-align:center; padding:15px; color:#ef4444; border:1px solid #ef4444; border-radius:4px;">
                                <strong style="display:block; margin-bottom:5px;">\u26A0 AI Analysis Unavailable</strong>
                                <span style="font-size:12px;">Failed to fetch intelligence. Please verify your connection or API keys.</span>
                                <br><br><span style="font-size:10px; color:#8a7a63;">(Error: ${e.message})</span>
                            </div>`;"""
                            
c = c.replace(old_fallback, new_fallback)

# 3. Clean up the manual fallback strings on lines 1319, 1329, 1339, 1349, 1357, 1365 to use JSON exactly
# "Unavailable" parsing logic is fine, we just instructed the prompt not to return it.
# We will clean up the logging timeout ms string based on the user's request.
c = c.replace("setTimeout(() => controller.abort(), 35000); // 35 seconds", "setTimeout(() => controller.abort(), 15000); // 15s wait max")
c = c.replace("isTimeout ? 'Fetch timeout after 35s' : e.message", "isTimeout ? 'Fetch timeout after 15s' : e.message")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
