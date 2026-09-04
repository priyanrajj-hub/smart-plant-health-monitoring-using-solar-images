const http = require('http');
const { spawn } = require('child_process');
let server;
let passed = 0; let failed = 0;
function log(status, name, detail) {
    console.log(`  [${status}] ${name}: ${detail}`);
    status === 'PASS' ? passed++ : failed++;
}
function httpGet(url) {
    return new Promise((resolve) => {
        http.get(url, (res) => {
            let data = '';
            res.on('data', c => data += c);
            res.on('end', () => resolve({ status: res.statusCode, body: data }));
        }).on('error', () => resolve({ status: 500, body: '' }));
    });
}
async function runTests() {
    try {
        const r1 = await httpGet('http://localhost:3000');
        r1.status === 200 ? log('PASS', 'Server boot', '200 OK') : log('FAIL', 'Server boot', r1.status);

        let htmlOK = r1.body.includes('purify.min.js') && r1.body.includes('[OSINT Proxy]') && r1.body.includes('[Simulated]') && !r1.body.includes('Recent Aerial Scan');
        htmlOK ? log('PASS', 'HTML Honesty', 'All labels present') : log('FAIL', 'HTML Honesty', 'Labels missing');

        const r2 = await httpGet('http://localhost:3000/api/health');
        const data = JSON.parse(r2.body);
        data.status === 'online' ? log('PASS', 'API Health', 'Online') : log('FAIL', 'API Health', 'Error');
    } catch (e) {
        log('FAIL', 'Exception', e.message);
    }
    return failed === 0;
}
server = spawn('node', ['server.js'], { cwd: __dirname });
setTimeout(async () => {
    const ok = await runTests();
    server.kill();
    process.exit(ok ? 0 : 1);
}, 2000);
