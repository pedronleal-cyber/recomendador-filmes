"""
Escolha dos pesos da recomendação por REFERÊNCIA (v6), só com pedidos de DESENVOLVIMENTO:
os pedidos de estilo "referência" de pedidos_teste.csv, pedidos_validacao.csv, pedidos_final.csv (71-90) e
pedidos_final2.csv (91-110, com o gabarito humano de gabarito_final2_humano.csv).
Os pedidos 111-140 e 141-170 são conjuntos consumidos e NÃO entram aqui.

As frases de referência do estresse (categoria "referencia") não têm gabarito: aparecem só como inspeção
(top 5 de cada combinação), sem entrar na escolha.

Regra de escolha (fixada antes de rodar): maior média entre NDCG@5 e HitRate@5; empate -> maior NDCG@5;
empate de novo -> fica a configuração atual (só etiquetas).

Uso: python -I avaliar_referencia.py           (mostra a tabela e grava relatorio_referencia_pesos.txt)
     python -I avaliar_referencia.py --gravar  (também grava os pesos escolhidos em pesos_t.json, chave "ref")
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

import motor as m
from motor_t import ARQ_PESOS, MotorT

COMBINACOES = [
    ("atual (só etiquetas)", {"ml": 0.0, "tmdb": 0.0, "tags": 1.0}),
    ("ML 0,5 / TMDB 0,2 / etiquetas 0,3", {"ml": 0.5, "tmdb": 0.2, "tags": 0.3}),
    ("ML 0,7 / TMDB 0,1 / etiquetas 0,2", {"ml": 0.7, "tmdb": 0.1, "tags": 0.2}),
]
SAIDA = "relatorio_referencia_pesos.txt"


def pedidos_dev():
    partes = []
    for arq in ["pedidos_teste.csv", "pedidos_validacao.csv", "pedidos_final.csv", "pedidos_final2.csv"]:
        d = pd.read_csv(arq, dtype=str, keep_default_na=False)
        partes.append(d[d.estilo.str.startswith("refer")][["numero", "estilo", "pedido", "boas_respostas"]])
    d = pd.concat(partes, ignore_index=True)
    # 91-110: gabarito humano (notas do autor), no lugar da coluna boas_respostas original
    hum = pd.read_csv("gabarito_final2_humano.csv", dtype=str, keep_default_na=False).set_index("numero").boas_respostas
    d["boas_respostas"] = [hum.get(n, b) if 91 <= int(n) <= 110 else b for n, b in zip(d.numero, d.boas_respostas)]
    assert not d.numero.astype(int).between(111, 170).any()
    return d


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    dev = pedidos_dev()
    tmp = os.path.join(tempfile.mkdtemp(), "ref_dev.csv")
    dev.to_csv(tmp, index=False, encoding="utf-8")
    estresse = pd.read_csv("pedidos_estresse.csv", dtype=str, keep_default_na=False)
    estresse = estresse[estresse.categoria == "referencia"]

    base = json.load(open(ARQ_PESOS, encoding="utf-8"))
    mt = MotorT(pesos={k: v for k, v in base.items() if k != "ref"})
    L = ["ESCOLHA DOS PESOS DA REFERÊNCIA (só pedidos de desenvolvimento)", "=" * 70,
         f"Pedidos de desenvolvimento ({len(dev)}): " + ", ".join(f"#{n}" for n in dev.numero),
         "HitRate@5 = pedidos com pelo menos 1 filme bom no top 5; NDCG@5 = 1 se os bons estão todos no topo.",
         "Escolha: maior média (NDCG@5 + HitRate@5)/2; empate -> maior NDCG@5; empate -> fica a atual.", ""]
    linhas, por_pedido, inspecao = [], {}, {}
    for nome, pr in COMBINACOES:
        mt.pesos = dict({k: v for k, v in base.items() if k != "ref"}, ref=pr)
        mt._cache = {}
        res = m.avaliar(mt, tmp)
        hit, ndcg = (res.acertou == "sim").mean(), res.ndcg5.mean()
        linhas.append((nome, pr, hit, ndcg, (hit + ndcg) / 2, res.precisao.mean()))
        por_pedido[nome] = res
        inspecao[nome] = [(p.numero, p.pedido, " | ".join(mt.recomendar(p.pedido)[0].titulo)) for p in estresse.itertuples()]
    L.append(f"{'combinação':<36}{'HitRate@5':>10}{'NDCG@5':>8}{'média':>8}{'precisão':>10}")
    for nome, pr, hit, ndcg, media, prec in linhas:
        L.append(f"{nome:<36}{hit:>10.2f}{ndcg:>8.3f}{media:>8.3f}{prec:>10.2f}")
    ordem = sorted(range(len(linhas)), key=lambda k: (-round(linhas[k][4], 6), -round(linhas[k][3], 6), k))
    escolhida = linhas[ordem[0]]
    L.append(f"\nESCOLHIDA: {escolhida[0]}  {json.dumps(escolhida[1])}")
    L.append("\nPOR PEDIDO (acertou / NDCG@5 / top 5)")
    for k, p in enumerate(dev.itertuples()):
        L.append(f"\n#{p.numero} \"{p.pedido}\"")
        for nome, *_ in linhas:
            r = por_pedido[nome].iloc[k]
            L.append(f"   {nome:<36} {r.acertou:<4} {r.ndcg5:.3f}  {r.top_titulos}")
    L.append("\nINSPEÇÃO: FRASES DE REFERÊNCIA DO ESTRESSE (sem gabarito; não entram na escolha)")
    for k, (n, ped, _) in enumerate(inspecao[linhas[0][0]]):
        L.append(f"\n#{n} \"{ped}\"")
        for nome, *_ in linhas:
            L.append(f"   {nome:<36} {inspecao[nome][k][2]}")
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:12 + len(linhas)]))
    print(f"... relatório completo em {SAIDA}")
    if "--gravar" in sys.argv:
        novo = dict({k: v for k, v in base.items() if k != "ref"}, ref=escolhida[1])
        json.dump(novo, open(ARQ_PESOS, "w", encoding="utf-8"))
        print(f"pesos_t.json atualizado: {json.dumps(novo)}")


if __name__ == "__main__":
    main()
