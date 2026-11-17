"""
Diagnósticos antes do motor novo (não cria motor nem preenche etiquetas).

1. Cobertura do Tag Genome por década no filmes_v2.csv.
2. Cobertura do gabarito: % dos filmes de boas_respostas que têm etiquetas, por arquivo de pedidos.
3. Teste de "emprestar etiquetas": estimar as etiquetas de um filme pela média dos 20 filmes
   etiquetados mais parecidos (palavras-chave + gêneros + década, similaridade de cosseno).
   Validação com 300 filmes que têm etiqueta, fingindo que não têm.

Uso:
    python -I diagnostico_tags.py
Saída: diagnostico_tags.txt (e o mesmo texto na tela).
"""
import glob
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ARQ_FILMES_V2 = "filmes_v2.csv"
ARQ_FILMES_V1 = "filmes.csv"
ARQ_ETIQUETAS = "etiquetas.csv"
PASTA_TG = os.path.join("dados_externos", "tag_genome")
ARQS_PEDIDOS = ["pedidos_teste.csv", "pedidos_validacao.csv", "pedidos_final.csv", "pedidos_final2.csv"]
VIZINHOS = 20
QTD_VALIDACAO = 300
SEMENTE = 42
TAGS_CLIMA = ["feel-good", "dark", "reflective", "funny", "sad",
              "depressing", "tense", "thought-provoking", "heartwarming", "atmospheric"]

linhas_saida = []


def out(texto=""):
    print(texto)
    linhas_saida.append(texto)


def pct(n, de):
    return f"{100 * n / de:.0f}%" if de else "-"


def numero_imdb(texto):
    digitos = "".join(c for c in str(texto) if c.isdigit())
    return int(digitos) if digitos else None


# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------

def carregar():
    f = pd.read_csv(ARQ_FILMES_V2, dtype={"imdb_id": str})
    f["ano_num"] = pd.to_numeric(f.ano, errors="coerce")
    etiq = pd.read_csv(ARQ_ETIQUETAS, dtype={"imdb_id": str})
    com_etiqueta = set(etiq.imdb_id)
    f["tem_etiqueta"] = f.imdb_id.isin(com_etiqueta)
    return f


def matriz_etiquetas(f):
    """Notas completas (1.084 etiquetas) do GLMER para os filmes etiquetados, uma linha por filme."""
    meta_arq = glob.glob(os.path.join(PASTA_TG, "**", "raw", "metadata.json"), recursive=True)[0]
    meta = pd.read_json(meta_arq, lines=True)
    meta["imdb_num"] = meta.imdbId.map(numero_imdb)
    ponte = dict(zip(meta.imdb_num, meta.item_id))
    g = f[f.tem_etiqueta].copy()
    g["item_id"] = g.imdb_id.map(lambda x: ponte.get(numero_imdb(x)))
    g = g.dropna(subset=["item_id"]).drop_duplicates("item_id")
    item_para_linha = dict(zip(g.item_id.astype(int), g.index))  # id do MovieLens -> linha do filmes_v2
    arq = glob.glob(os.path.join(PASTA_TG, "**", "scores", "glmer.csv"), recursive=True)[0]
    pedacos = [p[p.item_id.isin(item_para_linha)] for p in
               pd.read_csv(arq, chunksize=2_000_000, dtype={"tag": str, "item_id": "int32", "score": "float32"})]
    s = pd.concat(pedacos).pivot_table(index="item_id", columns="tag", values="score")
    s.index = [item_para_linha[i] for i in s.index]
    # Uma única célula vem vazia no arquivo (1 filme x 1 etiqueta): preenche com a média da etiqueta.
    s = s.fillna(s.mean())
    return s.sort_index()


# ---------------------------------------------------------------------------
# 1) Cobertura por década
# ---------------------------------------------------------------------------

def cobertura_decada(f):
    out("=" * 70)
    out("1) COBERTURA DO TAG GENOME POR DÉCADA (filmes_v2.csv)")
    out("=" * 70)
    out(f"{'Década':<10}{'Filmes':>8}{'Com etiqueta':>14}{'%':>6}")
    dec = (f.ano_num // 10 * 10)
    for d in range(1920, 2030, 10):
        g = f[dec == d]
        out(f"{str(d) + 's':<10}{len(g):>8}{g.tem_etiqueta.sum():>14}{pct(g.tem_etiqueta.sum(), len(g)):>6}")
    fora = f[(dec < 1920) | dec.isna()]
    if len(fora):
        out(f"(fora da tabela: {len(fora)} filme(s) antes de 1920 ou sem ano, {fora.tem_etiqueta.sum()} com etiqueta)")
    out(f"{'TOTAL':<10}{len(f):>8}{f.tem_etiqueta.sum():>14}{pct(f.tem_etiqueta.sum(), len(f)):>6}")
    por_ano = f[f.ano_num.between(2010, 2021)].groupby("ano_num").tem_etiqueta.agg(["size", "sum"])
    out("\nDetalhe 2010 a 2021 (ano: com etiqueta / filmes):")
    out("  " + "  ".join(f"{int(a)}: {r['sum']}/{r['size']}" for a, r in por_ano.iterrows()))
    out()


# ---------------------------------------------------------------------------
# 2) Cobertura do gabarito
# ---------------------------------------------------------------------------

def cobertura_gabarito(f):
    out("=" * 70)
    out("2) COBERTURA DO GABARITO (filmes de boas_respostas com etiqueta)")
    out("=" * 70)
    v1 = pd.read_csv(ARQ_FILMES_V1)
    # título -> ids do TMDB (o gabarito foi escrito com os títulos do filmes.csv)
    ids_por_titulo = {}
    for tab in (v1, f):
        for t, i in zip(tab.titulo, tab.id):
            ids_por_titulo.setdefault(t.strip(), set()).add(int(i))
    etiqueta_por_id = dict(zip(f.id.astype(int), f.tem_etiqueta))

    def situacao(titulo):
        ids = ids_por_titulo.get(titulo, set())
        no_v2 = [i for i in ids if i in etiqueta_por_id]
        if not no_v2:
            return "fora"
        return "com" if any(etiqueta_por_id[i] for i in no_v2) else "sem"

    out("Contagem por citação (um filme citado em 2 pedidos conta 2 vezes).")
    out("'fora' = o título não está no filmes_v2.csv.\n")
    out(f"{'Arquivo':<24}{'Citações':>9}{'Com etiq.':>11}{'Sem etiq.':>11}{'Fora v2':>9}{'% com':>8}"
        f"{'Únicos':>8}{'% únicos':>10}")
    poucos = []
    for arq in ARQS_PEDIDOS:
        if not os.path.exists(arq):
            out(f"{arq:<24} (não encontrado)")
            continue
        p = pd.read_csv(arq, encoding="utf-8", dtype=str, keep_default_na=False)
        cont = {"com": 0, "sem": 0, "fora": 0}
        unicos = {}
        for r in p.itertuples():
            titulos = [t.strip() for t in r.boas_respostas.split("|") if t.strip()]
            sit = [situacao(t) for t in titulos]
            for t, s in zip(titulos, sit):
                cont[s] += 1
                unicos[t] = s
            n_com = sit.count("com")
            if titulos and n_com < len(titulos) / 2:
                sem = [t for t, s in zip(titulos, sit) if s != "com"]
                poucos.append((arq, r.numero, r.estilo, r.pedido, n_com, len(titulos), sem))
        total = sum(cont.values())
        u_com = sum(1 for s in unicos.values() if s == "com")
        out(f"{arq:<24}{total:>9}{cont['com']:>11}{cont['sem']:>11}{cont['fora']:>9}{pct(cont['com'], total):>8}"
            f"{len(unicos):>8}{pct(u_com, len(unicos)):>10}")

    out(f"\nPedidos em que MENOS da metade das boas respostas tem etiqueta: {len(poucos)}")
    for arq, n, estilo, pedido, n_com, n_tot, sem in poucos:
        out(f"  #{n} [{estilo}] ({arq}) {n_com}/{n_tot} com etiqueta — {pedido}")
        out(f"       sem etiqueta: {' | '.join(sem)}")
    out()


# ---------------------------------------------------------------------------
# 3) Teste de "emprestar etiquetas"
# ---------------------------------------------------------------------------

def caracteristicas(f):
    """Cada filme vira um saco de 'fichas': palavras-chave, gêneros e década."""
    def fichas(r):
        kw = [f"kw:{k.strip().lower()}" for k in str(r.palavras_chave).split("|") if k.strip() and k != "nan"]
        gen = [f"g:{g.strip()}" for g in str(r.generos).split("|") if g.strip() and g != "nan"]
        dec = [f"d:{int(r.ano_num // 10 * 10)}"] if pd.notna(r.ano_num) else []
        return kw + gen + dec
    docs = [fichas(r) for r in f.itertuples()]
    vet = TfidfVectorizer(analyzer=lambda x: x, sublinear_tf=True)
    return vet.fit_transform(docs), np.array([len(d) for d in docs])


def estimar(X, linhas_alvo, linhas_base, T_base):
    """Média das etiquetas dos VIZINHOS filmes mais parecidos (dentro de linhas_base)."""
    sim = cosine_similarity(X[linhas_alvo], X[linhas_base])
    viz = np.argsort(-sim, axis=1)[:, :VIZINHOS]
    est = T_base[viz].mean(axis=1)
    sim_media = np.take_along_axis(sim, viz, axis=1).mean(axis=1)
    return est, sim_media


def correl_linhas(A, B):
    A = A - A.mean(axis=1, keepdims=True)
    B = B - B.mean(axis=1, keepdims=True)
    return (A * B).sum(axis=1) / np.sqrt((A ** 2).sum(axis=1) * (B ** 2).sum(axis=1))


def teste_emprestar(f, T):
    out("=" * 70)
    out('3) TESTE DE "EMPRESTAR ETIQUETAS"')
    out("=" * 70)
    X, n_fichas = caracteristicas(f)
    etiquetados = T.index.to_numpy()
    rng = np.random.default_rng(SEMENTE)
    val = np.sort(rng.choice(etiquetados, size=QTD_VALIDACAO, replace=False))
    base = np.setdiff1d(etiquetados, val)
    T_base = T.loc[base].to_numpy()
    real = T.loc[val].to_numpy()
    est, sim_val = estimar(X, val, base, T_base)
    media_global = T_base.mean(axis=0)
    chute = np.tile(media_global, (len(val), 1))

    out(f"Filmes etiquetados: {len(etiquetados)}. Validação: {len(val)} sorteados (semente {SEMENTE}); "
        f"vizinhos procurados só entre os outros {len(base)}.")
    out(f"Estimativa = média das etiquetas dos {VIZINHOS} vizinhos mais parecidos "
        f"(palavras-chave + gêneros + década, TF-IDF + cosseno).\n")

    c_est = correl_linhas(est, real)
    c_chute = correl_linhas(chute, real)
    c_est_c = correl_linhas(est - media_global, real - media_global)
    out("a) Correlação média por filme (estimativa x etiquetas reais, nas 1.084 etiquetas):")
    out(f"   Estimativa pelos vizinhos:                    {c_est.mean():.3f}  (mediana {np.median(c_est):.3f})")
    out(f"   Chute bobo (todo filme = média geral):        {c_chute.mean():.3f}")
    out(f"   Só o que é próprio do filme (tirando a média): {c_est_c.mean():.3f}  (chute bobo aqui = 0)")
    out("   -> A correlação 'crua' é alta até para o chute bobo, porque algumas etiquetas são altas em quase")
    out("      todo filme. A linha 'só o que é próprio do filme' é a que mostra se a estimativa sabe algo.")
    faixas = [(-1, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 1.01)]
    out("   Distribuição (só o que é próprio do filme): " +
        ", ".join(f"{a:.1f} a {min(b, 1):.1f}: {pct(((c_est_c >= a) & (c_est_c < b)).sum(), len(val))}"
                  for a, b in faixas))

    out(f"\nb) Etiquetas de clima: quantos dos 5 filmes com a nota REAL mais alta (entre os {len(val)})")
    out("   aparecem também no top 5 da ESTIMATIVA. Ao acaso, o esperado seria "
        f"{5 * 5 / len(val):.2f} de 5.")
    out(f"   {'Etiqueta':<20}{'Top 5 certo':>12}{'Top 20 certo':>14}{'Spearman':>10}   Top 5 real -> top 5 estimado")
    tags = list(T.columns)
    acertos5, acertos20 = [], []
    for tag in TAGS_CLIMA:
        j = tags.index(tag)
        top_real = np.argsort(-real[:, j])[:5]
        top_est = np.argsort(-est[:, j])[:5]
        a5 = len(set(top_real) & set(top_est))
        a20 = len(set(np.argsort(-real[:, j])[:20]) & set(np.argsort(-est[:, j])[:20]))
        rho = spearmanr(real[:, j], est[:, j]).correlation
        acertos5.append(a5)
        acertos20.append(a20)
        nomes = lambda idx: ", ".join(f.loc[val[i], "titulo"][:22] for i in idx[:3])
        out(f"   {tag:<20}{a5:>9}/5{a20:>11}/20{rho:>10.2f}   {nomes(top_real)} -> {nomes(top_est)}")
    out(f"   Média: {np.mean(acertos5):.1f}/5 no top 5 e {np.mean(acertos20):.1f}/20 no top 20 "
        f"(ao acaso: {5 * 5 / len(val):.2f}/5 e {20 * 20 / len(val):.1f}/20).")

    # Os filmes sem etiqueta acham vizinhos tão parecidos quanto os da validação?
    sem = f.index[~f.tem_etiqueta].to_numpy()
    _, sim_sem = estimar(X, sem, etiquetados, T.to_numpy())
    out("\nc) Os filmes SEM etiqueta acham vizinhos tão parecidos quanto os da validação?")
    out(f"   Similaridade média com os {VIZINHOS} vizinhos — validação: {sim_val.mean():.3f}; "
        f"filmes sem etiqueta: {sim_sem.mean():.3f}")
    rec = f.loc[sem, "ano_num"] >= 2015
    out(f"   Sem etiqueta de 2015+: {sim_sem[rec.to_numpy()].mean():.3f} ({rec.sum()} filmes); "
        f"sem etiqueta antes de 2015: {sim_sem[~rec.to_numpy()].mean():.3f} ({(~rec).sum()} filmes)")
    # Correlação da validação por faixa de similaridade, para saber o que esperar dos sem etiqueta
    out("   Qualidade na validação conforme a similaridade dos vizinhos (só o que é próprio do filme):")
    for a, b in [(0, 0.15), (0.15, 0.25), (0.25, 1)]:
        m = (sim_val >= a) & (sim_val < b)
        out(f"     similaridade {a:.2f} a {min(b, 1):.2f}: {m.sum():>3} filmes, correlação {c_est_c[m].mean() if m.any() else float('nan'):.3f}")
    out(f"   Filmes sem etiqueta com similaridade abaixo de 0,15: {pct((sim_sem < 0.15).sum(), len(sem))}")
    out(f"   Década nos sem etiqueta de 2020+: nenhum filme etiquetado é dos anos 2020, então a ficha "
        f"'d:2020' não ajuda a achar vizinhos.")
    out()
    return c_est_c.mean(), np.mean(acertos5), sim_val.mean(), sim_sem.mean()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    f = carregar()
    cobertura_decada(f)
    cobertura_gabarito(f)
    T = matriz_etiquetas(f)
    teste_emprestar(f, T)
    out("Fonte das etiquetas: MovieLens Tag Genome 2021 (GLMER), CC BY-NC 3.0. Vig et al. (2012); Kotkov et al. (2021).")
    with open("diagnostico_tags.txt", "w", encoding="utf-8") as arq:
        arq.write("\n".join(linhas_saida) + "\n")
    print("\nSalvo em diagnostico_tags.txt")


if __name__ == "__main__":
    main()
