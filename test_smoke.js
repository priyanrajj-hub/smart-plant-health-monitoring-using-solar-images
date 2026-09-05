/**
 * Smoke test: verifies the server boots, core routes respond,
 * and external API dependencies are reachable.
 */

const http = require('http');
const { spawn } = require('child_process');

let server;
let passed = 0;
let failed = 0;

function log(status, name, detail) {
    const icon = status === 'PASS' ? '[PASS]' : '[FAIL]';
    console.log(`  ${icon} ${name}: ${detail}`);
    if (status === 'PASS') passed++;
    else failed++;
}

function httpGet(url, timeoutMs = 8000) {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Timeout')), timeoutMs);
        const lib = url.startsWith('https') ? require('https') : http;
        lib.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                clearTimeout(timer);
                resolve({ status: res.statusCode, body: data });
            });
        }).on('error', (e) => {
            clearTimeout(timer);
            reject(e);
        });
    });
}

async function runTests() {
    console.log('\n=== Canopy Smoke Test Suite ===\n');

    try {
        const res = await httpGet('http://localhost:3000');
        if (res.status === 200 && res.body.includes('Canopy')) log('PASS', 'Server boot', `HTTP 200`);
        else log('FAIL', 'Server boot', `HTTP ${res.status}`);
    } catch (e) { log('FAIL', 'Server boot', e.message); }

    try {
        const res = await httpGet('http://localhost:3000');
        if (res.body.includes('purify.min.js')) log('PASS', 'DOMPurify CDN', 'Found');
        else log('FAIL', 'DOMPurify CDN', 'Not found');

        const checks = [
            { needle: '[OSINT Proxy]', label: 'NDVI proxy label' },
            { needle: '[Simulated]', label: 'Temporal simulated label' }
        ];
        for (const chk of checks) {
            if (res.body.includes(chk.needle)) log('PASS', chk.label, 'Honest label present');
            else log('FAIL', chk.label, 'Missing honest label');
        }

        if (res.body.includes('Recent Aerial Scan')) log('FAIL', 'Fake aerial scan claim', 'Still present');
        else log('PASS', 'Fake aerial scan claim', 'Removed');
    } catch (e) { log('FAIL', 'HTML Checks', e.message); }

    try {
        const res = await httpGet('http://localhost:3000/api/health');
        const data = JSON.parse(res.body);
        if (data.status === 'online') log('PASS', '/api/health route', 'Online');
        else log('FAIL', '/api/health route', 'Unexpected format');
    } catch (e) { log('FAIL', '/api/health route', e.message); }

    try {
        const res = await httpGet('https://api.open-meteo.com/v1/forecast?latitude=30.9&longitude=75.8&current=temperature_2m&timezone=auto');
        if (res.status === 200) log('PASS', 'Open-Meteo API', 'Reachable');
        else log('FAIL', 'Open-Meteo API', `HTTP ${res.status}`);
    } catch (e) { log('FAIL', 'Open-Meteo API', e.message); }

    try {
        const res = await httpGet('https://archive-api.open-meteo.com/v1/archive?latitude=30.9&longitude=75.8&daily=precipitation_sum&start_date=2023-08-20&end_date=2023-09-03&timezone=auto');
        if (res.status === 200) log('PASS', 'Archive API', 'Reachable');
        else log('FAIL', 'Archive API', `HTTP ${res.status}`);
    } catch (e) { log('FAIL', 'Archive API', e.message); }

    try {
        // Just checking reachability instead of heavy load query
        const res = await httpGet('https://overpass-api.de/api/status', 8000);
        if (res.status === 200) log('PASS', 'Overpass API', 'Reachable');
        else log('FAIL', 'Overpass API', `HTTP ${res.status}`);
    } catch (e) { log('FAIL', 'Overpass API', e.message); }

    console.log(`\n=== Results: ${passed} passed, ${failed} failed ===\n`);
    return failed === 0;
}

console.log('Starting server...');
server = spawn('node', ['server.js'], { cwd: __dirname });

setTimeout(async () => {
    const allPassed = await runTests();
    server.kill();
    process.exit(allPassed ? 0 : 1);
}, 2000);
