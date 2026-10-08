// Frame times of the V3 monogram while a pointer sweeps the hero (headless Chrome, GPU off: worst case).
import { launch } from "./cdp.mjs";
const url = process.argv[2] || "http://localhost:8840/cobalt-creation-site-v3/";
const p = await launch();
await p.viewport(1440, 900);
await p.goto(url, 3000);
const out = [];
for (const finish of ["foil", "gravure", "emboss", "leaf"]) {
  await p.eval(`document.querySelector('.finish [data-finish=${finish}]').click()`);
  await new Promise((r) => setTimeout(r, 2600));
  // real input events through the browser, one per frame
  const t0 = Date.now(); const frames = [];
  await p.eval(`(()=>{const k='${finish}';window.__run={k,d:[],last:0};(function f(now){const r=window.__run;if(!r||r.k!==k)return;if(r.last)r.d.push(now-r.last);r.last=now;requestAnimationFrame(f)})(performance.now())})()`);
  let i = 0;
  while (Date.now() - t0 < 4000) {
    const t = i++ / 60;
    await p.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: Math.round(720 + 600 * Math.cos(t * 2.1)), y: Math.round(420 + 300 * Math.sin(t * 1.7)) });
    await new Promise((r) => setTimeout(r, 16));
  }
  const d = await p.eval(`(()=>{const x=window.__run.d.slice(5).sort((a,b)=>a-b);window.__run=null;return x})()`);
  const med = d[Math.floor(d.length / 2)], p95 = d[Math.floor(d.length * 0.95)], worst = d[d.length - 1];
  out.push({ finish, frames: d.length, median: +med.toFixed(2), p95: +p95.toFixed(2), worst: +worst.toFixed(2) });
}
console.log(JSON.stringify(out, null, 1));
p.close();
