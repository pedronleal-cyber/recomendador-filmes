// Testa a página no Edge sem janela (via protocolo DevTools), como um celular de 375 px.
// Uso: node site_teste/testar_navegador.js "<url>" <arquivo_captura.png>
// Requer o servidor local rodando (python -m http.server 8765 --bind 127.0.0.1 dentro de site/).
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const url = process.argv[2];
const captura = process.argv[3];
const porta = 9333;
const perfil = fs.mkdtempSync(path.join(os.tmpdir(), "edge-teste-"));
const edge = spawn(EDGE, ["--headless=new", "--disable-gpu", "--no-first-run", "--disable-extensions",
  `--remote-debugging-port=${porta}`, `--user-data-dir=${perfil}`, "about:blank"], { stdio: "ignore" });

const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  let alvo;
  for (let k = 0; k < 50 && !alvo; k++) {
    try { alvo = (await (await fetch(`http://127.0.0.1:${porta}/json`)).json()).find((t) => t.type === "page"); } catch (e) { await esperar(200); }
  }
  const ws = new WebSocket(alvo.webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  let id = 0; const pend = new Map(); const console_ = [];
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pend.has(msg.id)) { pend.get(msg.id)(msg); pend.delete(msg.id); }
    if (msg.method === "Runtime.consoleAPICalled") console_.push(`[${msg.params.type}] ` + msg.params.args.map((a) => a.value ?? a.description).join(" "));
    if (msg.method === "Runtime.exceptionThrown") console_.push("[ERRO] " + (msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text));
    if (msg.method === "Log.entryAdded" && msg.params.entry.level === "error") console_.push("[log erro] " + msg.params.entry.text + " " + (msg.params.entry.url || ""));
  };
  const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await cmd("Runtime.enable"); await cmd("Log.enable"); await cmd("Page.enable");
  await cmd("Emulation.setDeviceMetricsOverride", { width: 375, height: 812, deviceScaleFactor: 2, mobile: true });
  await cmd("Page.navigate", { url });
  const ler = async (expr) => (await cmd("Runtime.evaluate", { expression: expr, returnByValue: true })).result.result.value;
  let estado;
  for (let k = 0; k < 100; k++) {
    await esperar(300);
    estado = await ler(`({pronto: document.body.dataset.pronto, erro: document.body.dataset.erro || "", modo: document.body.dataset.modo || "",
      filmes: [...document.querySelectorAll(".filme h2")].map(h => h.textContent),
      porque: [...document.querySelectorAll(".porque")].map(p => p.textContent),
      onde: [...document.querySelectorAll(".onde")].map(p => p.textContent.replace("Onde assistir no Brasil (assinatura)", "").trim()),
      aviso: document.getElementById("aviso").hidden ? "" : document.getElementById("aviso").textContent,
      largura: document.documentElement.scrollWidth})`);
    if (estado && (estado.erro || (estado.pronto && estado.filmes.length))) break;
  }
  const shot = await cmd("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  // botão "Gerar outros 5"
  let depoisMais = null;
  if (estado && estado.filmes.length) {
    await ler(`document.getElementById("mais").hidden ? 0 : (document.getElementById("mais").click(), 1)`);
    await esperar(500);
    depoisMais = await ler(`document.querySelectorAll(".filme").length`);
  }
  // blocos "Gostou dos resultados?" (não clica: clicar envia de verdade; para isso, ver testar_feedback.js)
  const contato = await ler(`({blocos_feedback: document.querySelectorAll(".feedback").length})`);
  // página admin (fora do site publicado): só quando o servidor roda na pasta do projeto (url com /site/)
  if (/\/site\//.test(url)) await cmd("Page.navigate", { url: url.replace(/site\/.*$/, "admin_local/admin.html") });
  await esperar(1500);
  const admin = await ler(`[...document.querySelectorAll("tbody tr")].map(tr => tr.textContent)`);
  fs.writeFileSync(captura, Buffer.from(shot.result.data, "base64"));
  console.log(JSON.stringify({ ...estado, cartoes_depois_de_gerar_outros_5: depoisMais, contato, admin_frases: /\/site\//.test(url) ? admin : "(não testada)", console: console_ }, null, 2));
  ws.close(); edge.kill();
  setTimeout(() => process.exit(0), 300);
})().catch((e) => { console.error("falhou:", e); edge.kill(); process.exit(1); });
