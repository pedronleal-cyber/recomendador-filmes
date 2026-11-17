"""
Etiquetagem pela IA (Claude), feita offline, dos filmes sem nenhuma fonte de etiquetas.
Mesmo vocabulário e escala do piloto (vocabulario_piloto.csv; notas 0.3/0.6/0.9; 10 a 15 por filme).

Comandos:
    python -I etiquetar_ia.py selecionar      -> escolhe os filmes da rodada (mais votados primeiro)
    python -I etiquetar_ia.py mostrar 1       -> mostra o lote 1 (título, ano, gêneros, palavras-chave, sinopse)
    python -I etiquetar_ia.py juntar          -> confere os lotes e salva etiquetas_ia.csv (origem "ia")

Os lotes ficam em ia_lotes/lote_NN.txt (um por lote; dá para parar e retomar).
Formato de cada linha:  tt1234567 | Título | tag=0.9; tag=0.6; ...
"""
import os
import sys

import pandas as pd

ARQ_FILMES = "filmes_v2.csv"
ARQ_ORIGEM = "filmes_sem_fonte.csv"
ARQ_VOCAB = "vocabulario_piloto.csv"
PASTA = "ia_lotes"
SELECAO = os.path.join(PASTA, "selecao.csv")
SAIDA = "etiquetas_ia.csv"
QTD_RODADA = 400
TAM_LOTE = 30
NOTAS_VALIDAS = {0.3, 0.6, 0.9}
MIN_TAGS, MAX_TAGS = 10, 15


def selecionar():
    os.makedirs(PASTA, exist_ok=True)
    src = pd.read_csv(ARQ_ORIGEM, dtype={"imdb_id": str}).dropna(subset=["imdb_id"])
    ja = set(pd.read_csv("etiquetas_ia_piloto.csv", dtype={"imdb_id": str}).imdb_id)
    src = src[~src.imdb_id.isin(ja)].sort_values("votos", ascending=False).head(QTD_RODADA)
    src[["imdb_id", "titulo", "ano", "votos"]].to_csv(SELECAO, index=False, encoding="utf-8")
    print(f"{len(src)} filmes selecionados -> {SELECAO} ({-(-len(src) // TAM_LOTE)} lotes de até {TAM_LOTE}); "
          f"votos de {src.votos.min()} a {src.votos.max()}")


def mostrar(n):
    sel = pd.read_csv(SELECAO, dtype={"imdb_id": str})
    lote = sel.iloc[(n - 1) * TAM_LOTE: n * TAM_LOTE]
    f = pd.read_csv(ARQ_FILMES, dtype={"imdb_id": str}).drop_duplicates("imdb_id").set_index("imdb_id")
    print(f"Lote {n}/{-(-len(sel) // TAM_LOTE)}: {len(lote)} filmes. Salvar em {PASTA}/lote_{n:02d}.txt\n")
    for imdb in lote.imdb_id:
        r = f.loc[imdb]
        kw = "|".join(str(r.palavras_chave).split("|")[:14]) if pd.notna(r.palavras_chave) else ""
        print(f"{imdb} | {r.titulo} ({r.titulo_original}, {r.ano}) | {r.generos}")
        print(f"   kw: {kw}")
        print(f"   {str(r.sinopse)[:240]}\n")


def juntar():
    vocab = set(pd.read_csv(ARQ_VOCAB).tag)
    sel = pd.read_csv(SELECAO, dtype={"imdb_id": str})
    esperados = set(sel.imdb_id)
    linhas, erros, vistos_filmes = [], [], set()
    arqs = sorted(a for a in os.listdir(PASTA) if a.startswith("lote_") and a.endswith(".txt"))
    for arq in arqs:
        for n, linha in enumerate(open(os.path.join(PASTA, arq), encoding="utf-8"), start=1):
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = [p.strip() for p in linha.split("|")]
            imdb, tags = partes[0], partes[-1]
            if imdb not in esperados:
                erros.append(f"{arq}:{n} {imdb} não está na seleção")
                continue
            if imdb in vistos_filmes:
                erros.append(f"{arq}:{n} {imdb} repetido")
                continue
            pares = [t.strip() for t in tags.split(";") if t.strip()]
            validos = []
            for p in pares:
                tag, _, nota = p.rpartition("=")
                tag = tag.strip()
                try:
                    nota = round(float(nota), 1)
                except ValueError:
                    erros.append(f"{arq}:{n} {imdb} nota inválida '{p}'")
                    continue
                if tag not in vocab:
                    erros.append(f"{arq}:{n} {imdb} fora do vocabulário: '{tag}'")
                elif nota not in NOTAS_VALIDAS:
                    erros.append(f"{arq}:{n} {imdb} nota {nota} em '{tag}'")
                elif tag in {v[0] for v in validos}:
                    erros.append(f"{arq}:{n} {imdb} etiqueta repetida '{tag}'")
                else:
                    validos.append((tag, nota))
            if not MIN_TAGS <= len(validos) <= MAX_TAGS:
                erros.append(f"{arq}:{n} {imdb} ficou com {len(validos)} etiquetas válidas")
            vistos_filmes.add(imdb)
            linhas += [{"imdb_id": imdb, "tag": t, "score": s, "origem": "ia"} for t, s in validos]
    d = pd.DataFrame(linhas, columns=["imdb_id", "tag", "score", "origem"])
    if not erros:
        d.to_csv(SAIDA, index=False, encoding="utf-8")
    print(f"{len(arqs)} lotes, {d.imdb_id.nunique()} filmes, {len(d)} etiquetas. "
          f"Faltam {len(esperados - vistos_filmes)} filmes. Erros: {len(erros)}"
          + ("" if erros else f" -> salvo em {SAIDA}"))
    for e in erros[:30]:
        print("   ", e)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selecionar":
        selecionar()
    elif cmd == "mostrar":
        mostrar(int(sys.argv[2]))
    elif cmd == "juntar":
        juntar()
    else:
        print(__doc__)
