"""
Tabela única de etiquetas (Tag Genome + MovieLens 32M + IA), na mesma régua.
Não cria nem altera o motor.

Uso:
    python -I unificar_etiquetas.py

Passos:
    1. Aplica as decisões sobre os sinônimos duvidosos -> sinonimos_ml32m_aprovados.csv
       (o sinonimos_ml32m.csv original fica como registro da proposta).
    2. Monta etiquetas_unificadas.csv: imdb_id, tag, score (posição percentual 0-1 dentro da
       etiqueta e da fonte), nota_original, fonte (tagenome / ml32m / ia).
    3. Relatório de cobertura -> relatorio_etiquetas.txt

Por que a "posição percentual": cada fonte mede de um jeito (Tag Genome dá notas altas em algumas
etiquetas para quase todo filme; no ml-32m 0,10 já é muito; a IA só usa 0,3/0,6/0,9). A posição
percentual responde sempre a mesma pergunta: dentro desta fonte, quão alto este filme está nesta
etiqueta em comparação com os outros filmes da mesma fonte?
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # para importar diagnostico_tags (mesma pasta)

import numpy as np
import pandas as pd

PASTA_ML = os.path.join("dados_externos", "ml32m", "ml-32m")
MIN_PESSOAS = 2
ML_BOA_ETIQ = 5
REMOVER_SEMPRE = {("life & death", "death"), ("love story", "love"),
                  ("family drama", "family"), ("first contact", "aliens")}
ARQS_IA = ["etiquetas_ia_piloto.csv", "etiquetas_ia.csv"]

linhas = []


def out(t=""):
    print(t)
    linhas.append(t)


def pct(n, de):
    return f"{100 * n / de:.0f}%" if de else "-"


def normalizar(t):
    return re.sub(r"\s+", " ", str(t).strip().lower())


def aprovar_sinonimos():
    sin = pd.read_csv("sinonimos_ml32m.csv", keep_default_na=False)
    sin["razao_tag_genome"] = pd.to_numeric(sin.razao_tag_genome, errors="coerce")
    duv = sin.duvidoso != ""
    regra = (duv & (sin.razao_tag_genome < 1.5) & (~sin.variante.str.contains(r"[\s-]")) & (sin.n_filmes > 1000))
    fixo = sin.apply(lambda r: (r.etiqueta_vocabulario, r.variante) in REMOVER_SEMPRE, axis=1)
    removidos = sin[fixo | regra]
    aprovados = sin[~(fixo | regra)]
    aprovados.to_csv("sinonimos_ml32m_aprovados.csv", index=False, encoding="utf-8")
    out("=" * 76)
    out("0) SINÔNIMOS APROVADOS (sinonimos_ml32m_aprovados.csv)")
    out("=" * 76)
    out(f"Duvidosos na proposta: {duv.sum()}. Removidos: {len(removidos)} "
        f"({fixo.sum()} por decisão direta, {(regra & ~fixo).sum()} pela regra razão<1,5 + palavra única + 1000+ filmes).")
    for r in removidos.itertuples():
        motivo = "decisão direta" if (r.etiqueta_vocabulario, r.variante) in REMOVER_SEMPRE else "regra"
        out(f"   - {r.etiqueta_vocabulario} <- {r.variante} (razão {r.razao_tag_genome}, {r.n_filmes} filmes; {motivo})")
    mantidos = aprovados[aprovados.duvidoso != ""]
    out(f"Duvidosos mantidos: {len(mantidos)}: " + ", ".join(f"{r.variante}->{r.etiqueta_vocabulario}" for r in mantidos.itertuples()))
    out(f"Linhas na tabela aprovada: {len(aprovados)} (de {len(sin)})")
    return aprovados


def posicao(df):
    """Posição percentual da nota dentro de cada (fonte, etiqueta): maior perto de 1, menor perto de 0."""
    return df.groupby("tag").nota_original.rank(pct=True, method="average")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    import diagnostico_tags as dg

    sin = aprovar_sinonimos()
    vocab = list(pd.read_csv("vocabulario_piloto.csv").tag)
    f = dg.carregar()
    f = f[f.imdb_id.notna() & (f.imdb_id != "")].drop_duplicates("imdb_id")
    partes = []

    # --- Tag Genome (GLMER), só as 150 etiquetas do vocabulário, todos os filmes etiquetados
    T = dg.matriz_etiquetas(dg.carregar())[vocab]
    T.index = dg.carregar().imdb_id.reindex(T.index).values
    T = T[~T.index.duplicated()]
    tg = T.stack().rename("nota_original").reset_index()
    tg.columns = ["imdb_id", "tag", "nota_original"]
    tg["score"] = posicao(tg)
    tg["fonte"] = "tagenome"
    partes.append(tg)

    # --- ml-32m: pessoas que usaram a etiqueta (ou sinônimo aprovado) / pessoas que etiquetaram o filme
    links = pd.read_csv(os.path.join(PASTA_ML, "links.csv")).dropna(subset=["tmdbId"])
    links["tmdbId"] = links.tmdbId.astype(int)
    ml_por_tmdb = links.drop_duplicates("tmdbId").set_index("tmdbId").movieId
    f["movieId"] = f.id.map(ml_por_tmdb)
    nossos = f.dropna(subset=["movieId"]).copy()
    nossos["movieId"] = nossos.movieId.astype(int)
    tags = pd.read_csv(os.path.join(PASTA_ML, "tags.csv"), dtype={"tag": str}).dropna(subset=["tag"])
    tags = tags[tags.movieId.isin(set(nossos.movieId))]
    tags["tag_n"] = tags.tag.map(normalizar)
    etiquetadores = tags.groupby("movieId").userId.nunique()
    var_para_vocab = dict(zip(sin.variante, sin.etiqueta_vocabulario))
    tags["vocab"] = tags.tag_n.map(var_para_vocab)
    pessoas = tags.dropna(subset=["vocab"]).groupby(["movieId", "vocab"]).userId.nunique().rename("pessoas").reset_index()
    pessoas = pessoas[pessoas.pessoas >= MIN_PESSOAS]
    pessoas["nota_original"] = pessoas.pessoas / pessoas.movieId.map(etiquetadores)
    imdb_por_ml = nossos.set_index("movieId").imdb_id
    pessoas["imdb_id"] = pessoas.movieId.map(imdb_por_ml)
    # base da posição: todos os filmes com etiquetas no ml-32m (quem não usou a etiqueta conta como 0)
    base_ml = etiquetadores.index
    ml_rows = []
    for tag, g in pessoas.groupby("vocab"):
        notas = pd.Series(0.0, index=base_ml)
        notas.loc[g.movieId.values] = g.nota_original.values
        rk = notas.rank(pct=True, method="average")
        gg = g.assign(score=rk.loc[g.movieId.values].values, tag=tag)
        ml_rows.append(gg[["imdb_id", "tag", "nota_original", "score"]])
    ml = pd.concat(ml_rows)
    ml["fonte"] = "ml32m"
    partes.append(ml)

    # --- IA (piloto + rodadas novas), mesma ideia: quem não recebeu a etiqueta conta como 0
    ia = pd.concat([pd.read_csv(a, dtype={"imdb_id": str}) for a in ARQS_IA if os.path.exists(a)])
    ia = ia.drop_duplicates(["imdb_id", "tag"])
    filmes_ia = ia.imdb_id.unique()
    ia_rows = []
    for tag, g in ia.groupby("tag"):
        notas = pd.Series(0.0, index=filmes_ia)
        notas.loc[g.imdb_id.values] = g.score.values
        rk = notas.rank(pct=True, method="average")
        ia_rows.append(pd.DataFrame({"imdb_id": g.imdb_id.values, "tag": tag,
                                     "nota_original": g.score.values, "score": rk.loc[g.imdb_id.values].values}))
    iad = pd.concat(ia_rows)
    iad["fonte"] = "ia"
    partes.append(iad)

    uni = pd.concat(partes, ignore_index=True)[["imdb_id", "tag", "score", "nota_original", "fonte"]]
    uni["score"] = uni.score.round(4)
    uni["nota_original"] = uni.nota_original.astype(float).round(4)
    uni = uni.sort_values(["imdb_id", "fonte", "score"], ascending=[True, True, False])
    uni.to_csv("etiquetas_unificadas.csv", index=False, encoding="utf-8")

    out("\n" + "=" * 76)
    out("1) TABELA ÚNICA (etiquetas_unificadas.csv)")
    out("=" * 76)
    out(f"{len(uni)} linhas, {uni.imdb_id.nunique()} filmes, {uni.tag.nunique()} etiquetas do vocabulário.")
    for fonte, g in uni.groupby("fonte"):
        out(f"   {fonte:<9} {g.imdb_id.nunique():>5} filmes, {len(g):>7} linhas "
            f"(nota original de {g.nota_original.min():.2f} a {g.nota_original.max():.2f}; média por filme "
            f"{len(g) / g.imdb_id.nunique():.1f} etiquetas)")
    out("   Tag Genome guarda as 150 etiquetas de cada filme (nota graduada); ml-32m e IA guardam só as que")
    out("   apareceram (ml-32m: 2+ pessoas; IA: 10 a 15 por filme). Filmes com mais de uma fonte têm uma linha por fonte.")
    exemplo = uni[(uni.imdb_id == "tt0816692") & (uni.tag.isin(["space", "emotional", "time travel"]))]
    out("   Exemplo (Interestelar):")
    for r in exemplo.itertuples():
        out(f"      {r.fonte:<9} {r.tag:<12} nota original {r.nota_original:<7} -> posição {r.score}")

    # ------------------------------------------------------------------ 3) relatório de cobertura
    out("\n" + "=" * 76)
    out("3) COBERTURA DAS FONTES")
    out("=" * 76)
    # "fonte boa" igual à análise anterior: ml-32m com 5+ etiquetas (quaisquer) de 2+ pessoas
    par = tags.groupby(["movieId", "tag_n"]).userId.nunique()
    ml_boa = par[par >= MIN_PESSOAS].groupby("movieId").size() >= ML_BOA_ETIQ
    f["TG"] = f.tem_etiqueta
    f["ML"] = f.movieId.map(ml_boa).fillna(False).astype(bool)
    f["IA"] = f.imdb_id.isin(set(filmes_ia))
    f["combo"] = f.apply(lambda r: "+".join(x for x in ("TG", "ML", "IA") if r[x]) or "nenhuma", axis=1)
    n = len(f)
    out("Combinações de fontes (TG = Tag Genome; ML = ml-32m com 5+ etiquetas de 2+ pessoas; IA = Claude):")
    for combo, c in f.combo.value_counts().items():
        out(f"   {combo:<10} {c:>5}  ({pct(c, n)})")
    sem = f[f.combo == "nenhuma"]
    out(f"Com alguma fonte: {n - len(sem)} ({pct(n - len(sem), n)}). Sem nenhuma: {len(sem)}.")
    out("\nCobertura por década (% com pelo menos uma fonte | sem fonte):")
    dec = f.ano_num // 10 * 10
    for d in range(1920, 2030, 10):
        g = f[dec == d]
        if len(g):
            s = (g.combo == "nenhuma").sum()
            out(f"   {str(d) + 's':<7} {len(g):>5} filmes  {pct(len(g) - s, len(g)):>5} com fonte | {s:>4} sem")
    out("Sem fonte por ano (2010+): " + ", ".join(
        f"{int(a)}: {c}" for a, c in sem[sem.ano_num >= 2010].ano_num.value_counts().sort_index().items()))
    sem.sort_values("votos", ascending=False)[["id", "imdb_id", "titulo", "titulo_original", "ano", "votos"]] \
        .to_csv("filmes_sem_fonte_atual.csv", index=False, encoding="utf-8")
    out(f"Lista atualizada dos que ainda faltam: filmes_sem_fonte_atual.csv ({len(sem)} filmes).")

    if os.path.exists("etiquetas_ia.csv"):
        novos = pd.read_csv("etiquetas_ia.csv", dtype={"imdb_id": str})
        tit = f.set_index("imdb_id")
        ids = novos.imdb_id.drop_duplicates()
        amostra = ids.sample(n=min(15, len(ids)), random_state=11)
        out(f"\nAmostra de {len(amostra)} filmes novos etiquetados pela IA (sorteados entre os {len(ids)} desta rodada):")
        for i in amostra:
            g = novos[novos.imdb_id == i].sort_values("score", ascending=False)
            out(f"   {tit.at[i, 'titulo']} ({tit.at[i, 'ano']}): " + ", ".join(f"{r.tag} {r.score}" for r in g.itertuples()))

    with open("relatorio_etiquetas.txt", "w", encoding="utf-8") as arq:
        arq.write("\n".join(linhas) + "\n")
    print("\nSalvo em relatorio_etiquetas.txt")


if __name__ == "__main__":
    main()
