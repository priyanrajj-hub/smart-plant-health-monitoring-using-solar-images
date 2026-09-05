module.exports = async function (req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    try {
        const { lat, lng } = req.body;

        if (!lat || !lng) {
            return res.status(400).json({ error: 'Missing coordinates (lat, lng)' });
        }

        const bbox = `${lat - 0.005},${lng - 0.005},${lat + 0.005},${lng + 0.005}`;
        const overpassQuery = `https://overpass-api.de/api/interpreter?data=[out:json];node(${bbox})["landuse"];way(${bbox})["landuse"];out;`;

        const response = await fetch(overpassQuery, {
            headers: {
                'User-Agent': 'SmartPlantHealthMonitoring/1.0 (Research Hackathon SIH26180)'
            }
        });

        if (!response.ok) {
            throw new Error(`Overpass API responded with status: ${response.status}`);
        }

        const data = await response.json();
        return res.status(200).json(data);
    } catch (err) {
        console.error("OSM Lookup Proxy Error:", err);
        return res.status(502).json({ error: 'Upstream Overpass API failure', details: err.message });
    }
};
