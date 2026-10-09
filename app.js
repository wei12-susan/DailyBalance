// Local-only HTTP server for the browser based daily journal.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');

const port = Number(process.env.JOURNAL_PORT || 38471);
const host = '127.0.0.1';
const dataPath = path.resolve(process.env.JOURNAL_DATA_FILE || path.join(__dirname, 'data.json'));
const pagePath = path.join(__dirname, 'index.html');

function send(res, status, body, type = 'application/json; charset=utf-8') {
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' });
  res.end(body);
}

const server = http.createServer((req, res) => {
  if (req.method === 'GET' && req.url === '/') {
    return fs.readFile(pagePath, (err, html) => err
      ? send(res, 500, JSON.stringify({ error: '网页文件读取失败' }))
      : send(res, 200, html, 'text/html; charset=utf-8'));
  }
  if (req.method === 'GET' && req.url === '/api/data') {
    return fs.readFile(dataPath, 'utf8', (err, text) => {
      if (!err) return send(res, 200, text);
      if (err.code === 'ENOENT') return send(res, 200, JSON.stringify({ settings: { calories: 2000, protein: 140 }, meals: [], training: [], wellness: [] }));
      return send(res, 500, JSON.stringify({ error: '本地数据读取失败' }));
    });
  }
  if (req.method === 'POST' && req.url === '/api/data') {
    let body = '';
    req.setEncoding('utf8');
    req.on('data', chunk => { body += chunk; if (body.length > 5_000_000) req.destroy(); });
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        if (!data || typeof data !== 'object' || !Array.isArray(data.meals) || !Array.isArray(data.training) || !Array.isArray(data.wellness)) throw new Error('bad data');
        fs.writeFile(dataPath, JSON.stringify(data, null, 2), 'utf8', err => err
          ? send(res, 500, JSON.stringify({ error: '保存失败' }))
          : send(res, 200, JSON.stringify({ ok: true })));
      } catch {
        send(res, 400, JSON.stringify({ error: '数据格式无效' }));
      }
    });
    return;
  }
  send(res, 404, JSON.stringify({ error: 'not found' }));
});

server.on('error', err => {
  if (err.code === 'EADDRINUSE') {
    spawn('cmd.exe', ['/c', 'start', '', `http://${host}:${port}`], { windowsHide: true, stdio: 'ignore' });
    setTimeout(() => process.exit(0), 500);
  } else {
    console.error(err);
    process.exit(1);
  }
});

server.listen(port, host, () => {
  spawn('cmd.exe', ['/c', 'start', '', `http://${host}:${port}`], { windowsHide: true, stdio: 'ignore' });
});

process.on('SIGINT', () => server.close(() => process.exit(0)));
process.on('SIGTERM', () => server.close(() => process.exit(0)));
