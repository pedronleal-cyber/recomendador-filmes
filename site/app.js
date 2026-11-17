// Liga a página ao motor T (motor.js). O que é digitado não sai do navegador, a não ser que a pessoa clique
// em 👍 / 👎 (ou "Conte pra gente"): aí a frase, os 5 filmes sugeridos e o comentário opcional vão para a planilha do criador.
// As capas são carregadas direto do TMDB (não são baixadas nem hospedadas aqui).
(function () {
  "use strict";
  // Receptor do feedback (Google Apps Script que grava numa planilha). Só recebe quando a pessoa clica.
  const FEEDBACK_URL = "COLE_AQUI_A_URL_DO_SEU_APPS_SCRIPT"; // ver docs/FEEDBACK.md
  // Sem URL configurada, os botões de feedback não aparecem e nada é enviado.
  const FEEDBACK_ATIVO = /^https:\/\/script\.google\.com\//.test(FEEDBACK_URL);
  const CHAVE_FRASES = "recomendador_frases_nao_entendidas";
  // As frases não entendidas só são guardadas quando o site roda no computador (admin_local/admin.html lê);
  // no site publicado, nada é guardado.
  const LOCAL = ["127.0.0.1", "localhost"].includes(location.hostname);
  const CHAVE_ASSINATURAS = "recomendador_minhas_assinaturas";
  const CANDIDATOS = 30, POR_VEZ = 5;
  const IMG = "https://image.tmdb.org/t/p/w342";
  const TMDB_FILME = "https://www.themoviedb.org/movie/";

  // Serviços agrupados (cada um junta as variações de nome que aparecem nos dados)
  const SERVICOS = [
    ["Netflix", /^Netflix/], ["Prime Video", /^Amazon Prime Video/], ["Max (HBO Max)", /^HBO Max/],
    ["Disney+", /^Disney Plus/], ["Globoplay", /^Globoplay/], ["Apple TV+", /^Apple TV( Amazon Channel)?$/],
    ["Paramount+", /^Paramount/], ["Telecine", /^Telecine/], ["Claro tv+ / Claro video", /^Claro/],
    ["Universal+", /^Universal\+/], ["MGM+", /^MGM/], ["Lionsgate+", /^Lionsgate/], ["MUBI", /^MUBI/],
    ["Looke", /^Looke/], ["Crunchyroll", /^Crunchyroll/], ["Oldflix", /^Oldflix/], ["Belas Artes à La Carte", /^Belas Artes/],
  ];

  const $ = (id) => document.getElementById(id);
  const campo = $("pedido"), botao = $("botao"), lista = $("resultados"), aviso = $("aviso"), mais = $("mais"),
    status = $("status"), controles = $("controles"), contagem = $("contagem");
  let motor = null, atual = null, candidatos = [], visiveis = POR_VEZ;
  // Feedback da busca atual (um só envio de 👍/👎 por busca; o detalhe opcional é uma 2ª linha)
  const novoFeedback = () => ({ enviado: false, avaliacao: "", detalheAberto: false, detalheEnviado: false, texto: "", erro: false });
  let fb = novoFeedback(), frasePedida = "";

  window.addEventListener("error", (e) => {
    document.body.dataset.erro = String(e.message || e);
    status.textContent = "Ops, algo deu errado: " + (e.message || e);
  });

  // ------------------------------------------------------------ armazenamento local (só neste navegador)
  const lerLocal = (k, padrao) => { try { return JSON.parse(localStorage.getItem(k)) ?? padrao; } catch (e) { return padrao; } };
  const gravarLocal = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* sem localStorage */ } };
  function guardarFrase(frase, modo) {
    if (!LOCAL) return;
    const lst = lerLocal(CHAVE_FRASES, []);
    lst.push({ quando: new Date().toISOString(), frase, modo });
    gravarLocal(CHAVE_FRASES, lst.slice(-500));
  }

  // ------------------------------------------------------------ utilidades
  const fmtNota = (x) => (x == null ? "" : "★ " + Number(x).toFixed(1).replace(".", ","));
  const fmtDur = (m) => (!m ? "" : m >= 60 ? `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, "0")}min` : `${m} min`);
  function el(tag, attrs = {}, ...filhos) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else e.setAttribute(k, v); }
    for (const f of filhos) if (f != null) e.append(f);
    return e;
  }
  const linkExterno = (href, attrs, ...filhos) => el("a", Object.assign({ href, target: "_blank", rel: "noopener noreferrer" }, attrs), ...filhos);
  const urlOndeAssistir = (f) => `${TMDB_FILME}${f.idTmdb}/watch?locale=BR`;

  // ------------------------------------------------------------ cartão do filme
  function capa(f) {
    if (f.poster) {
      return el("img", { class: "capa", src: IMG + f.poster, alt: "Capa de " + f.titulo, loading: "lazy",
        width: "342", height: "513", referrerpolicy: "no-referrer" });
    }
    return el("div", { class: "capa capa-vazia", role: "img", "aria-label": "Sem capa: " + f.titulo }, f.titulo);
  }
  function cartao(f, numero) {
    const curta = (f.sinopse || "").length > 220 ? f.sinopse.slice(0, 220).replace(/\s+\S*$/, "") + "…" : (f.sinopse || "Sem sinopse.");
    const sinopse = el("p", { class: "sinopse" }, curta);
    if (curta !== (f.sinopse || "Sem sinopse.")) {
      const ver = el("button", { type: "button", class: "vermais" }, "ver mais");
      ver.addEventListener("click", () => { sinopse.textContent = f.sinopse; });
      sinopse.append(" ", ver);
    }
    const meta = el("div", { class: "meta" });
    [f.generos.join(", "), fmtDur(f.duracao), fmtNota(f.nota)].filter(Boolean).forEach((t) => meta.append(el("span", {}, t)));

    const onde = el("div", { class: "onde" }, el("strong", {}, "Onde assistir no Brasil (assinatura)"));
    if (f.streaming.length) {
      const selos = el("div", { class: "selos" });
      f.streaming.forEach((s) => selos.append(linkExterno(urlOndeAssistir(f), { class: "selo", title: "Ver onde assistir (abre o TMDB)" }, s)));
      onde.append(selos);
    } else onde.append(el("span", { class: "sem-assinatura" }, "não encontrado em assinatura"));
    const acoes = el("div", { class: "acoes-filme" },
      linkExterno(urlOndeAssistir(f), { class: "botao-assistir" }, "Onde assistir"),
      el("span", { class: "fonte-streaming" }, "Dados de streaming: JustWatch"),
      linkExterno(TMDB_FILME + f.idTmdb, { class: "ver-tmdb" }, "Ver no TMDB"));

    const porque = el("p", { class: "porque" }, el("strong", {}, "Por que sugerimos: "));
    if (f.motivo.length) {
      const prefixo = f.motivo[0].fonte === "sinopse" ? "a sinopse fala de: " : f.motivo[0].fonte === "nota" ? "" : "combina com: ";
      porque.append(prefixo);
      f.motivo.forEach((m, k) => {
        if (k) porque.append(", ");
        porque.append(m.rotulo);
        if (m.estimada) porque.append(" ", el("span", { class: "estimada" }, "(etiqueta estimada)"));
      });
    } else porque.append("combina com o que você pediu");

    const texto = el("div", { class: "texto" },
      el("h2", {}, `${numero}. ${f.titulo} `, el("span", { class: "ano" }, f.ano ? `(${f.ano})` : "")),
      meta, sinopse, onde, acoes, porque);
    return el("li", { class: "filme" }, capa(f), texto);
  }

  // ------------------------------------------------------------ filtros e ordenação (só sobre os 30 candidatos)
  function montarServicos() {
    const salvos = new Set(lerLocal(CHAVE_ASSINATURAS, []));
    const caixa = $("servicos");
    SERVICOS.forEach(([nome]) => {
      const id = "srv-" + nome.replace(/\W+/g, "-");
      const cb = el("input", { type: "checkbox", id, value: nome });
      cb.checked = salvos.has(nome);
      cb.addEventListener("change", () => {
        gravarLocal(CHAVE_ASSINATURAS, [...document.querySelectorAll("#servicos input:checked")].map((x) => x.value));
        reiniciar();
      });
      caixa.append(el("label", { class: "servico", for: id }, cb, " " + nome));
    });
  }
  function filtrados() {
    const ordem = $("ordem").value, notaMin = +$("f-nota").value, anoMin = +$("f-ano").value, durMax = +$("f-duracao").value;
    const soAssinatura = $("f-assinatura").checked;
    const meus = [...document.querySelectorAll("#servicos input:checked")].map((x) => x.value);
    const regras = SERVICOS.filter(([nome]) => meus.includes(nome)).map(([, rx]) => rx);
    let lst = candidatos.filter((f) =>
      (!notaMin || (f.nota || 0) >= notaMin) &&
      (!anoMin || (f.ano || 0) >= anoMin) &&
      (!durMax || (f.duracao && f.duracao <= durMax)) &&
      (!soAssinatura || f.streaming.some((s) => regras.some((rx) => rx.test(s)))));
    const pos = new Map(candidatos.map((f, i) => [f, i]));
    const desempate = (a, b) => pos.get(a) - pos.get(b);
    if (ordem === "nota") lst = [...lst].sort((a, b) => (b.nota || 0) - (a.nota || 0) || desempate(a, b));
    else if (ordem === "recentes") lst = [...lst].sort((a, b) => (b.ano || 0) - (a.ano || 0) || desempate(a, b));
    else if (ordem === "votos") lst = [...lst].sort((a, b) => (b.votos || 0) - (a.votos || 0) || desempate(a, b));
    return { lst, soAssinaturaSemServico: soAssinatura && !meus.length };
  }
  function desenhar() {
    const { lst, soAssinaturaSemServico } = filtrados();
    lista.innerHTML = "";
    const mostrar = lst.slice(0, visiveis);
    mostrar.forEach((f, k) => lista.append(cartao(f, k + 1)));
    mais.hidden = lst.length <= visiveis;
    // Bloco "Gostou dos resultados?": logo abaixo dos 5 primeiros e, depois de "Ver mais 5", também no fim da lista
    if (mostrar.length && FEEDBACK_ATIVO) {
      const primeiro = el("li", { class: "feedback-item" }, blocoFeedback());
      const quinto = lista.children[Math.min(POR_VEZ, mostrar.length) - 1];
      quinto.after(primeiro);
    }
    $("feedback-fim").innerHTML = "";
    if (FEEDBACK_ATIVO && mostrar.length > POR_VEZ) $("feedback-fim").append(blocoFeedback());
    const filtrando = $("ordem").value !== "melhor" || $("f-nota").value !== "0" || $("f-ano").value !== "0" ||
      $("f-duracao").value !== "0" || $("f-assinatura").checked;
    if (!lst.length) {
      contagem.textContent = soAssinaturaSemServico
        ? "Marque pelo menos um serviço em “Minhas assinaturas” para usar esse filtro."
        : "Nenhum dos filmes que combinam com o seu pedido passa nesses filtros. Tente afrouxar algum filtro (ou desmarcar “Só na minha assinatura”).";
      contagem.className = "contagem vazio";
    } else {
      contagem.textContent = `${lst.length} ${lst.length === 1 ? "filme combina" : "filmes combinam"}` +
        (filtrando ? " com o pedido e os filtros" : "") + `; mostrando ${mostrar.length}.`;
      contagem.className = "contagem";
    }
    document.body.dataset.mostrando = String(mostrar.length);
  }
  function reiniciar() { visiveis = POR_VEZ; if (atual) desenhar(); }

  // ------------------------------------------------------------ feedback "Gostou dos resultados?"
  // Envia só quando a pessoa clica: frase, os 5 primeiros títulos mostrados, avaliação, comentário e modo do motor.
  // mode "no-cors" + text/plain: o Apps Script recebe sem precisar de CORS (a resposta não pode ser lida pela página).
  function enviarFeedback(avaliacao, comentario) {
    if (!FEEDBACK_ATIVO) return Promise.resolve(false);
    const corpo = {
      frase: frasePedida,
      filmes: filtrados().lst.slice(0, POR_VEZ).map((f) => f.titulo).join("; "),
      avaliacao, comentario: comentario || "", modo: atual ? atual.modo : "",
    };
    document.body.dataset.ultimoEnvio = JSON.stringify(corpo);
    return fetch(FEEDBACK_URL, { method: "POST", mode: "no-cors", headers: { "Content-Type": "text/plain" },
      body: JSON.stringify(corpo), keepalive: true }).then(() => true, () => false);
  }
  function votar(avaliacao) {
    if (fb.enviado) return;
    fb.enviado = true; fb.avaliacao = avaliacao;
    if (avaliacao === "ruim") fb.detalheAberto = true;
    atualizarBlocos();
    const meu = fb;
    enviarFeedback(avaliacao, "").then((ok) => {
      if (!ok && meu === fb) { fb.erro = true; atualizarBlocos(); }
      document.body.dataset.feedback = ok ? avaliacao : "erro";
    });
  }
  function enviarDetalhe() {
    const texto = fb.texto.trim();
    if (!texto || fb.detalheEnviado) {
      const caixa = document.querySelector(".fb-detalhe textarea");
      if (caixa) caixa.focus();
      return;
    }
    fb.detalheEnviado = true;
    atualizarBlocos();
    const meu = fb;
    enviarFeedback("ruim", texto).then((ok) => {
      if (!ok && meu === fb) { fb.erro = true; atualizarBlocos(); }
      document.body.dataset.detalhe = ok ? "enviado" : "erro";
    });
  }
  function blocoFeedback() {
    const b = el("section", { class: "feedback", "aria-label": "Avaliar os resultados" });
    preencherBloco(b);
    return b;
  }
  function preencherBloco(b) {
    b.innerHTML = "";
    b.append(el("p", { class: "fb-titulo" }, "Gostou dos resultados?"));
    const bom = el("button", { type: "button", class: "fb-botao fb-bom", "aria-pressed": String(fb.avaliacao === "bom") }, "👍 Gostei");
    const ruim = el("button", { type: "button", class: "fb-botao fb-ruim", "aria-pressed": String(fb.avaliacao === "ruim") }, "👎 Não era isso");
    bom.disabled = ruim.disabled = fb.enviado;
    bom.addEventListener("click", () => votar("bom"));
    ruim.addEventListener("click", () => votar("ruim"));
    b.append(el("div", { class: "fb-botoes" }, bom, ruim));
    if (fb.enviado) {
      b.append(el("p", { class: "fb-obrigado", role: "status" },
        fb.erro ? "Não consegui enviar agora. Confira sua conexão e tente de novo mais tarde." : "Obrigado!"));
    }
    if (fb.detalheAberto) {
      const det = el("div", { class: "fb-detalhe" });
      if (fb.detalheEnviado) det.append(el("p", { class: "fb-obrigado" }, fb.erro ? "" : "Detalhe enviado. Obrigado!"));
      else {
        const id = "fb-texto-" + Math.random().toString(36).slice(2, 8);
        const caixa = el("textarea", { id, rows: "3", maxlength: "500", placeholder: "Ex.: queria algo mais leve, ou filmes mais recentes" });
        caixa.value = fb.texto;
        caixa.addEventListener("input", () => {
          fb.texto = caixa.value;
          document.querySelectorAll(".fb-detalhe textarea").forEach((t) => { if (t !== caixa) t.value = caixa.value; });
        });
        const enviar = el("button", { type: "button", class: "fb-botao fb-enviar" }, "Enviar detalhe");
        enviar.addEventListener("click", enviarDetalhe);
        det.append(el("label", { for: id }, "Se quiser, conte o que você queria ver. Isso ajuda o criador do site a melhorar."),
          caixa, enviar);
      }
      b.append(det);
    }
  }
  function atualizarBlocos() {
    document.querySelectorAll(".feedback").forEach(preencherBloco);
    document.querySelectorAll(".fb-aviso").forEach((x) => { x.disabled = fb.detalheEnviado; });
  }
  // Botão dentro do aviso amarelo "Não entendi bem...": já envia "ruim" e leva até a caixinha opcional
  function botaoAviso() {
    const x = el("button", { type: "button", class: "fb-botao fb-aviso" }, "Não achou o que queria? Conte pra gente");
    x.addEventListener("click", () => {
      if (!fb.enviado) votar("ruim");
      else if (!fb.detalheAberto) { fb.detalheAberto = true; atualizarBlocos(); }
      const caixa = document.querySelector(".fb-detalhe textarea");
      if (caixa) { caixa.scrollIntoView({ behavior: "smooth", block: "center" }); caixa.focus({ preventScroll: true }); }
    });
    return x;
  }

  // ------------------------------------------------------------ busca
  function buscar(texto) {
    texto = (texto || "").trim();
    if (!texto || !motor) return;
    status.textContent = ""; aviso.hidden = true;
    fb = novoFeedback(); frasePedida = texto;
    delete document.body.dataset.feedback; delete document.body.dataset.detalhe; delete document.body.dataset.ultimoEnvio;
    // semente nova a cada busca: "me surpreenda" sorteia outros filmes; nos outros pedidos ela não muda nada
    atual = motor.recomendar(texto, { semente: Math.floor(Math.random() * 4294967296) });
    candidatos = atual.proximos(CANDIDATOS);  // ordem padrão = ordem do motor
    const avisosMotor = (atual.reconhecido.avisos || []).join(" ");
    if (atual.modo === "aleatorio") {
      aviso.textContent = "Sorteamos filmes bem avaliados para você. Busque de novo para sortear outros, ou clique em “Ver mais 5”." +
        (avisosMotor ? " " + avisosMotor : "");
      aviso.hidden = false;
    } else if (avisosMotor && atual.modo !== "sinopse" && atual.modo !== "reserva_populares") {
      aviso.textContent = avisosMotor;
      aviso.hidden = false;
    }
    if (atual.modo === "sinopse") {
      aviso.textContent = (avisosMotor ? avisosMotor + " " : "") +
        "Não entendi bem o seu pedido, então procurei nas sinopses por palavras parecidas com o que você escreveu. " +
        "Se quiser, tente descrever o gênero, o clima ou o tema (ex.: “comédia leve”, “suspense com reviravolta”).";
      if (FEEDBACK_ATIVO) aviso.append(" ", botaoAviso());
      aviso.hidden = false;
      guardarFrase(texto, atual.modo);
    } else if (atual.modo === "reserva_populares") {
      aviso.textContent = (avisosMotor ? avisosMotor + " " : "") +
        "Não entendi bem o seu pedido, mas estes são filmes que agradam a quase todo mundo. " +
        "Tente descrever o gênero, o clima ou o tema (ex.: “comédia leve”, “suspense com reviravolta”).";
      if (FEEDBACK_ATIVO) aviso.append(" ", botaoAviso());
      aviso.hidden = false;
      guardarFrase(texto, atual.modo);
    }
    document.body.dataset.modo = atual.modo;
    controles.hidden = !candidatos.length;
    visiveis = POR_VEZ;
    desenhar();
    if (!candidatos.length) status.textContent = "Nenhum filme encontrado com esse pedido. Tente pedir de outro jeito.";
  }

  $("busca").addEventListener("submit", (e) => { e.preventDefault(); buscar(campo.value); });
  campo.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); buscar(campo.value); } });
  document.querySelectorAll(".exemplo").forEach((b) => b.addEventListener("click", () => { campo.value = b.textContent; buscar(b.textContent); }));
  mais.addEventListener("click", () => { visiveis += POR_VEZ; desenhar(); });
  ["ordem", "f-nota", "f-ano", "f-duracao", "f-assinatura"].forEach((id) => $(id).addEventListener("change", reiniciar));
  montarServicos();

  status.textContent = "Carregando a lista de filmes…";
  MotorT.carregar("data/").then((m) => {
    motor = m;
    botao.disabled = false; botao.textContent = "Sugerir filmes";
    status.textContent = "";
    document.body.dataset.pronto = "1";
    const q = new URLSearchParams(location.search).get("q");
    if (q) { campo.value = q; buscar(q); }
  }).catch((e) => {
    status.textContent = "Não consegui carregar os dados. Abra o site por um servidor local (python -m http.server), não direto pelo arquivo.";
    document.body.dataset.erro = String(e.message || e);
  });
})();
