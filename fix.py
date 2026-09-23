import re
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace("document.getElementById('p-error').textContent = '';", "safetxt('p-error', '');")
c = c.replace("document.getElementById('p-region-name').textContent = \"Parcel Analysis Complete\";", "safetxt('p-region-name', 'Parcel Analysis Complete');")
c = c.replace("document.getElementById('p-ndvi').textContent = typeof ndvi === 'number' ? ndvi.toFixed(3) : \"No data\";", "safetxt('p-ndvi', typeof ndvi === 'number' ? ndvi.toFixed(3) : 'No data');")
c = c.replace("document.getElementById('p-source').textContent = sourceString;", "safetxt('p-source', sourceString);")
c = c.replace("document.getElementById('p-temp').textContent = `${t}°C`;", "safetxt('p-temp', `${t}°C`);")
c = c.replace("document.getElementById('p-humidity').textContent = `${h}%`;", "safetxt('p-humidity', `${h}%`);")
c = c.replace("document.getElementById('p-sun').textContent = `${sunHours} Hours`;", "safetxt('p-sun', `${sunHours} Hours`);")
c = c.replace("document.getElementById('p-uv').textContent = meteoData.daily.uv_index_max[0];", "safetxt('p-uv', meteoData.daily.uv_index_max[0]);")
c = c.replace("document.getElementById('p-temp').textContent = 'Unavailable';", "safetxt('p-temp', 'Unavailable');")
c = c.replace("document.getElementById('p-humidity').textContent = 'Unavailable';", "safetxt('p-humidity', 'Unavailable');")
c = c.replace("document.getElementById('p-sun').textContent = 'Unavailable';", "safetxt('p-sun', 'Unavailable');")
c = c.replace("document.getElementById('p-uv').textContent = 'Unavailable';", "safetxt('p-uv', 'Unavailable');")
c = c.replace("document.getElementById('p-rainfall').textContent = totalRain + ' mm';", "safetxt('p-rainfall', totalRain + ' mm');")
c = c.replace("document.getElementById('p-badge-text').textContent = statusPhase.toUpperCase();", "safetxt('p-badge-text', statusPhase.toUpperCase());")
c = re.sub(r'document\.getElementById\(\'p-coords\'\)\.textContent = `(.*?)\`;', r"safetxt('p-coords', `\1`);", c)
c = c.replace("document.getElementById('p-region-name').textContent = \"Analyzing Geometry...\";", "safetxt('p-region-name', \"Analyzing Geometry...\");")
c = c.replace("document.getElementById('p-badge-text').textContent = \"Fetching Live Data...\";", "safetxt('p-badge-text', \"Fetching Live Data...\");")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
