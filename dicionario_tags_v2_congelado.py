"""
Dicionário do motor T: expressões em português -> etiquetas do vocabulario_piloto.csv, com peso (0,5 a 1).

- Os 64 temas do dicionario.py reaproveitam os mesmos padrões (começos de palavra, sem acento).
- EXTRAS: expressões novas, tiradas dos pedidos 1 a 90 (incluindo o jeito de pedir do autor).
  Não foram usadas expressões dos pedidos 91 a 110 (teste final).

Para conferir (etiquetas que não existem no vocabulário, pesos fora de 0,5-1):
    python dicionario_tags.py
"""
from dicionario import DICIONARIO

# Tema do dicionario.py -> etiquetas com peso
MAPA_TEMAS = {
    "chorar / emocionante": {"tear jerker": 1, "sad": 0.9, "emotional": 0.9, "touching": 0.8, "poignant": 0.7, "bittersweet": 0.6},
    "tenso": {"tense": 1, "suspenseful": 0.9, "intense": 0.8, "claustrophobic": 0.5, "paranoid": 0.5},
    "maluco / confuso": {"mindfuck": 1, "surreal": 0.9, "absurd": 0.8, "enigmatic": 0.7, "complex": 0.7, "nonlinear": 0.6, "dreamlike": 0.6},
    "pensar / reflexivo": {"thought-provoking": 1, "reflective": 1, "cerebral": 0.8, "philosophical": 0.8, "existentialism": 0.6, "meditative": 0.5},
    "leve / alto astral": {"feel-good": 1, "light": 0.9, "heartwarming": 0.7, "funny": 0.6, "cute": 0.6, "whimsical": 0.5},
    "rir / engraçado": {"funny": 1, "hilarious": 1, "witty": 0.6, "silly": 0.6, "goofy": 0.5, "slapstick": 0.5},
    "amizade": {"friendship": 1, "unlikely friendships": 0.7},
    "pessoas diferentes": {"unlikely friendships": 1},
    "solidão": {"loneliness": 1, "melancholic": 0.6, "character study": 0.5},
    "trauma": {"mental illness": 0.8, "emotional": 0.6, "redemption": 0.6, "dark": 0.5},
    "superação": {"inspirational": 1, "underdog": 0.9, "redemption": 0.6, "feel-good": 0.5},
    "perda / luto": {"life & death": 1, "sad": 0.8, "emotional": 0.7, "bittersweet": 0.6, "tear jerker": 0.6},
    "reviravolta / final inesperado": {"twist ending": 1, "twists & turns": 0.9, "mindfuck": 0.6, "enigmatic": 0.5},
    "máfia": {"organized crime": 1, "corruption": 0.5, "betrayal": 0.5},
    "assalto / golpe": {"heist": 1, "twists & turns": 0.5},
    "viagem no tempo": {"time travel": 1, "time loop": 0.9, "alternate reality": 0.6},
    "sobrevivência": {"survival": 1},
    "natureza": {"survival": 0.6, "visually stunning": 0.5, "animals": 0.5},
    "inteligência artificial": {"artificial intelligence": 1, "technology": 0.8, "humanity": 0.6},
    "o que é ser humano": {"humanity": 1, "identity": 0.8, "existentialism": 0.7, "philosophical": 0.6},
    "carros / corrida": {"chase": 1, "fast paced": 0.8, "action packed": 0.6, "sports": 0.5},
    "mulheres fortes": {"action packed": 0.5, "survival": 0.5, "revenge": 0.5},
    "guerra / soldados": {"war": 1, "anti-war": 0.7, "sacrifice": 0.5},
    "esporte": {"sports": 1, "underdog": 0.8, "inspirational": 0.6},
    "história real": {"true story": 1},
    "super-herói": {"superhero": 1, "action packed": 0.5},
    "sombrio / pesado": {"dark": 1, "bleak": 0.9, "grim": 0.8, "depressing": 0.7, "disturbing": 0.7, "gritty": 0.6, "brutal": 0.5},
    "vilão": {"good versus evil": 0.8, "dark": 0.5},
    "luta / porrada": {"action packed": 1, "brutal": 0.7, "fast paced": 0.5, "revenge": 0.5},
    "medo": {"scary": 1, "creepy": 0.9, "eerie": 0.7, "ominous": 0.6, "disturbing": 0.5},
    "susto": {"campy": 0.8, "silly": 0.5, "gory": 0.5},
    "sangue / violência": {"gory": 1, "brutal": 0.9, "visceral": 0.8},
    "criança / família": {"kids and family": 1, "cute": 0.6, "heartwarming": 0.5},
    "romance / amor": {"romantic": 1, "love story": 1, "chick flick": 0.5},
    "aventura": {"epic": 0.6, "action packed": 0.5, "mythology": 0.5},
    "espaço": {"space": 1, "first contact": 0.5},
    "alienígena": {"alien invasion": 1, "first contact": 1, "space": 0.5},
    "zumbi": {"zombies": 1, "post-apocalyptic": 0.5},
    "vampiro": {"vampires": 1},
    "fantasma / espírito": {"ghosts": 1, "supernatural": 0.9},
    "serial killer": {"serial killer": 1},
    "vingança": {"revenge": 1},
    "espionagem": {"espionage": 1},
    "prisão / fuga": {"prison escape": 1},
    "escola / adolescência": {"high school": 1, "teen movie": 0.9, "coming of age": 0.8},
    "natal": {"christmas": 1},
    "cachorro / animais": {"animals": 1},
    "magia / bruxaria": {"magic": 1, "supernatural": 0.7, "fairy tale": 0.5},
    "medieval / dragões": {"epic": 0.7, "fairy tale": 0.6, "magic": 0.6, "mythology": 0.6, "period piece": 0.5},
    "fim do mundo / distopia": {"end of the world": 1, "post-apocalyptic": 0.9, "dystopia": 0.9},
    "futuro / tecnologia": {"technology": 1, "dystopia": 0.6, "artificial intelligence": 0.5},
    "sonho / realidade / memória": {"alternate reality": 0.9, "memory": 0.9, "dreamlike": 0.8, "mindfuck": 0.6},
    "investigação": {"police investigation": 1, "murder mystery": 1},
    "conspiração / política": {"conspiracy": 1, "politics": 1, "paranoid": 0.6},
    "drogas": {"addiction": 1},
    "música / dança": {"music": 1},
    "pais e filhos": {"parenthood": 1, "father daughter relationship": 0.8, "family drama": 0.8},
    "viagem / estrada": {"road trip": 1},
    "dinossauros": {"monster": 0.6, "animals": 0.5},
    "monstros": {"monster": 1},
    "desastre": {"survival": 0.8, "end of the world": 0.7},
    "psicológico": {"mental illness": 1, "paranoid": 0.8, "mindfuck": 0.7, "disturbing": 0.6, "cerebral": 0.5},
    "traição / ciúme": {"betrayal": 1, "obsession": 0.6},
    "casamento": {"family drama": 0.6, "love story": 0.5, "romantic": 0.5},
}

# Expressões novas (pedidos 1 a 90; jeito de pedir do autor)
EXTRAS = {
    "alegre": {"padroes": ["alegre", "feliz", "pra cima", "bom humor", "animar"],
               "tags": {"feel-good": 1, "heartwarming": 0.8, "light": 0.8, "cute": 0.7, "funny": 0.6}},
    "soco no estômago": {"padroes": ["soco no estomago", "devastador", "destruidor", "acabar comigo", "me destruir"],
                         "tags": {"visceral": 1, "bleak": 1, "depressing": 0.9, "brutal": 0.8, "disturbing": 0.8,
                                  "sad": 0.8, "tear jerker": 0.6}},
    "reflexivo / pensativo": {"padroes": ["reflexiv", "pensativ", "deixe pensando", "me faca pensar", "faz pensar"],
                              "tags": {"reflective": 1, "thought-provoking": 1, "cerebral": 0.8, "philosophical": 0.7}},
    "filosófico": {"padroes": ["filosof"],
                   "tags": {"philosophical": 1, "existentialism": 0.9, "cerebral": 0.8, "thought-provoking": 0.8}},
    "ver a vida de outro jeito": {"padroes": ["enxergar a vida", "ver a vida", "outra maneira", "outro jeito", "mudar minha vida", "perspectiva"],
                                  "tags": {"thought-provoking": 1, "philosophical": 0.8, "inspirational": 0.8,
                                           "reflective": 0.8, "existentialism": 0.6, "life & death": 0.5}},
    "mundo acabando": {"padroes": ["mundo acaba", "mundo acabando", "fim dos tempos"],
                       "tags": {"end of the world": 1, "post-apocalyptic": 0.9, "dystopia": 0.7, "survival": 0.6}},
    "vidrado na tela": {"padroes": ["vidrad", "grudad", "nao conseguir parar", "eletrizante", "freneti"],
                        "tags": {"tense": 1, "intense": 1, "suspenseful": 0.9, "fast paced": 0.7, "twists & turns": 0.5}},
    "non-sense": {"padroes": ["non.?sense", "sem sentido", "esquisit"],
                  "tags": {"absurd": 1, "surreal": 1, "quirky": 0.8, "silly": 0.6, "dark humor": 0.5}},
    "clichê": {"padroes": ["cliche", "previsivel", "batido", "formulaic"],
               "tags": {"campy": 0.8, "chick flick": 0.6, "sentimental": 0.6, "silly": 0.5}},
    "jogos mentais": {"padroes": ["jogos? menta", "jogo mental", "manipula", "mind game"],
                      "tags": {"mindfuck": 1, "twists & turns": 0.8, "paranoid": 0.7, "twist ending": 0.6, "cerebral": 0.6}},
    "personagem morre": {"padroes": ["morre", "morte de", "perde alguem", "matam"],
                         "tags": {"life & death": 1, "sad": 0.8, "twist ending": 0.6, "tear jerker": 0.6, "emotional": 0.6}},
    "surpresa": {"padroes": ["pega de surpresa", "surpresa", "surpreend"],
                 "tags": {"twist ending": 1, "twists & turns": 0.8}},
    "protagonista inteligente": {"padroes": ["inteligente", "genio", "esperto"],
                                 "tags": {"cerebral": 1, "witty": 0.7, "complex": 0.6}},
    "a dois / namorada": {"padroes": ["namorad", "a dois", "casal", "date\\b"],
                          "tags": {"romantic": 0.8, "love story": 0.6, "light": 0.6, "feel-good": 0.6, "funny": 0.5}},
    "sessão em casa": {"padroes": ["pizza", "pipoca", "fim de semana", "sabado", "sexta a noite"],
                       "tags": {"feel-good": 0.8, "funny": 0.7, "light": 0.7, "action packed": 0.5, "fast paced": 0.5}},
    "terror (clima)": {"padroes": ["terror", "horror"],
                       "tags": {"scary": 0.6, "creepy": 0.6}},
    "bruxa / demônio": {"padroes": ["brux", "satan", "demoni", "demonio", "possess", "exorcis", "ocult"],
                        "tags": {"supernatural": 1, "magic": 0.8, "religion": 0.6}},
    "suspense (clima)": {"padroes": ["suspense", "thriller"],
                         "tags": {"suspenseful": 1, "tense": 0.8}},
    "ação (clima)": {"padroes": ["acao\\b"],
                     "tags": {"action packed": 0.8, "fast paced": 0.5}},
    "humor ácido": {"padroes": ["acid", "sarcas", "ironi", "cinic"],
                    "tags": {"dark humor": 1, "satirical": 0.9, "witty": 0.8, "cynical": 0.8}},
    "tribunal": {"padroes": ["tribunal", "advogad", "julgamento", "juri\\b", "promotor"],
                 "tags": {"courtroom": 1, "justice": 0.6}},
    "hackers": {"padroes": ["hacker", "hackea", "computador", "internet"],
                "tags": {"technology": 1, "conspiracy": 0.6, "artificial intelligence": 0.5}},
    "família complicada": {"padroes": ["relac\\w* complicad", "conturbad", "familia disfuncional", "briga de familia"],
                           "tags": {"dysfunctional family": 1, "family drama": 0.8}},
    "biografia": {"padroes": ["cinebiografi", "biografi"],
                  "tags": {"true story": 1, "character study": 0.6}},
    "musical": {"padroes": ["musical"],
                "tags": {"music": 1}},
    # --- Correções depois do teste final (expressões que faltaram nos pedidos 91 a 110)
    "polícia": {"padroes": ["policia", "policiais", "detetive", "investigac"],
                "tags": {"police investigation": 1, "corruption": 0.6, "neo-noir": 0.6, "organized crime": 0.5, "gritty": 0.5}},
    "corrupção": {"padroes": ["corrup", "corrupt", "propina", "suborn"],
                  "tags": {"corruption": 1, "politics": 0.6, "conspiracy": 0.6}},
    "crime sério": {"padroes": ["crime\\w* seri", "seri[oa]s?\\b", "realist"],
                    "tags": {"gritty": 1, "dark": 0.7, "neo-noir": 0.7, "character study": 0.5}},
    "aconchegante": {"padroes": ["aconcheg", "quentinho", "cobertor", "conforto", "confortavel"],
                     "tags": {"feel-good": 1, "heartwarming": 1, "light": 0.8, "whimsical": 0.6, "cute": 0.6,
                              "nostalgic": 0.6, "romantic": 0.5}},
    "desligar a cabeça": {"padroes": ["desligar a cabeca", "desligar o cerebro", "sem pensar", "nao pensar", "descansar a cabeca", "relaxar"],
                          "tags": {"light": 1, "funny": 0.8, "feel-good": 0.8, "action packed": 0.6, "silly": 0.6, "fast paced": 0.5}},
    "fotografia / bonito de ver": {"padroes": ["fotografia", "bonito de ver", "lindo de ver", "visualmente", "visual\\b", "cinematografia", "imagens lindas"],
                                   "tags": {"visually stunning": 1, "stylized": 0.8, "atmospheric": 0.7, "epic": 0.5}},
    "adrenalina": {"padroes": ["adrenalina"],
                   "tags": {"action packed": 1, "fast paced": 1, "chase": 0.8, "intense": 0.7}},
    "perseguição": {"padroes": ["persegu"],
                    "tags": {"chase": 1, "action packed": 0.8, "fast paced": 0.8}},
    "clássico": {"padroes": ["classic"],
                 "tags": {"nostalgic": 0.5},
                 "nota": True},  # também dá um empurrão aos filmes mais bem avaliados (não há etiqueta "clássico")
    "com quem vai assistir (família)": {"padroes": ["com (meu|minha|meus|minhas) (pai|mae|pais|avo|avos|filho|filha|filhos|familia)",
                                                    "com a familia", "com os pais"],
                                        "tags": {"feel-good": 0.6, "epic": 0.5, "nostalgic": 0.5},
                                        "companhia": True},  # sai do texto antes dos temas ("pai" não vira tema)
    "não só pra criança": {"padroes": ["nao (seja )?so (pra|para) crianc", "pra adulto", "adultos tambem", "todas as idades"],
                           "tags": {"witty": 0.8, "emotional": 0.7, "heartwarming": 0.6, "thought-provoking": 0.5}},
    # --- Do teste do autor no site local (não veio dos pedidos 111 a 140)
    "tédio": {"padroes": ["tedio", "entediad", "sem nada (pra|para) fazer", "matar o tempo", "passar o tempo"],
              "tags": {"light": 1, "funny": 0.9, "fast paced": 0.8, "feel-good": 0.8, "action packed": 0.7}},
}

# Filtros de idioma só do motor T (somam aos do motor A; do teste do autor no site local).
# "Asiático" = idiomas do leste, sul e sudeste da Ásia que existem no catálogo.
IDIOMAS_T = [
    ["asiatic\\w*|do oriente|oriental|orientais", ["ja", "ko", "zh", "cn", "hi", "th", "id", "te"]],
]

# Termos que costumam vir negados ("sem ser triste", "nada pesado", "que não seja meloso").
# Quando um desses aparece NEGADO, as etiquetas dele são penalizadas e deixam de contar como positivas,
# mesmo que outro termo do mesmo tema esteja positivo (ex.: "emocionante, mas sem ser triste").
TAGS_POR_TERMO = {
    "trist": {"sad": 1, "tear jerker": 0.8, "depressing": 0.8, "melancholic": 0.6},
    "deprim|depressiv": {"depressing": 1, "bleak": 0.8, "sad": 0.6},
    "pesad": {"dark": 1, "bleak": 0.9, "depressing": 0.8, "disturbing": 0.8, "brutal": 0.7, "grim": 0.7},
    "violen|violent": {"brutal": 1, "gory": 0.8, "visceral": 0.7},
    "sangue|sangrent|gore\\b": {"gory": 1, "brutal": 0.7},
    "(termin|acab)\\w* mal|final (triste|ruim)": {"downbeat": 1, "sad": 0.8, "bleak": 0.6},
    "chor": {"tear jerker": 1, "sad": 0.8},
    "assust|medo": {"scary": 1, "creepy": 0.8},
    "romanc|romantic": {"romantic": 1, "love story": 0.8, "chick flick": 0.8, "sentimental": 0.6},
    "melos|brega|meloso": {"sentimental": 1, "chick flick": 0.7},
    "lent|parad[oa]|arrastad": {"slow paced": 1},
    "confus|complicad|confund": {"complex": 1, "mindfuck": 0.8, "nonlinear": 0.7},
    "infantil|bob[oa]|bobinh": {"kids and family": 0.8, "silly": 0.8, "goofy": 0.7},
}

# Padrões de temas do dicionario.py que NÃO valem no motor T (sem mexer no dicionario.py do motor A)
PADROES_REMOVIDOS = {"tenso": ["adrenalina"]}


def montar():
    """Junta temas e extras: nome -> {"padroes": [...], "tags": {etiqueta: peso}}."""
    d = {}
    for tema, tags in MAPA_TEMAS.items():
        padroes = [p for p in DICIONARIO[tema]["padroes"] if p not in PADROES_REMOVIDOS.get(tema, [])]
        d[tema] = {"padroes": padroes, "tags": tags}
    d.update(EXTRAS)
    return d


DICIONARIO_TAGS = montar()


def conferir():
    import pandas as pd
    vocab = set(pd.read_csv("vocabulario_piloto.csv").tag)
    problemas = []
    for nome, e in DICIONARIO_TAGS.items():
        for tag, peso in e["tags"].items():
            if tag not in vocab:
                problemas.append(f"{nome}: etiqueta '{tag}' não está no vocabulário")
            if not 0.5 <= peso <= 1:
                problemas.append(f"{nome}: peso {peso} fora de 0,5-1 em '{tag}'")
    for termo, tags in TAGS_POR_TERMO.items():
        for tag, peso in tags.items():
            if tag not in vocab:
                problemas.append(f"termo negável '{termo}': etiqueta '{tag}' não está no vocabulário")
            if not 0.5 <= peso <= 1:
                problemas.append(f"termo negável '{termo}': peso {peso} fora de 0,5-1")
    faltam_temas = [t for t in DICIONARIO if t not in MAPA_TEMAS]
    usadas = {t for e in DICIONARIO_TAGS.values() for t in e["tags"]}
    print(f"{len(DICIONARIO_TAGS)} entradas ({len(MAPA_TEMAS)} temas do dicionario.py + {len(EXTRAS)} extras); "
          f"{len(usadas)} das {len(vocab)} etiquetas do vocabulário são usadas.")
    print("Temas do dicionario.py sem mapeamento:", faltam_temas or "nenhum")
    print("Problemas:", problemas or "nenhum")


if __name__ == "__main__":
    conferir()
