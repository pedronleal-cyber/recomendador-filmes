// Teste do motor do site com frases novas (inventadas para o protótipo). Não é medição.
const fs = require("fs");
const path = require("path");
const base = path.join(__dirname, "..", "site");
const MotorT = require(path.join(base, "motor.js"));
const ler = (n) => JSON.parse(fs.readFileSync(path.join(base, "data", n + ".json"), "utf-8"));
const motor = MotorT.criar({ config: ler("config"), filmes: ler("filmes"), palavras: ler("palavras_chave"), etiquetas: ler("etiquetas"), tfidf: ler("tfidf") });
const frases = process.argv.slice(2);
for (const q of frases) {
  const r = motor.recomendar(q);
  console.log(`\n>> ${q}\n   caminho: ${r.modo}${r.aviso ? " | aviso: " + r.aviso : ""}`);
  r.proximos(5).forEach((f, k) => {
    const porque = f.motivo.map((m) => m.rotulo + (m.estimada ? " (etiqueta estimada)" : "")).join(", ");
    console.log(`   ${k + 1}. ${f.titulo} (${f.ano}) — ${f.streaming.length ? f.streaming.slice(0, 2).join(", ") : "não encontrado em assinatura"} | por quê: ${porque}`);
  });
}
