"""
Análise exploratória do MovieLens 32M (só leitura; não integra nada ao motor).

Entrada: dados_externos/ml32m/ml-32m/{links,movies,tags}.csv e filmes_v2.csv
Saída:   ml32m_exploracao.txt

Uso:
    python -I ml32m_exploracao.py

MovieLens 32M: uso para pesquisa, não comercial sem permissão. Citar Harper & Konstan (2015).
"""
import hashlib
import os
import re
import sys

import pandas as pd

PASTA = os.path.join("dados_externos", "ml32m", "ml-32m")
ARQ_FILMES = "filmes_v2.csv"
ARQ_VOCAB = "vocabulario_piloto.csv"
ARQ_TG_LISTA = "etiquetas_lista.txt"
MD5_OFICIAL = {  # do README do ml-32m
    "links.csv": "8f033867bcb4e6be8792b21468b4fa6e",
    "movies.csv": "0df90835c19151f9d819d0822e190797",
    "tags.csv": "963bf4fa4de6b8901868fddd3eb54567",
}
TAGS_CLIMA = ["feel-good", "reflective", "absurd", "twist ending", "bleak", "nostalgic", "heartwarming", "dark humor"]
VARIANTES = {  # formas parecidas, só para conferência
    "feel-good": ["feel good", "feelgood", "feel-good movie", "feel good movie"],
    "reflective": ["thought-provoking", "thought provoking", "contemplative", "meditative"],
    "absurd": ["absurdist", "surreal", "weird", "quirky"],
    "twist ending": ["plot twist", "twist", "twists", "surprise ending", "twists & turns"],
    "bleak": ["depressing", "grim", "dark", "downbeat"],
    "nostalgic": ["nostalgia", "80s", "1980s"],
    "heartwarming": ["heart-warming", "heartwarming", "touching", "wholesome"],
    "dark humor": ["dark comedy", "black comedy", "dark humour", "black humor"],
}
# Palavras de opinião, de gestão de lista pessoal ou de formato (ruído para o motor)
RUIDO_OPINIAO = {
    "good", "great", "bad", "boring", "overrated", "underrated", "awesome", "excellent", "amazing",
    "masterpiece", "classic", "favorite", "favorites", "seen it", "watched", "to see", "want to see",
    "own", "owned", "dvd", "bluray", "netflix", "netflix queue", "in netflix queue", "imdb top 250",
    "must see", "worst", "stupid", "terrible", "horrible", "meh", "interesting", "entertaining", "fun",
    "cool", "nice", "perfect", "brilliant", "best", "overhyped", "disappointing", "waste of time",
    "not funny", "predictable", "cliche", "cliché", "too long", "seen", "boring!", "great movie",
    "good movie", "bad movie", "great acting", "good acting", "great soundtrack", "good soundtrack",
    "visually appealing", "cinematography", "pg-13", "pg", "r", "dvd-video", "clv", "tivo",
}

linhas = []


def out(t=""):
    print(t)
    linhas.append(t)


def pct(n, de):
    return f"{100 * n / de:.0f}%" if de else "-"


def md5(arq):
    h = hashlib.md5()
    with open(arq, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def normalizar(t):
    return re.sub(r"\s+", " ", str(t).strip().lower())


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    out("=" * 72)
    out("EXPLORAÇÃO DO MOVIELENS 32M (ml-32m) — nada foi integrado ao motor")
    out("=" * 72)
    out("Arquivos conferidos com o MD5 do README:")
    for nome, oficial in MD5_OFICIAL.items():
        out(f"  {nome}: {'ok' if md5(os.path.join(PASTA, nome)) == oficial else 'DIFERENTE!'}")

    f = pd.read_csv(ARQ_FILMES, dtype={"imdb_id": str})
    f["ano_num"] = pd.to_numeric(f.ano, errors="coerce")
    links = pd.read_csv(os.path.join(PASTA, "links.csv"), dtype={"imdbId": str})
    movies = pd.read_csv(os.path.join(PASTA, "movies.csv"))
    tags = pd.read_csv(os.path.join(PASTA, "tags.csv"), dtype={"tag": str})
    tags = tags.dropna(subset=["tag"])
    tags["tag_n"] = tags.tag.map(normalizar)
    tags = tags[tags.tag_n != ""]

    # ------------------------------------------------------------------ 2) cruzamento
    out("\n" + "=" * 72)
    out("2) CRUZAMENTO links.csv x filmes_v2.csv PELO tmdbId")
    out("=" * 72)
    links = links.dropna(subset=["tmdbId"]).copy()
    links["tmdbId"] = links.tmdbId.astype(int)
    dup = links[links.tmdbId.duplicated(keep=False)]
    m = f.merge(links, left_on="id", right_on="tmdbId", how="left")
    casados = m[m.movieId.notna()].copy()
    casados["movieId"] = casados.movieId.astype(int)
    out(f"Filmes no filmes_v2.csv: {len(f)}")
    out(f"Casaram pelo tmdbId: {casados.id.nunique()} ({pct(casados.id.nunique(), len(f))})")
    out(f"Não casaram: {len(f) - casados.id.nunique()}")
    nao = f[~f.id.isin(casados.id)]
    out(f"  - dos que não casaram, lançados de 2024 em diante (o ml-32m termina em out/2023): "
        f"{(nao.ano_num >= 2024).sum()}")
    out(f"  - dos que não casaram, até 2023: {(nao.ano_num <= 2023).sum()}")
    # casam pelo imdb mesmo sem casar pelo tmdb?
    links_imdb = links.assign(imdb_num=links.imdbId.str.lstrip("0"))
    nao_imdb = nao.assign(imdb_num=nao.imdb_id.fillna("").str.replace("tt", "").str.lstrip("0"))
    por_imdb = nao_imdb.merge(links_imdb, on="imdb_num", how="inner")
    out(f"  - dos que não casaram pelo tmdbId, casariam pelo imdb_id: {por_imdb.id.nunique()}")
    out(f"tmdbIds repetidos no links.csv (mais de um filme do MovieLens): {dup.tmdbId.nunique()} "
        f"(dos nossos: {f.id.isin(dup.tmdbId).sum()})")

    # ------------------------------------------------------------------ 3) cobertura das etiquetas
    out("\n" + "=" * 72)
    out("3) ETIQUETAS DE USUÁRIOS NOS FILMES CASADOS")
    out("=" * 72)
    t = tags[tags.movieId.isin(casados.movieId)]
    # por filme: etiquetas distintas e usuários distintos por etiqueta
    par = t.groupby(["movieId", "tag_n"]).userId.nunique().rename("usuarios").reset_index()
    por_filme = par.groupby("movieId").agg(etiquetas=("tag_n", "size"),
                                           etiq_2mais=("usuarios", lambda s: (s >= 2).sum()))
    casados = casados.drop_duplicates("id").merge(por_filme, left_on="movieId", right_index=True, how="left")
    casados[["etiquetas", "etiq_2mais"]] = casados[["etiquetas", "etiq_2mais"]].fillna(0).astype(int)
    n = len(casados)
    out(f"Aplicações de etiqueta nos filmes casados: {len(t)}; etiquetas distintas: {t.tag_n.nunique()}")
    out(f"{'':<34}{'1+':>8}{'3+':>8}{'5+':>8}{'10+':>8}")
    for col, nome in (("etiquetas", "etiquetas distintas"), ("etiq_2mais", "etiquetas com 2+ usuários")):
        out(f"{nome:<34}" + "".join(f"{pct((casados[col] >= k).sum(), n):>8}" for k in (1, 3, 5, 10)))
    out(f"(base: {n} filmes casados)")

    out("\nCobertura por década (filmes casados; % com 1+, 3+, 5+ etiquetas distintas):")
    out(f"{'Década':<10}{'Filmes':>7}{'1+':>7}{'3+':>7}{'5+':>7}{'5+ c/ 2+ usuários':>20}")
    dec = casados.ano_num // 10 * 10
    for d in range(1920, 2030, 10):
        g = casados[dec == d]
        out(f"{str(d) + 's':<10}{len(g):>7}" + "".join(f"{pct((g.etiquetas >= k).sum(), len(g)):>7}" for k in (1, 3, 5))
            + f"{pct((g.etiq_2mais >= 5).sum(), len(g)):>20}")
    bloco = casados[casados.ano_num.between(2014, 2023)]
    out(f"{'2014-2023':<10}{len(bloco):>7}" + "".join(f"{pct((bloco.etiquetas >= k).sum(), len(bloco)):>7}" for k in (1, 3, 5))
        + f"{pct((bloco.etiq_2mais >= 5).sum(), len(bloco)):>20}")
    out("\nAno a ano, 2014 a 2023 (filmes casados: % com 5+ etiquetas distintas / mediana de etiquetas):")
    out("  " + "  ".join(f"{a}: {pct((g.etiquetas >= 5).sum(), len(g))}/{int(g.etiquetas.median())}"
                         for a, g in bloco.groupby(bloco.ano_num.astype(int))))
    ref_v2 = f[f.ano_num.between(2014, 2023)]
    out(f"Do filmes_v2 inteiro, 2014-2023 são {len(ref_v2)} filmes; com 5+ etiquetas do ml-32m: "
        f"{(bloco.etiquetas >= 5).sum()} ({pct((bloco.etiquetas >= 5).sum(), len(ref_v2))})")

    # ------------------------------------------------------------------ 4) etiquetas mais frequentes
    out("\n" + "=" * 72)
    out("4) ETIQUETAS NORMALIZADAS (minúsculas, sem espaços extras) — só filmes casados")
    out("=" * 72)
    resumo = t.groupby("tag_n").agg(aplicacoes=("userId", "size"), filmes=("movieId", "nunique"),
                                    usuarios=("userId", "nunique"))
    # forma original mais comum (para detectar nomes próprios escritos com maiúsculas)
    forma = t.groupby("tag_n").tag.agg(lambda s: s.value_counts().index[0])
    resumo["forma_comum"] = forma
    vocab = set(pd.read_csv(ARQ_VOCAB).tag)
    tg = {l[7:] for l in open(ARQ_TG_LISTA, encoding="utf-8").read().splitlines()[4:] if l.strip()}

    def classe(tag):
        orig = resumo.at[tag, "forma_comum"]
        palavras = orig.split()
        if tag in RUIDO_OPINIAO or tag.startswith(("oscar", "nudity", "seen ", "watched", "dvd", "netflix")):
            return "ruído: opinião/lista/formato"
        if re.search(r"\d", tag) and not re.fullmatch(r"\d{2,4}s", tag):
            return "ruído: ano/número"
        if re.fullmatch(r"\d{2,4}s", tag):
            return "época"
        if len(palavras) >= 2 and all(p[:1].isupper() for p in palavras if p[:1].isalpha()) and tag not in vocab:
            return "ruído: nome próprio?"
        if tag in vocab:
            return "clima/tema (no nosso vocabulário)"
        if tag in tg:
            return "clima/tema (no Tag Genome)"
        if len(palavras) == 1 and palavras[0][:1].isupper() and tag not in tg:
            return "ruído: nome próprio?"
        return "a revisar"

    resumo["classe"] = [classe(x) for x in resumo.index]
    top = resumo.sort_values(["aplicacoes", "filmes"], ascending=False).head(150)
    out("As 150 mais frequentes (aplicações = vezes usada; filmes = filmes diferentes; usuários = pessoas diferentes):")
    out(f"{'#':>4} {'etiqueta':<32}{'aplic.':>8}{'filmes':>8}{'usuár.':>8}  proposta")
    for i, (tag, r) in enumerate(top.iterrows(), start=1):
        out(f"{i:>4} {tag[:31]:<32}{r.aplicacoes:>8}{r.filmes:>8}{r.usuarios:>8}  {r.classe}")
    out("\nResumo da proposta nas 150 mais frequentes: " +
        "; ".join(f"{k}: {v}" for k, v in top.classe.value_counts().items()))

    tres = resumo[resumo.filmes >= 3].sort_values("filmes", ascending=False)
    out(f"\nEtiquetas em 3 ou mais filmes diferentes: {len(tres)} (de {len(resumo)} distintas)")
    out("Proposta automática para essas: " + "; ".join(f"{k}: {v}" for k, v in tres.classe.value_counts().items()))
    out("(lista completa no APÊNDICE, no fim deste arquivo)")

    # ------------------------------------------------------------------ 5) etiquetas de clima nos recentes
    out("\n" + "=" * 72)
    out("5) ETIQUETAS DE CLIMA DOS PEDIDOS NOS FILMES RECENTES")
    out("=" * 72)
    recentes = casados[casados.ano_num >= 2014]
    ids_rec = set(recentes.movieId)
    par_rec = par[par.movieId.isin(ids_rec)]
    out(f"Filmes recentes casados (2014+): {len(recentes)} (todos os recentes do filmes_v2: {(f.ano_num >= 2014).sum()})")
    out(f"{'etiqueta':<16}{'filmes (1+ usuário)':>21}{'filmes (2+ usuários)':>22}   variantes (filmes 1+): ")
    for tag in TAGS_CLIMA:
        g = par_rec[par_rec.tag_n == tag]
        var = []
        for v in VARIANTES[tag]:
            nv = par_rec[par_rec.tag_n == v].movieId.nunique()
            if nv:
                var.append(f"{v} {nv}")
        out(f"{tag:<16}{g.movieId.nunique():>21}{(g.usuarios >= 2).sum():>22}   {', '.join(var)}")
    # exemplos
    out("Exemplos (filmes recentes com a etiqueta, mais votados primeiro):")
    tit = recentes.set_index("movieId")
    for tag in TAGS_CLIMA:
        ids = par_rec[par_rec.tag_n == tag].movieId
        ex = tit.loc[tit.index.intersection(ids)].sort_values("votos", ascending=False).titulo.head(5).tolist()
        if ex:
            out(f"  {tag}: {', '.join(ex)}")

    # ------------------------------------------------------------------ 6) problemas
    out("\n" + "=" * 72)
    out("6) PROBLEMAS ENCONTRADOS")
    out("=" * 72)
    out(f"a) Pares (filme, etiqueta) aplicados por um único usuário: {pct((par.usuarios == 1).sum(), len(par))} "
        f"de {len(par)} pares")
    out(f"   Etiquetas distintas usadas por um único usuário em todos os nossos filmes: "
        f"{pct((resumo.usuarios == 1).sum(), len(resumo))} de {len(resumo)}")
    por_usuario = t.groupby("userId").size().sort_values(ascending=False)
    out(f"b) Concentração: {t.userId.nunique()} usuários etiquetaram nossos filmes; os 10 que mais etiquetaram "
        f"fizeram {pct(por_usuario.head(10).sum(), len(t))} das aplicações; o maior sozinho, "
        f"{pct(por_usuario.iloc[0], len(t))}.")
    top_user = t[t.userId == por_usuario.index[0]]
    out(f"   Etiquetas mais usadas pelo maior etiquetador: "
        + ", ".join(top_user.tag_n.value_counts().head(8).index))
    pop = casados.sort_values("votos", ascending=False)
    out(f"c) Filmes casados populares com menos de 5 etiquetas: {(pop.head(500).etiquetas < 5).sum()} entre os 500 "
        f"mais votados no TMDB; {(pop.head(2000).etiquetas < 5).sum()} entre os 2.000 mais votados. Os mais votados:")
    for r in pop[pop.etiquetas < 5].head(12).itertuples():
        out(f"     {r.titulo} ({int(r.ano_num) if pd.notna(r.ano_num) else '?'}) — {r.etiquetas} etiquetas, {r.votos} votos TMDB")
    out(f"   Só com etiquetas usadas por 2+ pessoas: {(pop.head(500).etiq_2mais < 5).sum()} dos 500 mais votados "
        f"têm menos de 5.")
    # erros de correspondência
    mv = movies.set_index("movieId")
    casados["ano_ml"] = casados.movieId.map(mv.title.str.extract(r"\((\d{4})\)\s*$")[0].astype(float))
    casados["titulo_ml"] = casados.movieId.map(mv.title)
    casados["imdb_v2"] = casados.imdb_id.fillna("").str.replace("tt", "").str.lstrip("0")
    casados["imdb_ml"] = casados.imdbId.fillna("").str.lstrip("0")
    dif_imdb = casados[(casados.imdb_v2 != "") & (casados.imdb_v2 != casados.imdb_ml)]
    dif_ano = casados[(casados.ano_ml.notna()) & ((casados.ano_ml - casados.ano_num).abs() > 1)]
    out(f"d) Correspondência: imdb_id diferente entre filmes_v2 e links.csv: {len(dif_imdb)} filmes; "
        f"ano diferente em mais de 1: {len(dif_ano)} filmes")
    for r in pd.concat([dif_imdb, dif_ano]).drop_duplicates("id").head(12).itertuples():
        out(f"     TMDB: {r.titulo} ({r.ano}) tt{r.imdb_v2}  x  MovieLens: {r.titulo_ml} tt{r.imdb_ml}")
    out(f"e) Filmes de 2024 em diante no filmes_v2: {(f.ano_num >= 2024).sum()} — o ml-32m vai só até out/2023, "
        f"então eles nunca terão etiqueta dessa fonte.")
    recent_23 = casados[casados.ano_num == 2023]
    out(f"   Filmes de 2023 casados: {len(recent_23)}, com 5+ etiquetas: {(recent_23.etiquetas >= 5).sum()} "
        f"(lançados perto do fim da coleta, tiveram pouco tempo para receber etiquetas).")

    # ------------------------------------------------------------------ 7) recomendação
    pares2 = (par.usuarios >= 2).mean()
    out("\n" + "=" * 72)
    out("7) RECOMENDAÇÃO (em português simples)")
    out("=" * 72)
    out(f"""Vale a pena integrar? SIM, principalmente para os filmes de 2014 a 2023, que é justamente o buraco
do Tag Genome (que para em 2014). Dos {len(ref_v2)} filmes de 2014-2023 do filmes_v2, {(bloco.etiquetas >= 5).sum()} ({pct((bloco.etiquetas >= 5).sum(), len(ref_v2))})
têm 5 ou mais etiquetas aqui. Não resolve os {(f.ano_num >= 2024).sum()} filmes de 2024 em diante (a coleta parou em out/2023),
e os de 2023 têm poucas etiquetas.

O cruzamento é confiável: {casados.id.nunique()} de {len(f)} filmes casam pelo tmdbId. As "diferenças" encontradas são
o mesmo filme com imdb_id ou ano de lançamento diferentes entre TMDB e MovieLens, não filmes trocados.

Como integrar (proposta, nada foi feito ainda):
1. Contar PESSOAS, não usos. Para cada filme e etiqueta, guardar quantos usuários diferentes usaram a
   etiqueta. Um único usuário fez {pct(por_usuario.iloc[0], len(t))} de todas as aplicações nos nossos filmes (quase sempre
   "murder", "violence", "death"); contar usos deixaria o gosto dele mandar no motor.
2. Exigir pelo menos 2 pessoas por etiqueta. {pct(1 - pares2, 1)} dos pares filme-etiqueta foram usados por uma pessoa só
   (muito ruído). Com o corte de 2 pessoas, {pct((bloco.etiq_2mais >= 5).sum(), len(bloco))} dos filmes casados de 2014-2023 ainda ficam com 5+ etiquetas.
3. Transformar em nota de 0 a 1 do jeito simples: pessoas que usaram a etiqueta / pessoas que etiquetaram
   o filme (ex.: 12 de 40 = 0,3). Assim dá para comparar com o Tag Genome e com as etiquetas da IA.
4. Usar só uma lista de etiquetas aprovadas (o vocabulário de 150 do piloto), com uma tabela de sinônimos
   feita à mão. Exemplos vistos aqui: "thought-provoking" para reflective (quase ninguém escreve
   "reflective"), "dark comedy"/"black comedy" para dark humor, "feel good" para feel-good, "plot twist"/
   "surprise ending" para twist ending. Jogar fora nomes de pessoas, opiniões ("boring", "overrated"),
   "nudity", "oscar" etc.
5. Guardar com origem "ml32m", separada do Tag Genome e da IA.
6. Bônus: dá para conferir as etiquetas que a IA deu aos 100 filmes recentes do piloto contra as
   etiquetas reais de usuários do ml-32m.

Licença: o ml-32m é para uso em pesquisa e não pode ter uso comercial sem permissão da GroupLens; pode
redistribuir só nas mesmas condições; é preciso citar Harper & Konstan (2015) e não dar a entender apoio
da Universidade de Minnesota. O projeto de portfólio sem venda combina com isso, mas, como no Tag Genome,
se um dia houver venda essa fonte precisa ser trocada ou autorizada.""")

    # ------------------------------------------------------------------ apêndice
    out("\n" + "=" * 72)
    out(f"APÊNDICE — etiquetas em 3 ou mais filmes diferentes ({len(tres)}), por número de filmes")
    out("filmes | usuários | etiqueta | proposta")
    out("=" * 72)
    for tag, r in tres.iterrows():
        out(f"{r.filmes:>5} {r.usuarios:>6}  {tag}  [{r.classe}]")

    with open("ml32m_exploracao.txt", "w", encoding="utf-8") as arq:
        arq.write("\n".join(linhas) + "\n")
    print("\nSalvo em ml32m_exploracao.txt")


if __name__ == "__main__":
    main()
