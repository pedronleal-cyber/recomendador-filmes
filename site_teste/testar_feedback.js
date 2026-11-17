// Testa o feedback "Gostou dos resultados?" no Edge sem janela (via protocolo DevTools).
// ATENÇÃO: os cenários que clicam ENVIAM DE VERDADE para a planilha (uma linha por clique de envio).
// Uso: node site_teste/testar_feedback.js "<url>" <largura> <cenario> <pasta_capturas>
//   cenario: ver (não clica) | bom_vermais | ruim_detalhe | aviso
// Requer o servidor local rodando (python -m http.server 8765 --bind 127.0.0.1 --directory site).
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const [url, largura, cenario, pasta] = process.argv.slice(2);
const L = +largura || 375;
const porta = 9334;
const perfil = fs.mkdtempSync(path.join(os.tmpdir(), "edge-fb-"));
const edge = spawn(EDGE, ["--headless=new", "--disable-gpu", "--no-first-run", "--disable-extensions",
  `--remote-debugging-port=${porta}`, `--user-data-dir=${perfil}`, "about:blank"], { stdio: "ignore" });
fs.mkdirSync(pasta, { recursive: true });

const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  let alvo;
  for (let k = 0; k < 50 && !alvo; k++) {
    try { alvo = (await (await fetch(`http://127.0.0.1:${porta}/json`)).json()).find((t) => t.type === "page"); } catch (e) { await esperar(200); }
  }
  const ws = new WebSocket(alvo.webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  let id = 0; const pend = new Map(); const console_ = []; const rede = [];
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pend.has(msg.id)) { pend.get(msg.id)(msg); pend.delete(msg.id); }
    if (msg.method === "Runtime.exceptionThrown") console_.push("[ERRO] " + (msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text));
    if (msg.method === "Log.entryAdded" && msg.params.entry.level === "error") console_.push("[log erro] " + msg.params.entry.text + " " + (msg.params.entry.url || ""));
    if (msg.method === "Network.requestWillBeSent" && /script\.google/.test(msg.params.request.url))
      rede.push({ etapa: "pedido", metodo: msg.params.request.method, url: msg.params.request.url.slice(0, 60) + "…", corpo: msg.params.request.postData || "" });
    if (msg.method === "Network.responseReceived" && /script\.google/.test(msg.params.response.url))
      rede.push({ etapa: "resposta", status: msg.params.response.status, tipo: msg.params.response.mimeType, url: msg.params.response.url.slice(0, 60) + "…" });
    if (msg.method === "Network.loadingFailed") rede.push({ etapa: "falhou", erro: msg.params.errorText, cors: msg.params.corsErrorStatus || "" });
  };
  const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await cmd("Runtime.enable"); await cmd("Log.enable"); await cmd("Page.enable"); await cmd("Network.enable");
  await cmd("Emulation.setDeviceMetricsOverride", { width: L, height: L < 600 ? 812 : 900, deviceScaleFactor: L < 600 ? 2 : 1, mobile: L < 600 });
  await cmd("Page.navigate", { url });
  const ler = async (expr) => (await cmd("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true })).result.result.value;
  const foto = async (nome, expr) => {
    if (expr) { await ler(expr); await esperar(400); }
    const shot = await cmd("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(pasta, nome), Buffer.from(shot.result.data, "base64"));
  };
  for (let k = 0; k < 400; k++) {
    await esperar(300);
    const ok = await ler(`!!(document.body.dataset.erro || (document.body.dataset.pronto && document.querySelector(".filme")))`);
    if (ok) break;
  }
  await esperar(800);
  const estado = () => ler(`({modo: document.body.dataset.modo, erro: document.body.dataset.erro || "",
    filmes: document.querySelectorAll(".filme").length, blocos: document.querySelectorAll(".feedback").length,
    bloco_depois_do_5o: document.querySelectorAll("#resultados > li")[5]?.className || "",
    botoes_desativados: [...document.querySelectorAll(".fb-bom, .fb-ruim")].map(b => b.disabled),
    obrigado: [...document.querySelectorAll(".fb-obrigado")].map(p => p.textContent),
    caixas_detalhe: document.querySelectorAll(".fb-detalhe textarea").length,
    botao_aviso: !!document.querySelector(".aviso:not([hidden]) .fb-aviso"),
    feedback: document.body.dataset.feedback || "", detalhe: document.body.dataset.detalhe || "",
    ultimo_envio: document.body.dataset.ultimoEnvio || "", largura_pagina: document.documentElement.scrollWidth})`);
  const r = { cenario, largura: L, inicio: await estado() };
  const rolarBloco = `document.querySelector(".feedback").scrollIntoView({block: "center"})`;
  await foto(`${cenario}_${L}_antes.png`, rolarBloco);
  if (cenario === "bom_vermais") {
    await ler(`document.getElementById("mais").click()`); await esperar(500);
    r.depois_ver_mais = await estado();
    await ler(`document.querySelectorAll(".fb-bom")[1].click()`); await esperar(4000);
    r.depois_clique = await estado();
    await foto(`${cenario}_${L}_depois_fim.png`, `document.querySelector("#feedback-fim .feedback").scrollIntoView({block: "center"})`);
    await foto(`${cenario}_${L}_depois_topo.png`, rolarBloco);
  } else if (cenario === "ruim_detalhe") {
    await ler(`document.querySelector(".fb-ruim").click()`); await esperar(4000);
    r.depois_ruim = await estado();
    await foto(`${cenario}_${L}_depois_ruim.png`, rolarBloco);
    await ler(`(() => { const t = document.querySelector(".fb-detalhe textarea"); t.value = "detalhe de teste enviado pelo Claude Code"; t.dispatchEvent(new Event("input")); document.querySelector(".fb-enviar").click(); })()`);
    await esperar(4000);
    r.depois_detalhe = await estado();
    await foto(`${cenario}_${L}_depois_detalhe.png`, rolarBloco);
  } else if (cenario === "aviso") {
    await foto(`${cenario}_${L}_aviso.png`, `document.getElementById("aviso").scrollIntoView({block: "start"})`);
    await ler(`document.querySelector(".fb-aviso").click()`); await esperar(4000);
    r.depois_aviso = await estado();
    await foto(`${cenario}_${L}_depois_aviso.png`);
  }
  r.rede = rede; r.console = console_;
  console.log(JSON.stringify(r, null, 2));
  ws.close(); edge.kill();
  setTimeout(() => process.exit(0), 300);
})().catch((e) => { console.error("falhou:", e); edge.kill(); process.exit(1); });
