// 用页面里真实的 richText 逻辑渲染几道带代码的题，检查输出是否成块
const fs = require('fs');

const html = fs.readFileSync('E:/CST/408/out/bigq.html', 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/);
let js = m[1];

// 只取需要的函数定义（整个 IIFE 依赖 DOM，这里单独抽出来）
function grab(name) {
  const re = new RegExp('function ' + name + '\\s*\\([\\s\\S]*?\\n  \\}');
  const hit = js.match(re);
  return hit ? hit[0] : null;
}

const src = [
  "function esc(s){ return String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c])); }",
  grab('isCode'), grab('joinCJK'), grab('richText'),
].filter(Boolean).join('\n');

if (src.indexOf('function richText') < 0) {
  console.log('抽取失败');
  process.exit(1);
}
eval(src);

const bigq = JSON.parse(fs.readFileSync('E:/CST/408/out/data/bigq.json', 'utf8'));

function show(y, q) {
  const r = bigq.find(x => x.y === y && x.q === q);
  if (!r) return console.log(`(${y}-${q}) 不存在`);
  console.log('='.repeat(78));
  console.log(`${y}-${q} 解析长度 ${r.sol.length}`);
  const out = richText(r.sol);
  const nPre = (out.match(/<pre class="code">/g) || []).length;
  const nP = (out.match(/<p class="para">/g) || []).length;
  console.log(`  -> ${nPre} 个代码块, ${nP} 个段落`);
  const pre = out.match(/<pre class="code">([\s\S]*?)<\/pre>/);
  if (pre) {
    console.log('  首个代码块前 6 行:');
    pre[1].split('\n').slice(0, 6).forEach(l => console.log('    | ' + l));
  }
}

show(2024, 41);
show(2010, 42);
show(2022, 41);
show(2025, 41);
