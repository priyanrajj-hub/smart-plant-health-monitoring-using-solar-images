import re

def main():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # Target the manual CanopyAI patch that was incorrect
        content = content.replace("CanopyAI.run({\n                            lat: centerLat, \n                            lon: centerLng, \n                            ndvi: typeof ndvi === 'number' ? ndvi : null, \n                            temperature: currentTemp, \n                            sunlightHours: meteoData?.daily?.sunshine_duration?.[0] != null ? +(meteoData.daily.sunshine_duration[0] / 3600).toFixed(1) : null,\n                            uvIndex: meteoData?.daily?.uv_index_max?.[0] != null ? meteoData.daily.uv_index_max[0] : null,\n                            humidity: meteoData && meteoData.current ? meteoData.current.relative_humidity_2m : null,\n                            cropType: document.getElementById('inferred-crop-label') ? document.getElementById('inferred-crop-label').textContent.replace(' (user-confirmed)', '') : savedCrop || (inf && inf.best_guess) || \"Vegetation\",\n                            cropConfidence: inf ? inf.confidence : null,\n                            areaHa: areaHa\n                        });", '')

        content = content.replace("// Canopy AI Fetch\n                        ", "")
        
        # Replace the innerHTML insight thing
        target = r"""document\.getElementById\('p-insight'\)\.innerHTML = typeof DOMPurify !== 'undefined' \? DOMPurify.sanitize\(insight, \{ ALLOWED_TAGS: \['em', 'strong', 'span', 'br', 'div'\], ALLOWED_ATTR: \['style'\] \}\) : insight;"""
        
        replacement = """// Canopy AI integration
                        CanopyAI.run({
                            lat: centerLat,
                            lon: centerLng,
                            ndvi: typeof ndvi === 'number' ? ndvi : null,
                            temperature: typeof currentTemp !== 'undefined' ? currentTemp : null,
                            sunlightHours: (typeof meteoData !== 'undefined' && meteoData && meteoData.daily && meteoData.daily.sunshine_duration) ? +(meteoData.daily.sunshine_duration[0] / 3600).toFixed(1) : null,
                            uvIndex: (typeof meteoData !== 'undefined' && meteoData && meteoData.daily && meteoData.daily.uv_index_max) ? meteoData.daily.uv_index_max[0] : null,
                            humidity: (typeof meteoData !== 'undefined' && meteoData && meteoData.current) ? meteoData.current.relative_humidity_2m : null,
                            cropType: (typeof inf !== 'undefined' && inf && inf.best_guess) ? inf.best_guess : ((typeof savedCrop !== 'undefined' && savedCrop) ? savedCrop : 'Vegetation'),
                            cropConfidence: (typeof inf !== 'undefined' && inf) ? inf.confidence : null,
                            areaHa: typeof areaHa !== 'undefined' ? areaHa : null
                        });
                        
                        // We also call init at start
                        CanopyAI.init({ panel: "#p-insight" });
                        """
        
        content = re.sub(target, replacement, content)

        if '<script src="canopy-ai.js"></script>' not in content:
            content = content.replace('</body>', '    <script src="canopy-ai.js"></script>\n</body>')

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Done!")
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
