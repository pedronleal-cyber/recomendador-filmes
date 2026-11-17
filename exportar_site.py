"""
Exporta os dados do motor T para o protótipo do site (site/data/*.json).
O site roda 100% no navegador, sem servidor, sem IA e sem login.

LICENÇA: etiquetas.json contém dados derivados do MovieLens (Tag Genome 2021, CC BY-NC 3.0; ml-32m, uso de
pesquisa). São redistribuídos sob as mesmas condições: sem uso comercial, com citações e sem sugerir endosso
da Universidade de Minnesota. Ver site/LICENCAS.html.

Uso:
    python -I exportar_site.py

Cortes que NÃO mudam os resultados:
- etiquetas: só os pares com posição > 0,5 (o motor T zera o resto) e só a maior fonte por etiqueta;
- notas como inteiros (posição × 10.000, exato porque o arquivo já tem 4 casas decimais);
- etiquetas, palavras-chave e raízes da sinopse por índice;
- índice da sinopse com as contagens brutas (o navegador refaz o TF-IDF igual ao scikit-learn).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

import motor as m
import motor_t as mt
from dicionario import DICIONARIO, GENEROS, PALAVRAS_META
from dicionario_tags import (ANTES_IDIOMA, DICIONARIO_TAGS, ESTUDIOS, IDIOMAS_T, PAISES, PALAVRAS_CHAVE_TMDB,
                             PESSOA_CONTEXTO, SEM_DADOS, TAGS_POR_TERMO)

PASTA = os.path.join("site", "data")
FONTES = ["tagenome", "ml32m", "ia"]

# Nome das etiquetas em português simples (para "Por que sugerimos")
ROTULOS_PT = {
    "feel-good": "alto astral", "heartwarming": "aquece o coração", "tear jerker": "de chorar", "sad": "triste",
    "bittersweet": "agridoce", "touching": "tocante", "poignant": "comovente", "emotional": "emocionante",
    "sentimental": "sentimental", "melancholic": "melancólico", "bleak": "desolador", "depressing": "deprimente",
    "downbeat": "final para baixo", "grim": "sombrio", "dark": "escuro / pesado", "gritty": "cru, realista",
    "disturbing": "perturbador", "creepy": "arrepiante", "eerie": "estranho e inquietante", "scary": "assustador",
    "ominous": "ameaçador", "tense": "tenso", "suspenseful": "cheio de suspense", "intense": "intenso",
    "atmospheric": "atmosférico", "claustrophobic": "claustrofóbico", "paranoid": "paranoico",
    "reflective": "reflexivo", "meditative": "contemplativo", "thought-provoking": "faz pensar",
    "cerebral": "cerebral", "philosophical": "filosófico", "funny": "engraçado", "hilarious": "hilário",
    "witty": "espirituoso", "silly": "bobinho", "goofy": "pastelão", "quirky": "excêntrico", "whimsical": "fantasioso",
    "absurd": "absurdo", "surreal": "surreal", "dreamlike": "onírico", "dark humor": "humor ácido",
    "satirical": "satírico", "cynical": "cínico", "inspirational": "inspirador", "nostalgic": "nostálgico",
    "romantic": "romântico", "cute": "fofo", "light": "leve", "visceral": "visceral", "brutal": "brutal",
    "campy": "exagerado de propósito", "friendship": "amizade", "unlikely friendships": "amizade improvável",
    "love story": "história de amor", "coming of age": "amadurecimento", "family drama": "drama familiar",
    "dysfunctional family": "família complicada", "father daughter relationship": "pai e filha",
    "parenthood": "pais e filhos", "loneliness": "solidão", "redemption": "redenção", "revenge": "vingança",
    "sacrifice": "sacrifício", "betrayal": "traição", "obsession": "obsessão", "greed": "ganância",
    "corruption": "corrupção", "justice": "justiça", "survival": "sobrevivência", "social commentary": "crítica social",
    "politics": "política", "war": "guerra", "anti-war": "contra a guerra", "racism": "racismo", "poverty": "pobreza",
    "mental illness": "saúde mental", "addiction": "vício", "life & death": "vida e morte",
    "existentialism": "existencial", "identity": "identidade", "memory": "memória", "destiny": "destino",
    "good versus evil": "bem contra o mal", "religion": "religião", "humanity": "humanidade",
    "artificial intelligence": "inteligência artificial", "technology": "tecnologia", "dystopia": "distopia",
    "end of the world": "fim do mundo", "post-apocalyptic": "pós-apocalíptico", "alien invasion": "invasão alienígena",
    "first contact": "contato com alienígenas", "time travel": "viagem no tempo", "time loop": "loop no tempo",
    "alternate reality": "realidade alternativa", "magic": "magia", "supernatural": "sobrenatural",
    "mythology": "mitologia", "fairy tale": "conto de fadas", "ghosts": "fantasmas", "zombies": "zumbis",
    "vampires": "vampiros", "monster": "monstros", "serial killer": "serial killer", "conspiracy": "conspiração",
    "organized crime": "crime organizado", "heist": "assalto / golpe", "espionage": "espionagem",
    "police investigation": "investigação policial", "courtroom": "tribunal", "prison escape": "fuga da prisão",
    "sports": "esporte", "underdog": "azarão", "music": "música", "superhero": "super-herói", "space": "espaço",
    "high school": "escola", "road trip": "pé na estrada", "small town": "cidade pequena", "christmas": "Natal",
    "animals": "animais", "true story": "história real", "twist ending": "final surpreendente",
    "twists & turns": "reviravoltas", "nonlinear": "fora de ordem", "mindfuck": "dá um nó na cabeça",
    "complex": "complexo", "enigmatic": "enigmático", "murder mystery": "mistério de assassinato",
    "chase": "perseguição", "visually stunning": "visual deslumbrante", "stylized": "estilizado",
    "character study": "estudo de personagem", "dialogue driven": "movido a diálogos",
    "multiple storylines": "várias histórias", "art house": "cinema de arte", "neo-noir": "neo-noir", "epic": "épico",
    "period piece": "de época", "slapstick": "comédia física", "parody": "paródia", "gory": "sangrento",
    "fast paced": "ritmo rápido", "slow paced": "ritmo lento", "action packed": "muita ação",
    "kids and family": "para a família", "teen movie": "adolescente", "chick flick": "comédia romântica leve",
}


def salvar(nome, obj):
    caminho = os.path.join(PASTA, nome)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    return caminho


def limpo(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(PASTA, exist_ok=True)
    f = m.carregar_filmes(mt.ARQ_FILMES_T)  # mesmo carregamento do motor T
    f["_serie_pt"] = f.titulo.map(mt.chave_serie)
    f["_serie_orig"] = f.titulo_original.map(mt.chave_serie)
    vocab = list(pd.read_csv("vocabulario_piloto.csv").tag)
    faltam = [t for t in vocab if t not in ROTULOS_PT]
    if faltam:
        sys.exit(f"Faltam rótulos em português para: {faltam}")

    # 1) Filmes (mesma ordem de linhas do filmes_v2.csv = mesma numeração do motor Python)
    campos = ["titulo", "titulo_original", "ano", "generos", "duracao_min", "nota", "votos", "sinopse",
              "streaming_assinatura_br", "idioma_original", "imdb_id", "nota_ajustada",
              "_tit", "_tit_orig", "_tit_curto", "_serie_pt", "_serie_orig", "id", "poster_path"]
    # Capas: só o endereço (poster_path); o site carrega a imagem direto do TMDB
    capas, datas_capas = {}, []
    if os.path.exists("posters.csv"):
        pc = pd.read_csv("posters.csv", dtype={"poster_path": str}, keep_default_na=False)
        capas = dict(zip(pc.id.astype(int), pc.poster_path))
        datas_capas = sorted(set(pc.data_busca))
    linhas = []
    for i in f.index:
        g = lambda c: f.at[i, c]
        linhas.append([limpo(g("titulo")), limpo(g("titulo_original")), limpo(g("ano")),
                       sorted(g("_generos")) if isinstance(g("generos"), str) else [],
                       limpo(g("duracao_min")), limpo(g("nota")), limpo(g("votos")), limpo(g("sinopse")),
                       limpo(g("streaming_assinatura_br")) or "", limpo(g("idioma_original")), limpo(g("imdb_id")),
                       float(g("_nota_ajustada")), g("_tit"), g("_tit_orig"), g("_tit_curto"),
                       g("_serie_pt"), g("_serie_orig"), int(g("id")), capas.get(int(g("id")), "") or None])
    salvar("filmes.json", {"campos": campos, "linhas": linhas})

    # 2) Palavras-chave (motor A): vocabulário + índices por filme
    vocab_kw = sorted({k for s in f._kw for k in s})
    pos_kw = {k: i for i, k in enumerate(vocab_kw)}
    salvar("palavras_chave.json", {"vocab": vocab_kw, "filmes": [sorted(pos_kw[k] for k in s) for s in f._kw]})

    # 3) Etiquetas: maior fonte por (filme, etiqueta), só posição > 0,5; [indice*3+fonte, nota*10000, ...]
    u = pd.read_csv(mt.ARQ_UNIFICADAS, dtype={"imdb_id": str})
    u = u[u.score > 0.5].copy()
    u["s"] = ((u.score - 0.5) / 0.5).clip(lower=0)
    u = u.sort_values("s", ascending=False, kind="stable").drop_duplicates(["imdb_id", "tag"])
    u["k"] = (u.score * 10000).round().astype(int)
    pos_tag = {t: i for i, t in enumerate(vocab)}
    por_imdb = {}
    for r in u.itertuples():
        por_imdb.setdefault(r.imdb_id, []).extend([pos_tag[r.tag] * 3 + FONTES.index(r.fonte), int(r.k)])
    etiq_filmes = [por_imdb.get(i, []) if isinstance(i, str) else [] for i in f.imdb_id]
    salvar("etiquetas.json", {"vocab": vocab, "rotulos_pt": [ROTULOS_PT[t] for t in vocab], "fontes": FONTES,
                              "filmes": etiq_filmes,
                              "licenca": "Dados derivados do MovieLens (GroupLens): Tag Genome 2021 (CC BY-NC 3.0) e ml-32m. Redistribuídos sob as mesmas condições: uso não comercial, com citação, sem endosso da Universidade de Minnesota. Ver LICENCAS.html."})

    # 4) Índice da sinopse: mesmo TfidfVectorizer do motor B; exporta contagens brutas e IDF
    textos = f.sinopse.map(m.preparar_texto)
    tfidf = TfidfVectorizer(sublinear_tf=True).fit(textos)
    vocab_tf = tfidf.get_feature_names_out().tolist()
    cv = CountVectorizer(vocabulary=vocab_tf)
    X = cv.transform(textos).tocsr()
    X.sort_indices()
    docs = []
    for i in range(X.shape[0]):
        ini, fim = X.indptr[i], X.indptr[i + 1]
        par = []
        for j, c in zip(X.indices[ini:fim], X.data[ini:fim]):
            par.extend([int(j), int(c)])
        docs.append(par)
    salvar("tfidf.json", {"vocab": vocab_tf, "idf": [float(x) for x in tfidf.idf_], "docs": docs})

    # 4b) v4: pessoas (só com 2+ filmes no catálogo), países, estúdios e coleções (creditos.csv, do TMDB).
    #     Mesmo índice que o motor_t.py monta (montar_creditos), para Python e JavaScript usarem os mesmos dados.
    #     Por filme: [diretores, elenco, "PAÍSES", grupos de estúdio, coleção]; pessoas por índice.
    cred = mt.montar_creditos(f, {t: j for j, t in enumerate(vocab_tf)})
    creditos_em = None
    if cred:
        creditos_em = cred["data_busca"]
        salvar("creditos.json", {
            "pessoas": cred["nomes"],
            "variantes": sorted([k, v] for k, v in cred["variantes"].items()),
            "ambiguos": sorted([k, v] for k, v in cred["ambiguos"].items()),
            "filmes": [[d, e, "|".join(p), es, col] for d, e, p, es, col in
                       zip(cred["dir"], cred["elenco"], cred["paises"], cred["estudios"], cred["colecao"])],
        })
        print(f"Pessoas indexadas (2+ filmes): {len(cred['nomes'])} | formas de nome: {len(cred['variantes'])} "
              f"| sobrenomes ambíguos: {len(cred['ambiguos'])}")
    elif os.path.exists(os.path.join(PASTA, "creditos.json")):
        os.remove(os.path.join(PASTA, "creditos.json"))

    # 4c) v6: recomendação por referência. Mesmo índice que o motor_t.py monta (montar_referencias).
    #     viz: por filme, [posição, pontos, posição, pontos...] (vizinhos do MovieLens, derivados das notas do ml-32m);
    #     rec: por filme, [posição...] (recomendados do TMDB, cache de 6 meses).
    refs = mt.montar_referencias(f)
    recomendados_em = None
    if refs:
        recomendados_em = refs["data_busca"]
        salvar("referencias.json", {
            "viz": [[x for par in v for x in par] for v in refs["viz"]],
            "rec": refs["rec"],
        })
        print(f"Referência: {sum(1 for v in refs['viz'] if v)} filmes com vizinhos do MovieLens | "
              f"{sum(1 for r in refs['rec'] if r)} com recomendados do TMDB no catálogo")
    elif os.path.exists(os.path.join(PASTA, "referencias.json")):
        os.remove(os.path.join(PASTA, "referencias.json"))

    # 5) Dicionários e regras (na mesma ordem do Python, como listas para preservar a ordem)
    config = {
        "dicionario_a": [[tema, d["padroes"], d["palavras_chave"]] for tema, d in DICIONARIO.items()],
        "generos": [[g, p] for g, p in GENEROS.items()],
        "palavras_meta": list(PALAVRAS_META),
        "dicionario_t": [[nome, e["padroes"], [[t, w] for t, w in e["tags"].items()],
                          bool(e.get("companhia", False)), bool(e.get("nota", False)),
                          [[t, w] for t, w in e.get("evita", {}).items()]]
                         for nome, e in DICIONARIO_TAGS.items()],
        "tags_por_termo": [[p, [[t, w] for t, w in tags.items()]] for p, tags in TAGS_POR_TERMO.items()],
        "palavras_vazias": sorted(m.PALAVRAS_VAZIAS),
        "palavras_de_pedido": sorted(mt.PALAVRAS_DE_PEDIDO),
        "negacoes": sorted(mt.NEGACOES), "volta_positivo": sorted(mt.VOLTA_POSITIVO),
        "servicos": [[k, v] for k, v in m.SERVICOS.items()],
        "idiomas": [[k, v] for k, v in m.IDIOMAS.items()],
        "pessoas": m.PESSOAS,
        "gatilhos_referencia": m.GATILHOS_REFERENCIA,
        "duracao_curto_padrao": m.DURACAO_CURTO_PADRAO,
        "top_n": m.TOP_N,
        "pesos": json.load(open(mt.ARQ_PESOS, encoding="utf-8")),
        "limiar_sinopse": mt.LIMIAR_SINOPSE,
        "aviso_leve": mt.AVISO_LEVE,
        "idiomas_t": IDIOMAS_T,
        # v3 (rodada de correções do estresse): mesmas regras do motor_t.py
        "ano_atual_python": mt.ANO_ATUAL, "anos_recente": mt.ANOS_RECENTE, "ano_antigo_max": mt.ANO_ANTIGO_MAX,
        "ano_moderno_min": mt.ANO_MODERNO_MIN, "nota_bem_avaliado": mt.NOTA_BEM_AVALIADO,
        "nota_aleatorio": mt.NOTA_ALEATORIO, "nota_pouco_conhecido": mt.NOTA_POUCO_CONHECIDO,
        "duracao_nao_longo": mt.DURACAO_NAO_LONGO, "duracao_longo": mt.DURACAO_LONGO,
        "peso_palavra_do_titulo": mt.PESO_PALAVRA_DO_TITULO, "min_letras_correcao": mt.MIN_LETRAS_CORRECAO,
        "mediana_votos": float(f.votos.median()),
        "gatilhos_referencia_t": mt.GATILHOS_REFERENCIA_T, "artigos_ref": mt.ARTIGOS_REF,
        "separa_ref_dupla": mt.SEPARA_REF_DUPLA, "gatilhos_dupla_t": mt.GATILHOS_DUPLA_T,
        "servicos_t": mt.SERVICOS_T, "apelidos_servico": mt.APELIDOS_SERVICO, "contexto_servico": mt.CONTEXTO_SERVICO,
        "nota_regras": mt.NOTA_REGRAS, "bem_avaliado": mt.BEM_AVALIADO,
        "duracao_ate": mt.DURACAO_ATE, "duracao_mais_de": mt.DURACAO_MAIS_DE, "hora_e_meia": mt.HORA_E_MEIA,
        "nao_longo_antes": sorted(mt.NAO_LONGO_ANTES), "nao_longo_depois": sorted(mt.NAO_LONGO_DEPOIS),
        "longo_reforco": sorted(mt.LONGO_REFORCO),
        "epoca_recente": mt.EPOCA_RECENTE, "epoca_antigo": mt.EPOCA_ANTIGO, "epoca_velho": mt.EPOCA_VELHO,
        "antigo_nao_antes": sorted(mt.ANTIGO_NAO_ANTES), "antigo_nao_depois": sorted(mt.ANTIGO_NAO_DEPOIS),
        "epoca_moderno": mt.EPOCA_MODERNO, "aleatorio": mt.ALEATORIO, "pouco_conhecido": mt.POUCO_CONHECIDO,
        "palavras_chave_tmdb": PALAVRAS_CHAVE_TMDB, "sem_dados": SEM_DADOS,
        "rotulos_palavra_chave": {"vietnam war": "Guerra do Vietnã", "world war ii": "Segunda Guerra",
                                  "black and white": "preto e branco", "alien": "alienígenas"},
        "correcoes": [list(x) for x in mt.CORRECOES_ORDENADAS], "vocab_correcao": mt.VOCAB_CORRECAO,
        "padroes_cobertura": mt.PADROES_COBERTURA,
        # v4: pessoas, países e estúdios
        "paises": PAISES, "estudios": ESTUDIOS, "antes_idioma": ANTES_IDIOMA, "pessoa_contexto": PESSOA_CONTEXTO,
        "re_nome_maiusculo": mt.RE_NOME_MAIUSCULO, "max_palavras_nome": mt.MAX_PALAVRAS_NOME,
        "aviso_pessoa_desconhecida": mt.AVISO_PESSOA_DESCONHECIDA, "aviso_sobrenome_ambiguo": mt.AVISO_SOBRENOME_AMBIGUO,
        "aviso_pessoa_sem_combinar": mt.AVISO_PESSOA_SEM_COMBINAR,
    }
    salvar("config.json", config)

    # 6) Datas dos dados (Termos do TMDB: cache de no máximo 6 meses). A data que conta é a do download
    #    do TMDB (filmes_v2.csv); a admin_local/admin.html avisa em vermelho depois de 150 dias.
    import datetime
    baixado = datetime.date.fromtimestamp(os.path.getmtime(mt.ARQ_FILMES_T)).isoformat()
    capas_em = datas_capas[0] if datas_capas else None  # a busca mais antiga é a que vence primeiro
    mais_antigo = min([d for d in (baixado, capas_em, creditos_em, recomendados_em) if d])
    salvar("versao.json", {"data_gerado_em": datetime.date.today().isoformat(), "dados_tmdb_baixados_em": baixado,
                           "posters_buscados_em": capas_em, "creditos_buscados_em": creditos_em,
                           "recomendados_buscados_em": recomendados_em,
                           "dado_tmdb_mais_antigo": mais_antigo,
                           "cache_max_dias": 180, "alerta_dias": 150})

    print("Arquivos gerados em site/data/:")
    total = 0
    for nome in sorted(os.listdir(PASTA)):
        tam = os.path.getsize(os.path.join(PASTA, nome))
        total += tam
        print(f"  {nome:<20} {tam / 1e6:6.2f} MB")
    print(f"  {'TOTAL':<20} {total / 1e6:6.2f} MB")
    print(f"Filmes: {len(f)} | pares filme-etiqueta: {len(u)} | palavras-chave: {len(vocab_kw)} | raízes da sinopse: {len(vocab_tf)}")


if __name__ == "__main__":
    main()
