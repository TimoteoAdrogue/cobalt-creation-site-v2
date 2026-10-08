// Runtime checks for V2 / V3 in headless Chrome.
//   node tools/verify.mjs <base-url> <out-dir>
// Per page and width (1440, 768, 390): console errors, failed requests, horizontal overflow,
// third-party requests before any interaction, layout shift, content left hidden, contrast,
// keyboard focus visibility, and a full-page screenshot. Then a reduced-motion pass.
import { launch } from "./cdp.mjs";
import { mkdirSync, writeFileSync } from "node:fs";

const base = process.argv[2];
const out = process.argv[3] || "compare";
mkdirSync(out, { recursive: true });
const PAGES = ["", "creation-d-objet-unique/", "ateliers-de-personnalisation/", "design-graphique-design-papier/",
  "coffrets-packaging/", "contact-feedback/", "politique-de-confidentialite/"];
const WIDTHS = [[1440, 900, false], [768, 1024, true], [390, 844, true]];
const origin = new URL(base).origin;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const p = await launch({ port: 9334 });
const report = { base, pages: [], problems: [] };
let errors = [], failed = [], third = [];
p.on((m) => {
  if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
  if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") errors.push(m.params.args.map((a) => a.value || a.description).join(" "));
  if (m.method === "Log.entryAdded" && m.params.entry.level === "error") errors.push(m.params.entry.text + " " + (m.params.entry.url || ""));
  if (m.method === "Network.loadingFailed" && !m.params.canceled) failed.push(m.params.errorText + " " + m.params.requestId);
  if (m.method === "Network.responseReceived" && m.params.response.status >= 400) failed.push(m.params.response.status + " " + m.params.response.url);
  if (m.method === "Network.requestWillBeSent") {
    const u = m.params.request.url;
    if (!u.startsWith(origin) && !u.startsWith("data:") && !u.startsWith("blob:")) third.push(u);
  }
});
await p.send("Page.addScriptToEvaluateOnNewDocument", { source: `window.__cls=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}` });

const scrollThrough = `(async()=>{const H=()=>document.documentElement.scrollHeight;for(let y=0;y<H();y+=Math.round(innerHeight*0.7)){scrollTo(0,y);await new Promise(r=>setTimeout(r,140))}scrollTo(0,H());await new Promise(r=>setTimeout(r,900));return true})()`;

const contrast = `(()=>{
  const parse=s=>{const m=s.match(/rgba?\\(([^)]+)\\)/);if(!m)return null;const v=m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number);return {r:v[0],g:v[1],b:v[2],a:v.length>3?v[3]:1}};
  const lum=c=>{const f=x=>{x/=255;return x<=0.04045?x/12.92:((x+0.055)/1.055)**2.4};return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b)};
  const blend=(top,bot)=>({r:top.r*top.a+bot.r*(1-top.a),g:top.g*top.a+bot.g*(1-top.a),b:top.b*top.a+bot.b*(1-top.a),a:1});
  const ratio=(a,b)=>{const x=lum(a),y=lum(b);return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05)};
  const bgOf=el=>{let layers=[];let photo=false;for(let n=el;n;n=n.parentElement){const cs=getComputedStyle(n);const c=parse(cs.backgroundColor);if(cs.backgroundImage!=='none'&&!/gradient/.test(cs.backgroundImage)&&n!==document.documentElement&&n!==document.body)photo=true;if(c&&c.a>0){layers.push(c);if(c.a>=1)break}}
    let worst=[{r:255,g:255,b:255,a:1},{r:0,g:0,b:0,a:1}];if(layers.length&&layers[layers.length-1].a>=1)worst=[layers.pop()];
    return {cands:worst.map(w=>layers.reverse().reduce((acc,l)=>blend(l,acc),w)),photo}};
  const bad=[];
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  const seen=new Set();
  while(walker.nextNode()){const t=walker.currentNode;if(!t.textContent.trim())continue;const el=t.parentElement;if(seen.has(el))continue;seen.add(el);
    const cs=getComputedStyle(el);if(cs.visibility==='hidden'||cs.display==='none')continue;const r=el.getBoundingClientRect();if(!r.width||!r.height)continue;
    if(el.closest('.sr-only,[aria-hidden=true],dialog:not([open]),.mono,.menu:not(.is-open),.ov:not(.is-open),[hidden]'))continue;
    if(/transparent|rgba\\(0, 0, 0, 0\\)/.test(cs.color))continue;
    const fg=parse(cs.color);const {cands,photo}=bgOf(el);if(photo)continue;
    const size=parseFloat(cs.fontSize),bold=+cs.fontWeight>=600;const need=(size>=24||(size>=18.66&&bold))?3:4.5;
    const min=Math.min(...cands.map(b=>ratio(fg.a<1?blend(fg,b):fg,b)));
    if(min<need)bad.push({text:t.textContent.trim().slice(0,40),cls:el.className&&el.className.baseVal===undefined?el.className:'',ratio:+min.toFixed(2),need,size})}
  return bad})()`;

const hiddenLeft = `(()=>[...document.querySelectorAll('[data-reveal],[data-settle]')].filter(e=>getComputedStyle(e).opacity<0.99&&!e.closest('[hidden]')).map(e=>e.className).slice(0,10))()`;

for (const path of PAGES) {
  for (const [w, h, mobile] of WIDTHS) {
    errors = []; failed = []; third = [];
    await p.viewport(w, h, mobile);
    await p.goto(base + path, 1800);
    const cls = await p.eval("window.__cls");
    const thirdBefore = [...new Set(third)];
    await p.eval(scrollThrough);
    const ov = await p.eval("({sw:document.documentElement.scrollWidth,iw:innerWidth})");
    const hid = await p.eval(hiddenLeft);
    const bad = await p.eval(contrast);
    const name = (path.replace(/\/$/, "") || "home") + "-" + w;
    // viewport-by-viewport captures (full-page capture resizes the viewport and distorts 100dvh layouts)
    const H = await p.eval("document.documentElement.scrollHeight");
    let k = 0;
    for (let y = 0; y < H && k < 40; y += h, k++) {
      await p.eval(`scrollTo(0,${y})`); await sleep(260);
      await p.shot(`${out}/${name}-seg${String(k).padStart(2, "0")}.jpg`, false);
    }
    const row = { page: path || "/", width: w, cls: +cls.toFixed(4), overflow: ov.sw > ov.iw ? ov : null, errors: [...new Set(errors)],
      failed: [...new Set(failed)], thirdPartyBeforeClick: thirdBefore, hiddenAfterScroll: hid, contrast: bad.slice(0, 8) };
    report.pages.push(row);
    const issues = [];
    if (row.overflow) issues.push("overflow " + JSON.stringify(row.overflow));
    if (row.errors.length) issues.push("console " + row.errors.join(" | "));
    if (row.failed.length) issues.push("failed " + row.failed.join(" | "));
    if (row.thirdPartyBeforeClick.length) issues.push("third-party " + row.thirdPartyBeforeClick.join(" "));
    if (row.cls > 0.02) issues.push("CLS " + row.cls);
    if (hid.length) issues.push("hidden " + hid.join(","));
    if (bad.length) issues.push("contrast " + JSON.stringify(bad.slice(0, 4)));
    console.log(`${name}: ${issues.length ? issues.join(" || ") : "ok"}`);
    if (issues.length) report.problems.push({ name, issues });
  }
}

// keyboard focus visibility (home, desktop)
await p.viewport(1440, 900, false);
await p.goto(base, 1500);
const focusLog = [];
for (let i = 0; i < 18; i++) {
  await p.send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  await p.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  await sleep(120);
  focusLog.push(await p.eval(`(()=>{const e=document.activeElement;const cs=getComputedStyle(e);return {el:e.tagName+'.'+(e.className||'')+' '+(e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,30),outline:cs.outlineStyle!=='none'&&parseFloat(cs.outlineWidth)>0}})()`));
}
const noRing = focusLog.filter((f) => !f.outline);
console.log("focus: " + (noRing.length ? "missing ring on " + noRing.map((f) => f.el).join(" | ") : `ok (${focusLog.length} stops)`));
report.focus = focusLog;

// reduced motion
await p.media([{ name: "prefers-reduced-motion", value: "reduce" }]);
for (const path of PAGES) {
  await p.goto(base + path, 1500);
  await p.eval(scrollThrough);
  const hid = await p.eval(hiddenLeft);
  const moving = await p.eval(`(async()=>{const t=document.querySelector('.bn__track');const m=document.querySelector('.mq');const g=document.querySelector('.trust__grid');
    const a=t?getComputedStyle(t).transform:null;await new Promise(r=>setTimeout(r,3500));const b=t?getComputedStyle(t).transform:null;
    return {bannerMoved:t?a!==b:false,marquee:m?getComputedStyle(m).display:null,grid:g?getComputedStyle(g).display:null}})()`);
  const issues = [];
  if (hid.length) issues.push("hidden " + hid.join(","));
  if (moving.bannerMoved) issues.push("banner autoplays under reduced motion");
  if (moving.marquee && moving.marquee !== "none") issues.push("marquee visible under reduced motion");
  console.log(`reduced ${path || "/"}: ${issues.length ? issues.join(" || ") : "ok"}`);
  if (issues.length) report.problems.push({ name: "reduced " + path, issues });
}
writeFileSync(`${out}/report.json`, JSON.stringify(report, null, 1));
console.log(`problems: ${report.problems.length}`);
p.close();
