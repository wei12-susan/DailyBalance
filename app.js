// Local-only HTTP server for the browser based daily journal.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');

const port = Number(process.env.JOURNAL_PORT || 38472);
const host = '127.0.0.1';
const dataPath = path.resolve(process.env.JOURNAL_DATA_FILE || path.join(__dirname, 'data.json'));
const foodsPath = path.join(__dirname, 'foods.local.json');
const pagePath = path.join(__dirname, 'index.html');
let foodsCache;

function loadFoods() {
  if (foodsCache) return foodsCache;
  try { foodsCache = JSON.parse(fs.readFileSync(foodsPath, 'utf8')); }
  catch { foodsCache = []; }
  return foodsCache;
}

function send(res, status, body, type = 'application/json; charset=utf-8') {
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' });
  res.end(body);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${host}:${port}`);
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
  if (req.method === 'GET' && url.pathname === '/api/foods/search') {
    const query = (url.searchParams.get('q') || '').trim().toLowerCase();
    if (!query) return send(res, 200, JSON.stringify({ foods: [], databaseAvailable: loadFoods().length > 0 }));
    const foods = loadFoods();
    const normalize = value => String(value || '').toLowerCase().replace(/[\s（）()，,、·.-]/g, '');
    const q = normalize(query);
    const aliases = {
      '白米饭': ['米饭'], '米饭': ['米饭(蒸，代表值)', '米饭(蒸，粳米)'], '大米': ['稻米'],
      '红薯': ['甘薯'], '地瓜': ['甘薯'], '土豆': ['马铃薯'], '西红柿': ['番茄'],
      '鸡胸肉': ['鸡胸脯肉', '鸡肉'], '鸡胸': ['鸡胸脯肉', '鸡肉'], '瘦牛肉': ['牛肉'],
      '猪瘦肉': ['猪肉'], '三文鱼': ['鲑鱼'], '燕麦片': ['燕麦']
    };
    const terms = [q, ...(aliases[query] || []).map(normalize)];
    const results = foods.map(food => {
      const name = normalize(food.name);
      const score = Math.max(...terms.map(term => name === term ? 100 : name.startsWith(term) ? 80 : name.includes(term) ? 60 : term.includes(name) ? 40 : 0));
      return { ...food, score };
    }).filter(food => food.score > 0).sort((a, b) => b.score - a.score || a.name.length - b.name.length).slice(0, 20).map(({ score, ...food }) => food);
    return send(res, 200, JSON.stringify({ foods: results, databaseAvailable: foods.length > 0 }));
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
