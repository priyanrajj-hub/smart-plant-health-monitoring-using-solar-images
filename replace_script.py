import re

def main():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix textContent
        content = re.sub(r"document\.getElementById\((['\"])(.*?)\1\)\.textContent\s*=\s*([^;\n]+);", r"CanopyAI.setText(\1\2\1, \3);", content)

        # Replace Gemini Fetch block
        start_marker = "// SERVERLESS GEMINI FETCH (Secure Edge Endpoint)"
        end_marker = "clearInterval(aiTimerInterval);"
        
        idx_start = content.find(start_marker)
        idx_end = content.find(end_marker, idx_start)
        
        if idx_start != -1 and idx_end != -1:
            idx_end += len(end_marker)
            
            replacement = """// Canopy AI Fetch
                        CanopyAI.run({
                            lat: centerLat, 
                            lon: centerLng, 
                            ndvi: typeof ndvi === 'number' ? ndvi : null, 
                            temperature: currentTemp, 
                            sunlightHours: meteoData?.daily?.sunshine_duration?.[0] != null ? +(meteoData.daily.sunshine_duration[0] / 3600).toFixed(1) : null,
                            uvIndex: meteoData?.daily?.uv_index_max?.[0] != null ? meteoData.daily.uv_index_max[0] : null,
                            humidity: meteoData && meteoData.current ? meteoData.current.relative_humidity_2m : null,
                            cropType: document.getElementById('inferred-crop-label') ? document.getElementById('inferred-crop-label').textContent.replace(' (user-confirmed)', '') : savedCrop || (inf && inf.best_guess) || "Vegetation",
                            cropConfidence: inf ? inf.confidence : null,
                            areaHa: areaHa
                        });
                        """
            
            # The canopyAI needs cropType properly. Since we don't have inf exactly available down there without scope issues, let's use the local variables we already collected.
            
            content = content[:idx_start] + replacement + "\n" + content[idx_end:]
            print("Successfully replaced Gemini API block with CanopyAI.run")
        else:
            print("Could not find Gemini block markers.")

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
