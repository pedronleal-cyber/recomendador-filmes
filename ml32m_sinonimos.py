"""
MovieLens 32M: tabela de sinônimos, conferência das etiquetas da IA e cobertura combinada.
Só análise; não integra nada ao motor.

Uso:
    python -I ml32m_sinonimos.py

Saídas:
    sinonimos_ml32m.csv      etiqueta_vocabulario, variante, n_filmes (+ colunas de conferência)
    ml32m_conferencia.txt    relatório (amostra, conferência do piloto, cobertura combinada)
    filmes_sem_fonte.csv     filmes sem nenhuma fonte boa de etiquetas (os que faltam etiquetar)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # para importar diagnostico_tags (mesma pasta)

import numpy as np
import pandas as pd

PASTA = os.path.join("dados_externos", "ml32m", "ml-32m")
MIN_FILMES = 3          # variante precisa aparecer em 3+ filmes do ml-32m
MIN_PESSOAS = 2         # nota do ml-32m só conta com 2+ pessoas
ML_BOA_ETIQ = 5         # "ml32m bom" = 5+ etiquetas com 2+ pessoas
TAGS_CLIMA = ["feel-good", "bleak", "reflective", "funny", "sad",
              "tense", "thought-provoking", "heartwarming", "twist ending", "absurd"]

# ---------------------------------------------------------------------------
# Sinônimos feitos à mão (o que os usuários escrevem no lugar das nossas etiquetas).
# Cada variante só vale se existir em 3+ filmes do ml-32m (o script confere).
# ---------------------------------------------------------------------------
MANUAL = {
    "feel-good": ["feel good movie", "feel-good movie", "uplifting", "cheerful", "happy"],
    "heartwarming": ["touching", "heart warming", "wholesome", "sweet"],
    "tear jerker": ["tearjerker", "tear-jerker", "made me cry", "cry", "crying", "tissues"],
    "sad": ["sadness", "heartbreaking", "sad ending"],
    "bittersweet": ["bitter-sweet"],
    "touching": ["moving"],
    "poignant": ["powerful"],
    "emotional": ["emotionally powerful", "emotions"],
    "sentimental": ["sappy", "schmaltzy"],
    "melancholic": ["melancholy", "melancholia"],
    "bleak": ["hopeless", "nihilistic", "nihilism", "pessimistic"],
    "depressing": ["depression"],
    "downbeat": ["sad ending", "unhappy ending"],
    "grim": ["grimdark"],
    "dark": ["dark themes", "dark fantasy"],
    "gritty": ["raw", "realistic"],
    "disturbing": ["unsettling", "uncomfortable", "shocking"],
    "creepy": ["spooky", "creepy kids"],
    "eerie": ["haunting"],
    "scary": ["frightening", "terrifying", "scary as hell", "horrifying"],
    "ominous": ["foreboding"],
    "tense": ["tension", "nail-biter", "edge of your seat"],
    "suspenseful": ["suspense", "suspensful"],
    "intense": ["gripping"],
    "atmospheric": ["atmosphere", "moody"],
    "claustrophobic": ["claustrophobia"],
    "paranoid": ["paranoia"],
    "reflective": ["contemplative", "introspective"],
    "meditative": ["slow and meditative"],
    "thought-provoking": ["thought provoking", "makes you think", "deep"],
    "cerebral": ["intellectual", "intelligent"],
    "philosophical": ["philosophy"],
    "funny": ["humorous", "humor", "very funny", "funny!"],
    "hilarious": ["laugh out loud", "funny as hell"],
    "witty": ["clever", "smart"],
    "silly": ["silly fun"],
    "goofy": ["goofy fun"],
    "quirky": ["eccentric", "offbeat", "weird"],
    "whimsical": ["charming"],
    "absurd": ["absurdist", "absurdism", "absurdity", "bizarre"],
    "surreal": ["surrealism", "surrealist"],
    "dreamlike": ["dreamy", "dream-like"],
    "dark humor": ["dark comedy", "black comedy", "black humor", "dark humour", "black humour", "gallows humor"],
    "satirical": ["satire"],
    "cynical": ["cynicism"],
    "inspirational": ["inspiring", "motivational"],
    "nostalgic": ["nostalgia"],
    "romantic": ["romance"],
    "cute": ["adorable"],
    "light": ["lighthearted", "light-hearted", "light hearted"],
    "visceral": ["raw violence"],
    "brutal": ["brutality", "brutal violence"],
    "campy": ["camp", "cheesy"],
    "friendship": ["friends", "male friendship", "female friendship"],
    "unlikely friendships": ["unlikely friendship", "odd couple", "buddy movie"],
    "love story": ["love"],
    "coming of age": ["growing up"],
    "family drama": ["family relationships", "family"],
    "dysfunctional family": ["family dysfunction"],
    "father daughter relationship": ["father-daughter relationship"],
    "parenthood": ["parenting", "fatherhood", "motherhood"],
    "loneliness": ["lonely", "isolation", "solitude"],
    "revenge": ["vengeance", "revenge story"],
    "sacrifice": ["self-sacrifice", "self sacrifice"],
    "betrayal": ["double cross"],
    "obsession": ["obsessive"],
    "corruption": ["police corruption", "political corruption"],
    "social commentary": ["social critique", "social criticism", "class"],
    "politics": ["political"],
    "war": ["war movie", "world war ii", "wwii", "vietnam war"],
    "anti-war": ["anti war"],
    "racism": ["race issues", "race relations", "race"],
    "mental illness": ["mental health", "insanity", "schizophrenia"],
    "addiction": ["drug addiction", "alcoholism", "drug abuse"],
    "life & death": ["death", "mortality"],
    "existentialism": ["existential", "existential crisis"],
    "memory": ["memory loss", "amnesia", "memories"],
    "destiny": ["fate"],
    "good versus evil": ["good vs evil", "good vs. evil"],
    "religion": ["christianity", "faith", "religious"],
    "artificial intelligence": ["ai", "a.i."],
    "dystopia": ["dystopian", "dystopic future", "distopia"],
    "end of the world": ["apocalypse", "apocalyptic"],
    "post-apocalyptic": ["post apocalyptic", "postapocalyptic"],
    "first contact": ["alien contact", "aliens"],
    "alternate reality": ["alternate universe", "parallel universe", "multiverse", "alternate timeline"],
    "supernatural": ["paranormal"],
    "mythology": ["greek mythology", "norse mythology"],
    "fairy tale": ["fairytale"],
    "ghosts": ["haunted house"],
    "monster": ["creature"],
    "conspiracy": ["conspiracy theory"],
    "organized crime": ["mafia", "mob", "gangsters", "gangster"],
    "heist": ["robbery", "bank robbery"],
    "espionage": ["spy", "spies", "spying"],
    "police investigation": ["investigation", "detective"],
    "courtroom": ["courtroom drama", "court", "trial", "legal drama"],
    "prison escape": ["prison break"],
    "superhero": ["superheroes", "super hero", "super-hero", "comic book"],
    "space": ["outer space", "space travel"],
    "road trip": ["road movie"],
    "animals": ["animal", "talking animals"],
    "true story": ["based on a true story", "based on true story", "true events", "biopic"],
    "twist ending": ["plot twist", "surprise ending", "twist", "twists", "unexpected ending", "twisted ending"],
    "twists & turns": ["twists and turns", "plot twists"],
    "nonlinear": ["non-linear", "nonlinear timeline", "non-linear timeline", "nonlinear narrative"],
    "mindfuck": ["mind-bending", "mind bending", "mindbending", "mind-fuck", "mind fuck"],
    "complex": ["complicated", "complex plot", "intricate"],
    "enigmatic": ["mysterious", "ambiguous", "open ending"],
    "murder mystery": ["whodunit", "whodunnit"],
    "chase": ["car chase", "chase scenes"],
    "visually stunning": ["stunning visuals", "gorgeous", "beautiful"],
    "stylized": ["stylish", "stylised"],
    "character study": ["character driven", "character-driven"],
    "dialogue driven": ["dialogue", "talky"],
    "multiple storylines": ["interwoven storylines", "ensemble cast"],
    "art house": ["arthouse", "art-house", "artsy"],
    "neo-noir": ["noir", "film noir"],
    "period piece": ["period drama", "historical"],
    "parody": ["spoof"],
    "gory": ["gore", "bloody", "splatter", "gruesome"],
    "fast paced": ["fast-paced"],
    "slow paced": ["slow", "slow-paced", "slow burn"],
    "action packed": ["action-packed"],
    "kids and family": ["family friendly", "family-friendly", "kids", "children"],
    "teen movie": ["teen", "teenagers"],
    "chick flick": ["chick-flick", "girlie movie"],
}

# Mapeamentos que o Claude considera duvidosos (para o autor revisar), com o motivo.
DUVIDOSOS = {
    ("visually stunning", "beautiful"): "'beautiful' pode ser elogio genérico, não visual",
    ("family drama", "family"): "'family' é usado também para filme infantil",
    ("love story", "love"): "'love' é amplo (amor de família, amizade)",
    ("romantic", "romance"): "'romance' é gênero, não clima",
    ("life & death", "death"): "'death' marca qualquer morte na trama",
    ("first contact", "aliens"): "'aliens' inclui invasão e terror, não só primeiro contato",
    ("war", "world war ii"): "período específico, não 'guerra' no geral",
    ("quirky", "weird"): "'weird' pode ser estranho no sentido de surreal ou ruim",
    ("witty", "clever"): "'clever' pode ser trama esperta, não diálogo espirituoso",
    ("cerebral", "intelligent"): "'intelligent' é meio elogio",
    ("gritty", "realistic"): "'realistic' nem sempre é 'cru/sujo'",
    ("poignant", "powerful"): "'powerful' é elogio genérico",
    ("campy", "cheesy"): "'cheesy' costuma ser crítica",
    ("dark", "dark fantasy"): "subgênero, não só clima escuro",
    ("multiple storylines", "ensemble cast"): "elenco grande não garante várias histórias",
    ("period piece", "historical"): "'historical' pode ser fato real, não filme de época",
    ("true story", "biopic"): "biografia é um tipo de história real, mas não o contrário",
    ("superhero", "comic book"): "nem todo filme de HQ é de super-herói",
    ("social commentary", "class"): "'class' pode ser elogio ('classy') ou escola",
    ("racism", "race"): "'race' também é corrida",
    ("intense", "gripping"): "'gripping' é meio elogio",
    ("enigmatic", "open ending"): "final aberto não é o mesmo que enigmático",
    ("feel-good", "happy"): "'happy' pode ser só 'happy ending'",
    ("heartwarming", "sweet"): "'sweet' pode ser fofo, não comovente",
    ("slow paced", "slow"): "'slow' às vezes é crítica ('chato')",
    ("dialogue driven", "dialogue"): "'dialogue' pode ser elogio ao diálogo",
    ("kids and family", "children"): "'children' pode marcar personagens crianças, não público",
    ("police investigation", "detective"): "detetive particular não é polícia",
}

# Ruído que nunca entra (opinião, nudez, prêmios, gestão de lista)
PROIBIDOS = re.compile(r"^(good|great|bad|boring|overrated|underrated|awesome|excellent|amazing|masterpiece|"
                       r"classic|favorite|seen it|watched|dvd|netflix|imdb top 250|stupid|terrible|worst|"
                       r"predictable|too long|visually appealing|cinematography|great soundtrack|great acting)$"
                       r"|nudity|oscar")

linhas = []


def out(t=""):
    print(t)
    linhas.append(t)


def pct(n, de):
    return f"{100 * n / de:.0f}%" if de else "-"


def normalizar(t):
    return re.sub(r"\s+", " ", str(t).strip().lower())


def formas(tag):
    """Variações de grafia automáticas: hífen/espaço, plural/singular, &/and, humor/humour."""
    fs = {tag, tag.replace("-", " "), tag.replace("-", ""), tag.replace(" ", "-"), tag.replace(" ", ""),
          tag.replace("&", "and"), tag.replace(" & ", " and "), tag.replace("humor", "humour")}
    fs |= {f + "s" for f in list(fs)} | {f[:-1] for f in list(fs) if f.endswith("s")}
    return {f for f in fs if f}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    import diagnostico_tags as dg

    vocab = list(pd.read_csv("vocabulario_piloto.csv").tag)
    f = dg.carregar()  # filmes_v2 + tem_etiqueta (Tag Genome)
    links = pd.read_csv(os.path.join(PASTA, "links.csv")).dropna(subset=["tmdbId"])
    links["tmdbId"] = links.tmdbId.astype(int)
    tags = pd.read_csv(os.path.join(PASTA, "tags.csv"), dtype={"tag": str}).dropna(subset=["tag"])
    tags["tag_n"] = tags.tag.map(normalizar)
    tmdb_para_ml = links.drop_duplicates("tmdbId").set_index("tmdbId").movieId
    f["movieId"] = f.id.map(tmdb_para_ml)
    nossos = set(f.movieId.dropna().astype(int))

    filmes_por_tag = tags.groupby("tag_n").movieId.nunique()
    filmes_nossos_por_tag = tags[tags.movieId.isin(nossos)].groupby("tag_n").movieId.nunique()

    # ------------------------------------------------------------------ 1) sinônimos
    linhas_sin, ja_usada, descartadas = [], {}, []
    for v in vocab:
        candidatos = [(c, "grafia") for c in sorted(formas(v))] + [(c, "manual") for c in MANUAL.get(v, [])]
        for c, origem in candidatos:
            c = normalizar(c)
            if PROIBIDOS.search(c):
                descartadas.append((v, c, "opinião/nudez/prêmio"))
                continue
            n = int(filmes_por_tag.get(c, 0))
            if n < MIN_FILMES:
                if origem == "manual":
                    descartadas.append((v, c, f"só {n} filme(s)"))
                continue
            if c in ja_usada and ja_usada[c] != v:
                descartadas.append((v, c, f"já mapeada para '{ja_usada[c]}'"))
                continue
            if c in ja_usada:
                continue
            ja_usada[c] = v
            linhas_sin.append({"etiqueta_vocabulario": v, "variante": c, "n_filmes": n,
                               "n_filmes_nossos": int(filmes_nossos_por_tag.get(c, 0)),
                               "origem": "exata" if c == v else origem,
                               "duvidoso": DUVIDOSOS.get((v, c), "")})
    sin = pd.DataFrame(linhas_sin)

    # Conferência estatística com o Tag Genome: nos filmes com a variante (e com Tag Genome),
    # a nota GLMER da etiqueta do vocabulário é quantas vezes a média geral?
    T = dg.matriz_etiquetas(f)
    linha_por_ml = {int(m): i for i, m in f.movieId.dropna().items() if i in T.index}
    filmes_com = tags[tags.movieId.isin(linha_por_ml)].groupby("tag_n").movieId.unique()
    razoes, ns = [], []
    for r in sin.itertuples():
        ids = filmes_com.get(r.variante, [])
        linhas_tg = [linha_por_ml[m] for m in ids]
        if len(linhas_tg) >= 3 and r.etiqueta_vocabulario in T.columns:
            razoes.append(round(float(T.loc[linhas_tg, r.etiqueta_vocabulario].mean() / T[r.etiqueta_vocabulario].mean()), 2))
        else:
            razoes.append(np.nan)
        ns.append(len(linhas_tg))
    sin["filmes_com_tag_genome"] = ns
    sin["razao_tag_genome"] = razoes  # >1 = a variante aponta para filmes com nota alta na etiqueta
    sin.to_csv("sinonimos_ml32m.csv", index=False, encoding="utf-8")

    out("=" * 76)
    out("1) TABELA DE SINÔNIMOS (sinonimos_ml32m.csv)")
    out("=" * 76)
    out(f"{len(sin)} linhas: {(sin.origem == 'exata').sum()} exatas, {(sin.origem == 'grafia').sum()} de grafia, "
        f"{(sin.origem == 'manual').sum()} manuais. Etiquetas do vocabulário com pelo menos 1 forma no ml-32m: "
        f"{sin.etiqueta_vocabulario.nunique()} de {len(vocab)}.")
    sem = [v for v in vocab if v not in set(sin.etiqueta_vocabulario)]
    out(f"Sem nenhuma forma no ml-32m (3+ filmes): {sem or 'nenhuma'}")
    out(f"Variantes manuais descartadas: {len(descartadas)} (ex.: " +
        "; ".join(f"{v} <- {c} ({m})" for v, c, m in descartadas[:8]) + ")")
    out("razao_tag_genome = nota média do Tag Genome para a etiqueta nos filmes que têm a variante, dividida pela")
    out("média geral. Perto de 1 = a variante não indica nada; quanto maior, melhor.")
    amostra = pd.concat([
        sin[sin.duvidoso != ""].sort_values("n_filmes", ascending=False).head(10),
        sin[(sin.duvidoso == "") & (sin.origem != "exata")].sort_values("n_filmes", ascending=False).head(30),
    ])
    out(f"\nAmostra de {len(amostra)} linhas (as 10 primeiras são as duvidosas):")
    out(f"{'etiqueta_vocabulario':<24}{'variante':<26}{'filmes':>7}{'nossos':>7}{'razão TG':>9}  observação")
    for r in amostra.itertuples():
        rz = "" if pd.isna(r.razao_tag_genome) else f"{r.razao_tag_genome:.1f}"
        out(f"{r.etiqueta_vocabulario[:23]:<24}{r.variante[:25]:<26}{r.n_filmes:>7}{r.n_filmes_nossos:>7}{rz:>9}  "
            f"{'DUVIDOSO: ' + r.duvidoso if r.duvidoso else r.origem}")
    fracos = sin[(sin.origem != "exata") & (sin.razao_tag_genome < 1.5)]
    out(f"\nVariantes com razão Tag Genome abaixo de 1,5 (indicam pouco; candidatas a sair): {len(fracos)}")
    out("  " + "; ".join(f"{r.etiqueta_vocabulario} <- {r.variante} ({r.razao_tag_genome})" for r in fracos.itertuples()))

    # ------------------------------------------------------------------ notas do ml-32m
    var_para_vocab = dict(zip(sin.variante, sin.etiqueta_vocabulario))
    t = tags[tags.movieId.isin(nossos)].copy()
    etiquetadores = t.groupby("movieId").userId.nunique()
    t["vocab"] = t.tag_n.map(var_para_vocab)
    tv = t.dropna(subset=["vocab"])
    pessoas = tv.groupby(["movieId", "vocab"]).userId.nunique().rename("pessoas").reset_index()
    pessoas["nota"] = np.where(pessoas.pessoas >= MIN_PESSOAS,
                               pessoas.pessoas / pessoas.movieId.map(etiquetadores), 0.0)
    nota_ml = pessoas.pivot_table(index="movieId", columns="vocab", values="nota", fill_value=0).reindex(columns=vocab, fill_value=0)

    # ------------------------------------------------------------------ 2) conferência do piloto
    out("\n" + "=" * 76)
    out("2) CONFERÊNCIA: etiquetas da IA (100 filmes recentes) x ml-32m")
    out("=" * 76)
    ia = pd.read_csv("etiquetas_ia_piloto.csv", dtype={"imdb_id": str})
    imdb_para_ml = f.dropna(subset=["movieId"]).drop_duplicates("imdb_id").set_index("imdb_id").movieId.astype(int)
    filmes_ia = list(dict.fromkeys(ia.imdb_id))
    com_ml = [i for i in filmes_ia if i in imdb_para_ml.index and etiquetadores.get(imdb_para_ml[i], 0) >= 5]
    out(f"Filmes do piloto: {len(filmes_ia)}; com pelo menos 5 pessoas etiquetando no ml-32m: {len(com_ml)}")
    sem_ml = [i for i in filmes_ia if i not in com_ml]
    if sem_ml:
        tit = f.drop_duplicates("imdb_id").set_index("imdb_id").titulo
        out("  Sem dados suficientes no ml-32m: " + ", ".join(tit.get(i, i) for i in sem_ml))
    M = (ia.pivot_table(index="imdb_id", columns="tag", values="score")
         .reindex(index=com_ml, columns=vocab).fillna(0).to_numpy())
    R = nota_ml.reindex([imdb_para_ml[i] for i in com_ml]).fillna(0).to_numpy()
    media = R.mean(axis=0)

    def correl(A, B):
        A = A - A.mean(axis=1, keepdims=True)
        B = B - B.mean(axis=1, keepdims=True)
        den = np.sqrt((A ** 2).sum(axis=1) * (B ** 2).sum(axis=1))
        return np.where(den > 0, (A * B).sum(axis=1) / np.where(den > 0, den, 1), np.nan)

    c = correl(M, R)
    c_p = correl(M, R - media)
    c_chute = correl(np.tile(media, (len(com_ml), 1)), R)
    out(f"\na) Correlação por filme (150 etiquetas): crua {np.nanmean(c):.3f}; própria do filme {np.nanmean(c_p):.3f} "
        f"(chute bobo = média do ml-32m para todo filme: crua {np.nanmean(c_chute):.3f}, própria 0)")
    out("   Distribuição (própria do filme): " + ", ".join(
        f"{a:.1f} a {min(b, 1):.1f}: {((c_p >= a) & (c_p < b)).mean():.0%}" for a, b in [(-1, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 1.01)]))
    out(f"   Etiquetas com nota > 0 no ml-32m por filme (média): {(R > 0).sum(axis=1).mean():.1f}; "
        f"etiquetas da IA por filme: {(M > 0).sum(axis=1).mean():.1f}")

    rng = np.random.default_rng(0)
    out(f"\nb) Clima: dos 5 filmes com maior nota da IA, quantos estão no top 10 do ml-32m (entre {len(com_ml)}).")
    out(f"   Ao acaso: {5 * 10 / len(com_ml):.2f}. Empates desfeitos ao acaso (média de 2.000 sorteios).")
    out(f"   {'etiqueta':<20}{'acerto':>8}{'filmes c/ nota ml>0':>21}{'filmes c/ etiqueta IA':>23}")
    res = []
    for tag in TAGS_CLIMA:
        j = vocab.index(tag)
        top_real = set(np.argsort(-R[:, j], kind="stable")[:10])
        validos = (R[:, j] > 0).sum()
        total = 0
        for _ in range(2000):
            ordem = np.lexsort((rng.random(len(com_ml)), -M[:, j]))
            total += len(top_real & set(ordem[:5]))
        a = total / 2000
        res.append(a)
        nota = "" if validos >= 10 else "  (menos de 10 filmes com nota no ml-32m: top 10 inclui zeros)"
        out(f"   {tag:<20}{a:>6.1f}/5{validos:>21}{int((M[:, j] > 0).sum()):>23}{nota}")
    out(f"   Média: {np.mean(res):.1f}/5")

    # Concordância por etiqueta: das vezes que a IA deu 0,6+, em quantas o ml-32m tem a etiqueta (2+ pessoas)?
    # E das vezes que o ml-32m tem a etiqueta com força (nota >= 0,05), em quantas a IA deu a etiqueta?
    out("\nc) Concordância por etiqueta (só etiquetas usadas 5+ vezes por algum dos lados):")
    out("   'IA confirmada' = quando a IA deu 0,6 ou 0,9, o ml-32m também tem a etiqueta (2+ pessoas).")
    out("   'ml lembrada'   = quando o ml-32m tem a etiqueta com nota 0,05+, a IA também deu a etiqueta.")
    out(f"   {'etiqueta':<26}{'IA confirmada':>15}{'ml lembrada':>14}")
    conc = []
    for j, tag in enumerate(vocab):
        ia_forte = M[:, j] >= 0.6
        ml_forte = R[:, j] >= 0.05
        if ia_forte.sum() + ml_forte.sum() < 5:
            continue
        conf = (R[ia_forte, j] > 0).mean() if ia_forte.any() else np.nan
        lemb = (M[ml_forte, j] > 0).mean() if ml_forte.any() else np.nan
        conc.append((tag, conf, ia_forte.sum(), lemb, ml_forte.sum()))
    conc_df = pd.DataFrame(conc, columns=["tag", "conf", "n_ia", "lemb", "n_ml"])
    for r in conc_df.sort_values("conf", ascending=False).itertuples():
        cf = "-" if pd.isna(r.conf) else f"{r.conf:.0%} de {r.n_ia}"
        lb = "-" if pd.isna(r.lemb) else f"{r.lemb:.0%} de {r.n_ml}"
        out(f"   {r.tag:<26}{cf:>15}{lb:>14}")

    # Maiores discordâncias concretas
    tit_ml = f.dropna(subset=["movieId"]).drop_duplicates("movieId").set_index(f.dropna(subset=["movieId"]).drop_duplicates("movieId").movieId.astype(int)).titulo
    disc = []
    for a, i in enumerate(com_ml):
        for j, tag in enumerate(vocab):
            if M[a, j] >= 0.9 and R[a, j] == 0:
                disc.append(("IA 0,9 / ml-32m 0", tit_ml[imdb_para_ml[i]], tag, R[a, j]))
            if M[a, j] == 0 and R[a, j] >= 0.15:
                disc.append((f"IA 0 / ml-32m {R[a, j]:.2f}", tit_ml[imdb_para_ml[i]], tag, R[a, j]))
    out(f"\nd) Discordâncias fortes: IA deu 0,9 e ninguém (2+) usou: {sum(1 for d in disc if d[0].startswith('IA 0,9'))}; "
        f"ml-32m com nota 0,15+ e a IA não deu: {sum(1 for d in disc if not d[0].startswith('IA 0,9'))}")
    for tipo in ("IA 0 /", "IA 0,9"):
        exs = [d for d in disc if d[0].startswith(tipo)]
        exs = sorted(exs, key=lambda d: -d[3])[:12]
        for d in exs:
            out(f"     {d[0]:<20} {d[1][:40]:<41} {d[2]}")

    # ------------------------------------------------------------------ 3) cobertura combinada
    out("\n" + "=" * 76)
    out("3) COBERTURA COMBINADA DOS 6.000 FILMES")
    out("=" * 76)
    par_all = t.groupby(["movieId", "tag_n"]).userId.nunique()
    ml_boa_qualquer = (par_all[par_all >= MIN_PESSOAS].groupby("movieId").size() >= ML_BOA_ETIQ)
    ml_boa_vocab = ((pessoas[pessoas.pessoas >= MIN_PESSOAS].groupby("movieId").size()) >= ML_BOA_ETIQ)
    f["fonte_tg"] = f.tem_etiqueta
    f["fonte_ml"] = f.movieId.map(ml_boa_qualquer).fillna(False).astype(bool)
    f["fonte_ml_vocab"] = f.movieId.map(ml_boa_vocab).fillna(False).astype(bool)
    f["fonte_ia"] = f.imdb_id.isin(set(ia.imdb_id))
    f["alguma"] = f.fonte_tg | f.fonte_ml | f.fonte_ia
    f["alguma_estrita"] = f.fonte_tg | f.fonte_ml_vocab | f.fonte_ia
    n = len(f)
    out(f"Tag Genome: {f.fonte_tg.sum()} | ml-32m com 5+ etiquetas (quaisquer) de 2+ pessoas: {f.fonte_ml.sum()} | "
        f"ml-32m com 5+ etiquetas DO VOCABULÁRIO de 2+ pessoas: {f.fonte_ml_vocab.sum()} | IA (piloto): {f.fonte_ia.sum()}")
    out(f"Com pelo menos uma fonte boa: {f.alguma.sum()} ({pct(f.alguma.sum(), n)}); SEM nenhuma: {(~f.alguma).sum()}")
    out(f"Versão estrita (ml-32m só conta com 5+ etiquetas do vocabulário): com fonte {f.alguma_estrita.sum()} "
        f"({pct(f.alguma_estrita.sum(), n)}); sem nenhuma: {(~f.alguma_estrita).sum()}")
    out(f"Só o ml-32m cobre (sem Tag Genome nem IA): {(f.fonte_ml & ~f.fonte_tg & ~f.fonte_ia).sum()}")

    out("\nFilmes SEM nenhuma fonte, por ano (versão principal / versão estrita):")
    sem_f = f[~f.alguma]
    sem_e = f[~f.alguma_estrita]
    anos = sorted(set(sem_e.ano_num.dropna().astype(int)))
    por_ano = []
    for a in anos:
        x, y = (sem_f.ano_num == a).sum(), (sem_e.ano_num == a).sum()
        tot = (f.ano_num == a).sum()
        por_ano.append(f"{a}: {x}/{y} de {tot}")
    for k in range(0, len(por_ano), 6):
        out("  " + "   ".join(por_ano[k:k + 6]))
    dec = sem_f.ano_num // 10 * 10
    out("Por década (principal): " + ", ".join(f"{int(d)}s: {c}" for d, c in dec.value_counts().sort_index().items()))
    sem_f.sort_values("votos", ascending=False)[["id", "imdb_id", "titulo", "titulo_original", "ano", "votos"]] \
        .to_csv("filmes_sem_fonte.csv", index=False, encoding="utf-8")
    out(f"\nLista salva em filmes_sem_fonte.csv ({len(sem_f)} filmes, mais votados primeiro). Os 10 mais votados:")
    for r in sem_f.sort_values("votos", ascending=False).head(10).itertuples():
        out(f"   {r.titulo} ({r.ano}) — {r.votos} votos")

    with open("ml32m_conferencia.txt", "w", encoding="utf-8") as arq:
        arq.write("\n".join(linhas) + "\n")
    print("\nSalvo em ml32m_conferencia.txt")


if __name__ == "__main__":
    main()
