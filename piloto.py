"""
Piloto: etiquetas atribuídas pelo Claude (origem "ia"), feitas uma vez, offline.

Comandos:
    python -I piloto.py conferir            -> confere se o vocabulário existe no Tag Genome
    python -I piloto.py selecionar          -> sorteia os 150 filmes do teste às cegas e os 100 recentes
    python -I piloto.py mostrar cego 1      -> mostra o lote 1 (título, ano, gêneros, palavras-chave, sinopse)
    python -I piloto.py mostrar recentes 1
    python -I piloto.py juntar              -> junta os lotes em piloto_cego.csv e etiquetas_ia_piloto.csv
    python -I piloto.py avaliar             -> compara o teste às cegas com o Tag Genome (GLMER)

Os lotes ficam em piloto_lotes/ (um arquivo por lote, para poder retomar).
Formato de cada linha de um lote:
    tt0088763 | De Volta para o Futuro | time travel=0.9; funny=0.6; nostalgic=0.6; ...
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # para importar diagnostico_tags (mesma pasta)

import numpy as np
import pandas as pd

ARQ_FILMES = "filmes_v2.csv"
ARQ_ETIQUETAS_TG = "etiquetas.csv"
ARQ_VOCAB = "vocabulario_piloto.csv"
PASTA_LOTES = "piloto_lotes"
SEL_CEGO = os.path.join(PASTA_LOTES, "selecao_cego.csv")
SEL_RECENTES = os.path.join(PASTA_LOTES, "selecao_recentes.csv")
TAM_LOTE = {"cego": 30, "recentes": 25}
NOTAS_VALIDAS = {0.3, 0.6, 0.9}
MIN_TAGS, MAX_TAGS = 10, 15
SEMENTE = 7
ESTRATOS_CEGO = {(1980, 1989): 35, (1990, 1999): 40, (2000, 2009): 45, (2010, 2013): 30}  # total 150
QTD_RECENTES = 100
TAGS_CLIMA = ["feel-good", "bleak", "reflective", "funny", "sad",
              "tense", "thought-provoking", "heartwarming", "twist ending", "absurd"]


def vocabulario():
    return pd.read_csv(ARQ_VOCAB)


def filmes():
    f = pd.read_csv(ARQ_FILMES, dtype={"imdb_id": str})
    f["ano_num"] = pd.to_numeric(f.ano, errors="coerce")
    f["tem_etiqueta"] = f.imdb_id.isin(set(pd.read_csv(ARQ_ETIQUETAS_TG, dtype={"imdb_id": str}).imdb_id))
    return f


# ---------------------------------------------------------------------------

def conferir():
    v = vocabulario()
    linhas = open("etiquetas_lista.txt", encoding="utf-8").read().splitlines()[4:]
    existentes = {l[7:] for l in linhas if l.strip()}
    faltando = [t for t in v.tag if t not in existentes]
    print(f"Vocabulário: {len(v)} etiquetas  ->  " + ", ".join(f"{g}: {n}" for g, n in v.grupo.value_counts().items()))
    print("Duplicadas:", v.tag[v.tag.duplicated()].tolist() or "nenhuma")
    print("Não existem no Tag Genome:", faltando or "nenhuma")
    faltam_clima = [t for t in TAGS_CLIMA if t not in set(v.tag)]
    print("Etiquetas de clima do teste fora do vocabulário:", faltam_clima or "nenhuma")


def selecionar():
    os.makedirs(PASTA_LOTES, exist_ok=True)
    f = filmes()
    # Filmes cujas etiquetas já apareceram nesta conversa (os 300 da validação do diagnostico_tags.py
    # e Toy Story) ficam de fora, para o teste ser às cegas de verdade.
    etiquetados = np.sort(f.index[f.tem_etiqueta].to_numpy())
    vistos = set(np.random.default_rng(42).choice(etiquetados, size=300, replace=False))
    vistos |= set(f.index[f.imdb_id == "tt0114709"])
    rng = np.random.default_rng(SEMENTE)
    escolhidos = []
    for (a, b), n in ESTRATOS_CEGO.items():
        pool = f.index[f.tem_etiqueta & f.ano_num.between(a, b) & ~f.index.isin(list(vistos))].to_numpy()
        escolhidos += list(rng.choice(pool, size=n, replace=False))
    cego = f.loc[sorted(escolhidos)].sample(frac=1, random_state=SEMENTE)  # embaralha as épocas nos lotes
    cego[["imdb_id", "titulo", "ano"]].to_csv(SEL_CEGO, index=False, encoding="utf-8")

    rec = f[~f.tem_etiqueta & (f.ano_num >= 2014) & f.imdb_id.notna()].sort_values("votos", ascending=False)
    rec.head(QTD_RECENTES)[["imdb_id", "titulo", "ano", "votos"]].to_csv(SEL_RECENTES, index=False, encoding="utf-8")
    print(f"Teste às cegas: {len(cego)} filmes -> {SEL_CEGO}")
    print("  por década:", cego.ano_num.floordiv(10).mul(10).value_counts().sort_index().to_dict())
    print(f"Recentes: {min(QTD_RECENTES, len(rec))} filmes -> {SEL_RECENTES} "
          f"(votos de {rec.head(QTD_RECENTES).votos.min()} a {rec.head(QTD_RECENTES).votos.max()})")


def mostrar(qual, n_lote):
    sel = pd.read_csv(SEL_CEGO if qual == "cego" else SEL_RECENTES, dtype={"imdb_id": str})
    tam = TAM_LOTE[qual]
    lote = sel.iloc[(n_lote - 1) * tam: n_lote * tam]
    f = filmes().drop_duplicates("imdb_id").set_index("imdb_id")
    total = -(-len(sel) // tam)
    print(f"Lote {n_lote}/{total} ({qual}): {len(lote)} filmes. Salvar em {PASTA_LOTES}/{qual}_{n_lote:02d}.txt\n")
    for imdb in lote.imdb_id:
        r = f.loc[imdb]
        kw = "|".join(str(r.palavras_chave).split("|")[:20]) if pd.notna(r.palavras_chave) else ""
        print(f"{imdb} | {r.titulo} ({r.titulo_original}, {r.ano}) | {r.generos}")
        print(f"   kw: {kw}")
        print(f"   {str(r.sinopse)[:330]}\n")


def ler_lotes(qual, vocab):
    linhas, erros = [], []
    sel = pd.read_csv(SEL_CEGO if qual == "cego" else SEL_RECENTES, dtype={"imdb_id": str})
    esperados = set(sel.imdb_id)
    arqs = sorted(a for a in os.listdir(PASTA_LOTES) if a.startswith(qual + "_") and a.endswith(".txt"))
    for arq in arqs:
        for n, linha in enumerate(open(os.path.join(PASTA_LOTES, arq), encoding="utf-8"), start=1):
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = [p.strip() for p in linha.split("|")]
            imdb, tags = partes[0], partes[-1]
            if imdb not in esperados:
                erros.append(f"{arq}:{n} {imdb} não está na seleção")
            pares = [t.strip() for t in tags.split(";") if t.strip()]
            if not MIN_TAGS <= len(pares) <= MAX_TAGS:
                erros.append(f"{arq}:{n} {imdb} tem {len(pares)} etiquetas")
            vistos = set()
            for p in pares:
                tag, _, nota = p.rpartition("=")
                tag = tag.strip()
                try:
                    nota = round(float(nota), 1)
                except ValueError:
                    erros.append(f"{arq}:{n} {imdb} nota inválida em '{p}'")
                    continue
                if tag not in vocab:
                    erros.append(f"{arq}:{n} {imdb} etiqueta fora do vocabulário: '{tag}'")
                elif nota not in NOTAS_VALIDAS:
                    erros.append(f"{arq}:{n} {imdb} nota {nota} não é 0.3/0.6/0.9")
                elif tag in vistos:
                    erros.append(f"{arq}:{n} {imdb} etiqueta repetida: '{tag}'")
                else:
                    vistos.add(tag)
                    linhas.append({"imdb_id": imdb, "tag": tag, "score": nota})
    d = pd.DataFrame(linhas, columns=["imdb_id", "tag", "score"])
    return d, erros, esperados - set(d.imdb_id), len(arqs)


def juntar():
    vocab = set(vocabulario().tag)
    for qual, saida in (("cego", "piloto_cego.csv"), ("recentes", "etiquetas_ia_piloto.csv")):
        d, erros, faltam, n_arqs = ler_lotes(qual, vocab)
        if qual == "recentes":
            d["origem"] = "ia"
        d.to_csv(saida, index=False, encoding="utf-8")
        print(f"{saida}: {d.imdb_id.nunique()} filmes, {len(d)} linhas ({n_arqs} lotes). "
              f"Faltam {len(faltam)} filmes. Erros: {len(erros)}")
        for e in erros[:30]:
            print("   ", e)


# ---------------------------------------------------------------------------

def correl_linhas(A, B):
    A = A - A.mean(axis=1, keepdims=True)
    B = B - B.mean(axis=1, keepdims=True)
    den = np.sqrt((A ** 2).sum(axis=1) * (B ** 2).sum(axis=1))
    return np.where(den > 0, (A * B).sum(axis=1) / np.where(den > 0, den, 1), np.nan)


def top_k_esperado(minhas, reais, k_meu=5, k_real=10, sorteios=2000, rng=None):
    """Quantos dos meus top 5 estão no top 10 real. Empates nas minhas notas são desfeitos ao acaso
    (média de muitos sorteios), para não favorecer nenhum filme."""
    rng = rng or np.random.default_rng(0)
    top_real = set(np.argsort(-reais, kind="stable")[:k_real])
    total = 0
    for _ in range(sorteios):
        ordem = np.lexsort((rng.random(len(minhas)), -minhas))
        total += len(top_real & set(ordem[:k_meu]))
    return total / sorteios


def avaliar():
    import diagnostico_tags as dg

    vocab = list(vocabulario().tag)
    meu, erros, faltam, _ = ler_lotes("cego", set(vocab))
    if faltam or erros:
        sys.exit(f"Teste às cegas incompleto: faltam {len(faltam)} filmes, {len(erros)} erros. Rode 'juntar'.")
    f = dg.carregar()
    T = dg.matriz_etiquetas(f)[vocab]  # notas reais (GLMER), só no vocabulário
    imdb_por_linha = f.imdb_id
    linha_por_imdb = {v: k for k, v in imdb_por_linha.items()}
    filmes_teste = list(dict.fromkeys(meu.imdb_id))
    linhas = [linha_por_imdb[i] for i in filmes_teste]
    real = T.loc[linhas].to_numpy()
    M = (meu.pivot_table(index="imdb_id", columns="tag", values="score")
         .reindex(index=filmes_teste, columns=vocab).fillna(0).to_numpy())

    resto = T.index.difference(linhas)
    media = T.loc[resto].to_numpy().mean(axis=0)
    # Estimativa pelos vizinhos (método do diagnóstico), para comparar
    X, _ = dg.caracteristicas(f)
    viz, _ = dg.estimar(X, np.array(linhas), resto.to_numpy(), T.loc[resto].to_numpy())

    out = []
    p = lambda s="": (print(s), out.append(s))
    p("=" * 70)
    p(f"TESTE ÀS CEGAS: etiquetas do Claude x Tag Genome (GLMER), {len(linhas)} filmes, "
      f"{len(vocab)} etiquetas do vocabulário")
    p("=" * 70)
    p(f"Etiquetas por filme (Claude): média {(M > 0).sum(axis=1).mean():.1f}")
    c_meu = correl_linhas(M, real)
    c_viz = correl_linhas(viz, real)
    c_chute = correl_linhas(np.tile(media, (len(linhas), 1)), real)
    c_meu_p = correl_linhas(M, real - media)
    c_viz_p = correl_linhas(viz - media, real - media)
    p("\na) Correlação por filme (só nas etiquetas do vocabulário):")
    p(f"   {'':<44}{'crua':>8}{'própria do filme':>18}")
    p(f"   {'Claude':<44}{np.nanmean(c_meu):>8.3f}{np.nanmean(c_meu_p):>18.3f}")
    p(f"   {'Emprestar dos 20 vizinhos (diagnóstico)':<44}{np.nanmean(c_viz):>8.3f}{np.nanmean(c_viz_p):>18.3f}")
    p(f"   {'Chute bobo (média geral para todo filme)':<44}{np.nanmean(c_chute):>8.3f}{0:>18.3f}")
    p("   'própria do filme' = correlação com o que o filme tem de diferente da média (a que importa).")
    faixas = [(-1, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 1.01)]
    p("   Distribuição Claude (própria do filme): " +
      ", ".join(f"{a:.1f} a {min(b, 1):.1f}: {((c_meu_p >= a) & (c_meu_p < b)).mean():.0%}" for a, b in faixas))

    p(f"\nb) Etiquetas de clima: quantos dos 5 filmes com maior nota (entre os {len(linhas)}) estão")
    p(f"   entre os 10 maiores do Tag Genome. Ao acaso: {5 * 10 / len(linhas):.2f} de 5.")
    p(f"   {'Etiqueta':<20}{'Claude':>8}{'Vizinhos':>10}{'Filmes c/ etiqueta (Claude)':>30}")
    rng = np.random.default_rng(0)
    res_meu, res_viz = [], []
    for tag in TAGS_CLIMA:
        j = vocab.index(tag)
        a = top_k_esperado(M[:, j], real[:, j], rng=rng)
        b = len(set(np.argsort(-viz[:, j])[:5]) & set(np.argsort(-real[:, j])[:10]))
        res_meu.append(a)
        res_viz.append(b)
        p(f"   {tag:<20}{a:>6.1f}/5{b:>8}/5{int((M[:, j] > 0).sum()):>30}")
    p(f"   {'Média':<20}{np.mean(res_meu):>6.1f}/5{np.mean(res_viz):>8.1f}/5")

    # Precisão das etiquetas dadas: quando o Claude deu 0.9, qual a nota real média?
    p("\nc) Calibração: nota real média (GLMER) conforme a nota do Claude:")
    for nota in (0.0, 0.3, 0.6, 0.9):
        m = M == nota
        p(f"   Claude {nota:.1f}: nota real média {real[m].mean():.2f}  ({m.sum()} pares)")
    with open("piloto_resultado.txt", "w", encoding="utf-8") as arq:
        arq.write("\n".join(out) + "\n")
    print("\nSalvo em piloto_resultado.txt")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "conferir":
        conferir()
    elif cmd == "selecionar":
        selecionar()
    elif cmd == "mostrar":
        mostrar(sys.argv[2], int(sys.argv[3]))
    elif cmd == "juntar":
        juntar()
    elif cmd == "avaliar":
        avaliar()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
