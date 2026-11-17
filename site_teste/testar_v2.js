// Testa as melhorias do site (capas, "Onde assistir", filtros, ordenação, "ver mais 5") no Edge sem janela.
// Uso: node site_teste/testar_v2.js <pasta_capturas>
// Requer o servidor local rodando (python -m http.server 8765 --bind 127.0.0.1 dentro de site/).
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const BASE = "http://127.0.0.1:8765/";
const pasta = process.argv[2] || ".";
const FRASES = [
  "estou com minha namorada e queremos ver algo que seja divertido",
  "quero algo pra me tirar do tédio",
  "queria um suspense, com drama, romance e que fosse asiático e também que fosse dos anos 2020 pra hoje em dia",
  "me vê um filme de ação em que o protagonista seja muito inteligente",
];
const porta = 9334;
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
  let id = 0; const pend = new Map(); let erros = [];
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pend.has(msg.id)) { pend.get(msg.id)(msg); pend.delete(msg.id); }
    if (msg.method === "Runtime.consoleAPICalled" && ["error", "warning"].includes(msg.params.type))
      erros.push(`[${msg.params.type}] ` + msg.params.args.map((a) => a.value ?? a.description).join(" "));
    if (msg.method === "Runtime.exceptionThrown") erros.push("[ERRO] " + (msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text));
    if (msg.method === "Log.entryAdded" && msg.params.entry.level === "error") erros.push("[log erro] " + msg.params.entry.text + " " + (msg.params.entry.url || ""));
  };
  const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  const ler = async (expr) => (await cmd("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true })).result.result.value;
  await cmd("Runtime.enable"); await cmd("Log.enable"); await cmd("Page.enable");

  const estado = () => ler(`({modo: document.body.dataset.modo || "", erro: document.body.dataset.erro || "",
    filmes: [...document.querySelectorAll(".filme h2")].map(h => h.textContent.trim()),
    contagem: document.getElementById("contagem").textContent,
    capas: document.querySelectorAll("img.capa").length, capas_vazias: document.querySelectorAll(".capa-vazia").length,
    capas_carregadas: [...document.querySelectorAll("img.capa")].filter(i => i.complete && i.naturalWidth > 0).length,
    lazy: [...document.querySelectorAll("img.capa")].every(i => i.loading === "lazy" && i.alt.startsWith("Capa de ")),
    botoes: [...document.querySelectorAll(".botao-assistir")].map(a => a.href + " target=" + a.target + " rel=" + a.rel).slice(0, 2),
    selos_link: [...document.querySelectorAll("a.selo")].length, justwatch: document.querySelectorAll(".fonte-streaming").length,
    ver_tmdb: [...document.querySelectorAll(".ver-tmdb")].map(a => a.href).slice(0, 1),
    largura: document.documentElement.scrollWidth, mais_visivel: !document.getElementById("mais").hidden})`);
  const esperarPronto = async () => {
    for (let k = 0; k < 100; k++) {
      await esperar(300);
      const e = await ler(`({p: document.body.dataset.pronto, n: document.querySelectorAll(".filme").length, erro: document.body.dataset.erro || ""})`);
      if (e.erro || (e.p && e.n)) return;
    }
  };
  const esperarCapas = () => ler(`Promise.race([Promise.all([...document.querySelectorAll("img.capa")].slice(0, 5).map(i => { i.loading = "eager";
      return i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; }); })), new Promise(r => setTimeout(r, 8000))]).then(() => 1)`);
  const mudar = (idCampo, valor) => ler(`(() => { const e = document.getElementById("${idCampo}");
      if (e.type === "checkbox") e.checked = ${JSON.stringify(valor)}; else e.value = ${JSON.stringify(valor)};
      e.dispatchEvent(new Event("change")); return 1; })()`);
  const salvar = async (nome, altura) => {
    const shot = await cmd("Page.captureScreenshot", { format: "png", captureBeyondViewport: true,
      clip: { x: 0, y: 0, width: altura.w, height: altura.h, scale: 1 } });
    fs.writeFileSync(path.join(pasta, nome), Buffer.from(shot.result.data, "base64"));
  };

  const relatorio = [];
  for (let n = 0; n < FRASES.length; n++) {
    erros = [];
    await cmd("Emulation.setDeviceMetricsOverride", { width: 375, height: 812, deviceScaleFactor: 1, mobile: true });
    await cmd("Page.navigate", { url: BASE + "?q=" + encodeURIComponent(FRASES[n]) });
    await esperarPronto();
    const lazyAntes = await ler(`[...document.querySelectorAll("img.capa")].every(i => i.loading === "lazy" && i.alt.startsWith("Capa de "))`);
    await esperarCapas(); await esperar(400);
    const r = { frase: FRASES[n], ...(await estado()), lazy: lazyAntes };
    const h = await ler(`Math.min(document.documentElement.scrollHeight, 2600)`);
    await salvar(`frase${n + 1}_celular.png`, { w: 375, h });
    // ver mais 5
    await ler(`document.getElementById("mais").click(), 1`); await esperar(300);
    r.cartoes_depois_ver_mais = await ler(`document.querySelectorAll(".filme").length`);
    r.contagem_depois_ver_mais = await ler(`document.getElementById("contagem").textContent`);
    // ordenações (primeiro filme de cada)
    r.ordenar = {};
    for (const o of ["nota", "recentes", "votos", "melhor"]) {
      await mudar("ordem", o); await esperar(150);
      r.ordenar[o] = (await estado()).filmes.slice(0, 3);
    }
    if (n === 0) {
      // filtros: nota 7+, a partir de 2000, até 2h; depois só Netflix
      await mudar("f-nota", "7"); await mudar("f-ano", "2000"); await mudar("f-duracao", "120"); await esperar(150);
      r.filtro_nota7_ano2000_ate2h = await estado().then((e) => ({ contagem: e.contagem, filmes: e.filmes }));
      await ler(`(() => { const c = document.querySelector('#servicos input[value="Netflix"]'); c.checked = true; c.dispatchEvent(new Event("change")); return 1; })()`);
      await mudar("f-assinatura", true); await esperar(150);
      r.filtro_mais_so_netflix = await estado().then((e) => ({ contagem: e.contagem, filmes: e.filmes }));
      r.assinatura_salva_no_navegador = await ler(`localStorage.getItem("recomendador_minhas_assinaturas")`);
      await mudar("f-nota", "8"); await mudar("f-ano", "2020"); await mudar("f-duracao", "100"); await esperar(150);
      r.filtro_sem_resultado = await estado().then((e) => ({ contagem: e.contagem, filmes: e.filmes }));
      await salvar("filtro_sem_resultado_celular.png", { w: 375, h: 900 });
      // limpa os filtros (a assinatura marcada continua salva)
      await mudar("f-nota", "0"); await mudar("f-ano", "0"); await mudar("f-duracao", "0"); await mudar("f-assinatura", false);
      // computador
      await cmd("Emulation.setDeviceMetricsOverride", { width: 1200, height: 900, deviceScaleFactor: 1, mobile: false });
      await cmd("Page.navigate", { url: BASE + "?q=" + encodeURIComponent(FRASES[n]) });
      await esperarPronto(); await esperarCapas(); await esperar(400);
      r.largura_computador = await ler(`document.documentElement.scrollWidth`);
      await salvar("frase1_computador.png", { w: 1200, h: 1500 });
    }
    r.erros_console = erros;
    relatorio.push(r);
  }
  fs.writeFileSync(path.join(pasta, "relatorio_testar_v2.json"), JSON.stringify(relatorio, null, 2));
  console.log(JSON.stringify(relatorio, null, 2));
  ws.close(); edge.kill();
  setTimeout(() => process.exit(0), 300);
})().catch((e) => { console.error("falhou:", e); edge.kill(); process.exit(1); });
