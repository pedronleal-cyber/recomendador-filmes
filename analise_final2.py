"""
Análise do teste final (pedidos 91 a 110). Só lê os resultados já gerados; não muda motor, dicionário nem pesos.

Uso:
    python -I analise_final2.py
Saídas: relatorio_teste_final.txt e resultados_T_final2_top5.csv
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

import motor as m

MOTORES = ["A", "B", "H70", "T", "T-palavras"]
VISTOS_ANTES = {95, 99, 102}
linhas = []


def out(t=""):
    print(t)
    linhas.append(t)


def tabela(res_por_motor, titulo):
    out("\n" + titulo)
    out(f"{'motor':<12}{'acerto':>14}{'precisão':>10}{'NDCG@5':>8}{'cobertura':>11}{'estrito (autor)':>17}{'avisos':>8}")
    for nome, res in res_por_motor.items():
        r = m.resumo_metricas(res)
        estrito = f"{(res.acertou_estrito == 'sim').sum()}/{len(res)}" if "acertou_estrito" in res else "–"
        out(f"{nome:<12}{m.txt_acerto(r):>14}{r['precisao']:>10.2f}{r['ndcg5']:>8.3f}{r['cobertura']:>11}"
            f"{estrito:>17}{r['avisos']:>8}")


def por_estilo(res_por_motor):
    base = res_por_motor["A"]
    for metrica, rotulo in (("acerto", "Acerto por estilo"), ("ndcg5", "NDCG@5 por estilo"), ("precisao", "Precisão por estilo")):
        out(f"\n{rotulo}:")
        out(f"{'estilo':<12}{'n':>4}" + "".join(f"{n:>12}" for n in res_por_motor))
        for e in dict.fromkeys(base.estilo):
            ln = f"{e:<12}{(base.estilo == e).sum():>4}"
            for res in res_por_motor.values():
                g = res[res.estilo == e]
                v = (g.acertou == "sim").mean() if metrica == "acerto" else g[metrica].mean()
                ln += f"{v:>12.0%}" if metrica == "acerto" else f"{v:>12.2f}"
            out(ln)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    res = {n: pd.read_csv(f"resultados_{n}_final2.csv", keep_default_na=False) for n in MOTORES}
    for r in res.values():
        for c in ("precisao", "ndcg5"):
            r[c] = pd.to_numeric(r[c])
    pedidos = m.ler_pedidos("pedidos_final2.csv").set_index("numero")

    out("=" * 80)
    out("TESTE FINAL — pedidos 91 a 110 (rodado uma única vez; dicionário, pesos e motor não mudaram)")
    out("=" * 80)
    out("A, B e H70 usam o catálogo de 2.000 filmes; T e T-palavras, o de 6.000.")
    out("Nota estrita: a coluna filmes_do_autor está vazia no pedidos_final2.csv, então não se aplica (–).")
    out("T = pesos 0,7 etiquetas / 0,3 palavras-chave / 0 sinopse. T-palavras = mesmo motor T com 0 / 1 / 0.")
    tabela(res, "1) Todos os 20 pedidos:")
    por_estilo({k: v for k, v in res.items()})
    sem = {n: r[~r.numero.isin(VISTOS_ANTES)] for n, r in res.items()}
    tabela(sem, f"\n2) Sem os pedidos {sorted(VISTOS_ANTES)} (já vistos num diagnóstico): 17 pedidos")
    rt, rp = m.resumo_metricas(res["T"]), m.resumo_metricas(res["T-palavras"])
    out(f"\n3) Ganho das etiquetas (T contra T só com palavras-chave): acerto {rp['acertos']} -> {rt['acertos']} "
        f"de 20; NDCG@5 {rp['ndcg5']:.3f} -> {rt['ndcg5']:.3f}; precisão {rp['precisao']:.2f} -> {rt['precisao']:.2f}")
    ganhos = res["T"].merge(res["T-palavras"], on="numero", suffixes=("", "_p"))
    so_t = ganhos[(ganhos.acertou == "sim") & (ganhos.acertou_p == "não")].numero.tolist()
    so_p = ganhos[(ganhos.acertou == "não") & (ganhos.acertou_p == "sim")].numero.tolist()
    out(f"   Pedidos que só o T (com etiquetas) acertou: {so_t}; que só o T-palavras acertou: {so_p}")

    # 4) Erros do T
    from motor_t import MotorT
    mt = MotorT()
    f = mt.filmes
    imdb_com_fonte = set(pd.read_csv("etiquetas_unificadas.csv", usecols=["imdb_id"], dtype=str).imdb_id)
    tit_para_imdb = f.groupby("titulo").imdb_id.apply(lambda s: set(s.dropna()))
    rT = res["T"]
    erros = rT[rT.acertou == "não"]
    out(f"\n4) Pedidos que o T errou: {len(erros)} de 20")
    for r in erros.itertuples():
        c = mt.componentes(r.pedido)  # releitura das etiquetas ativadas (mesmo cálculo do teste)
        p = pedidos.loc[r.numero]
        gab = [t.strip() for t in p.boas_respostas.split("|") if t.strip()]
        sem_fonte = [t for t in gab if not (tit_para_imdb.get(t, set()) & imdb_com_fonte)]
        out(f"\n  #{r.numero} [{r.estilo}] {r.pedido}")
        if r.aviso:
            out(f"     AVISO: {r.aviso}")
        out("     top 5: " + " · ".join(str(getattr(r, f"top{i}")) for i in range(1, 6) if getattr(r, f"top{i}", "")))
        out(f"     etiquetas ativadas: {', '.join(f'{k} {v}' for k, v in c['pos'].items()) or 'nenhuma'}")
        if c["neg"]:
            out(f"     etiquetas negadas: {', '.join(c['neg'])}")
        out(f"     filtros: {r.filtros_aplicados or 'nenhum'}" + (f" | referência: {r.referencia}" if r.referencia else ""))
        out(f"     gabarito sem fonte de etiquetas: {len(sem_fonte)} de {len(gab)}"
            + (f" ({', '.join(sem_fonte[:6])}{'...' if len(sem_fonte) > 6 else ''})" if sem_fonte else ""))

    # 5) Top 5 do T por pedido, para o autor avaliar
    linhas_top = []
    for r in rT.itertuples():
        p = pedidos.loc[r.numero]
        gab = {t.strip() for t in p.boas_respostas.split("|") if t.strip()}
        citados_autor = {t.strip() for t in p.filmes_do_autor.split("|") if t.strip()}
        for i in range(1, 6):
            v = getattr(r, f"top{i}", "")
            if not v:
                continue
            mt_ = re.match(r"^(.*) \((\d{4})\)$", v)
            titulo, ano = (mt_.group(1), mt_.group(2)) if mt_ else (v, "")
            linhas_top.append({"numero": r.numero, "estilo": r.estilo, "pedido": r.pedido, "posicao": i,
                               "titulo": titulo, "ano": ano, "no_gabarito": "sim" if titulo in gab else "não",
                               "citado_pelo_autor": "sim" if titulo in citados_autor else "não", "nota_do_autor": ""})
        if r.aviso:
            linhas_top.append({"numero": r.numero, "estilo": r.estilo, "pedido": r.pedido, "posicao": "",
                               "titulo": r.aviso, "ano": "", "no_gabarito": "", "citado_pelo_autor": "", "nota_do_autor": ""})
    pd.DataFrame(linhas_top).to_csv("resultados_T_final2_top5.csv", index=False, encoding="utf-8")
    out(f"\n5) Top 5 do T por pedido salvo em resultados_T_final2_top5.csv ({len(linhas_top)} linhas; "
        f"coluna nota_do_autor em branco para ele preencher).")

    with open("relatorio_teste_final.txt", "w", encoding="utf-8") as arq:
        arq.write("\n".join(linhas) + "\n")
    print("\nSalvo em relatorio_teste_final.txt")


if __name__ == "__main__":
    main()
