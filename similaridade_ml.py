"""
Similaridade "quem gostou de X também gostou de Y" a partir das notas do MovieLens 32M (ratings.csv).

- Lê dados_externos/ml32m/ratings/ratings.csv em pedaços (2 milhões de linhas por vez).
- Liga ao catálogo pelo links.csv (tmdbId = id do filmes_v2.csv). Fica só com notas >= 4.0 ("gostou").
- Vetores binários "usuário gostou" por filme. Para cada par: co = usuários que gostaram dos dois,
  cosseno = co / sqrt(n_x * n_y), sim = cosseno * co / (co + 20). Só vale com co >= 30.
- Guarda os 30 vizinhos mais fortes de cada filme em vizinhos_ml.csv (id, posicao, vizinho_id, pontos, co),
  com pontos = round(sim * 1000).

Licença: derivado das notas do MovieLens 32M (GroupLens). Uso só para pesquisa e não comercial; não sugerir
endosso da Universidade de Minnesota. Ver site/LICENCAS.html.

Uso: python -I similaridade_ml.py            (gera vizinhos_ml.csv)
     python -I similaridade_ml.py mostrar    (só mostra os vizinhos dos filmes de exemplo)
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import sparse

RATINGS = "dados_externos/ml32m/ratings/ratings.csv"
LINKS = "dados_externos/ml32m/ml-32m/links.csv"
CATALOGO = "filmes_v2.csv"
SAIDA = "vizinhos_ml.csv"
NOTA_MIN = 4.0
MIN_CO = 30
ENCOLHE = 20
TOP = 30
EXEMPLOS = ["Interestelar", "Parasita", "Matrix", "Toy Story: Um Mundo de Aventuras", "Cisne Negro",
            "Whiplash: Em Busca da Perfeição", "O Auto da Compadecida",
            "Clube da Luta"]


def gerar():
    cat = pd.read_csv(CATALOGO, usecols=["id", "titulo", "ano"])
    ids = cat.id.tolist()
    col = {t: k for k, t in enumerate(ids)}
    links = pd.read_csv(LINKS).dropna(subset=["tmdbId"])
    links["tmdbId"] = links.tmdbId.astype(int)
    links = links[links.tmdbId.isin(col)]
    mov2col = dict(zip(links.movieId, links.tmdbId.map(col)))
    print(f"Filmes do catálogo ligados ao MovieLens: {len(set(mov2col.values()))} de {len(ids)}")

    us, it = [], []
    lidas = 0
    for ch in pd.read_csv(RATINGS, usecols=["userId", "movieId", "rating"], chunksize=2_000_000,
                          dtype={"userId": np.int32, "movieId": np.int32, "rating": np.float32}):
        lidas += len(ch)
        ch = ch[(ch.rating >= NOTA_MIN) & ch.movieId.isin(mov2col.keys())]
        us.append(ch.userId.to_numpy())
        it.append(ch.movieId.map(mov2col).to_numpy(np.int32))
        print(f"  {lidas:,} linhas lidas".replace(",", "."), end="\r")
    us, it = np.concatenate(us), np.concatenate(it)
    print(f"\nNotas >= {NOTA_MIN} em filmes do catálogo: {len(us):,}".replace(",", "."))
    _, urow = np.unique(us, return_inverse=True)
    X = sparse.csr_matrix((np.ones(len(us), np.float32), (urow, it)), shape=(urow.max() + 1, len(ids)))
    X.data[:] = 1  # binário (dois movieId para o mesmo filme contam uma vez)
    X.sum_duplicates()
    X.data[:] = 1
    n = np.asarray(X.sum(axis=0)).ravel()
    print(f"Usuários: {X.shape[0]:,} | filmes com alguma nota >= 4: {(n > 0).sum()}".replace(",", "."))
    co = (X.T @ X).toarray()  # usuários em comum (6000 x 6000)
    np.fill_diagonal(co, 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        cos = co / np.sqrt(np.outer(n, n))
    sim = np.nan_to_num(cos) * co / (co + ENCOLHE)
    sim[co < MIN_CO] = 0
    linhas = []
    for k in range(len(ids)):
        s = sim[k]
        top = np.argsort(-s, kind="stable")[:TOP]
        top = top[s[top] > 0]
        for pos, j in enumerate(top, 1):
            p = int(round(s[j] * 1000))
            if p > 0:
                linhas.append((ids[k], pos, ids[j], p, int(co[k, j])))
    out = pd.DataFrame(linhas, columns=["id", "posicao", "vizinho_id", "pontos", "co"])
    out.to_csv(SAIDA, index=False)
    com = out.id.nunique()
    print(f"\n{SAIDA}: {len(out):,} linhas, {os.path.getsize(SAIDA) / 1e6:.2f} MB".replace(",", "."))
    print(f"COBERTURA: {com} de {len(ids)} filmes têm vizinhos; {len(ids) - com} ficaram sem.")
    sem = cat[~cat.id.isin(out.id)]
    ligados = set(links.tmdbId)
    print(f"  dos sem vizinhos: {(~sem.id.isin(ligados)).sum()} fora do MovieLens; "
          f"{sem.id.isin(ligados).sum()} no MovieLens mas com poucas notas >= 4 / poucos usuários em comum")
    print("  sem vizinhos por ano de lançamento:")
    faixas = pd.cut(sem.ano, [0, 1999, 2009, 2019, 2023, 2100], labels=["até 1999", "2000-2009", "2010-2019",
                                                                         "2020-2023", "2024+"])
    tot = pd.cut(cat.ano, [0, 1999, 2009, 2019, 2023, 2100], labels=["até 1999", "2000-2009", "2010-2019",
                                                                       "2020-2023", "2024+"])
    for fx in faixas.cat.categories:
        print(f"    {fx:<10} {(faixas == fx).sum():>5} de {(tot == fx).sum():>5}")
    mostrar()


def mostrar():
    cat = pd.read_csv(CATALOGO, usecols=["id", "titulo", "ano", "votos"])
    nome = dict(zip(cat.id, cat.titulo + " (" + cat.ano.astype(str) + ")"))
    v = pd.read_csv(SAIDA)
    print("\nVIZINHOS DE FILMES CONHECIDOS (só para olhar; nada foi ajustado com base nisto)")
    for t in EXEMPLOS:
        c = cat[cat.titulo == t].sort_values("votos", ascending=False)
        if c.empty:
            print(f"\n{t}: não está no catálogo")
            continue
        fid = c.id.iloc[0]
        vv = v[v.id == fid].head(10)
        print(f"\n{nome[fid]}:" + ("  (sem vizinhos)" if vv.empty else ""))
        for r in vv.itertuples():
            print(f"   {r.posicao:>2}. {nome.get(r.vizinho_id, r.vizinho_id)}  [{r.pontos}, {r.co} em comum]")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    mostrar() if sys.argv[1:] == ["mostrar"] else gerar()
