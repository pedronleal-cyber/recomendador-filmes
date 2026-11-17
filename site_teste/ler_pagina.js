// Abre uma página no Edge sem janela (375 px) e imprime o resultado de uma expressão JS e os erros do console.
// Uso: node site_teste/ler_pagina.js "<url>" "<expressao>" [captura.png]
const { spawn } = require("child_process");
const fs = require("fs"); const os = require("os"); const path = require("path");
const [url, expr, captura] = process.argv.slice(2);
const porta = 9334;
const edge = spawn("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", ["--headless=new", "--disable-gpu",
  "--no-first-run", "--disable-extensions", `--remote-debugging-port=${porta}`,
  `--user-data-dir=${fs.mkdtempSync(path.join(os.tmpdir(), "edge-ler-"))}`, "about:blank"], { stdio: "ignore" });
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  let alvo;
  for (let k = 0; k < 50 && !alvo; k++) {
    try { alvo = (await (await fetch(`http://127.0.0.1:${porta}/json`)).json()).find((t) => t.type === "page"); } catch (e) { await esperar(200); }
  }
  const ws = new WebSocket(alvo.webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
  let id = 0; const pend = new Map(); const erros = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
    if (m.method === "Runtime.exceptionThrown") erros.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
    if (m.method === "Log.entryAdded" && m.params.entry.level === "error") erros.push(m.params.entry.text + " " + (m.params.entry.url || ""));
  };
  const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await cmd("Runtime.enable"); await cmd("Log.enable"); await cmd("Page.enable");
  await cmd("Emulation.setDeviceMetricsOverride", { width: 375, height: 812, deviceScaleFactor: 2, mobile: true });
  await cmd("Page.navigate", { url }); await esperar(2500);
  const v = (await cmd("Runtime.evaluate", { expression: expr, returnByValue: true })).result.result.value;
  if (captura) { const s = await cmd("Page.captureScreenshot", { format: "png" }); fs.writeFileSync(captura, Buffer.from(s.result.data, "base64")); }
  console.log(JSON.stringify({ resultado: v, erros_console: erros }, null, 2));
  ws.close(); edge.kill(); setTimeout(() => process.exit(0), 300);
})().catch((e) => { console.error(e); edge.kill(); process.exit(1); });
