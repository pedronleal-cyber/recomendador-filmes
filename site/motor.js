/*
 * Motor T em JavaScript — mesmo comportamento do motor_t.py (Python).
 * Roda 100% no navegador (ou no Node, para testes). Sem IA, sem servidor, sem bibliotecas.
 *
 * Dados (gerados por exportar_site.py em site/data/): config.json, filmes.json, palavras_chave.json,
 * etiquetas.json (derivado do MovieLens: uso não comercial, com citação; ver LICENCAS.html), tfidf.json.
 */
(function (global) {
  "use strict";

  const f32 = Math.fround;

  // ------------------------------------------------------------------ texto
  function semAcento(s) {
    return String(s).toLowerCase().normalize("NFKD").replace(/\p{Mn}/gu, "");
  }
  // v7: igual ao so_letras do Python
  const soLetras = (s) => (String(s).match(/[a-z0-9]+/g) || []).join(" ");
  function separarEspacos(s) {
    s = s.trim();
    return s ? s.split(/\s+/) : [];
  }
  function tirarPontas(s, chars) {
    let a = 0, b = s.length;
    while (a < b && chars.includes(s[a])) a++;
    while (b > a && chars.includes(s[b - 1])) b--;
    return s.slice(a, b);
  }
  const cacheRe = new Map();
  function re(padrao, flags) {
    const chave = flags + "\u0000" + padrao;
    if (!cacheRe.has(chave)) cacheRe.set(chave, new RegExp(padrao, flags));
    const r = cacheRe.get(chave);
    r.lastIndex = 0;
    return r;
  }
  function* acharTodos(padrao, texto) {
    const r = new RegExp(padrao, "g");
    let m;
    while ((m = r.exec(texto)) !== null) {
      yield m;
      if (m[0] === "") r.lastIndex++;
    }
  }

  // ------------------------------------------------------------------ raiz das palavras (Snowball português)
  const VOGAIS = new Set("aeiouáéíóúâêô");
  const ehV = (c) => VOGAIS.has(c);
  function regioes(w) {
    const n = w.length;
    let pV = n, p1 = n, p2 = n;
    if (n >= 2) {
      if (ehV(w[0])) {
        if (!ehV(w[1])) { for (let i = 2; i < n; i++) if (ehV(w[i])) { pV = i + 1; break; } }
        else { for (let i = 2; i < n; i++) if (!ehV(w[i])) { pV = i + 1; break; } }
      } else {
        if (!ehV(w[1])) { for (let i = 2; i < n; i++) if (ehV(w[i])) { pV = i + 1; break; } }
        else if (n >= 3) pV = 3;
      }
    }
    const passar = (i, pred) => { for (; i < n; i++) if (pred(w[i])) return i + 1; return -1; };
    let i = passar(0, ehV);
    if (i >= 0) { i = passar(i, (c) => !ehV(c));
      if (i >= 0) { p1 = i; i = passar(i, ehV);
        if (i >= 0) { i = passar(i, (c) => !ehV(c)); if (i >= 0) p2 = i; } } }
    return { pV, p1, p2 };
  }
  function maisLongo(w, lista, limite = 0) {
    let melhor = null;
    for (const s of lista) if (s.length <= w.length - limite && w.endsWith(s) && (!melhor || s.length > melhor.length)) melhor = s;
    return melhor;
  }
  const PADRAO_A = ["eza", "ezas", "ico", "ica", "icos", "icas", "ismo", "ismos", "ável", "ível", "ista", "istas", "oso", "osa",
    "osos", "osas", "amento", "amentos", "imento", "imentos", "adora", "ador", "aça~o", "adoras", "adores", "aço~es", "ante",
    "antes", "ância"];
  const PADRAO = { A: PADRAO_A, B: ["logia", "logias"], C: ["uça~o", "uço~es"], D: ["ência", "ências"], E: ["amente"],
    F: ["mente"], G: ["idade", "idades"], H: ["iva", "ivo", "ivas", "ivos"], I: ["ira", "iras"] };
  const TODOS_PADRAO = Object.values(PADRAO).flat();
  const VERBO = ["ada", "ida", "ia", "aria", "eria", "iria", "ará", "ara", "erá", "era", "irá", "ava", "asse", "esse", "isse",
    "aste", "este", "iste", "ei", "arei", "erei", "irei", "am", "iam", "ariam", "eriam", "iriam", "aram", "eram", "iram", "avam",
    "em", "arem", "erem", "irem", "assem", "essem", "issem", "ado", "ido", "ando", "endo", "indo", "ara~o", "era~o", "ira~o",
    "ar", "er", "ir", "as", "adas", "idas", "ias", "arias", "erias", "irias", "arás", "aras", "erás", "eras", "irás", "avas",
    "es", "ardes", "erdes", "irdes", "ares", "eres", "ires", "asses", "esses", "isses", "astes", "estes", "istes", "is", "ais",
    "eis", "íeis", "aríeis", "eríeis", "iríeis", "áreis", "areis", "éreis", "ereis", "íreis", "ireis", "ásseis", "ésseis",
    "ísseis", "áveis", "ados", "idos", "ámos", "amos", "íamos", "aríamos", "eríamos", "iríamos", "áramos", "éramos", "íramos",
    "ávamos", "emos", "aremos", "eremos", "iremos", "ássemos", "êssemos", "íssemos", "imos", "armos", "ermos", "irmos", "eu",
    "iu", "ou", "ira", "iras"];
  function raiz(palavra) {
    let w = palavra.replace(/ã/g, "a~").replace(/õ/g, "o~");
    const { pV, p1, p2 } = regioes(w);
    const corta = (n) => { w = w.slice(0, w.length - n); };
    function padrao() {
      const s = maisLongo(w, TODOS_PADRAO);
      if (!s) return false;
      const ini = w.length - s.length;
      const grupo = Object.keys(PADRAO).find((g) => PADRAO[g].includes(s));
      if (grupo === "A") { if (ini < p2) return false; corta(s.length); return true; }
      if (grupo === "B") { if (ini < p2) return false; w = w.slice(0, ini) + "log"; return true; }
      if (grupo === "C") { if (ini < p2) return false; w = w.slice(0, ini) + "u"; return true; }
      if (grupo === "D") { if (ini < p2) return false; w = w.slice(0, ini) + "ente"; return true; }
      if (grupo === "E") {
        if (ini < p1) return false;
        corta(s.length);
        const s2 = maisLongo(w, ["iv", "os", "ic", "ad"]);
        if (s2 && w.length - s2.length >= p2) {
          corta(s2.length);
          if (s2 === "iv" && w.endsWith("at") && w.length - 2 >= p2) corta(2);
        }
        return true;
      }
      if (grupo === "F") {
        if (ini < p2) return false;
        corta(s.length);
        const s2 = maisLongo(w, ["ante", "avel", "ível"]);
        if (s2 && w.length - s2.length >= p2) corta(s2.length);
        return true;
      }
      if (grupo === "G") {
        if (ini < p2) return false;
        corta(s.length);
        const s2 = maisLongo(w, ["abil", "ic", "iv"]);
        if (s2 && w.length - s2.length >= p2) corta(s2.length);
        return true;
      }
      if (grupo === "H") {
        if (ini < p2) return false;
        corta(s.length);
        if (w.endsWith("at") && w.length - 2 >= p2) corta(2);
        return true;
      }
      if (grupo === "I") {
        if (ini < pV || w[ini - 1] !== "e") return false;
        w = w.slice(0, ini) + "ir";
        return true;
      }
      return false;
    }
    function verbo() {
      const s = maisLongo(w, VERBO, pV);
      if (!s) return false;
      corta(s.length);
      return true;
    }
    if (padrao() || verbo()) {
      if (w.endsWith("i") && w[w.length - 2] === "c" && w.length - 1 >= pV) corta(1);
    } else {
      const s = maisLongo(w, ["os", "a", "i", "o", "á", "í", "ó"]);
      if (s && w.length - s.length >= pV) corta(s.length);
    }
    const s = maisLongo(w, ["e", "é", "ê", "ç"]);
    if (s === "ç") w = w.slice(0, -1) + "c";
    else if (s && w.length - 1 >= pV) {
      corta(1);
      if ((w.endsWith("u") && w[w.length - 2] === "g") || (w.endsWith("i") && w[w.length - 2] === "c")) {
        if (w.length - 1 >= pV) corta(1);
      }
    }
    return w.replace(/a~/g, "ã").replace(/o~/g, "õ");
  }

  const NOMES_IDIOMA = { ja: "japonês", ko: "coreano", fr: "francês", es: "espanhol", it: "italiano", de: "alemão",
    pt: "português", cn: "chinês", zh: "chinês", hi: "hindi" };

  // ------------------------------------------------------------------ arredondamento igual ao numpy (metade para o par)
  function arred4(x) {
    const y = x * 10000;
    let r = Math.round(y);
    if (Math.abs(y - Math.trunc(y)) === 0.5) r = 2 * Math.round(y / 2);
    return r / 10000;
  }

  // ------------------------------------------------------------------ escala 0 a 1 (com ou sem precisão simples)
  function escala(valores, idx, simples) {
    let menor = Infinity, maior = -Infinity;
    for (const i of idx) { const v = valores[i]; if (v < menor) menor = v; if (v > maior) maior = v; }
    const out = new Map();
    if (maior === menor) { for (const i of idx) out.set(i, 0); return out; }
    if (simples) { const d = f32(maior - menor); for (const i of idx) out.set(i, f32(f32(valores[i] - menor) / d)); }
    else { const d = maior - menor; for (const i of idx) out.set(i, (valores[i] - menor) / d); }
    return out;
  }

  // ================================================================== Motor
  function criar(dados) {
    const cfg = dados.config;
    const F = dados.filmes;
    const c = Object.fromEntries(F.campos.map((nome, i) => [nome, i]));
    const n = F.linhas.length;
    const col = (nome) => F.linhas.map((l) => l[c[nome]]);
    const filmes = {
      titulo: col("titulo"), tituloOrig: col("titulo_original"), ano: col("ano"),
      generos: col("generos").map((g) => new Set(g)), generosLista: col("generos"), duracao: col("duracao_min"),
      nota: col("nota"), votos: col("votos"), sinopse: col("sinopse"), streaming: col("streaming_assinatura_br"),
      idioma: col("idioma_original"), imdb: col("imdb_id"), notaAj: Float64Array.from(col("nota_ajustada")),
      tit: col("_tit"), titOrig: col("_tit_orig"), titCurto: col("_tit_curto"),
      seriePt: col("_serie_pt"), serieOrig: col("_serie_orig"),
      id: "id" in c ? col("id") : new Array(n).fill(null),
      poster: "poster_path" in c ? col("poster_path") : new Array(n).fill(null),
    };
    // v7: títulos sem pontuação ("corra!" -> "corra"), para a referência preferir o título exato
    filmes.titSl = filmes.tit.map(soLetras);
    filmes.titOrigSl = filmes.titOrig.map(soLetras);
    filmes.titCurtoSl = filmes.titCurto.map(soLetras);
    const vazias = new Set(cfg.palavras_vazias);
    const palavrasPedido = new Set(cfg.palavras_de_pedido);
    const negacoes = new Set(cfg.negacoes);
    const voltaPositivo = new Set(cfg.volta_positivo);

    // Palavras-chave (motor A)
    const kwVocab = dados.palavras.vocab;
    const kwPos = new Map(kwVocab.map((k, i) => [k, i]));
    const kwFilmes = dados.palavras.filmes;
    const kwMeta = kwVocab.map((k) => cfg.palavras_meta.some((m) => k.includes(m)));
    const dicA = cfg.dicionario_a.map(([tema, padroes, termos]) => ({
      tema, padroes, termos: new Set(termos.map((t) => kwPos.get(t)).filter((x) => x !== undefined)) }));

    // Etiquetas: coluna por etiqueta (precisão simples, como no Python)
    const E = dados.etiquetas;
    const nTags = E.vocab.length;
    const tagIdx = new Map(E.vocab.map((t, j) => [t, j]));
    const colTag = Array.from({ length: nTags }, () => new Float32Array(n));
    const origemTag = Array.from({ length: nTags }, () => new Uint8Array(n));
    E.filmes.forEach((lst, i) => {
      for (let k = 0; k < lst.length; k += 2) {
        const j = Math.floor(lst[k] / 3), fonte = lst[k] % 3;
        colTag[j][i] = f32((lst[k + 1] / 10000 - 0.5) / 0.5);
        origemTag[j][i] = fonte + 1;
      }
    });
    const normas = new Float32Array(n);
    for (let i = 0; i < n; i++) {
      let s = 0;
      for (let j = 0; j < nTags; j++) { const v = colTag[j][i]; if (v) s = f32(s + f32(v * v)); }
      const r = f32(Math.sqrt(s));
      normas[i] = r > 0 ? r : 1;
    }

    // Índice da sinopse (TF-IDF igual ao scikit-learn: tf sublinear, idf suavizado, norma l2)
    const T = dados.tfidf;
    const tfPos = new Map(T.vocab.map((t, j) => [t, j]));
    const idf = Float64Array.from(T.idf);
    const postings = Array.from({ length: T.vocab.length }, () => []);
    const docTermos = new Array(n);
    T.docs.forEach((lst, i) => {
      const termos = [], pesos = [];
      for (let k = 0; k < lst.length; k += 2) { termos.push(lst[k]); pesos.push((Math.log(lst[k + 1]) + 1) * idf[lst[k]]); }
      normalizar(pesos); normalizar(pesos);
      termos.forEach((t, k) => postings[t].push([i, pesos[k]]));
      docTermos[i] = new Set(termos);
    });
    function normalizar(v) {
      let s = 0; for (const x of v) s += x * x;
      const r = Math.sqrt(s);
      if (r > 0) for (let k = 0; k < v.length; k++) v[k] /= r;
    }
    function prepararTexto(texto) {
      const palavras = (semAcento(texto).match(/[a-z0-9]+/g) || []).filter((p) => !vazias.has(p) && p.length > 1);
      return palavras.map(raiz);
    }
    function similaridade(raizes) {
      const cont = new Map();
      for (const r of raizes) { if (r.length < 2) continue; const j = tfPos.get(r); if (j !== undefined) cont.set(j, (cont.get(j) || 0) + 1); }
      const sim = new Float64Array(n);
      if (!cont.size) return sim;
      const termos = [...cont.keys()].sort((a, b) => a - b);
      const pesos = termos.map((j) => (Math.log(cont.get(j)) + 1) * idf[j]);
      normalizar(pesos); normalizar(pesos);
      termos.forEach((j, k) => { for (const [i, w] of postings[j]) sim[i] += pesos[k] * w; });
      return sim;
    }

    // ---------------------------------------------------------------- negação
    function negacaoA(texto, pos) {
      const partes = texto.slice(0, pos).split(/[,.;!?]/);
      const antes = separarEspacos(partes[partes.length - 1]).slice(-3);
      for (let i = 0; i < antes.length; i++) {
        if (["nao", "sem", "nada", "nem"].includes(antes[i])) {
          return antes.slice(i + 1).some((q) => ["so", "apenas", "somente"].includes(q)) ? "nao_so" : "nao";
        }
      }
      return null;
    }
    function acharA(texto, padroes) {
      let sim = false, nao = false;
      for (const p of padroes) for (const m of acharTodos("\\b(?:" + p + ")", texto)) {
        const neg = negacaoA(texto, m.index);
        if (neg === null) sim = true; else if (neg === "nao") nao = true;
      }
      return sim ? "sim" : nao ? "nao" : null;
    }
    function negacaoT(texto, pos, janela = 10) {
      const partes = texto.slice(0, pos).split(/[.;!?]/);
      const palavras = separarEspacos(partes[partes.length - 1].split(",").join(" ")).slice(-janela);
      for (let i = palavras.length - 1; i >= 0; i--) {
        const p = palavras[i];
        if (voltaPositivo.has(p)) return null;
        if (negacoes.has(p)) return palavras.slice(i + 1, i + 3).some((q) => ["so", "apenas", "somente"].includes(q)) ? "nao_so" : "nao";
      }
      return null;
    }
    function acharT(texto, padroes) {
      let sim = false, nao = false;
      for (const p of padroes) for (const m of acharTodos("\\b(?:" + p + ")", texto)) {
        const neg = negacaoT(texto, m.index);
        if (neg === null) sim = true; else if (neg === "nao") nao = true;
      }
      return sim ? "sim" : nao ? "nao" : null;
    }

    // ---------------------------------------------------------------- filtros, referência, análise (motor A)
    function acharFiltros(t) {
      const filtros = {};
      const incluir = [], excluir = [];
      for (const [g, padroes] of cfg.generos) {
        const r = acharA(t, padroes);
        if (r === "sim") incluir.push(g); else if (r === "nao") excluir.push(g);
      }
      if (incluir.length) filtros.generos = incluir;
      if (excluir.length) filtros.sem_generos = excluir;
      let m = re("menos de (\\d+)\\s*h\\s*(\\d+)?", "").exec(t);
      if (m) filtros.duracao_max = parseInt(m[1]) * 60 + parseInt(m[2] || "0");
      else if ((m = re("menos de (\\d+)\\s*min", "").exec(t))) filtros.duracao_max = parseInt(m[1]);
      else if (re("\\bcurt[oa]\\b", "").test(t)) filtros.duracao_max = cfg.duracao_curto_padrao;
      for (const [palavra, servico] of cfg.servicos) {
        if (re("\\b" + palavra + "\\b", "").test(t)) { filtros.streaming = servico; break; }
      }
      if ((m = re("\\banos (\\d{2,4})\\b", "").exec(t))) {
        let d = parseInt(m[1]);
        if (d < 100) d += d >= 30 ? 1900 : 2000;
        filtros.ano_min = d; filtros.ano_max = d + 9;
      } else if ((m = re("\\bde (19\\d\\d|20\\d\\d)\\b", "").exec(t))) {
        filtros.ano_min = filtros.ano_max = parseInt(m[1]);
      }
      for (const [padrao, codigos] of cfg.idiomas) {
        if (re("\\b(" + padrao + ")\\b", "").test(t)) { filtros.idiomas = codigos; break; }
      }
      return filtros;
    }
    function aplicarFiltros(filtros) {
      const ok = new Array(n).fill(true);
      const kwSim = (filtros.palavras_chave || []).map((k) => kwPos.get(k));
      const kwNao = (filtros.sem_palavras_chave || []).map((k) => kwPos.get(k));
      for (let i = 0; i < n; i++) {
        if ("duracao_max" in filtros) { const d = filmes.duracao[i]; ok[i] = ok[i] && d !== null && d > 0 && d < filtros.duracao_max; }
        if ("duracao_ate" in filtros) { const d = filmes.duracao[i]; ok[i] = ok[i] && d !== null && d > 0 && d <= filtros.duracao_ate; }
        if ("duracao_minima" in filtros) { const d = filmes.duracao[i]; ok[i] = ok[i] && d !== null && d >= filtros.duracao_minima; }
        if ("streaming" in filtros) ok[i] = ok[i] && (filmes.streaming[i] || "").toLowerCase().includes(filtros.streaming);
        if ("ano_min" in filtros) { const a = filmes.ano[i]; ok[i] = ok[i] && a !== null && a >= filtros.ano_min && a <= filtros.ano_max; }
        if ("idiomas" in filtros) ok[i] = ok[i] && filtros.idiomas.includes(filmes.idioma[i]);
        if ("nota_min" in filtros) {
          const v = filmes.nota[i];
          ok[i] = ok[i] && v !== null && (filtros.nota_estrita ? v > filtros.nota_min : v >= filtros.nota_min);
        }
        if ("votos_max" in filtros) ok[i] = ok[i] && filmes.votos[i] !== null && filmes.votos[i] < filtros.votos_max;
        for (const k of kwSim) ok[i] = ok[i] && kwFilmes[i].includes(k);
        for (const k of kwNao) ok[i] = ok[i] && !kwFilmes[i].includes(k);
        for (const g of filtros.sem_generos || []) ok[i] = ok[i] && !filmes.generos[i].has(g);
        if (cred) { // v4: pessoas (todas as citadas), países e estúdios (qualquer um dos citados); negados excluem
          for (const g of filtros.pessoas || []) ok[i] = ok[i] && g.some((x) => cred.pessoas[i].has(x));
          if (filtros.pessoas_alguma && filtros.pessoas_alguma.length) ok[i] = ok[i] && filtros.pessoas_alguma.some((g) => g.some((x) => cred.pessoas[i].has(x)));
          for (const x of filtros.sem_pessoas || []) ok[i] = ok[i] && !cred.pessoas[i].has(x);
          if (filtros.paises && filtros.paises.length) ok[i] = ok[i] && filtros.paises.some((g) => paisOk(cred.paises[i], filmes.idioma[i], PAISES[g][3]));
          for (const g of filtros.sem_paises || []) ok[i] = ok[i] && !saiNoNegado(cred.paises[i], PAISES[g][3]);
          if (filtros.estudios && filtros.estudios.length) ok[i] = ok[i] && filtros.estudios.some((g) => cred.estudios[i].has(g));
          for (const g of filtros.sem_estudios || []) ok[i] = ok[i] && !cred.estudios[i].has(g);
        }
      }
      if ("generos" in filtros) {
        const quer = filtros.generos;
        const todos = ok.map((v, i) => v && quer.every((g) => filmes.generos[i].has(g)));
        const nTodos = todos.filter(Boolean).length;
        if (nTodos >= cfg.top_n || quer.length === 1) return todos;
        return ok.map((v, i) => v && quer.some((g) => filmes.generos[i].has(g)));
      }
      return ok;
    }
    function acharReferencia(t) {
      for (const m of acharTodos(cfg.gatilhos_referencia, t)) {
        const nome = tirarPontas(m[1].split(/,| mas | so que | porem | e que /)[0], " .!?");
        if (!nome) continue;
        const exato = [];
        for (let i = 0; i < n; i++) if (filmes.tit[i] === nome || filmes.titOrig[i] === nome || filmes.titCurto[i] === nome) exato.push(i);
        if (exato.length) return [nome, exato];
        if (cfg.pessoas[nome]) {
          const lista = new Set(cfg.pessoas[nome]);
          return [nome, filmes.titulo.map((t, i) => (lista.has(t) ? i : -1)).filter((i) => i >= 0)];
        }
        const franquia = [];
        for (let i = 0; i < n; i++) if (filmes.tit[i].startsWith(nome + " ") || filmes.titOrig[i].startsWith(nome + " ")) franquia.push(i);
        if (franquia.length) return [nome, franquia];
      }
      return [null, []];
    }
    function analisar(pedido) {
      let t = semAcento(pedido);
      const [refNome, refIdx] = acharReferencia(t);
      if (refNome) t = t.split(refNome).join(" ");
      return { texto: t, filtros: acharFiltros(t), referencia: refNome || "", refIdx };
    }
    function pontuarA(a) {
      const temas = [], negados = [];
      for (const d of dicA) {
        const r = acharA(a.texto, d.padroes);
        if (r === "sim") temas.push(d); else if (r === "nao") negados.push(d);
      }
      const pontos = new Float64Array(n);
      for (const d of temas) for (let i = 0; i < n; i++) {
        let b = 0; for (const k of kwFilmes[i]) if (d.termos.has(k)) b++;
        pontos[i] += (b > 0 ? 1 : 0) + 0.1 * Math.max(b - 1, 0);
      }
      for (const d of negados) for (let i = 0; i < n; i++) {
        if (kwFilmes[i].some((k) => d.termos.has(k))) pontos[i] -= 1;
      }
      if (a.refIdx.length) {
        const cont = new Map();
        for (const i of a.refIdx) for (const k of kwFilmes[i]) if (!kwMeta[k]) cont.set(k, (cont.get(k) || 0) + 1);
        for (let i = 0; i < n; i++) {
          let s = 0; for (const k of kwFilmes[i]) if (cont.has(k)) s += cont.get(k) / a.refIdx.length;
          pontos[i] += s;
        }
      }
      return { pontos, temas: temas.map((d) => d.tema), negados: negados.map((d) => d.tema), temasObj: temas };
    }

    // ---------------------------------------------------------------- séries
    function mesmaFamilia(k1, k2) {
      if (!k1 || !k2) return false;
      if (k1 === k2) return true;
      const [curta, longa] = k1.length <= k2.length ? [k1, k2] : [k2, k1];
      return curta.length >= 5 && longa.startsWith(curta + " ");
    }

    const dicT = cfg.dicionario_t.map(([nome, padroes, tags, companhia, nota, evita]) => ({ nome, padroes, tags, companhia, nota, evita: evita || [] }));
    const dicTOrdenado = [...dicT.filter((e) => e.companhia), ...dicT.filter((e) => !e.companhia)];

    // ================================================================ v3: rodada de correções do estresse
    // (mesmas regras do motor_t.py; listas e números vêm do config.json)
    const ANO_ATUAL = new Date().getFullYear();
    const setDe = (lst) => new Set(lst);
    const naoLongoAntes = setDe(cfg.nao_longo_antes), naoLongoDepois = setDe(cfg.nao_longo_depois), longoReforco = setDe(cfg.longo_reforco);
    const antigoNaoAntes = setDe(cfg.antigo_nao_antes), antigoNaoDepois = setDe(cfg.antigo_nao_depois);
    const ignorarCorrecao = new Set([...vazias, ...palavrasPedido, ...negacoes, ...voltaPositivo]);

    // raízes do índice da sinopse -> filmes com essa raiz no título (português ou original)
    const tituloTermo = new Map();
    for (let i = 0; i < n; i++) {
      const raizes = new Set(prepararTexto((filmes.titulo[i] || "") + " " + (filmes.tituloOrig[i] || "")));
      for (const r of raizes) { const j = tfPos.get(r); if (j !== undefined) { if (!tituloTermo.has(j)) tituloTermo.set(j, new Set()); tituloTermo.get(j).add(i); } }
    }
    const escaparRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const palavraAntes = (t, pos) => { const p = t.slice(0, pos).match(/[a-z0-9]+/g); return p ? p[p.length - 1] : ""; };
    const palavraDepois = (t, fim) => { const p = t.slice(fim).match(/[a-z0-9]+/g); return p ? p[0] : ""; };
    const numero = (s) => parseFloat(s.replace(",", "."));
    const naoNegado = (t, pos) => negacaoT(t, pos) !== "nao";

    function distancia1(a, b) {
      if (a === b) return true;
      const la = a.length, lb = b.length;
      if (Math.abs(la - lb) > 1) return false;
      if (la === lb) {
        const dif = [];
        for (let i = 0; i < la; i++) if (a[i] !== b[i]) dif.push(i);
        if (dif.length === 1) return true;
        return dif.length === 2 && dif[1] === dif[0] + 1 && a[dif[0]] === b[dif[1]] && a[dif[1]] === b[dif[0]];
      }
      const [curta, longa] = la < lb ? [a, b] : [b, a];
      let i = 0;
      while (i < curta.length && curta[i] === longa[i]) i++;
      return curta.slice(i) === longa.slice(i + 1);
    }
    function corrigir(texto) {
      const correcoes = [];
      for (const [errado, certo] of cfg.correcoes) {
        const novo = texto.replace(new RegExp("\\b" + escaparRe(errado) + "\\b", "g"), certo);
        if (novo !== texto) { correcoes.push([errado, certo]); texto = novo; }
      }
      const suspeitas = [];
      for (const w of acharTodos("[a-z]+", texto)) {
        const p = w[0];
        if (p.length >= cfg.min_letras_correcao && !ignorarCorrecao.has(p) && !tfPos.has(raiz(p))) suspeitas.push(w);
      }
      if (!suspeitas.length) return [texto, correcoes];
      const cobertos = [];
      for (const padrao of cfg.padroes_cobertura) for (const x of acharTodos("\\b(?:" + padrao + ")", texto)) cobertos.push([x.index, x.index + x[0].length]);
      const trocas = [];
      for (const w of suspeitas) {
        const p = w[0], ini = w.index, fim = w.index + p.length;
        if (cobertos.some(([a, b]) => a < fim && ini < b)) continue;
        let feito = false;
        for (const lit of cfg.vocab_correcao) {
          for (const k of [lit.length, lit.length + 1, lit.length - 1]) {
            if (k >= 1 && k <= p.length && distancia1(p.slice(0, k), lit)) {
              trocas.push([ini, fim, lit + p.slice(k)]); correcoes.push([p, lit + p.slice(k)]); feito = true; break;
            }
          }
          if (feito) break;
        }
      }
      for (let k = trocas.length - 1; k >= 0; k--) { const [ini, fim, novo] = trocas[k]; texto = texto.slice(0, ini) + novo + texto.slice(fim); }
      return [texto, correcoes];
    }
    // v7: ordem de preferência igual ao Python: título exato (completo ou curto, com ou sem pontuação; se vários,
    // o mais votado) -> lista à mão de pessoa -> franquia
    function resolverRef(nome, minPalavrasFranquia = 1) {
      const alvos = [nome, ...cfg.artigos_ref.map((a) => a + " " + nome)];
      for (const cols of [[filmes.tit, filmes.titSl, filmes.titOrig, filmes.titOrigSl, filmes.titCurto, filmes.titCurtoSl]]) {
        const achados = new Set();
        for (const alvo of alvos) {
          const sl = soLetras(alvo);
          for (let k = 0; k < cols.length; k += 2) {
            const c = cols[k], cSl = cols[k + 1];
            for (let i = 0; i < n; i++) if (c[i] === alvo || (sl !== "" && cSl[i] === sl)) achados.add(i);
          }
        }
        if (achados.size) {
          let melhor = -1;
          for (const i of [...achados].sort((x, y) => x - y)) if (melhor < 0 || filmes.votos[i] > filmes.votos[melhor]) melhor = i;
          return [melhor];
        }
      }
      for (const alvo of alvos) {
        if (cfg.pessoas[alvo]) {
          const lista = new Set(cfg.pessoas[alvo]);
          return filmes.titulo.map((x, i) => (lista.has(x) ? i : -1)).filter((i) => i >= 0);
        }
      }
      if (nome.split(/\s+/).filter((x) => x).length >= minPalavrasFranquia) {
        for (const alvo of alvos) {
          const franquia = [];
          for (let i = 0; i < n; i++) if (filmes.tit[i].startsWith(alvo + " ") || filmes.titOrig[i].startsWith(alvo + " ")) franquia.push(i);
          if (franquia.length) return franquia;
        }
      }
      return [];
    }
    // v6: se o nome não for um título, tenta dois títulos ("Matrix com Titanic") -> referência dupla
    // v7: gatilhos só de referência dupla ("entre X e Y", "meio X meio Y", "um X com cara de Y")
    function acharReferenciaT(t) {
      const resto = (fim) => tirarPontas(t.slice(fim).split(/,| mas | so que | porem | e que /)[0], " .!?");
      function dupla(nome, minPalavras) {
        for (const sep of acharTodos(cfg.separa_ref_dupla, nome)) {
          const n1 = nome.slice(0, sep.index).trim(), n2 = nome.slice(sep.index + sep[0].length).trim();
          if (n1 && n2) {
            const g1 = resolverRef(n1, minPalavras), g2 = resolverRef(n2, minPalavras);
            if (g1.length && g2.length) return [nome, [...new Set([...g1, ...g2])], [g1, g2]];
          }
        }
        return null;
      }
      for (const m of acharTodos(cfg.gatilhos_referencia_t, t)) {
        const nome = resto(m.index + m[0].length);
        if (!nome) continue;
        const idx = resolverRef(nome);
        if (idx.length) return [nome, idx, [idx]];
        const achou = dupla(nome, 1);
        if (achou) return achou;
      }
      for (const m of acharTodos(cfg.gatilhos_dupla_t, t)) {
        const nome = resto(m.index + m[0].length);
        const achou = nome ? dupla(nome, 2) : null;
        if (achou) return achou;
      }
      return [null, [], []];
    }
    function acharStreamingT(t) {
      for (const [padrao, servico] of cfg.servicos_t) {
        for (const m of acharTodos("\\b(?:" + padrao + ")(?!\\w)", t)) if (naoNegado(t, m.index)) return servico;
      }
      for (const [apelido, servico] of cfg.apelidos_servico) {
        for (const m of acharTodos("\\b" + cfg.contexto_servico + "(?:" + apelido + ")(?!\\w)", t)) if (naoNegado(t, m.index)) return servico;
      }
      return null;
    }
    function acharDuracaoT(t) {
      const minutos = (m) => (m.length === 2 ? parseInt(m[1]) : parseInt(m[1]) * 60 + (m[2] ? 30 : parseInt(m[3] || "0")));
      for (const p of cfg.duracao_mais_de) { const m = re(p, "").exec(t); if (m) return { duracao_minima: minutos(m) + 1 }; }
      for (const p of cfg.duracao_ate) { const m = re(p, "").exec(t); if (m) return { duracao_ate: minutos(m) }; }
      if (re(cfg.hora_e_meia, "").test(t)) return { duracao_ate: 90 };
      for (const m of acharTodos("\\blong[oa]s?\\b", t)) {
        const antes = palavraAntes(t, m.index), depois = palavraDepois(t, m.index + m[0].length);
        if (naoLongoAntes.has(antes) || naoLongoDepois.has(depois)) continue;
        if (negacaoT(t, m.index) === "nao") return { duracao_ate: cfg.duracao_nao_longo };
        if (m[0] === "longo" || m[0] === "longos" || longoReforco.has(antes)) return { duracao_minima: cfg.duracao_longo };
      }
      return {};
    }
    function acharEpocaT(t) {
      const achados = [];
      for (const p of cfg.epoca_recente) for (const m of acharTodos(p, t)) if (naoNegado(t, m.index)) achados.push([m.index, [ANO_ATUAL - cfg.anos_recente, 9999]]);
      for (const m of acharTodos(cfg.epoca_antigo, t)) {
        if (!antigoNaoAntes.has(palavraAntes(t, m.index)) && !antigoNaoDepois.has(palavraDepois(t, m.index + m[0].length)) && naoNegado(t, m.index)) achados.push([m.index, [0, cfg.ano_antigo_max]]);
      }
      for (const m of acharTodos(cfg.epoca_velho, t)) if (naoNegado(t, m.index)) achados.push([m.index, [0, cfg.ano_antigo_max]]);
      for (const m of acharTodos(cfg.epoca_moderno, t)) if (palavraAntes(t, m.index) !== "arte" && naoNegado(t, m.index)) achados.push([m.index, [cfg.ano_moderno_min, 9999]]);
      let melhor = null;
      for (const x of achados) if (melhor === null || x[0] < melhor[0]) melhor = x;
      return melhor ? melhor[1] : null;
    }
    function subirNota(filtros, valor, estrita) {
      const atual = filtros.nota_min;
      if (atual === undefined || valor > atual || (valor === atual && estrita)) { filtros.nota_min = valor; filtros.nota_estrita = estrita; }
    }
    function acharNotaT(t, filtros) {
      for (const [padrao, estrita] of cfg.nota_regras) {
        for (const m of acharTodos(padrao, t)) {
          const v = numero(m[1]);
          if (v <= 10 && naoNegado(t, m.index)) { subirNota(filtros, v, estrita); return; }
        }
      }
      for (const padrao of cfg.bem_avaliado) {
        for (const m of acharTodos("\\b(?:" + padrao + ")", t)) if (naoNegado(t, m.index)) { subirNota(filtros, cfg.nota_bem_avaliado, false); return; }
      }
    }
    function analisarT(pedido) {
      let t = semAcento(pedido);
      const [refNome, refIdx, refGrupos] = acharReferenciaT(t);
      if (refNome) t = t.split(refNome).join(" ");
      const avisos = [];
      // v4: pessoas e estúdios antes da correção de digitação; saem do texto
      const pessoas = [], semPessoas = [];
      let estudios = [], semEstudios = [];
      if (cred) {
        const trechos = [];
        for (const [forma, ids, ini, fim, amb] of acharPessoas(t)) {
          trechos.push([ini, fim]);
          if (amb) { avisos.push(formatar(cfg.aviso_sobrenome_ambiguo, forma, ids.map((i) => cred.nomes[i]).join(", "))); continue; }
          const neg = negacaoT(t, ini);
          if (neg === "nao") { for (const i of ids) if (!semPessoas.includes(i)) semPessoas.push(i); }
          else if (neg === null && !pessoas.some((g) => g.length === ids.length && g.every((x, k) => x === ids[k]))) pessoas.push([...ids]);
        }
        let trEst;
        [estudios, semEstudios, trEst] = acharEstudios(t);
        t = tirarTrechos(t, [...trechos, ...trEst]);
        const desconhecida = acharPessoaDesconhecida(pedido, t);
        if (desconhecida) avisos.push(formatar(cfg.aviso_pessoa_desconhecida, desconhecida));
      }
      let correcoes;
      [t, correcoes] = corrigir(t);
      const aleatorio = re(cfg.aleatorio, "").test(t);
      if (aleatorio) t = t.replace(new RegExp(cfg.aleatorio, "g"), " ");
      for (const [padrao, aviso] of cfg.sem_dados) {
        const ms = [...acharTodos("\\b(?:" + padrao + ")", t)];
        if (ms.some((x) => naoNegado(t, x.index))) { avisos.push(aviso); t = t.replace(new RegExp("\\b(?:" + padrao + ")", "g"), " "); }
      }
      const filtros = acharFiltros(t);
      delete filtros.streaming;
      const servico = acharStreamingT(t);
      if (servico) filtros.streaming = servico;
      if (!("duracao_max" in filtros)) Object.assign(filtros, acharDuracaoT(t));
      if (!("ano_min" in filtros)) { const ep = acharEpocaT(t); if (ep) { filtros.ano_min = ep[0]; filtros.ano_max = ep[1]; } }
      acharNotaT(t, filtros);
      const kwS = [], kwN = [];
      for (const [padrao, kw] of cfg.palavras_chave_tmdb) {
        const r = acharT(t, [padrao]);
        if (r === "sim") kwS.push(kw); else if (r === "nao") kwN.push(kw);
      }
      if (kwS.length) filtros.palavras_chave = kwS;
      if (kwN.length) filtros.sem_palavras_chave = kwN;
      if ([...acharTodos(cfg.pouco_conhecido, t)].some((x) => naoNegado(t, x.index))) {
        filtros.votos_max = cfg.mediana_votos;
        subirNota(filtros, cfg.nota_pouco_conhecido, false);
      }
      if (aleatorio) { filtros.aleatorio = true; subirNota(filtros, cfg.nota_aleatorio, false); }
      if (cred) { // v4: pessoas, estúdios e países viram filtros
        if (pessoas.length) filtros.pessoas = pessoas;
        if (semPessoas.length) filtros.sem_pessoas = semPessoas;
        if (estudios.length) filtros.estudios = estudios;
        if (semEstudios.length) filtros.sem_estudios = semEstudios;
        const [paises, semPaises] = acharPaises(t);
        if (paises.length) filtros.paises = paises;
        if (semPaises.length) filtros.sem_paises = semPaises;
        // "filme francês" agora é país de produção; o idioma só vale com "em francês / idioma francês"
        if ((paises.length || semPaises.length) && "idiomas" in filtros) {
          let explicito = false;
          for (const [p] of cfg.idiomas) for (const m of acharTodos("\\b(" + p + ")\\b", t)) if (antesIdioma.has(palavraAntes(t, m.index))) explicito = true;
          if (!explicito) delete filtros.idiomas;
        }
      }
      return { texto: t, filtros, referencia: refNome || "", refIdx, refGrupos, correcoes, avisos };
    }
    // reserva por sinopse: palavra do pedido que está no título do filme vale só 10%
    function similaridadeReserva(raizes) {
      const cont = new Map();
      for (const r of raizes) { if (r.length < 2) continue; const j = tfPos.get(r); if (j !== undefined) cont.set(j, (cont.get(j) || 0) + 1); }
      const sim = new Float64Array(n);
      if (!cont.size) return sim;
      const termos = [...cont.keys()].sort((a, b) => a - b);
      const pesos = termos.map((j) => (Math.log(cont.get(j)) + 1) * idf[j]);
      normalizar(pesos); normalizar(pesos);
      termos.forEach((j, k) => {
        const noTitulo = tituloTermo.get(j);
        for (const [i, w] of postings[j]) {
          let v = w * pesos[k];
          if (noTitulo && noTitulo.has(i)) v *= cfg.peso_palavra_do_titulo;
          sim[i] += v;
        }
      });
      return sim;
    }
    // sorteio igual ao Python (FNV-1a para a semente, mulberry32 para os números)
    function sementeDoTexto(s) {
      let h = 0x811c9dc5;
      for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
      return h >>> 0;
    }
    function mulberry32(a) {
      return function () {
        a |= 0; a = (a + 0x6d2b79f5) | 0;
        let t = Math.imul(a ^ (a >>> 15), 1 | a);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    }
    function embaralhar(lista, semente) {
      const lst = [...lista], rnd = mulberry32(semente >>> 0);
      for (let i = lst.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [lst[i], lst[j]] = [lst[j], lst[i]]; }
      return lst;
    }

    // ================================================================ v4: pessoas, países, estúdios e franquias
    // (creditos.json, do TMDB; mesmas regras do motor_t.py). Sem o arquivo, o motor funciona como a v3.
    const C = dados.creditos || null;
    const cred = C ? {
      nomes: C.pessoas, variantes: new Map(C.variantes), ambiguos: new Map(C.ambiguos),
      dir: C.filmes.map((x) => x[0]), pessoas: C.filmes.map((x) => new Set([...x[0], ...x[1]])),
      paises: C.filmes.map((x) => (x[2] ? x[2].split("|") : [])), estudios: C.filmes.map((x) => new Set(x[3])),
      colecao: C.filmes.map((x) => x[4]),
    } : null;
    const PAISES = cfg.paises || [], ESTUDIOS = cfg.estudios || [];
    // v6: vizinhos do MovieLens ([pos, pontos, pos, pontos...]) e recomendados do TMDB ([pos...]) por filme
    const R = dados.referencias || null;
    const refs = R ? {
      viz: R.viz.map((x) => { const l = []; for (let k = 0; k < x.length; k += 2) l.push([x[k], x[k + 1]]); return l; }),
      rec: R.rec,
    } : null;
    const antesIdioma = new Set(cfg.antes_idioma || []);
    const bloqueadasNome = new Set([...vazias, ...palavrasPedido, ...negacoes, ...voltaPositivo]);
    const formatar = (modelo, ...valores) => valores.reduce((s, v) => s.replace("{}", () => v), modelo);
    let reCobertura = null;
    function coberto(texto) {
      if (!reCobertura) reCobertura = new RegExp(cfg.padroes_cobertura.map((p) => "(?:\\b(?:" + p + "))").join("|"));
      return reCobertura.test(texto);
    }
    const normalizarNome = (s) => (semAcento(s).match(/[a-z0-9]+/g) || []).join(" ");
    const semAcentoMaiusc = (s) => String(s).normalize("NFKD").replace(/\p{Mn}/gu, "");
    function paisOk(paises, idioma, grupo) {
      if (!paises.length) return false;
      if (paises.every((p) => p in grupo)) return true;
      if (idioma === "en" && paises.includes("US") && !("US" in grupo)) return false;
      return paises.some((p) => p in grupo && grupo[p].includes(idioma));
    }
    const soDoGrupo = (paises, grupo) => paises.length > 0 && paises.every((p) => p in grupo);
    // País negado: "não seja americano" tira todo filme com EUA na produção; os outros, só os feitos só no grupo.
    const saiNoNegado = (paises, grupo) => ("US" in grupo ? paises.includes("US") : soDoGrupo(paises, grupo));
    function acharPessoas(t) {
      const toks = [...acharTodos("[a-z0-9]+", t)].map((m) => [m[0], m.index, m.index + m[0].length]);
      const achados = [];
      let i = 0;
      while (i < toks.length) {
        let achou = false;
        for (let k = Math.min(cfg.max_palavras_nome, toks.length - i); k > 0; k--) {
          const chave = toks.slice(i, i + k).map((x) => x[0]).join(" ");
          if (cred.variantes.has(chave) || cred.ambiguos.has(chave)) {
            const amb = !cred.variantes.has(chave);
            achados.push([chave, amb ? cred.ambiguos.get(chave) : cred.variantes.get(chave), toks[i][1], toks[i + k - 1][2], amb]);
            i += k; achou = true; break;
          }
        }
        if (!achou) i++;
      }
      return achados;
    }
    function acharEstudios(t) {
      const sim = [], nao = [], trechos = [];
      ESTUDIOS.forEach(([padrao, , , conflita], g) => {
        for (const m of acharTodos("\\b(?:" + padrao + ")(?!\\w)", t)) {
          const fim = m.index + m[0].length;
          if (conflita && (/^\s*(?:\+|plus\b)/.test(t.slice(fim)) || re("\\b" + cfg.contexto_servico + "$", "").test(t.slice(0, m.index)))) continue;
          const neg = negacaoT(t, m.index);
          if (neg === "nao") { if (!nao.includes(g)) nao.push(g); } else if (neg === null && !sim.includes(g)) sim.push(g);
          trechos.push([m.index, fim]);
        }
      });
      return [sim.filter((g) => !nao.includes(g)), nao, trechos];
    }
    function acharPaises(t) {
      const sim = [], nao = [];
      PAISES.forEach((p, g) => {
        for (const m of acharTodos("\\b(?:" + p[0] + ")", t)) {
          if (antesIdioma.has(palavraAntes(t, m.index))) continue;
          const neg = negacaoT(t, m.index);
          if (neg === "nao") { if (!nao.includes(g)) nao.push(g); } else if (neg === null && !sim.includes(g)) sim.push(g);
        }
      });
      return [sim.filter((g) => !nao.includes(g)), nao];
    }
    function tirarTrechos(t, trechos) {
      const ord = [...trechos].sort((x, y) => (y[0] - x[0]) || (y[1] - x[1]));
      for (const [ini, fim] of ord) t = t.slice(0, ini) + " " + t.slice(fim);
      return t;
    }
    function acharPessoaDesconhecida(original, t) {
      const palavrasT = " " + (t.match(/[a-z0-9]+/g) || []).join(" ") + " ";
      const desconhecido = (nome) => {
        if (!nome || !palavrasT.includes(" " + nome + " ") || coberto(nome)) return false;
        for (let i = 0; i < n; i++) {
          if (filmes.tit[i] === nome || filmes.titOrig[i] === nome || filmes.titCurto[i] === nome ||
            filmes.tit[i].startsWith(nome + " ") || filmes.titOrig[i].startsWith(nome + " ")) return false;
        }
        return true;
      };
      for (const m of acharTodos(cfg.pessoa_contexto, t)) {
        const nome = [];
        for (const w of (t.slice(m.index + m[0].length).match(/[a-z0-9]+|[,.;!?]/g) || []).slice(0, 3)) {
          if (bloqueadasNome.has(w) || !/^[a-z]+$/.test(w)) break;
          nome.push(w);
        }
        if (desconhecido(nome.join(" "))) return nome.join(" ");
      }
      for (const m of acharTodos(cfg.re_nome_maiusculo, semAcentoMaiusc(original))) {
        const toks = normalizarNome(m[0]).split(" ").filter(Boolean);
        let corrida = [];
        for (const w of [...toks, ""]) {
          if (w && !bloqueadasNome.has(w)) { corrida.push(w); continue; }
          if (corrida.length >= 2 && desconhecido(corrida.join(" "))) return corrida.join(" ");
          corrida = [];
        }
      }
      return null;
    }

    // ---------------------------------------------------------------- componentes (igual ao MotorT.componentes)
    function componentes(pedido) {
      let a = analisarT(pedido);
      let texto = a.texto;
      const pos = new Map(), neg = new Map(), temas = [], temasNeg = [], evita = new Map();
      let usaNota = false;
      for (const e of dicTOrdenado) {
        const r = acharT(texto, e.padroes);
        if (r === "sim") {
          temas.push(e.nome);
          usaNota = usaNota || e.nota;
          for (const [t, w] of e.tags) pos.set(t, Math.max(pos.get(t) || 0, w));
          for (const [t, w] of e.evita) evita.set(t, Math.max(evita.get(t) || 0, w));
          if (e.companhia) for (const p of e.padroes) texto = texto.replace(new RegExp("\\b(?:" + p + ")", "g"), " ");
        } else if (r === "nao") {
          temasNeg.push(e.nome);
          for (const [t, w] of e.tags) neg.set(t, Math.max(neg.get(t) || 0, w));
        }
      }
      for (const t of [...neg.keys()]) if (pos.has(t)) neg.delete(t);
      for (const [t, w] of evita) { neg.set(t, Math.max(neg.get(t) || 0, w)); pos.delete(t); }
      const termosNegados = [];
      for (const [padrao, tags] of cfg.tags_por_termo) {
        for (const m of acharTodos("\\b(?:" + padrao + ")", texto)) {
          if (negacaoT(texto, m.index) === "nao") {
            termosNegados.push(m[0]);
            for (const [t, w] of tags) { neg.set(t, Math.max(neg.get(t) || 0, w)); pos.delete(t); }
            break;
          }
        }
      }
      const filtros = Object.assign({}, a.filtros);
      delete filtros.generos; delete filtros.sem_generos;
      const incluir = [], excluirG = [];
      for (const [g, padroes] of cfg.generos) {
        const r = acharT(texto, padroes);
        if (r === "sim") incluir.push(g); else if (r === "nao") excluirG.push(g);
      }
      if (incluir.length) filtros.generos = incluir;
      if (excluirG.length) filtros.sem_generos = excluirG;
      // Idiomas só do motor T ("asiático"), quando o pedido não citou um idioma específico
      if (!("idiomas" in filtros)) {
        for (const [padrao, codigos] of cfg.idiomas_t || []) {
          if (re("\\b(" + padrao + ")\\b", "").test(texto)) { filtros.idiomas = codigos; break; }
        }
      }
      a = Object.assign({}, a, { filtros, texto });

      // pontuação das etiquetas (precisão simples, mesma ordem do Python)
      const dict = new Float32Array(n);
      for (const [t, w] of pos) { const col = colTag[tagIdx.get(t)], fw = f32(w); for (let i = 0; i < n; i++) dict[i] = f32(dict[i] + f32(fw * col[i])); }
      for (const [t, w] of neg) { const col = colTag[tagIdx.get(t)], fw = f32(w); for (let i = 0; i < n; i++) dict[i] = f32(dict[i] - f32(fw * col[i])); }

      // referência: perfil de etiquetas do filme citado (cosseno) + exclusão da série
      let refCos = null;
      const excluir = new Set(a.refIdx);
      if (a.refIdx.length) {
        refCos = cosPerfil(a.refIdx);
        for (const i of a.refIdx) {
          for (let k = 0; k < n; k++) {
            if (mesmaFamilia(filmes.serieOrig[k], filmes.serieOrig[i]) || mesmaFamilia(filmes.seriePt[k], filmes.seriePt[i])) excluir.add(k);
          }
        }
        // v4: filme citado que pertence a uma coleção do TMDB (franquia): sai a coleção inteira
        if (cred) {
          const colecoes = new Set(a.refIdx.map((i) => cred.colecao[i]).filter((x) => x));
          if (colecoes.size) for (let k = 0; k < n; k++) if (colecoes.has(cred.colecao[k])) excluir.add(k);
        }
      }
      const ok = aplicarFiltros(filtros);
      let candidatos = [];
      for (let i = 0; i < n; i++) if (ok[i] && !excluir.has(i)) candidatos.push(i);
      // v4: nenhum filme da pessoa combina com o resto do pedido -> mostra os filmes dela (de qualquer uma das citadas)
      if (filtros.pessoas && filtros.pessoas.length && !candidatos.length) {
        const so = aplicarFiltros({ pessoas_alguma: filtros.pessoas });
        const alt = [];
        for (let i = 0; i < n; i++) if (so[i] && !excluir.has(i)) alt.push(i);
        if (alt.length) {
          candidatos = alt;
          const nomes = filtros.pessoas.map((g) => cred.nomes[g[0]]).join(" e ");
          a = Object.assign({}, a, { avisos: [...a.avisos, formatar(cfg.aviso_pessoa_sem_combinar, nomes, nomes)] });
        }
      }
      // v6: referência com vizinhos do MovieLens e recomendados do TMDB (pesos.ref); sem eles, só etiquetas (como antes)
      let refNovo = null;
      const pr = cfg.pesos.ref;
      if (a.refGrupos.length && pr && (pr.ml || pr.tmdb) && refs) {
        refNovo = pontuarReferencia(a.refGrupos, candidatos, pr);
        candidatos = refNovo.candidatos;
      }

      const A = pontuarA(analisar(pedido));
      // sinopse (motor B): só é usada na nota final se o peso B for maior que zero
      let B = null;
      if (cfg.pesos.b !== 0) {
        let busca = a.texto;
        if (a.refIdx.length) busca += " " + a.refIdx.map((i) => filmes.sinopse[i] || "").join(" ");
        B = similaridade(prepararTexto(busca));
      }
      // sinopse para a reserva: sem as palavras de pedido que não dizem nada sobre o filme
      const palavras = (texto.match(/[a-z0-9]+/g) || []).filter((p) => !palavrasPedido.has(p) && !vazias.has(p));
      const raizesReserva = palavras.length ? prepararTexto(palavras.join(" ")) : [];
      const simReserva = palavras.length ? similaridadeReserva(raizesReserva) : new Float64Array(n);

      const entendeu = pos.size > 0 || neg.size > 0 || A.temas.length > 0 || A.negados.length > 0 ||
        Object.keys(filtros).length > 0 || a.refIdx.length > 0;
      return { a, candidatos, dict, refCos, refNovo, A, B, simReserva, raizesReserva, palavrasReserva: palavras,
        pos, neg, temas, temasNeg, termosNegados, excluir, entendeu, usaTags: pos.size > 0 || neg.size > 0, usaNota };
    }

    // cosseno entre o perfil de etiquetas (média) dos filmes idx e cada filme; null sem etiquetas (igual ao Python)
    function cosPerfil(idx) {
      const perfil = new Float32Array(nTags);
      for (let j = 0; j < nTags; j++) {
        let s = 0; for (const i of idx) s = f32(s + colTag[j][i]);
        perfil[j] = f32(s / idx.length);
      }
      let soma = 0; for (const v of perfil) soma += v;
      if (!(soma > 0)) return null;
      let np2 = 0; for (const v of perfil) np2 = f32(np2 + f32(v * v));
      const normaPerfil = f32(Math.sqrt(np2));
      const out = new Float32Array(n);
      for (let i = 0; i < n; i++) {
        let d = 0; for (let j = 0; j < nTags; j++) { const v = colTag[j][i]; if (v) d = f32(d + f32(v * perfil[j])); }
        out[i] = f32(d / f32(normas[i] * normaPerfil));
      }
      return out;
    }
    // v6: ML x vizinhos + TMDB x recomendados + etiquetas x cosseno, cada parte 0-1 nos candidatos; dupla: soma
    function pontuarReferencia(grupos, candidatos, pr) {
      const ml = new Float64Array(n), tm = new Float64Array(n), tag = new Float64Array(n);
      let temMl = false;
      const porGrupo = [];
      for (const g of grupos) {
        const mlg = new Float64Array(n), tmg = new Float64Array(n);
        for (const r of g) {
          for (const [j, p] of refs.viz[r]) if (p > mlg[j]) mlg[j] = p;
          for (const j of refs.rec[r]) tmg[j] = 1;
          if (refs.viz[r].length) temMl = true;
        }
        for (let i = 0; i < n; i++) { ml[i] += mlg[i]; tm[i] += tmg[i]; }
        const cg = cosPerfil(g);
        if (cg) for (let i = 0; i < n; i++) tag[i] += cg[i];
        porGrupo.push({ g, mlg, tmg });
      }
      let wMl = pr.ml, wTm = pr.tmdb, wTag = pr.tags;
      let cand = candidatos;
      if (!temMl) {
        const soma = wTm + wTag;
        wMl = 0; wTm = soma ? wTm / soma : 0; wTag = soma ? wTag / soma : 0;
      } else {
        const uniao = candidatos.filter((i) => ml[i] > 0 || tm[i] > 0);
        if (uniao.length >= cfg.top_n) cand = uniao;
      }
      const eMl = escala(ml, cand, false), eTm = escala(tm, cand, false), eTag = escala(tag, cand, false);
      const pontos = new Float64Array(n);
      for (const i of cand) pontos[i] = wMl * eMl.get(i) + wTm * eTm.get(i) + wTag * eTag.get(i);
      return { pontos, candidatos: cand, porGrupo };
    }

    // ---------------------------------------------------------------- recomendar
    function recomendar(pedido, opcoes = {}) {
      const cp = componentes(pedido);
      const cand = cp.candidatos;
      const p = cfg.pesos;
      let final, modo, aviso = "";
      const soFiltros = !(cp.usaTags || cp.a.refIdx.length || cp.A.temas.length || cp.usaNota);
      if (cp.a.filtros.aleatorio) {
        // sorteio entre os candidatos (já com nota 7,5+); sem semente, ela sai do pedido (igual ao Python)
        modo = "aleatorio";
        const semente = opcoes.semente === undefined || opcoes.semente === null ? sementeDoTexto(semAcento(pedido)) : opcoes.semente;
        const ordemSorteio = embaralhar(cand, semente);
        final = new Map(ordemSorteio.map((i, k) => [i, (ordemSorteio.length - k) / ordemSorteio.length]));
      } else if (cp.entendeu && soFiltros) {
        modo = "filtros";
        final = escala(filmes.notaAj, cand, false);
      } else if (cp.entendeu) {
        modo = "etiquetas";
        const partes = [];
        if (cp.usaTags) partes.push({ v: escala(cp.dict, cand, true), simples: true });
        if (cp.refNovo) partes.push({ v: escala(cp.refNovo.pontos, cand, false), simples: false });
        else if (cp.refCos) partes.push({ v: escala(cp.refCos, cand, true), simples: true });
        if (cp.usaNota) partes.push({ v: escala(filmes.notaAj, cand, false), simples: false });
        // soma das partes (precisão simples enquanto todas forem simples, como no pandas)
        const tags = new Map();
        let simples = true;
        if (!partes.length) for (const i of cand) tags.set(i, 0);
        else {
          for (const i of cand) tags.set(i, 0);
          for (const parte of partes) {
            simples = simples && parte.simples;
            for (const i of cand) { const s = tags.get(i) + parte.v.get(i); tags.set(i, simples ? f32(s) : s); }
          }
          for (const i of cand) { const d = tags.get(i) / partes.length; tags.set(i, simples ? f32(d) : d); }
        }
        const tagsArr = new Float64Array(n); for (const [i, v] of tags) tagsArr[i] = v;
        const eT = escala(tagsArr, cand, simples);
        const eA = escala(cp.A.pontos, cand, false);
        const eB = cp.B ? escala(cp.B, cand, false) : null;
        const pT = simples ? f32(p.tags) : p.tags;
        final = new Map();
        for (const i of cand) {
          let v = simples ? f32(pT * eT.get(i)) : pT * eT.get(i);
          v = v + p.a * eA.get(i);
          if (eB) v = v + p.b * eB.get(i);
          final.set(i, v);
        }
      } else {
        let max = -Infinity; for (const i of cand) if (cp.simReserva[i] > max) max = cp.simReserva[i];
        if (max >= cfg.limiar_sinopse) { modo = "sinopse"; final = escala(cp.simReserva, cand, false); }
        else { modo = "reserva_populares"; aviso = cfg.aviso_leve; final = escala(filmes.notaAj, cand, false); }
      }
      const pontos = new Map(); for (const [i, v] of final) pontos.set(i, arred4(v));
      const ordem = [...cand].sort((x, y) => (pontos.get(y) - pontos.get(x)) || (filmes.notaAj[y] - filmes.notaAj[x]) || (x - y));

      // seleção com diversidade (no máximo 1 filme por série), em páginas de 5
      const chaves = [], escolhidos = [];
      let cursor = 0;
      function proximos(qtd = cfg.top_n) {
        const novos = [];
        while (cursor < ordem.length && novos.length < qtd) {
          const i = ordem[cursor++];
          if (chaves.some(([k1, k2]) => mesmaFamilia(filmes.serieOrig[i], k1) || mesmaFamilia(filmes.seriePt[i], k2))) continue;
          chaves.push([filmes.serieOrig[i], filmes.seriePt[i]]);
          escolhidos.push(i);
          novos.push(descrever(i));
        }
        return novos;
      }
      function descrever(i) {
        return {
          indice: i, titulo: filmes.titulo[i], tituloOriginal: filmes.tituloOrig[i], ano: filmes.ano[i],
          generos: filmes.generosLista[i], duracao: filmes.duracao[i], nota: filmes.nota[i], sinopse: filmes.sinopse[i],
          votos: filmes.votos[i], idTmdb: filmes.id[i], poster: filmes.poster[i],
          streaming: filmes.streaming[i] ? filmes.streaming[i].split("|") : [], pontos: pontos.get(i), motivo: motivo(i),
        };
      }
      function motivo(i) {
        const itens = [];
        if (modo === "etiquetas") {
          const casadas = [];
          for (const [t, w] of cp.pos) {
            const j = tagIdx.get(t), v = colTag[j][i];
            if (v > 0) casadas.push({ rotulo: E.rotulos_pt[j], estimada: origemTag[j][i] === 3, peso: w * v, fonte: E.fontes[origemTag[j][i] - 1] });
          }
          casadas.sort((x, y) => y.peso - x.peso);
          casadas.slice(0, 4).forEach((x) => itens.push(x));
          for (const d of cp.A.temasObj) {
            if (kwFilmes[i].some((k) => d.termos.has(k))) itens.push({ rotulo: d.tema, estimada: false, fonte: "palavras-chave" });
          }
          let motivoRef = false;
          if (cp.refNovo) {
            // v6: quem gostou do filme citado (MovieLens) / recomendado pelo TMDB
            for (const { g, mlg, tmg } of cp.refNovo.porGrupo) {
              const deMl = g.find((r) => refs.viz[r].some(([j]) => j === i));
              if (mlg[i] > 0 && deMl !== undefined) { itens.push({ rotulo: "quem gostou de " + filmes.titulo[deMl] + " também gostou", estimada: false, fonte: "MovieLens" }); motivoRef = true; }
              const deTm = g.find((r) => refs.rec[r].includes(i));
              if (tmg[i] > 0 && deTm !== undefined) { itens.push({ rotulo: "recomendado a quem gosta de " + filmes.titulo[deTm], estimada: false, fonte: "TMDB" }); motivoRef = true; }
            }
          }
          if (!motivoRef && cp.a.refIdx.length && cp.refCos && cp.refCos[i] > 0) itens.push({ rotulo: "perfil parecido com " + filmes.titulo[cp.a.refIdx[0]], estimada: false, fonte: "referência" });
        } else if (modo === "sinopse") {
          const termos = docTermos[i];
          const vistas = new Set();
          cp.palavrasReserva.forEach((pal) => {
            const r = raiz(pal);
            const j = tfPos.get(r);
            if (j !== undefined && termos.has(j) && !vistas.has(pal)) { vistas.add(pal); itens.push({ rotulo: pal, estimada: false, fonte: "sinopse" }); }
          });
        } else if (modo === "filtros") {
          itens.push({ rotulo: "um dos mais bem avaliados entre os que passam nos filtros", estimada: false, fonte: "nota" });
        } else if (modo === "aleatorio") {
          itens.push({ rotulo: "sorteado entre os filmes com nota " + String(cp.a.filtros.nota_min).replace(".", ",") + "+", estimada: false, fonte: "nota" });
        } else {
          itens.push({ rotulo: "um dos filmes mais bem avaliados", estimada: false, fonte: "nota" });
        }
        // Filtros reconhecidos também explicam a sugestão (só texto; não muda o ranking)
        const fl = cp.a.filtros;
        if (modo === "etiquetas" || modo === "filtros" || modo === "aleatorio") {
          const add = (rotulo) => itens.push({ rotulo, estimada: false, fonte: "filtro" });
          (fl.generos || []).forEach((g) => add("gênero " + g.toLowerCase()));
          if (fl.idiomas) add("filme em " + (NOMES_IDIOMA[fl.idiomas[0]] || fl.idiomas[0]));
          if (fl.streaming) add("no catálogo " + fl.streaming.replace(/\b\w/g, (x) => x.toUpperCase()));
          if (fl.duracao_max) add("menos de " + fl.duracao_max + " min");
          if (fl.duracao_ate) add("até " + fl.duracao_ate + " min");
          if (fl.duracao_minima) add("a partir de " + fl.duracao_minima + " min");
          if (fl.ano_min !== undefined) {
            add(fl.ano_min === fl.ano_max ? "de " + fl.ano_min : fl.ano_max >= 9999 ? "de " + fl.ano_min + " em diante"
              : fl.ano_min <= 0 ? "até " + fl.ano_max : "anos " + fl.ano_min + "–" + fl.ano_max);
          }
          if (fl.nota_min !== undefined && !fl.aleatorio) add((fl.nota_estrita ? "nota acima de " : "nota ") + String(fl.nota_min).replace(".", ",") + (fl.nota_estrita ? "" : "+"));
          if (fl.votos_max) add("pouco conhecido");
          (fl.palavras_chave || []).forEach((k) => add(cfg.rotulos_palavra_chave[k] || k));
          (fl.sem_palavras_chave || []).forEach((k) => add("sem " + (cfg.rotulos_palavra_chave[k] || k)));
          if (cred) { // v4: pessoa, país e estúdio
            for (const g of fl.pessoas || []) {
              const pid = g.find((x) => cred.pessoas[i].has(x));
              if (pid !== undefined) add(cred.dir[i].includes(pid) ? "dirigido por " + cred.nomes[pid] : "com " + cred.nomes[pid] + " no elenco");
            }
            for (const x of fl.sem_pessoas || []) add("sem " + cred.nomes[x]);
            for (const g of fl.paises || []) if (paisOk(cred.paises[i], filmes.idioma[i], PAISES[g][3])) add(PAISES[g][1] + " (país de produção)");
            for (const g of fl.sem_paises || []) add(PAISES[g][2]);
            for (const g of fl.estudios || []) if (cred.estudios[i].has(g)) add("estúdio " + ESTUDIOS[g][1]);
            for (const g of fl.sem_estudios || []) add("não é do estúdio " + ESTUDIOS[g][1]);
          }
        }
        // Sem repetir o mesmo nome (ex.: etiqueta "espaço" e tema "espaço")
        const vistos = new Set();
        return itens.filter((x) => { const k = x.rotulo.toLowerCase(); if (vistos.has(k)) return false; vistos.add(k); return true; });
      }
      return {
        modo, aviso, proximos,
        reconhecido: { temas: cp.temas, temasNegados: cp.temasNeg, temasMotorA: cp.A.temas, termosNegados: cp.termosNegados,
          filtros: cp.a.filtros, referencia: cp.a.referencia, avisos: cp.a.avisos, correcoes: cp.a.correcoes,
          pessoas: cred ? (cp.a.filtros.pessoas || []).map((g) => cred.nomes[g[0]]) : [],
          excluidos: [...cp.excluir].sort((x, y) => x - y).map((i) => filmes.titulo[i]) },
      };
    }

    return { recomendar, raiz, semAcento, prepararTexto, n };
  }

  // Carregar no navegador
  async function carregar(base = "data/") {
    // Um arquivo de cada vez (downloads simultâneos grandes foram cortados no teste local com antivírus);
    // tenta de novo até 5 vezes, com pausa crescente, se a conexão cair.
    const nomes = ["config", "filmes", "palavras_chave", "etiquetas", "tfidf", "creditos", "referencias"];
    // sem creditos.json o site funciona como a v3 (sem pessoas, países e estúdios); sem referencias.json, a referência usa só etiquetas
    const opcionais = new Set(["creditos", "referencias"]);
    const dados = {};
    for (const nm of nomes) {
      let erro;
      for (let tentativa = 0; tentativa < 5; tentativa++) {
        if (tentativa) await new Promise((ok) => setTimeout(ok, 400 * tentativa));
        try {
          const r = await fetch(base + nm + ".json", { cache: "no-cache" });
          if (r.status === 404 && opcionais.has(nm)) { dados[nm] = null; erro = null; break; }
          if (!r.ok) throw new Error("Falha ao carregar " + nm + " (" + r.status + ")");
          dados[nm] = await r.json();
          erro = null;
          break;
        } catch (e) { erro = e; }
      }
      if (erro) throw erro;
    }
    return criar({ config: dados.config, filmes: dados.filmes, palavras: dados.palavras_chave, etiquetas: dados.etiquetas, tfidf: dados.tfidf, creditos: dados.creditos, referencias: dados.referencias });
  }

  const api = { criar, carregar, raiz, semAcento };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else global.MotorT = api;
})(typeof self !== "undefined" ? self : this);
