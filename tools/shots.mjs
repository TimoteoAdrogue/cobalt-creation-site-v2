// Viewport screenshots at chosen scroll positions (headless Chrome, real rAF, so scroll animations run).
//   node tools/shots.mjs <url> <outprefix> <width> <height> <mobile 0|1> <pos,pos,...>   (pos in px, or "b" for bottom, "eN" for element selector index)
import { launch } from "./cdp.mjs";
const [url, out, w, h, mob, list] = process.argv.slice(2);
const p = await launch({ port: 9335 });
await p.viewport(+w, +h, mob === "1");
await p.goto(url, 2500);
const errs = [];
p.on((m) => { if (m.method === "Runtime.exceptionThrown") errs.push(m.params.exceptionDetails.exception?.description); });
let k = 0;
for (const pos of list.split(",")) {
  const y = pos === "b" ? "document.documentElement.scrollHeight" : pos;
  // glide there in steps so scroll-linked animations see the journey
  await p.eval(`(async()=>{const t=${y};const s=scrollY;for(let i=1;i<=12;i++){scrollTo(0,s+(t-s)*i/12);await new Promise(r=>setTimeout(r,40))}})()`);
  await new Promise((r) => setTimeout(r, 1300));
  await p.shot(`${out}-${String(k++).padStart(2, "0")}.jpg`);
}
const info = await p.eval("({h:document.documentElement.scrollHeight,sw:document.documentElement.scrollWidth,iw:innerWidth})");
console.log(JSON.stringify(info), errs.length ? "ERRORS " + errs.join(" | ") : "no errors");
p.close();
