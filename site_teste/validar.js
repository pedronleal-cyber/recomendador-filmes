// Compara o motor JS (site/motor.js) com as saídas do Python (referencia_python.json e raizes_python.json).
// Não é medição de desempenho: só confere se o porte é fiel.
const fs = require("fs");
const path = require("path");
const base = path.join(__dirname, "..", "site");
const MotorT = require(path.join(base, "motor.js"));
const ler = (nome) => JSON.parse(fs.readFileSync(path.join(base, "data", nome + ".json"), "utf-8"));

const raizesPy = JSON.parse(fs.readFileSync(path.join(__dirname, "raizes_python.json"), "utf-8"));
let iguais = 0; const difs = [];
for (const [w, r] of Object.entries(raizesPy)) { if (MotorT.raiz(w) === r) iguais++; else difs.push([w, r, MotorT.raiz(w)]); }
console.log(`1) Raízes das palavras: ${iguais} de ${Object.keys(raizesPy).length} iguais` + (difs.length ? `; diferentes (ex.): ${JSON.stringify(difs.slice(0, 10))}` : ""));

const t0 = Date.now();
const temCreditos = fs.existsSync(path.join(base, "data", "creditos.json"));
const temRefs = fs.existsSync(path.join(base, "data", "referencias.json"));
const motor = MotorT.criar({ config: ler("config"), filmes: ler("filmes"), palavras: ler("palavras_chave"), etiquetas: ler("etiquetas"), tfidf: ler("tfidf"), creditos: temCreditos ? ler("creditos") : null, referencias: temRefs ? ler("referencias") : null });
console.log(`   (motor JS carregado em ${((Date.now() - t0) / 1000).toFixed(1)} s)`);
const ref = JSON.parse(fs.readFileSync(path.join(__dirname, "referencia_python.json"), "utf-8"));
let identicos = 0, mesmoConjunto = 0, modosIguais = 0, avisosIguais = 0; const diferentes = [], avisosDif = [];
const tempos = [];
for (const r of ref) {
  const t1 = Date.now();
  const res = motor.recomendar(r.pedido);
  const top = res.proximos(5);
  tempos.push(Date.now() - t1);
  const idxJs = top.map((x) => x.indice);
  if (res.modo === r.modo) modosIguais++;
  if (JSON.stringify(res.reconhecido.avisos || []) === JSON.stringify(r.avisos || [])) avisosIguais++;
  else avisosDif.push({ numero: r.numero, py: r.avisos, js: res.reconhecido.avisos });
  if (JSON.stringify(idxJs) === JSON.stringify(r.top)) identicos++;
  else {
    const mesmo = idxJs.length === r.top.length && idxJs.every((i) => r.top.includes(i));
    if (mesmo) mesmoConjunto++;
    diferentes.push({ numero: r.numero, modoPy: r.modo, modoJs: res.modo, py: r.top, js: idxJs, pontosPy: r.pontos, pontosJs: top.map((x) => x.pontos), mesmoConjunto: mesmo });
  }
}
console.log(`2) Top 5 (pedidos 91 a 170 + frases do estresse 201 a 361 + inventadas): ${identicos} de ${ref.length} idênticos (mesmos filmes na mesma ordem); ` +
  `${mesmoConjunto} com os mesmos filmes em outra ordem; ${ref.length - identicos - mesmoConjunto} com filmes diferentes. ` +
  `Caminho de resposta igual em ${modosIguais} de ${ref.length}. Avisos iguais em ${avisosIguais} de ${ref.length}.`);
console.log(`   Tempo médio por pedido no JS: ${(tempos.reduce((a, b) => a + b, 0) / tempos.length).toFixed(0)} ms`);
for (const d of diferentes) console.log("   diferença:", JSON.stringify(d));
for (const d of avisosDif) console.log("   aviso diferente:", JSON.stringify(d));
