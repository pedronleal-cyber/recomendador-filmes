"""
Cruza os filmes do filmes_v2.csv com o MovieLens Tag Genome 2021 pelo imdb_id.

Entrada (dentro de dados_externos/tag_genome/):
    raw/metadata.json   -> liga o id do MovieLens (item_id) ao id do IMDB (imdbId)
    raw/tags.json       -> lista de etiquetas (só para conferência)
    scores/glmer.csv    -> nota de relevância (0 a 1) de cada etiqueta para cada filme
                           (método original de Vig et al. 2012; o TagDL foi descartado porque
                           infla algumas etiquetas genéricas, ex.: "catastrophe" em quase todo filme)

Saída:
    etiquetas.csv        -> imdb_id, tag, score (as 30 etiquetas mais relevantes de cada filme)
    etiquetas_lista.txt  -> as etiquetas, com quantos filmes têm cada uma com score acima de 0,7
    e um resumo de cobertura na tela.

Uso:
    python -I cruzar_tag_genome.py

Licença do Tag Genome: CC BY-NC 3.0 (uso não comercial). Citar Vig et al. (2012) e Kotkov et al. (2021).
"""
import glob
import json
import os
import sys

import pandas as pd

PASTA = os.path.join("dados_externos", "tag_genome")
ARQ_SCORES = "glmer.csv"
ARQ_FILMES = "filmes_v2.csv"
TOP_POR_FILME = 30
SCORE_ALTO = 0.7
ANO_RECENTE = 2022


def achar(nome):
    """Acha o arquivo dentro da pasta do Tag Genome, seja qual for a pasta-raiz do zip."""
    achados = glob.glob(os.path.join(PASTA, "**", nome), recursive=True)
    if not achados:
        sys.exit(f"Não achei {nome} dentro de {PASTA}")
    return achados[0]


def numero_imdb(texto):
    """'tt0114709' ou '0114709' -> 114709 (para comparar os dois formatos)."""
    digitos = "".join(c for c in str(texto) if c.isdigit())
    return int(digitos) if digitos else None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    filmes = pd.read_csv(ARQ_FILMES, dtype={"imdb_id": str})
    filmes["imdb_num"] = filmes.imdb_id.map(numero_imdb)
    filmes["ano_num"] = pd.to_numeric(filmes.ano, errors="coerce")

    # 1) id do MovieLens <-> id do IMDB
    with open(achar(os.path.join("raw", "metadata.json")), encoding="utf-8") as f:
        meta = pd.DataFrame([json.loads(linha) for linha in f if linha.strip()])
    meta["imdb_num"] = meta.imdbId.map(numero_imdb)
    meta = meta.dropna(subset=["imdb_num"]).drop_duplicates("imdb_num")
    ponte = dict(zip(meta.imdb_num.astype(int), meta.item_id))

    filmes["item_id"] = filmes.imdb_num.map(lambda n: ponte.get(n) if n else None)

    # 2) Notas de relevância (GLMER). Lê o arquivo grande em pedaços e guarda só os nossos filmes.
    nossos = set(filmes.item_id.dropna().astype(int))
    pedacos, etiquetas_vistas = [], set()
    for p in pd.read_csv(achar(os.path.join("scores", ARQ_SCORES)), chunksize=2_000_000,
                         dtype={"tag": str, "item_id": "int32", "score": "float32"}):
        etiquetas_vistas.update(p.tag.unique())
        pedacos.append(p[p.item_id.isin(nossos)])
    scores = pd.concat(pedacos, ignore_index=True)
    todas_etiquetas = sorted(etiquetas_vistas)

    com_etiquetas = set(scores.item_id.unique())
    filmes["tem_etiquetas"] = filmes.item_id.map(lambda i: pd.notna(i) and int(i) in com_etiquetas)

    # 3) etiquetas.csv: as 30 mais relevantes de cada filme
    item_para_imdb = (filmes.dropna(subset=["item_id"])
                      .assign(item_id=lambda d: d.item_id.astype(int))
                      .drop_duplicates("item_id").set_index("item_id").imdb_id)
    top = (scores.sort_values(["item_id", "score"], ascending=[True, False])
           .groupby("item_id").head(TOP_POR_FILME).copy())
    top["imdb_id"] = top.item_id.map(item_para_imdb)
    top["score"] = top.score.round(4)
    top[["imdb_id", "tag", "score"]].to_csv("etiquetas.csv", index=False, encoding="utf-8")

    # 4) etiquetas_lista.txt: cada etiqueta e quantos dos nossos filmes a têm com score alto
    altos = scores[scores.score > SCORE_ALTO].groupby("tag").size()
    contagem = pd.Series(0, index=todas_etiquetas).add(altos, fill_value=0).astype(int)
    contagem = contagem.sort_index().sort_values(ascending=False, kind="stable")
    with open("etiquetas_lista.txt", "w", encoding="utf-8") as f:
        f.write(f"Etiquetas do MovieLens Tag Genome 2021 ({len(contagem)} etiquetas).\n")
        f.write(f"Número = quantos filmes do {ARQ_FILMES} têm a etiqueta com score acima de {SCORE_ALTO}.\n")
        f.write("Fonte: MovieLens Tag Genome (CC BY-NC 3.0). Vig et al. (2012); Kotkov et al. (2021).\n\n")
        for tag, n in contagem.items():
            f.write(f"{n:>5}  {tag}\n")

    # 5) Resumo de cobertura
    total = len(filmes)

    def pct(n, de=total):
        return f"{n} ({100 * n / de:.0f}%)" if de else "0"

    recentes = filmes[filmes.ano_num >= ANO_RECENTE]
    antigos = filmes[filmes.ano_num < ANO_RECENTE]
    print("\n===== COBERTURA DO TAG GENOME =====")
    print("Filmes no filmes_v2.csv:", total)
    print("Com imdb_id:", pct(filmes.imdb_num.notna().sum()))
    print("Achados no MovieLens (metadata):", pct(filmes.item_id.notna().sum()))
    print("Com etiquetas do Tag Genome (casaram):", pct(filmes.tem_etiquetas.sum()))
    print("Sem etiquetas:", pct((~filmes.tem_etiquetas).sum()))
    print(f"  - sem imdb_id: {filmes.imdb_num.isna().sum()}")
    print(f"  - imdb_id não está no MovieLens: {(filmes.imdb_num.notna() & filmes.item_id.isna()).sum()}")
    print(f"  - está no MovieLens, mas fora do Tag Genome: {(filmes.item_id.notna() & ~filmes.tem_etiquetas).sum()}")
    print(f"\nFilmes até {ANO_RECENTE - 1}: {len(antigos)}, com etiquetas: {pct(antigos.tem_etiquetas.sum(), len(antigos))}")
    print(f"Filmes de {ANO_RECENTE} em diante: {len(recentes)}, com etiquetas: "
          f"{pct(recentes.tem_etiquetas.sum(), len(recentes))}")
    print("\nCom etiquetas, por década:")
    dec = (filmes.ano_num // 10 * 10)
    for d, g in filmes.groupby(dec):
        print(f"  {int(d)}s: {pct(g.tem_etiquetas.sum(), len(g))} de {len(g)}")
    print(f"\nAno mais recente com etiquetas: {int(filmes[filmes.tem_etiquetas].ano_num.max())}")
    print(f"Etiquetas no Tag Genome: {len(todas_etiquetas)}")
    print(f"etiquetas.csv: {len(top)} linhas ({top.imdb_id.nunique()} filmes x até {TOP_POR_FILME} etiquetas)")
    print(f"Etiquetas que nenhum dos nossos filmes tem acima de {SCORE_ALTO}: {(contagem == 0).sum()}")
    print("\nFonte: MovieLens Tag Genome 2021 (CC BY-NC 3.0). Vig et al. (2012); Kotkov et al. (2021).")


if __name__ == "__main__":
    main()
