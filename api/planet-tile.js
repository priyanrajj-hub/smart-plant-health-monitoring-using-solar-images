// Vercel Serverless Function / Local Proxy: GET /api/planet-tile
// Proxies Planet tile requests or falls back smoothly to high-res global satellite tiles
export default async function handler(req, res) {
    const { x, y, z } = req.query;
    if (!x || !y || !z) return res.status(400).json({ error: "Missing xyz params" });

    const PLANET_KEY = process.env.PLANET_API_KEY || "PLAK755889448c664e4698de15b8272505a6";

    // Try Planet's active mosaics or fallback to high-resolution Google Hybrid / Esri tile
    const mosaicName = "global_monthly_2023_01_mosaic";
    const planetUrl = `https://tiles.planet.com/basemaps/v1/planet-tiles/${mosaicName}/gmap/${z}/${x}/${y}.png?api_key=${PLANET_KEY}`;

    try {
        let response = await fetch(planetUrl);

        // If Planet account doesn't have active paid Basemap subscription or 404s, fallback to high-res satellite tile
        if (!response.ok) {
            const fallbackSatellite = `https://mt1.google.com/vt/lyrs=y&x=${x}&y=${y}&z=${z}`;
            response = await fetch(fallbackSatellite);
        }

        if (!response.ok) {
            return res.status(response.status).json({ error: "Tile fetch failed" });
        }

        const arrayBuffer = await response.arrayBuffer();

        res.setHeader("Content-Type", response.headers.get("content-type") || "image/jpeg");
        res.setHeader("Access-Control-Allow-Origin", "*");
        res.setHeader("Cache-Control", "public, max-age=86400, s-maxage=86400");

        return res.status(200).send(Buffer.from(arrayBuffer));
    } catch (err) {
        console.error("Tile Proxy Error:", err);
        return res.status(500).json({ error: "Failed to proxy tile", details: err.message });
    }
}
