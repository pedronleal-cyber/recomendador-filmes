"""
ADIÇÕES AO DICIONÁRIO DO MOTOR T (rodada 2, a partir do diagnóstico de estresse).

Origem: relatorio_estresse.txt (frases pedidos_estresse.csv, #201 a #361) e o teste do autor no site local.
NÃO usa nenhuma expressão dos pedidos 111 a 140 (teste cego final, proibido para ajustes).
Todas as etiquetas abaixo existem no vocabulario_piloto.csv (o claude code deve conferir com
python dicionario_tags.py antes de aplicar).

Formato igual ao EXTRAS do dicionario_tags.py:
    "nome": {"padroes": [regex sem acento], "tags": {etiqueta: peso}, ["evita": {etiqueta: peso}], [flags]}
Campo novo opcional "evita": etiquetas que devem ser penalizadas quando a expressão aparece
(mesmo mecanismo da negação em TAGS_POR_TERMO). Se o motor ainda não tiver isso, implementar.
"""

EXTRAS_V2 = {
    # ---------- Emoções ----------
    "abraço / acolher": {"padroes": ["abrac", "acolh", "consol", "me anim"],
                         "tags": {"heartwarming": 1, "feel-good": 0.8, "touching": 0.7, "light": 0.6}},
    "estressado / cansado": {"padroes": ["estress", "cansad", "exaust", "sobrecarreg", "esgotad"],
                             "tags": {"light": 1, "feel-good": 0.8, "funny": 0.6, "cute": 0.5},
                             "evita": {"tense": 0.8, "intense": 0.8, "brutal": 0.6, "disturbing": 0.6}},
    "motivado / inspirar": {"padroes": ["motiva", "inspira", "dar uma forca", "dar um animo", "volta por cima"],
                            "tags": {"inspirational": 1, "underdog": 0.8, "feel-good": 0.7, "redemption": 0.5}},
    "saudade": {"padroes": ["saudade", "saudos", "lembranc"],
                "tags": {"nostalgic": 1, "bittersweet": 0.7, "heartwarming": 0.6, "coming of age": 0.5}},
    "calmo / tranquilo": {"padroes": ["calm[oa]", "calmin", "tranquil", "sossego", "sereno", "serena", "suave"],
                          "tags": {"light": 1, "meditative": 0.8, "feel-good": 0.7, "whimsical": 0.5, "atmospheric": 0.5},
                          "evita": {"tense": 0.9, "intense": 0.9, "scary": 0.8, "brutal": 0.7, "suspenseful": 0.6}},
    "ansioso": {"padroes": ["ansios"],
                "tags": {"light": 1, "feel-good": 0.8, "meditative": 0.6, "cute": 0.5},
                "evita": {"tense": 0.9, "intense": 0.9, "suspenseful": 0.8, "scary": 0.8}},
    "coração partido": {"padroes": ["coracao partido", "coracao quebrado", "terminei", "fim de namoro", "desilusao amorosa", "sofrendo de amor"],
                        "tags": {"sad": 1, "romantic": 0.8, "bittersweet": 0.8, "tear jerker": 0.7, "love story": 0.7, "emotional": 0.7}},
    "raiva / intenso": {"padroes": ["raiva", "odio\\b", "revoltad", "intens[oa]\\b"],
                        "tags": {"intense": 1, "brutal": 0.7, "revenge": 0.7, "visceral": 0.7, "action packed": 0.6, "gritty": 0.5}},
    "sem energia / preguiça": {"padroes": ["sem energia", "sem animo", "preguic", "moleza"],
                               "tags": {"light": 1, "feel-good": 0.8, "funny": 0.6, "cute": 0.5},
                               "evita": {"tense": 0.7, "intense": 0.7, "complex": 0.6}},
    "esperança": {"padroes": ["esperanc", "otimis", "dias melhores"],
                  "tags": {"inspirational": 1, "heartwarming": 0.8, "feel-good": 0.7, "redemption": 0.7, "survival": 0.5}},

    # ---------- Ocasiões ----------
    "primeiro encontro / dia dos namorados": {"padroes": ["primeiro encontro", "encontro romantic", "dia dos namorados"],
                                              "tags": {"romantic": 1, "love story": 0.8, "feel-good": 0.7, "light": 0.7, "funny": 0.6}},
    "galera / bagunça": {"padroes": ["galera", "com (os )?amigos", "turma", "bagunc", "zoeira", "festa\\b"],
                         "tags": {"funny": 1, "hilarious": 0.8, "silly": 0.7, "goofy": 0.6, "light": 0.6, "action packed": 0.5}},
    "festa do pijama": {"padroes": ["festa do pijama", "pijama"],
                        "tags": {"teen movie": 0.9, "funny": 0.8, "silly": 0.6, "coming of age": 0.5, "cute": 0.5}},
    "viagem / algo que prenda": {"padroes": ["aviao", "viagem longa", "que prenda", "prender", "prenda"],
                                 "tags": {"fast paced": 0.9, "suspenseful": 0.8, "twists & turns": 0.8, "action packed": 0.7, "intense": 0.6}},
    "chuva / frio": {"padroes": ["chuv", "friozinho", "dia frio", "noite fria"],
                     "tags": {"heartwarming": 0.8, "feel-good": 0.7, "atmospheric": 0.6, "romantic": 0.5, "melancholic": 0.5}},
    "de fundo / sem prestar atenção": {"padroes": ["cozinhand", "de fundo", "fazendo outra coisa", "sem prestar atencao", "passando roupa"],
                                       "tags": {"light": 1, "funny": 0.8, "feel-good": 0.7},
                                       "evita": {"complex": 0.8, "nonlinear": 0.8, "dialogue driven": 0.6, "mindfuck": 0.8}},
    "agrada a todos": {"padroes": ["todo mundo", "todos gostem", "todos goste", "agrad\\w* a todos", "unanimidade"],
                       "tags": {"feel-good": 0.8, "funny": 0.6, "epic": 0.5, "kids and family": 0.5},
                       "nota": True},

    # ---------- Modificadores de gênero ----------
    "épico": {"padroes": ["epic[oa]s?\\b", "grandios"],
              "tags": {"epic": 1, "visually stunning": 0.6, "mythology": 0.5}},
    "divertido": {"padroes": ["divertid", "diversao"],
                  "tags": {"funny": 0.9, "light": 0.9, "feel-good": 0.8, "fast paced": 0.5}},

    # ---------- Temas abstratos ----------
    "ambição / poder": {"padroes": ["ambic", "poder\\b", "poderos", "ganancia", "cobica"],
                        "tags": {"greed": 1, "corruption": 0.7, "politics": 0.7, "betrayal": 0.5, "dark": 0.5}},
    "liberdade": {"padroes": ["liberdade", "livre\\b", "libertar", "libertac"],
                  "tags": {"inspirational": 0.7, "prison escape": 0.6, "underdog": 0.5, "redemption": 0.5, "survival": 0.5}},
    "fé / religião": {"padroes": ["\\bfe\\b", "religi", "\\bdeus\\b", "espiritu", "crenca"],
                      "tags": {"religion": 1, "philosophical": 0.6, "existentialism": 0.5, "reflective": 0.5}},
    "vícios": {"padroes": ["vicio", "viciad", "drog", "alcool", "dependenc"],
               "tags": {"addiction": 1, "bleak": 0.6, "disturbing": 0.5, "depressing": 0.5}},
    "inteligência / loucura": {"padroes": ["inteligenc(?!\\w* artificial)", "brilhante", "mente brilhante"],
                               "tags": {"cerebral": 1, "mental illness": 0.5, "complex": 0.6, "witty": 0.5}},
    "juventude / rebeldia": {"padroes": ["juventud", "rebeld"],
                             "tags": {"coming of age": 1, "teen movie": 0.6, "social commentary": 0.5, "high school": 0.5}},
    "pais e filhos": {"padroes": ["pais e filhos", "pai e filho", "mae e filh", "paternidade", "maternidade", "pai solo", "mae solo"],
                      "tags": {"parenthood": 1, "family drama": 0.8, "father daughter relationship": 0.7, "emotional": 0.5}},
    "mentira / traição": {"padroes": ["mentir", "mentira", "enganad", "farsa", "hipocris"],
                          "tags": {"betrayal": 0.9, "twists & turns": 0.6, "conspiracy": 0.5, "twist ending": 0.5}},
    "justiça": {"padroes": ["justica", "injustic", "justiceir"],
                "tags": {"justice": 1, "courtroom": 0.5, "revenge": 0.5, "corruption": 0.5}},
    "situação extrema": {"padroes": ["situacao extrema", "no limite", "contra o tempo"],
                         "tags": {"survival": 1, "intense": 0.7, "tense": 0.6}},
    "cidade grande": {"padroes": ["cidade grande", "metropole", "vida urbana"],
                      "tags": {"loneliness": 0.7, "melancholic": 0.5, "character study": 0.5}},
    "amor próprio / ser diferente": {"padroes": ["amor proprio", "autoestima", "se aceitar", "aceitacao", "ser diferente"],
                                     "tags": {"identity": 1, "coming of age": 0.7, "inspirational": 0.7, "social commentary": 0.4}},
    "morte / mortalidade": {"padroes": ["sobre (a )?morte", "mortalidade", "luto\\b", "finitude"],
                            "tags": {"life & death": 1, "existentialism": 0.8, "reflective": 0.8, "sad": 0.6}},
}

# expressões que o motor deve tratar como filtro de nota ("filme topzera" = muito bem avaliado)
GIRIAS_BEM_AVALIADO = ["topzera", "top\\b", "show de bola", "da hora", "dahora", "massa\\b", "brabo", "foda", "muito bom", "excelente", "obra.?prima", "aclamad", "premiad"]

# palavras de preenchimento a ignorar (não contam como "termo não reconhecido")
PALAVRAS_VAZIAS_EXTRA = ["verdadeira", "verdadeiro", "bagulho", "coisa", "negocio", "troco", "algo", "cinema", "forte", "novo", "nova", "grande", "proprio", "propria"]

# expressão (normalizada) -> palavra-chave do campo palavras_chave do TMDB (conferir contagem no catálogo; só usar com 20+ filmes)
PALAVRAS_CHAVE_TMDB = {
    "vietna": "vietnam war",
    "segunda guerra|nazis": "world war ii",
    "preto e branco": "black and white",
    "filme mudo|cinema mudo": "silent film",
    "marvel": "marvel cinematic universe",
    "alienigen|alien\\b": "alien",
}

# erros de digitação e abreviações comuns (aplicar ANTES de procurar padrões)
CORRECOES_DIGITACAO = {
    "aksao": "acao", "acsao": "acao", "ficsao": "ficcao", "ficssao": "ficcao", "cientifica": "cientifica",
    "suspence": "suspense", "suspensse": "suspense", "comedia romantica": "comedia romantica",
    "qro": "quero", "q ro": "quero", "vc": "voce", "vcs": "voces", "pq": "porque", "tbm": "tambem", "tb": "tambem",
    "msm": "mesmo", "td": "tudo", "blz": "beleza", "pra": "para", "pro": "para o",
    "terrror": "terror", "teror": "terror", "romamce": "romance", "comdia": "comedia", "anamacao": "animacao", "animaçao": "animacao",
}

if __name__ == "__main__":
    import csv, sys
    vocab = {r["tag"] for r in csv.DictReader(open("vocabulario_piloto.csv", encoding="utf-8"))}
    ruins = []
    for nome, d in EXTRAS_V2.items():
        for campo in ("tags", "evita"):
            for t, p in d.get(campo, {}).items():
                if t not in vocab: ruins.append((nome, campo, t))
                if not (0.3 <= p <= 1): ruins.append((nome, campo, t, "peso", p))
    print("entradas:", len(EXTRAS_V2), "| problemas:", ruins if ruins else "nenhum")
