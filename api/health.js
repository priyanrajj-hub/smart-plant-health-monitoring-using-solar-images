module.exports = async (req, res) => {
    // Standard Node.js Vercel Function
    const geminiKey = process.env.GEMINI_API_KEY;
    const sentinelKey = process.env.SENTINEL_HUB_SECRET;

    res.status(200).json({
        status: 'online',
        timestamp: new Date().toISOString(),
        integrations: {
            gemini_api: {
                configured: !!geminiKey,
                status: geminiKey ? "healthy" : "missing_credentials"
            },
            sentinel_api: {
                configured: !!sentinelKey,
                status: sentinelKey ? "healthy" : "missing_credentials"
            },
            database: {
                configured: false,
                status: "not_implemented"
            }
        }
    });
};
