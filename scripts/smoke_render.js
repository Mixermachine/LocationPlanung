// Headless smoke test for locations.html: parse inline script, run in VM with stub DOM/Leaflet.
"use strict";
const fs = require('fs'), vm = require('vm');

// Universal chainable stub: every property is a function returning chainable stub.
function chainStub() {
  const f = function () { return stubObj; };
  const stubObj = new Proxy(f, {
    get(t, k) {
      if (k === Symbol.toPrimitive) return () => 0;
      if (k === 'length') return 0;
      if (k in t) return t[k];
      return (t[k] = chainStub());
    },
    set(t, k, v) { t[k] = v; return true; },
    apply() { return stubObj; },
  });
  return stubObj;
}
function elStub() {
  return new Proxy(Object.assign(function () { return undefined; }, {
    style: {}, textContent: '', value: '', dataset: {},
    children: [],
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
  }), {
    get(t, k) {
      if (k === Symbol.toPrimitive) return () => '';
      if (k in t) return t[k];
      return (t[k] = elStub());
    },
    set(t, k, v) { t[k] = v; return true; },
  });
}

const ctx = {
  window: null,
  URLSearchParams,
  history: { replaceState() {} },
  document: {
    addEventListener() {}, getElementById: () => elStub(), querySelectorAll: () => [],
    createElement: () => elStub(), body: { appendChild() {} },
  },
  location: { hash: '' },
  console: { log() {}, error() {} },
  fetch: () => Promise.resolve({ ok: true, json: () => Promise.resolve([]) }),
  L: chainStub(),
};
ctx.window = ctx;
vm.createContext(ctx);
const html = fs.readFileSync('locations.html', 'utf8');
const m = html.match(/<script>([\s\S]*)<\/script>\s*<\/body>/);
if (!m) { console.error('kein inline <script> gefunden'); process.exit(1); }
vm.runInContext(m[1], ctx);
console.log('SMOKE OK: inline script laeuft ohne Exception');
