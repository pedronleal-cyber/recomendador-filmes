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
    "alegre": {"padroes": ["alegre", "feliz", "(pra|para) cima", "bom humor", "animar"],
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
    "não só pra criança": {"padroes": ["nao (seja )?so (pra|para) crianc", "(pra|para) adulto", "adultos tambem", "todas as idades"],
                           "tags": {"witty": 0.8, "emotional": 0.7, "heartwarming": 0.6, "thought-provoking": 0.5}},
    # --- Do teste do autor no site local (não veio dos pedidos 111 a 140)
    "tédio": {"padroes": ["tedio", "entediad", "sem nada (pra|para) fazer", "matar o tempo", "passar o tempo"],
              "tags": {"light": 1, "funny": 0.9, "fast paced": 0.8, "feel-good": 0.8, "action packed": 0.7}},
}

# --- Rodada 2 (v3): expressões de adicoes_dicionario_v2.py, tiradas do diagnóstico de estresse
# (pedidos_estresse.csv, só descoberta de falhas) e do teste do autor no site. NÃO usa os pedidos 111 a 140.
# Campo "evita": etiquetas penalizadas quando a expressão aparece (mesmo mecanismo da negação por termo).
# "pais e filhos" já existia como tema: as duas versões são juntadas em montar() (padrões somados, maior peso).
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

# ---------------------------------------------------------------------------
# Rodada 2 (v3): listas de adicoes_dicionario_v2.py
# ---------------------------------------------------------------------------
# Expressão (sem acento) -> palavra-chave do TMDB. Só entram as que têm 20+ filmes no catálogo
# (contagem em tabela_revisao.md). Positiva = filtro (só filmes com a palavra-chave); negada = exclui.
#   Ficaram de fora: "filme mudo|cinema mudo" -> silent film (19 filmes) e "marvel" -> marvel cinematic universe (0).
PALAVRAS_CHAVE_TMDB = [
    ["vietna", "vietnam war"],                        # 21 filmes
    ["segunda guerra|nazis", "world war ii"],         # 103 filmes
    ["preto e branco|preto-e-branco|p&b", "black and white"],  # 138 filmes
    ["alienigen|alien\\b", "alien"],                  # 146 filmes
]
# Pedidos que o catálogo não consegue atender com segurança: o motor avisa em vez de chutar
SEM_DADOS = [
    ["filmes? mud[oa]s?|cinema mudo|era muda",
     "Não consigo filtrar filmes mudos: no catálogo só 19 filmes têm essa marcação, poucos demais para confiar."],
]
# Gírias que viram filtro de nota ("filme topzera" = muito bem avaliado; nota 7,5+)
GIRIAS_BEM_AVALIADO = ["topzera", "top\\b", "show de bola", "da hora", "dahora", "massa\\b", "brabo", "foda",
                       "muito bom", "excelente", "obra.?prima", "aclamad", "premiad"]
# Palavras de preenchimento (não contam como "não reconhecidas"; ficam fora da reserva por sinopse)
PALAVRAS_VAZIAS_EXTRA = ["verdadeira", "verdadeiro", "bagulho", "coisa", "negocio", "troco", "algo", "cinema",
                         "forte", "novo", "nova", "grande", "proprio", "propria"]
# Erros de digitação e abreviações (aplicados ANTES de procurar padrões; palavra inteira)
CORRECOES_DIGITACAO = {
    "aksao": "acao", "acsao": "acao", "ficsao": "ficcao", "ficssao": "ficcao",
    "suspence": "suspense", "suspensse": "suspense",
    "qro": "quero", "q ro": "quero", "vc": "voce", "vcs": "voces", "pq": "porque", "tbm": "tambem", "tb": "tambem",
    "msm": "mesmo", "td": "tudo", "blz": "beleza", "pra": "para", "pro": "para o",
    "terrror": "terror", "teror": "terror", "romamce": "romance", "comdia": "comedia", "anamacao": "animacao",
}


# ===========================================================================
# Rodada v4: pessoas, países e estúdios (dados do TMDB em creditos.csv, gerado por buscar_creditos.py)
# ===========================================================================
# Países: [padrão, rótulo positivo, rótulo negado, códigos ISO do país de produção, idiomas de cada país].
# Um filme é do país pedido quando:
#   - foi produzido SÓ em países do grupo; ou
#   - um país do grupo está entre os de produção E o idioma original é um idioma desse país
#     (menos coprodução falada em inglês com os EUA, quando os EUA não estão no grupo: Interestelar (GB|US) não é britânico).
# Negado ("não seja francês"): sai o filme cujos países de produção são todos do grupo (ex.: só França).
# Exceção (rodada final4, etapa 0): "não seja americano" tira TODO filme com EUA (US) entre os países de produção.
# Quando a palavra vem depois de "em / língua / idioma" ("falado em francês"), vale o idioma, não o país.
_EUROPA = {"FR": ["fr"], "IT": ["it"], "DE": ["de"], "ES": ["es", "ca"], "GB": ["en"], "IE": ["en", "ga"],
           "PT": ["pt"], "NL": ["nl"], "BE": ["fr", "nl"], "SE": ["sv"], "NO": ["no", "nb", "nn"], "DK": ["da"],
           "FI": ["fi", "sv"], "IS": ["is"], "PL": ["pl"], "AT": ["de"], "CH": ["de", "fr", "it"], "CZ": ["cs"],
           "HU": ["hu"], "RO": ["ro"], "GR": ["el"], "RU": ["ru"], "SU": ["ru"]}
_LATINA = {"AR": ["es"], "MX": ["es"], "BR": ["pt"], "CL": ["es"], "CO": ["es"], "PE": ["es"], "UY": ["es"],
           "VE": ["es"], "CU": ["es"]}
_NORDICOS = {"SE": ["sv"], "NO": ["no", "nb", "nn"], "DK": ["da"], "FI": ["fi", "sv"], "IS": ["is"]}
PAISES = [
    ["latino-?american\\w*|sul-?american\\w*|latin[oa]s?\\b","filme latino-americano", "não é produção só latino-americana", _LATINA],
    ["(?<!latino-)(?<!latino )(?<!sul-)(?<!sul )(?<!norte-)(?<!futebol )american\\w*|norte-american\\w*|estadunidense\\w*"
     "|hollywood\\w*", "produção americana", "sem participação americana na produção", {"US": ["en"]}],
    ["frances\\w*", "filme francês", "não é produção só francesa", {"FR": ["fr"]}],
    ["italian\\w*", "filme italiano", "não é produção só italiana", {"IT": ["it"]}],
    ["alema\\w*", "filme alemão", "não é produção só alemã", {"DE": ["de"], "AT": ["de"]}],
    ["espanho\\w*", "filme espanhol", "não é produção só espanhola", {"ES": ["es", "ca"]}],
    ["japon\\w*", "filme japonês", "não é produção só japonesa", {"JP": ["ja"]}],
    ["sul-corean\\w*|corean\\w*", "filme coreano", "não é produção só coreana", {"KR": ["ko"]}],
    ["chines\\w*|hong kong", "filme chinês", "não é produção só chinesa", {"CN": ["zh", "cn"], "HK": ["cn", "zh"], "TW": ["zh"]}],
    ["indian[oa]s?\\b(?! jones)|bollywood", "filme indiano", "não é produção só indiana",
     {"IN": ["hi", "te", "ta", "ml", "kn", "bn", "mr", "pa"]}],
    ["argentin\\w*", "filme argentino", "não é produção só argentina", {"AR": ["es"]}],
    ["mexican\\w*", "filme mexicano", "não é produção só mexicana", {"MX": ["es"]}],
    ["nordic\\w*|escandinav\\w*", "filme nórdico", "não é produção só nórdica", _NORDICOS],
    ["suec[oa]s?\\b", "filme sueco", "não é produção só sueca", {"SE": ["sv"]}],
    ["norueg\\w*", "filme norueguês", "não é produção só norueguesa", {"NO": ["no", "nb", "nn"]}],
    ["dinamarqu\\w*", "filme dinamarquês", "não é produção só dinamarquesa", {"DK": ["da"]}],
    ["finlandes\\w*", "filme finlandês", "não é produção só finlandesa", {"FI": ["fi", "sv"]}],
    ["islandes\\w*", "filme islandês", "não é produção só islandesa", {"IS": ["is"]}],
    ["brasileir\\w*|nacional\\b|nacionais\\b", "filme brasileiro", "não é produção só brasileira", {"BR": ["pt"]}],
    ["britanic\\w*|ingles\\b|inglesa\\b|ingleses\\b|inglesas\\b", "filme britânico", "não é produção só britânica",
     {"GB": ["en"]}],
    ["irlandes\\w*", "filme irlandês", "não é produção só irlandesa", {"IE": ["en", "ga"]}],
    ["australian\\w*", "filme australiano", "não é produção só australiana", {"AU": ["en"]}],
    ["canadens\\w*", "filme canadense", "não é produção só canadense", {"CA": ["en", "fr"]}],
    ["russ[oa]s?\\b|sovietic\\w*", "filme russo", "não é produção só russa", {"RU": ["ru"], "SU": ["ru"]}],
    ["iranian\\w*", "filme iraniano", "não é produção só iraniana", {"IR": ["fa"]}],
    ["turc[oa]s?\\b", "filme turco", "não é produção só turca", {"TR": ["tr"]}],
    ["polones\\w*", "filme polonês", "não é produção só polonesa", {"PL": ["pl"]}],
    ["holandes\\w*", "filme holandês", "não é produção só holandesa", {"NL": ["nl"]}],
    ["belgas?\\b", "filme belga", "não é produção só belga", {"BE": ["fr", "nl"]}],
    ["chilen\\w*", "filme chileno", "não é produção só chilena", {"CL": ["es"]}],
    ["colombian\\w*", "filme colombiano", "não é produção só colombiana", {"CO": ["es"]}],
    ["tailandes\\w*", "filme tailandês", "não é produção só tailandesa", {"TH": ["th"]}],
    ["europe\\w*", "filme europeu", "não é produção só europeia", _EUROPA],
]
# Palavras logo antes que fazem a palavra valer como idioma, não como país ("falado em francês")
ANTES_IDIOMA = ["em", "lingua", "idioma", "audio"]

# Estúdios: [padrão, rótulo, trechos do nome da produtora no TMDB, conflita com streaming?].
# "conflita com streaming": não vale logo depois de "na / no / tem na..." ("na Disney" = streaming; "da Disney" = estúdio)
# nem antes de "+"/"plus" ("Disney+").
ESTUDIOS = [
    ["studio ghibli|estudio ghibli|ghibli", "Studio Ghibli", ["studio ghibli"], False],
    ["pixar", "Pixar", ["pixar"], False],
    ["walt disney|disney", "Disney", ["disney"], True],
    ["marvel", "Marvel", ["marvel"], False],
    ["dc comics|\\bdc\\b", "DC", ["dc comics", "dc entertainment", "dc films", "dc studios"], False],
    ["a24", "A24", ["a24"], False],
    ["dreamworks", "DreamWorks", ["dreamworks"], False],
    ["warner", "Warner Bros.", ["warner bros"], False],
    ["universal pictures|universal studios|da universal", "Universal", ["universal pictures"], False],
    ["blumhouse", "Blumhouse", ["blumhouse"], False],
    ["illumination", "Illumination", ["illumination"], False],
    ["laika", "Laika", ["laika"], False],
    ["aardman", "Aardman", ["aardman"], False],
    ["lucasfilm", "Lucasfilm", ["lucasfilm"], False],
    ["sony pictures|da sony|columbia pictures", "Sony / Columbia", ["sony pictures", "columbia pictures"], False],
    ["20th century|20th century fox|da fox", "20th Century Fox", ["20th century", "twentieth century"], False],
    ["miramax", "Miramax", ["miramax"], False],
    ["lionsgate|lions gate", "Lionsgate", ["lionsgate", "lions gate"], False],
    ["toho", "Toho", ["toho"], False],
    ["toei", "Toei", ["toei"], False],
    ["amblin", "Amblin", ["amblin"], False],
    ["studiocanal|studio canal", "StudioCanal", ["studiocanal"], False],
    ["globo filmes", "Globo Filmes", ["globo filmes"], False],
]
# Pessoas: frases que sempre anunciam um nome ("dirigido por ..."); se o nome não for reconhecido, o site avisa.
PESSOA_CONTEXTO = ("\\b(?:dirigid[oa]s? por|direcao d[eoa]|do diretor|da diretora|com o ator|com a atriz"
                   "|estrelad[oa]s? por|estrelando|atuacao d[eoa])\\s+")
# Palavras comuns do português que nunca valem como sobrenome sozinho ("domingo de preguiça" não é Colman Domingo;
# o nome completo continua valendo). Complementa a regra automática (palavra em minúscula nas sinopses).
NAO_SOBRENOME = """
domingo sabado segunda terca quarta quinta sexta feira janeiro fevereiro marco abril maio junho julho agosto
setembro outubro novembro dezembro verao inverno outono primavera natal pascoa carnaval branco branca preto preta
negro negra verde azul rosa roxo amarelo vermelho cinza dourado moreno morena bravo brava placido machado santo santa
canada cristo deus rei rainha principe sol lua mar luz paz amor vida morte noite dia chuva neve fogo terra pedra
ferro flores campos rios monte vale rocha costa castelo guerra filho filha leao lobo cruz cordeiro coelho raposa
paris londres roma alaska indiana toquio berlim madri madrid lisboa veneza florenca milao napoles viena praga moscou
dublin chicago boston texas vegas brooklyn manhattan harlem detroit denver dakota montana nevada georgia carolina
virginia florida dallas houston jersey york hudson israel lima santiago havana cuba bahia amazonas sahara sydney
melbourne toronto montreal quebec cairo bangkok tibet everest sicilia toscana holanda irlanda escocia gales
normandia provence monaco marrocos africa asia europa america brasil mexico india china japao coreia hollywood
""".split()  # v7: lugares nunca valem como sobrenome sozinhos ("romance em Paris" não é Jerry Paris)
# Partículas de sobrenome ("Guillermo del Toro" -> sobrenome "del toro")
PARTICULAS_NOME = ["de", "del", "da", "di", "do", "dos", "das", "van", "von", "le", "la", "du", "der", "den", "mac", "st"]


# >>> EXTRAS_V8 (gerado por expressoes.py construir; não editar à mão)
# Uma entrada por etiqueta, com os jeitos de pedir do conjunto de TREINO (80%) de expressoes_etiquetas.csv,
# escritos pelo Claude (offline). Os padrões de cada etiqueta vão juntos numa só expressão regular.
EXTRAS_V8 = {
    'expr: absurd': {"padroes": ['what[\\s-]+the[\\s-]+fuck|porra[\\s-]+e[\\s-]+essa|loucura[\\s-]+total|muito[\\s-]+doido|muito[\\s-]+louco|sem[\\s-]+sentido|non[\\s-]+sense|loucurada|maluquice|doideira|nonsense|absurda|absurdo|bizarro|viajado|absurd|insano|maluco|surto'], "tags": {'absurd': 1.0}},
    'expr: action packed': {"padroes": ['acao[\\s-]+desenfreada[\\s-]+do[\\s-]+inicio[\\s-]+ao[\\s-]+fim|acao[\\s-]+do[\\s-]+comeco[\\s-]+ao[\\s-]+fim|tiro[\\s-]+porrada[\\s-]+e[\\s-]+bomba|sequencias[\\s-]+de[\\s-]+acao|acao[\\s-]+sem[\\s-]+parar|cenas[\\s-]+de[\\s-]+luta|acao[\\s-]+frenetica|action[\\s-]+packed|muita[\\s-]+acao|acao[\\s-]+pura|acao[\\s-]+raiz|explosoes|explosao|tiroteio|lutas|tiros'], "tags": {'action packed': 1.0}},
    'expr: addiction': {"padroes": ['clinica[\\s-]+de[\\s-]+reabilitacao|usuario[\\s-]+de[\\s-]+drogas|vicio[\\s-]+em[\\s-]+drogas|reabilitacao|abstinencia|dependencia|alcoolatra|alcoolismo|traficante|addiction|overdose|chapado|cocaina|heroina|recaida|viciado|bebida|drogas|junkie|rehab'], "tags": {'addiction': 1.0}},
    'expr: alien invasion': {"padroes": ['invasores[\\s-]+do[\\s-]+espaco|invasao[\\s-]+extraterrestre|alienigenas[\\s-]+atacando|homenzinhos[\\s-]+verdes|invasao[\\s-]+alienigena|naves[\\s-]+no[\\s-]+ceu|discos[\\s-]+voadores|nave[\\s-]+alienigena|alien[\\s-]+invasion|contato[\\s-]+hostil|disco[\\s-]+voador|extraterrestres|extraterrestre|alienigenas|alienigena|marcianos|ovnis'], "tags": {'alien invasion': 1.0}},
    'expr: alternate reality': {"padroes": ['e[\\s-]+se[\\s-]+a[\\s-]+realidade[\\s-]+fosse[\\s-]+outra|linha[\\s-]+do[\\s-]+tempo[\\s-]+alternativa|portal[\\s-]+pra[\\s-]+outro[\\s-]+mundo|vivemos[\\s-]+numa[\\s-]+simulacao|realidade[\\s-]+alternativa|realidades[\\s-]+paralelas|universos[\\s-]+paralelos|realidade[\\s-]+paralela|alternate[\\s-]+reality|dimensao[\\s-]+paralela|realidade[\\s-]+virtual|universo[\\s-]+paralelo|outras[\\s-]+dimensoes|mundo[\\s-]+invertido|mundo[\\s-]+paralelo|outra[\\s-]+dimensao|outro[\\s-]+eu|multiverso|dimensoes|portal'], "tags": {'alternate reality': 1.0}},
    'expr: animals': {"padroes": ['bichinho[\\s-]+de[\\s-]+estimacao|animal[\\s-]+de[\\s-]+estimacao|animal[\\s-]+morrendo|fazendinha|cachorros|cachorro|golfinho|animais|animals|cavalos|bichos|cavalo|bicho|gatos'], "tags": {'animals': 1.0}},
    'expr: anti-war': {"padroes": ['guerra[\\s-]+nao[\\s-]+tem[\\s-]+vencedores|lado[\\s-]+humano[\\s-]+da[\\s-]+guerra|estresse[\\s-]+pos[\\s-]+traumatico|cicatrizes[\\s-]+da[\\s-]+guerra|criancas[\\s-]+na[\\s-]+guerra|guerra[\\s-]+sem[\\s-]+sentido|absurdo[\\s-]+da[\\s-]+guerra|critica[\\s-]+a[\\s-]+guerra|horror[\\s-]+da[\\s-]+guerra|trauma[\\s-]+de[\\s-]+guerra|veterano[\\s-]+traumatizado|civis[\\s-]+na[\\s-]+guerra|volta[\\s-]+da[\\s-]+guerra|war[\\s-]+is[\\s-]+hell|anti[\\s-]+guerra|anti[\\s-]+war|pela[\\s-]+paz|antiguerra|pacifista'], "tags": {'anti-war': 1.0}},
    'expr: art house': {"padroes": ['lento[\\s-]+e[\\s-]+artistico|cinema[\\s-]+de[\\s-]+autor|europeu[\\s-]+de[\\s-]+arte|cinema[\\s-]+de[\\s-]+arte|cinema[\\s-]+experimental|cinema[\\s-]+alternativo|cinema[\\s-]+autoral|cinema[\\s-]+europeu|art[\\s-]+house|experimental|independente|artistico|arthouse|cinefilo|festival|autoral|cannes'], "tags": {'art house': 1.0}},
    'expr: artificial intelligence': {"padroes": ['rebeliao[\\s-]+das[\\s-]+maquinas|robo[\\s-]+com[\\s-]+sentimentos|maquinas[\\s-]+que[\\s-]+pensam|maquina[\\s-]+que[\\s-]+sente|computador[\\s-]+consciente|assistente[\\s-]+virtual|maquina[\\s-]+consciente|singularidade|replicante|algoritmo|androides|sintetico|androide|ciborgue|maquinas|chatbot|skynet'], "tags": {'artificial intelligence': 1.0}},
    'expr: atmospheric': {"padroes": ['transportar[\\s-]+pra[\\s-]+outro[\\s-]+lugar|ambientacao[\\s-]+caprichada|ambientacao[\\s-]+incrivel|ambientacao[\\s-]+lenta|clima[\\s-]+envolvente|atmosfera[\\s-]+densa|vibe[\\s-]+noturna|contemplativo|ambientacao|atmosferico|transportar|contemplar|atmosfera|climatico|paisagens|sensorial|imersivo|imersao|climao'], "tags": {'atmospheric': 1.0}},
    'expr: betrayal': {"padroes": ['golpe[\\s-]+do[\\s-]+melhor[\\s-]+amigo|apunhalada[\\s-]+pelas[\\s-]+costas|facada[\\s-]+nas[\\s-]+costas|puxada[\\s-]+de[\\s-]+tapete|double[\\s-]+cross|amigo[\\s-]+falso|jogo[\\s-]+duplo|adulterio|falsidade|trairagem|betrayal|rasteira|traicao|traidor|amante|chifre|traido|vibora|corno|judas|trair'], "tags": {'betrayal': 1.0}},
    'expr: bittersweet': {"padroes": ['meio[\\s-]+feliz[\\s-]+meio[\\s-]+triste|alegria[\\s-]+com[\\s-]+tristeza|felicidade[\\s-]+melancolica|triste[\\s-]+mas[\\s-]+bonito|vitoria[\\s-]+com[\\s-]+perda|doido[\\s-]+mas[\\s-]+bonito|bonito[\\s-]+e[\\s-]+triste|riso[\\s-]+e[\\s-]+lagrima|amargo[\\s-]+e[\\s-]+doce|nostalgia[\\s-]+agridoce|rir[\\s-]+e[\\s-]+chorar|chorar[\\s-]+sorrindo|sorrir[\\s-]+chorando|comedia[\\s-]+triste|final[\\s-]+agridoce|sabor[\\s-]+agridoce|saudade[\\s-]+boa|bittersweet|agridoce|dramedia|dramedy'], "tags": {'bittersweet': 1.0}},
    'expr: bleak': {"padroes": ['fadado[\\s-]+ao[\\s-]+fracasso|nada[\\s-]+termina[\\s-]+bem|sombrio[\\s-]+e[\\s-]+triste|mundo[\\s-]+sem[\\s-]+saida|sem[\\s-]+final[\\s-]+feliz|cinza[\\s-]+e[\\s-]+frio|vazio[\\s-]+existencial|miseria[\\s-]+humana|sem[\\s-]+esperanca|so[\\s-]+desgraca|desesperancoso|desesperanca|pessimismo|pessimista|desolacao|desolador|desgraca|hopeless|niilista|bleak'], "tags": {'bleak': 1.0}},
    'expr: brutal': {"padroes": ['cruel[\\s-]+e[\\s-]+violento|banho[\\s-]+de[\\s-]+sangue|violencia[\\s-]+grafica|violencia[\\s-]+pesada|muita[\\s-]+violencia|muito[\\s-]+violento|ultraviolento|carnificina|quebradeira|sanguinario|sem[\\s-]+do|porradaria|truculento|violencia|massacre|violento|matanca|brutal|sangue'], "tags": {'brutal': 1.0}},
    'expr: campy': {"padroes": ['so[\\s-]+bad[\\s-]+it[\\s-]+s[\\s-]+good|atuacao[\\s-]+canastrona|exageradissimo|tranqueira|canastrao|exagerado|breguice|caricato|trashzao|galhofa|cafona|kitsch|campy|tosco|trash'], "tags": {'campy': 1.0}},
    'expr: cerebral': {"padroes": ['queimar[\\s-]+os[\\s-]+neuronios|complexo[\\s-]+de[\\s-]+pensar|fritar[\\s-]+o[\\s-]+cerebro|usar[\\s-]+a[\\s-]+cabeca|cerebro[\\s-]+fritando|cult[\\s-]+intelectual|queimar[\\s-]+neuronio|prestar[\\s-]+atencao|exige[\\s-]+atencao|quebra[\\s-]+cabeca|mind[\\s-]+bending|intelectual|raciocinio|cabecudo|cerebral|logica|puzzle|heady'], "tags": {'cerebral': 1.0}},
    'expr: character study': {"padroes": ['mente[\\s-]+de[\\s-]+um[\\s-]+personagem|retrato[\\s-]+de[\\s-]+uma[\\s-]+pessoa|mergulho[\\s-]+num[\\s-]+personagem|estudo[\\s-]+de[\\s-]+personagem|drama[\\s-]+de[\\s-]+personagem|protagonista[\\s-]+complexo|personagem[\\s-]+complexo|personagem[\\s-]+marcante|atuacao[\\s-]+impecavel|one[\\s-]+man[\\s-]+show|atuacao[\\s-]+marcante|character[\\s-]+study|ator[\\s-]+brilhando|grande[\\s-]+atuacao|retrato[\\s-]+intimo|atuacao[\\s-]+forte|personagem[\\s-]+so|personagem|intimista'], "tags": {'character study': 1.0}},
    'expr: chase': {"padroes": ['fugir[\\s-]+de[\\s-]+todo[\\s-]+mundo|perseguicao[\\s-]+de[\\s-]+carro|perseguido[\\s-]+por[\\s-]+todos|fugindo[\\s-]+da[\\s-]+policia|perseguicao[\\s-]+eletrizante|cacador[\\s-]+e[\\s-]+presa|fuga[\\s-]+alucinante|on[\\s-]+the[\\s-]+run|correndo[\\s-]+atras|cacada[\\s-]+humana|sendo[\\s-]+cacado|corre[\\s-]+corre|em[\\s-]+fuga|correria|fugindo|manhunt|cacada|chase'], "tags": {'chase': 1.0}},
    'expr: chick flick': {"padroes": ['comedia[\\s-]+romantica[\\s-]+feminina|ver[\\s-]+com[\\s-]+as[\\s-]+amigas|casamento[\\s-]+e[\\s-]+amigas|comedia[\\s-]+de[\\s-]+amigas|noite[\\s-]+das[\\s-]+garotas|sessao[\\s-]+das[\\s-]+amigas|noite[\\s-]+de[\\s-]+meninas|filminho[\\s-]+romantico|moda[\\s-]+e[\\s-]+amor|chick[\\s-]+flick|girls[\\s-]+night|pras[\\s-]+amigas|chick[\\s-]+lit|mulherzinha|acucarado|madrinhas|garotas|amigas'], "tags": {'chick flick': 1.0}},
    'expr: christmas': {"padroes": ['festas[\\s-]+de[\\s-]+fim[\\s-]+de[\\s-]+ano|presentes[\\s-]+de[\\s-]+natal|vespera[\\s-]+de[\\s-]+natal|arvore[\\s-]+de[\\s-]+natal|clima[\\s-]+de[\\s-]+natal|magia[\\s-]+do[\\s-]+natal|ceia[\\s-]+de[\\s-]+natal|espirito[\\s-]+natalino|inverno[\\s-]+natalino|fim[\\s-]+de[\\s-]+ano|papai[\\s-]+noel|polo[\\s-]+norte|dezembro|natalina|duendes|holiday|natal|renas'], "tags": {'christmas': 1.0}},
    'expr: claustrophobic': {"padroes": ['falta[\\s-]+de[\\s-]+ar|single[\\s-]+location|elevador[\\s-]+preso|espaco[\\s-]+fechado|lugar[\\s-]+fechado|so[\\s-]+cenario|claustrofobico|claustrophobic|claustrofobia|confinamento|soterrado|sufocante|trancados|apertado|trancado|caverna|sufocar|bunker'], "tags": {'claustrophobic': 1.0}},
    'expr: coming of age': {"padroes": ['passagem[\\s-]+pra[\\s-]+vida[\\s-]+adulta|deixar[\\s-]+de[\\s-]+ser[\\s-]+crianca|encontrar[\\s-]+a[\\s-]+si[\\s-]+mesmo|descobrir[\\s-]+quem[\\s-]+sou|rito[\\s-]+de[\\s-]+passagem|crise[\\s-]+dos[\\s-]+vinte|anos[\\s-]+de[\\s-]+escola|coming[\\s-]+of[\\s-]+age|verao[\\s-]+inesquecivel|juventude[\\s-]+perdida|sair[\\s-]+de[\\s-]+casa|primeiro[\\s-]+emprego|ultimo[\\s-]+verao|virar[\\s-]+adulto|amadurecimento|adolescente|descobertas|crescendo|formatura|crescer'], "tags": {'coming of age': 1.0}},
    'expr: complex': {"padroes": ['assistir[\\s-]+de[\\s-]+novo[\\s-]+pra[\\s-]+entender|precisar[\\s-]+ver[\\s-]+duas[\\s-]+vezes|dificil[\\s-]+de[\\s-]+acompanhar|dificil[\\s-]+de[\\s-]+entender|cheio[\\s-]+de[\\s-]+detalhes|denso[\\s-]+e[\\s-]+complexo|historia[\\s-]+complexa|roteiro[\\s-]+elaborado|exige[\\s-]+raciocinio|enredo[\\s-]+complexo|varias[\\s-]+camadas|nada[\\s-]+obvio|complicadinho|multicamadas|labirintico|sofisticado|complicado|detalhista|intrincado|complexa|complexo'], "tags": {'complex': 1.0}},
    'expr: conspiracy': {"padroes": ['conspiracao[\\s-]+do[\\s-]+governo|eles[\\s-]+estao[\\s-]+escondendo|nova[\\s-]+ordem[\\s-]+mundial|segredo[\\s-]+do[\\s-]+governo|verdade[\\s-]+escondida|governo[\\s-]+esconde|trama[\\s-]+politica|acobertamento|cover[\\s-]+up|whistleblower|encobrimento|conspiracao|denunciante|conspiracy|illuminati|vazamento|complo|dossie'], "tags": {'conspiracy': 1.0}},
    'expr: corruption': {"padroes": ['trafico[\\s-]+de[\\s-]+influencia|lavagem[\\s-]+de[\\s-]+dinheiro|desvio[\\s-]+de[\\s-]+dinheiro|mafia[\\s-]+no[\\s-]+governo|politico[\\s-]+corrupto|policia[\\s-]+corrupta|dinheiro[\\s-]+sujo|juiz[\\s-]+comprado|sistema[\\s-]+podre|tudo[\\s-]+comprado|caixa[\\s-]+dois|corruption|rachadinha|corrupcao|mensalao|subornar|conluio|propina|bribe'], "tags": {'corruption': 1.0}},
    'expr: courtroom': {"padroes": ['inocente[\\s-]+ou[\\s-]+culpado|drama[\\s-]+de[\\s-]+tribunal|sessao[\\s-]+do[\\s-]+juri|julgamento[\\s-]+famoso|processo[\\s-]+judicial|caso[\\s-]+judicial|julgamento|promotoria|audiencia|courtroom|advogado|promotor|tribunal|acusado|objecao'], "tags": {'courtroom': 1.0}},
    'expr: creepy': {"padroes": ['esquisito[\\s-]+e[\\s-]+assustador|estranhamente[\\s-]+assustador|bonecos[\\s-]+assustadores|frio[\\s-]+na[\\s-]+espinha|vizinho[\\s-]+estranho|pele[\\s-]+arrepiada|casa[\\s-]+estranha|dar[\\s-]+calafrio|dar[\\s-]+arrepio|creepypasta|sinistrinho|arrepiante|calafrios|arrepios|calafrio|sinistro|arrepio|medonho|uncanny|creepy'], "tags": {'creepy': 1.0}},
    'expr: cute': {"padroes": ['apertar[\\s-]+de[\\s-]+tao[\\s-]+fofo|bichinhos[\\s-]+fofos|bichinho[\\s-]+fofo|muito[\\s-]+fofo|bonitinho|delicinha|fofissimo|adoravel|filhotes|fofinho|fofura|kawaii|pureza|meigo'], "tags": {'cute': 1.0}},
    'expr: cynical': {"padroes": ['dinheiro[\\s-]+acima[\\s-]+de[\\s-]+tudo|sem[\\s-]+fe[\\s-]+na[\\s-]+humanidade|anti[\\s-]+heroi[\\s-]+cinico|tudo[\\s-]+e[\\s-]+interesse|sarcasmo[\\s-]+amargo|ninguem[\\s-]+presta|sem[\\s-]+ilusoes|amargurado|calculista|desiludido|hipocrisia|descrenca|descrente|desilusao|hipocrita|cinismo|cynical|egoista|amargo|cinico'], "tags": {'cynical': 1.0}},
    'expr: dark': {"padroes": ['sombrio[\\s-]+de[\\s-]+verdade|sujo[\\s-]+e[\\s-]+sombrio|atmosfera[\\s-]+pesada|mente[\\s-]+perturbada|moralmente[\\s-]+cinza|clima[\\s-]+pesado|lado[\\s-]+obscuro|lado[\\s-]+negro|vibe[\\s-]+dark|darkzao|obscuro|pesadao|sombrio|trevoso|gotico|denso'], "tags": {'dark': 1.0}},
    'expr: dark humor': {"padroes": ['rir[\\s-]+do[\\s-]+que[\\s-]+nao[\\s-]+devia|humor[\\s-]+politicamente[\\s-]+incorreto|sem[\\s-]+limites[\\s-]+no[\\s-]+humor|sarcastico[\\s-]+e[\\s-]+sombrio|cinico[\\s-]+e[\\s-]+engracado|politicamente[\\s-]+incorreto|humor[\\s-]+sem[\\s-]+nocao|rir[\\s-]+da[\\s-]+desgraca|comedia[\\s-]+morbida|comedia[\\s-]+sombria|morte[\\s-]+engracada|gallows[\\s-]+humor|humor[\\s-]+doentio|humor[\\s-]+morbido|black[\\s-]+comedy|piada[\\s-]+pesada|dark[\\s-]+comedy|humor[\\s-]+acido|humor[\\s-]+negro|dark[\\s-]+humor'], "tags": {'dark humor': 1.0}},
    'expr: depressing': {"padroes": ['acabar[\\s-]+com[\\s-]+meu[\\s-]+dia|angustiante[\\s-]+e[\\s-]+triste|sofrimento[\\s-]+sem[\\s-]+fim|derrubar[\\s-]+o[\\s-]+astral|afundar[\\s-]+na[\\s-]+bad|fundo[\\s-]+do[\\s-]+poco|tristeza[\\s-]+profunda|deixar[\\s-]+deprimido|deixar[\\s-]+arrasado|ficar[\\s-]+deprimido|depressao[\\s-]+pura|baixo[\\s-]+astral|bad[\\s-]+pesada|depressing|depressivo|deprimente|arrasador|deprimir|downer|depre'], "tags": {'depressing': 1.0}},
    'expr: destiny': {"padroes": ['caminhos[\\s-]+que[\\s-]+se[\\s-]+cruzam|encontro[\\s-]+do[\\s-]+destino|nasceu[\\s-]+pra[\\s-]+isso|sorte[\\s-]+e[\\s-]+destino|missao[\\s-]+de[\\s-]+vida|tinha[\\s-]+que[\\s-]+ser|estava[\\s-]+escrito|vidas[\\s-]+cruzadas|coincidencias|predestinado|escolhido|profecia|destino|destiny|acaso|carma|karma'], "tags": {'destiny': 1.0}},
    'expr: dialogue driven': {"padroes": ['parece[\\s-]+peca[\\s-]+de[\\s-]+teatro|baseado[\\s-]+em[\\s-]+dialogos|personagens[\\s-]+conversando|cheio[\\s-]+de[\\s-]+dialogos|dialogos[\\s-]+inteligentes|discussao[\\s-]+acalorada|gente[\\s-]+conversando|dialogos[\\s-]+longos|dialogue[\\s-]+driven|conversa[\\s-]+longa|muita[\\s-]+conversa|muito[\\s-]+dialogo|peca[\\s-]+filmada|so[\\s-]+conversa|bate[\\s-]+papo|verborragico|conversa|dialogo|falacao|teatral|talky'], "tags": {'dialogue driven': 1.0}},
    'expr: disturbing': {"padroes": ['precisar[\\s-]+de[\\s-]+estomago|dificil[\\s-]+de[\\s-]+assistir|deixar[\\s-]+desconfortavel|incomoda[\\s-]+muito|desconfortavel|mal[\\s-]+estar|traumatizante|perturbadora|perturbador|traumatizar|disturbing|perturbar|repulsivo|chocante|incomodo|doentio|nojento|chocar|trauma'], "tags": {'disturbing': 1.0}},
    'expr: downbeat': {"padroes": ['ritmo[\\s-]+arrastado[\\s-]+e[\\s-]+triste|final[\\s-]+aberto[\\s-]+e[\\s-]+triste|contido[\\s-]+e[\\s-]+triste|cansado[\\s-]+da[\\s-]+vida|clima[\\s-]+pra[\\s-]+baixo|morno[\\s-]+e[\\s-]+triste|tom[\\s-]+pra[\\s-]+baixo|final[\\s-]+frustrante|tom[\\s-]+melancolico|final[\\s-]+amargo|sem[\\s-]+alegria|sem[\\s-]+brilho|tom[\\s-]+sobrio|tom[\\s-]+baixo|desencanto|frustracao|desanimo|downbeat|apagado|sobrio'], "tags": {'downbeat': 1.0}},
    'expr: dreamlike': {"padroes": ['sonho[\\s-]+dentro[\\s-]+de[\\s-]+sonho|delicado[\\s-]+e[\\s-]+estranho|atmosfera[\\s-]+de[\\s-]+sonho|poetico[\\s-]+e[\\s-]+visual|como[\\s-]+um[\\s-]+sonho|fantasia[\\s-]+onirica|sonhar[\\s-]+acordado|dream[\\s-]+logic|dreamlike|flutuante|hipnotico|ethereal|ilusorio|nebuloso|flutuar|onirico|etereo|ilusao|sonhos|nevoa|sonho'], "tags": {'dreamlike': 1.0}},
    'expr: dysfunctional family': {"padroes": ['natal[\\s-]+em[\\s-]+familia[\\s-]+desastroso|familia[\\s-]+que[\\s-]+se[\\s-]+odeia|parentes[\\s-]+insuportaveis|dysfunctional[\\s-]+family|familia[\\s-]+disfuncional|familia[\\s-]+problematica|familia[\\s-]+complicada|familia[\\s-]+excentrica|familia[\\s-]+baguncada|familia[\\s-]+esquisita|jantar[\\s-]+desastroso|familia[\\s-]+quebrada|parentes[\\s-]+malucos|caos[\\s-]+familiar|familia[\\s-]+louca|familia[\\s-]+zoada|lar[\\s-]+desfeito|pais[\\s-]+toxicos|mae[\\s-]+toxica|pai[\\s-]+toxico'], "tags": {'dysfunctional family': 1.0}},
    'expr: dystopia': {"padroes": ['rebeliao[\\s-]+contra[\\s-]+o[\\s-]+sistema|sociedade[\\s-]+perfeita[\\s-]+falsa|governo[\\s-]+controla[\\s-]+tudo|sociedade[\\s-]+controlada|governo[\\s-]+totalitario|sociedade[\\s-]+distopica|futuro[\\s-]+autoritario|vigilancia[\\s-]+total|controle[\\s-]+mental|estado[\\s-]+policial|futuro[\\s-]+opressor|regime[\\s-]+opressor|futuro[\\s-]+sombrio|utopia[\\s-]+falsa|big[\\s-]+brother|totalitarismo|cyberpunk|distopico|dystopian|distopia|dystopia'], "tags": {'dystopia': 1.0}},
    'expr: eerie': {"padroes": ['misterioso[\\s-]+e[\\s-]+estranho|onirico[\\s-]+e[\\s-]+assustador|nao[\\s-]+esta[\\s-]+certo|atmosfera[\\s-]+estranha|sobrenatural[\\s-]+sutil|errado[\\s-]+no[\\s-]+ar|espacos[\\s-]+liminares|sensacao[\\s-]+estranha|silencio[\\s-]+estranho|lugar[\\s-]+abandonado|vazio[\\s-]+assustador|cidade[\\s-]+fantasma|clima[\\s-]+estranho|fantasmagorico|inquietante|abandonado|assombrado|estranho|liminar|neblina|quieto'], "tags": {'eerie': 1.0}},
    'expr: emotional': {"padroes": ['emocao[\\s-]+do[\\s-]+comeco[\\s-]+ao[\\s-]+fim|montanha[\\s-]+russa[\\s-]+de[\\s-]+emocoes|mexer[\\s-]+com[\\s-]+os[\\s-]+sentimentos|montanha[\\s-]+russa[\\s-]+emocional|roller[\\s-]+coaster[\\s-]+emocional|intenso[\\s-]+de[\\s-]+sentimentos|carregado[\\s-]+de[\\s-]+emocao|cortar[\\s-]+o[\\s-]+coracao|cheio[\\s-]+de[\\s-]+emocao|flor[\\s-]+da[\\s-]+pele|carga[\\s-]+emocional|drama[\\s-]+emocional|emocoes[\\s-]+fortes|muito[\\s-]+emotivo|sentir[\\s-]+tudo|sentimentalismo|dramalhao|emocional|emotional|emotivo|emocao'], "tags": {'emotional': 1.0}},
    'expr: end of the world': {"padroes": ['ultimo[\\s-]+dia[\\s-]+na[\\s-]+terra|fim[\\s-]+da[\\s-]+humanidade|mundo[\\s-]+vai[\\s-]+acabar|mundo[\\s-]+em[\\s-]+perigo|acabar[\\s-]+o[\\s-]+mundo|catastrofe[\\s-]+global|planeta[\\s-]+morrendo|pandemia[\\s-]+mortal|colapso[\\s-]+global|mundo[\\s-]+acabando|virus[\\s-]+mortal|apocaliptico|cataclismo|catastrofe|asteroide|pandemia|meteoro|cometa'], "tags": {'end of the world': 1.0}},
    'expr: enigmatic': {"padroes": ['aberto[\\s-]+a[\\s-]+interpretacoes|perguntas[\\s-]+sem[\\s-]+resposta|cheio[\\s-]+de[\\s-]+misterio|cheio[\\s-]+de[\\s-]+simbolos|cheio[\\s-]+de[\\s-]+enigmas|deixa[\\s-]+duvidas|sem[\\s-]+respostas|final[\\s-]+aberto|indecifravel|ambiguidade|enigmatico|misteriosa|misterioso|criptico|cryptic|enigmas|enigma'], "tags": {'enigmatic': 1.0}},
    'expr: epic': {"padroes": ['larger[\\s-]+than[\\s-]+life|batalhas[\\s-]+enormes|epico[\\s-]+historico|aventura[\\s-]+epica|cenas[\\s-]+gigantes|jornada[\\s-]+epica|grandiosidade|superproducao|blockbuster|espetaculo|monumental|grandioso|trilogia|filmaco|epicos|filmao|epico|sagas'], "tags": {'epic': 1.0}},
    'expr: espionage': {"padroes": ['agencia[\\s-]+de[\\s-]+inteligencia|operacao[\\s-]+secreta|servico[\\s-]+secreto|agente[\\s-]+secreto|missao[\\s-]+secreta|agente[\\s-]+duplo|contraespionagem|espionagem|espionage|codinome|disfarce|espionar|espioes|espiao|espia'], "tags": {'espionage': 1.0}},
    'expr: existentialism': {"padroes": ['crise[\\s-]+de[\\s-]+meia[\\s-]+idade|sentido[\\s-]+da[\\s-]+existencia|liberdade[\\s-]+e[\\s-]+angustia|falta[\\s-]+de[\\s-]+proposito|por[\\s-]+que[\\s-]+existimos|crise[\\s-]+dos[\\s-]+trinta|absurdo[\\s-]+da[\\s-]+vida|angustia[\\s-]+existencial|solidao[\\s-]+existencial|existential[\\s-]+crisis|crise[\\s-]+existencial|tedio[\\s-]+existencial|vazio[\\s-]+existencial|repensar[\\s-]+tudo|existencialismo|existencialista|existentialism|existencial|proposito'], "tags": {'existentialism': 1.0}},
    'expr: fairy tale': {"padroes": ['historia[\\s-]+de[\\s-]+princesa|felizes[\\s-]+para[\\s-]+sempre|historia[\\s-]+de[\\s-]+ninar|princesa[\\s-]+e[\\s-]+dragao|conto[\\s-]+de[\\s-]+fadas|principe[\\s-]+encantado|castelo[\\s-]+encantado|era[\\s-]+uma[\\s-]+vez|maca[\\s-]+envenenada|reino[\\s-]+encantado|reino[\\s-]+distante|fada[\\s-]+madrinha|irmaos[\\s-]+grimm|madrasta[\\s-]+ma|fairy[\\s-]+tale|fairytale|princesas|princesa|fabulas|fabula'], "tags": {'fairy tale': 1.0}},
    'expr: family drama': {"padroes": ['relacao[\\s-]+entre[\\s-]+irmaos|segredos[\\s-]+de[\\s-]+familia|casamento[\\s-]+em[\\s-]+crise|criacao[\\s-]+dos[\\s-]+filhos|feridas[\\s-]+de[\\s-]+familia|reuniao[\\s-]+de[\\s-]+familia|separacao[\\s-]+dos[\\s-]+pais|briga[\\s-]+de[\\s-]+familia|drama[\\s-]+de[\\s-]+familia|drama[\\s-]+em[\\s-]+familia|ceia[\\s-]+de[\\s-]+familia|familia[\\s-]+complicada|conflito[\\s-]+familiar|pai[\\s-]+e[\\s-]+filho|relacao[\\s-]+familiar|irmaos[\\s-]+brigados|drama[\\s-]+familiar|divorcio|heranca|netos'], "tags": {'family drama': 1.0}},
    'expr: fast paced': {"padroes": ['passa[\\s-]+num[\\s-]+piscar[\\s-]+de[\\s-]+olhos|nao[\\s-]+para[\\s-]+um[\\s-]+segundo|nenhum[\\s-]+momento[\\s-]+parado|direto[\\s-]+ao[\\s-]+ponto|cheio[\\s-]+de[\\s-]+acao|ritmo[\\s-]+alucinante|passa[\\s-]+rapidinho|ritmo[\\s-]+acelerado|ritmo[\\s-]+frenetico|sem[\\s-]+enrolacao|passa[\\s-]+voando|sem[\\s-]+barriga|fast[\\s-]+paced|nao[\\s-]+para|acelerado|frenetico|correria|dinamico|agitado|ligeiro|rapido'], "tags": {'fast paced': 1.0}},
    'expr: father daughter relationship': {"padroes": ['laco[\\s-]+entre[\\s-]+pai[\\s-]+e[\\s-]+filha|reconciliacao[\\s-]+com[\\s-]+o[\\s-]+pai|pai[\\s-]+solteiro[\\s-]+com[\\s-]+filha|pai[\\s-]+e[\\s-]+filha[\\s-]+viajando|pai[\\s-]+ausente[\\s-]+e[\\s-]+filha|relacao[\\s-]+pai[\\s-]+e[\\s-]+filha|menininha[\\s-]+e[\\s-]+o[\\s-]+pai|paternidade[\\s-]+com[\\s-]+filha|pai[\\s-]+com[\\s-]+a[\\s-]+filha|papai[\\s-]+e[\\s-]+filhinha|resgatar[\\s-]+a[\\s-]+filha|daddy[\\s-]+s[\\s-]+girl|dia[\\s-]+dos[\\s-]+pais|filha[\\s-]+do[\\s-]+pai|filha[\\s-]+e[\\s-]+pai|pai[\\s-]+e[\\s-]+filha|father[\\s-]+daughter|pai[\\s-]+protetor|paizao'], "tags": {'father daughter relationship': 1.0}},
    'expr: feel-good': {"padroes": ['ficar[\\s-]+de[\\s-]+bem[\\s-]+com[\\s-]+a[\\s-]+vida|sair[\\s-]+com[\\s-]+o[\\s-]+coracao[\\s-]+leve|sair[\\s-]+sorrindo[\\s-]+do[\\s-]+filme|deixar[\\s-]+de[\\s-]+bom[\\s-]+humor|deixar[\\s-]+leve[\\s-]+e[\\s-]+feliz|astral[\\s-]+la[\\s-]+em[\\s-]+cima|gostosinho[\\s-]+de[\\s-]+ver|levantar[\\s-]+o[\\s-]+astral|levantar[\\s-]+o[\\s-]+moral|sorriso[\\s-]+no[\\s-]+rosto|curar[\\s-]+a[\\s-]+bad|com[\\s-]+a[\\s-]+vida|desopilar[\\s-]+feliz|felicidade[\\s-]+pura|otimismo[\\s-]+bobo|alto[\\s-]+astral|good[\\s-]+vibes|feel[\\s-]+good|vibe[\\s-]+boa|otimista'], "tags": {'feel-good': 1.0}},
    'expr: first contact': {"padroes": ['encontro[\\s-]+com[\\s-]+extraterrestre|conversar[\\s-]+com[\\s-]+alienigenas|vida[\\s-]+fora[\\s-]+da[\\s-]+terra|comunicacao[\\s-]+com[\\s-]+aliens|decifrar[\\s-]+a[\\s-]+linguagem|nao[\\s-]+estamos[\\s-]+sozinhos|visitantes[\\s-]+do[\\s-]+espaco|chegada[\\s-]+dos[\\s-]+aliens|mensagem[\\s-]+do[\\s-]+espaco|linguagem[\\s-]+alienigena|sinal[\\s-]+do[\\s-]+espaco|contatos[\\s-]+imediatos|aliens[\\s-]+pacificos|contato[\\s-]+imediato|primeiro[\\s-]+contato|vida[\\s-]+inteligente|first[\\s-]+contact|nave[\\s-]+pousou|radiotelescopio|et[\\s-]+amigo'], "tags": {'first contact': 1.0}},
    'expr: friendship': {"padroes": ['lealdade[\\s-]+entre[\\s-]+amigos|amizade[\\s-]+de[\\s-]+infancia|grupo[\\s-]+de[\\s-]+amigos|amizade[\\s-]+bonita|best[\\s-]+friends|buddy[\\s-]+movie|companheirismo|camaradagem|broderagem|friendship|irmandade|panelinha|parceiros|bromance|parceria|amizade|amigos|galera|squad|turma'], "tags": {'friendship': 1.0}},
    'expr: funny': {"padroes": ['dar[\\s-]+boas[\\s-]+risadas|rir[\\s-]+um[\\s-]+pouco|muita[\\s-]+risada|tirar[\\s-]+sarro|dar[\\s-]+risada|divertidissimo|comediazinha|engracadinho|gargalhadas|divertido|engracado|humorado|resenha|risadas|comico|piadas|funny|piada'], "tags": {'funny': 1.0}},
    'expr: ghosts': {"padroes": ['casa[\\s-]+mal[\\s-]+assombrada|ver[\\s-]+gente[\\s-]+morta|espirito[\\s-]+vingativo|mansao[\\s-]+assombrada|casa[\\s-]+assombrada|mal[\\s-]+assombrado|alma[\\s-]+penada|assombracoes|assombracao|assombrado|aparicoes|fantasmas|aparicao|espectro|ghosts|vultos|vulto'], "tags": {'ghosts': 1.0}},
    'expr: good versus evil': {"padroes": ['luta[\\s-]+do[\\s-]+bem[\\s-]+contra[\\s-]+o[\\s-]+mal|salvar[\\s-]+o[\\s-]+mundo[\\s-]+do[\\s-]+mal|bem[\\s-]+contra[\\s-]+o[\\s-]+mal|senhor[\\s-]+das[\\s-]+trevas|good[\\s-]+versus[\\s-]+evil|herois[\\s-]+e[\\s-]+viloes|mocinho[\\s-]+e[\\s-]+vilao|derrotar[\\s-]+o[\\s-]+mal|forcas[\\s-]+do[\\s-]+mal|contra[\\s-]+o[\\s-]+mal|good[\\s-]+vs[\\s-]+evil|luz[\\s-]+e[\\s-]+trevas|vilao[\\s-]+poderoso|batalha[\\s-]+final|vilao[\\s-]+malvado|lado[\\s-]+sombrio|mal[\\s-]+absoluto|versus[\\s-]+mal|maniqueista|mocinhos'], "tags": {'good versus evil': 1.0}},
    'expr: goofy': {"padroes": ['personagem[\\s-]+atrapalhado|bagunca[\\s-]+engracada|personagem[\\s-]+pateta|lerdo[\\s-]+engracado|mane[\\s-]+engracado|maluco[\\s-]+beleza|humor[\\s-]+fisico|atrapalhado|escorregoes|desastrado|maluquinho|trapalhada|lesadinho|trapalhao|doidinho|caretas|careta|lesado|tombos|goofy'], "tags": {'goofy': 1.0}},
    'expr: gory': {"padroes": ['sangue[\\s-]+pra[\\s-]+todo[\\s-]+lado|banho[\\s-]+de[\\s-]+sangue|violencia[\\s-]+explicita|cenas[\\s-]+explicitas|sangue[\\s-]+jorrando|cenas[\\s-]+fortes|muita[\\s-]+tripa|desmembramento|sanguinolento|mutilacao|sangueira|splatter|visceras|nojeira|tortura|sangue|tripas'], "tags": {'gory': 1.0}},
    'expr: greed': {"padroes": ['bilionario[\\s-]+sem[\\s-]+escrupulos|lucro[\\s-]+acima[\\s-]+de[\\s-]+tudo|ganancia[\\s-]+sem[\\s-]+limites|bolsa[\\s-]+de[\\s-]+valores|poder[\\s-]+e[\\s-]+dinheiro|sede[\\s-]+de[\\s-]+dinheiro|mercado[\\s-]+financeiro|fraude[\\s-]+financeira|ricos[\\s-]+gananciosos|golpe[\\s-]+financeiro|especulacao|ganancioso|ambicioso|mesquinho|dinheiro|ganancia|ambicao|avareza|greed'], "tags": {'greed': 1.0}},
    'expr: grim': {"padroes": ['pesado[\\s-]+e[\\s-]+sombrio|frio[\\s-]+e[\\s-]+cruel|escuridao[\\s-]+moral|realidade[\\s-]+dura|mundo[\\s-]+sombrio|sem[\\s-]+piedade|crueldade|morbidez|sinistro|funebre|funesto|lugubre|macabro|morbido|sombrio|severo|trevas|cruel'], "tags": {'grim': 1.0}},
    'expr: gritty': {"padroes": ['realidade[\\s-]+nua[\\s-]+e[\\s-]+crua|realista[\\s-]+e[\\s-]+sujo|periferia[\\s-]+violenta|sangue[\\s-]+e[\\s-]+suor|crime[\\s-]+de[\\s-]+rua|violencia[\\s-]+urbana|pe[\\s-]+na[\\s-]+lama|estetica[\\s-]+suja|nu[\\s-]+e[\\s-]+cru|realismo[\\s-]+sujo|sem[\\s-]+maquiagem|realismo[\\s-]+cru|sem[\\s-]+glamour|quebrada|submundo|aspero|favela|gritty'], "tags": {'gritty': 1.0}},
    'expr: heartwarming': {"padroes": ['abraco[\\s-]+em[\\s-]+forma[\\s-]+de[\\s-]+filme|gente[\\s-]+boa[\\s-]+ajudando[\\s-]+gente|quentinho[\\s-]+no[\\s-]+coracao|fofura[\\s-]+que[\\s-]+emociona|amolecer[\\s-]+o[\\s-]+coracao|derreter[\\s-]+o[\\s-]+coracao|aquecer[\\s-]+o[\\s-]+coracao|cheio[\\s-]+de[\\s-]+afeto|coracao[\\s-]+quentinho|coracao[\\s-]+aquecido|historia[\\s-]+bonita|alma[\\s-]+boa|heartwarming|acolhedor|wholesome|conforta|bondade|carinho|ternura|terno'], "tags": {'heartwarming': 1.0}},
    'expr: heist': {"padroes": ['roubo[\\s-]+de[\\s-]+cassino|assalto[\\s-]+a[\\s-]+banco|plano[\\s-]+de[\\s-]+roubo|roubo[\\s-]+de[\\s-]+joias|roubo[\\s-]+a[\\s-]+banco|arrombar[\\s-]+cofre|golpe[\\s-]+perfeito|plano[\\s-]+perfeito|con[\\s-]+artist|trapaceiros|golpistas|quadrilha|assaltos|assalto|ladrao|roubar|caper|cofre|golpe|roubo'], "tags": {'heist': 1.0}},
    'expr: high school': {"padroes": ['adolescentes[\\s-]+na[\\s-]+escola|baile[\\s-]+de[\\s-]+formatura|corredor[\\s-]+da[\\s-]+escola|atleta[\\s-]+da[\\s-]+escola|lider[\\s-]+de[\\s-]+torcida|turma[\\s-]+da[\\s-]+escola|nerd[\\s-]+da[\\s-]+escola|volta[\\s-]+as[\\s-]+aulas|sala[\\s-]+de[\\s-]+aula|escola[\\s-]+americana|ensino[\\s-]+medio|vida[\\s-]+escolar|high[\\s-]+school|ultimo[\\s-]+ano|intercambio|colegial|valentao|colegio|escola'], "tags": {'high school': 1.0}},
    'expr: hilarious': {"padroes": ['cair[\\s-]+da[\\s-]+cadeira[\\s-]+de[\\s-]+rir|rir[\\s-]+ate[\\s-]+doer[\\s-]+a[\\s-]+barriga|passar[\\s-]+mal[\\s-]+de[\\s-]+rir|engracado[\\s-]+pra[\\s-]+caramba|absurdamente[\\s-]+engracado|doer[\\s-]+a[\\s-]+barriga|rir[\\s-]+ate[\\s-]+chorar|chorar[\\s-]+de[\\s-]+rir|morrer[\\s-]+de[\\s-]+rir|rachar[\\s-]+de[\\s-]+rir|rachar[\\s-]+o[\\s-]+bico|rir[\\s-]+sem[\\s-]+parar|mijar[\\s-]+de[\\s-]+rir|rolar[\\s-]+de[\\s-]+rir|muito[\\s-]+engracado|rir[\\s-]+muito|rir[\\s-]+alto|gargalhada|hilariante|gargalhar|hilarious|hilario|kkkkk'], "tags": {'hilarious': 1.0}},
    'expr: humanity': {"padroes": ['lado[\\s-]+bom[\\s-]+das[\\s-]+pessoas|gente[\\s-]+ajudando[\\s-]+gente|licao[\\s-]+de[\\s-]+humanidade|todos[\\s-]+somos[\\s-]+iguais|nos[\\s-]+torna[\\s-]+humanos|ajudar[\\s-]+o[\\s-]+proximo|amor[\\s-]+ao[\\s-]+proximo|dignidade[\\s-]+humana|natureza[\\s-]+humana|bondade[\\s-]+humana|conexao[\\s-]+humana|ser[\\s-]+humano|solidariedade|generosidade|humanidade|compaixao|dignidade|gentileza|humanismo|humanity|empatia'], "tags": {'humanity': 1.0}},
    'expr: identity': {"padroes": ['descobrir[\\s-]+a[\\s-]+propria[\\s-]+identidade|busca[\\s-]+por[\\s-]+identidade|crise[\\s-]+de[\\s-]+identidade|troca[\\s-]+de[\\s-]+identidade|descobrir[\\s-]+quem[\\s-]+e|sair[\\s-]+do[\\s-]+armario|assumir[\\s-]+quem[\\s-]+e|ser[\\s-]+voce[\\s-]+mesmo|identidade[\\s-]+secreta|dupla[\\s-]+identidade|quem[\\s-]+eu[\\s-]+sou|se[\\s-]+aceitar|autodescoberta|pertencimento|lgbtqia|origens|raizes'], "tags": {'identity': 1.0}},
    'expr: inspirational': {"padroes": ['correr[\\s-]+atras[\\s-]+dos[\\s-]+sonhos|historia[\\s-]+de[\\s-]+superacao|licao[\\s-]+de[\\s-]+motivacao|forca[\\s-]+de[\\s-]+vontade|exemplo[\\s-]+de[\\s-]+vida|realizar[\\s-]+sonhos|sonho[\\s-]+realizado|nunca[\\s-]+desistir|nao[\\s-]+desistir|inspirational|dar[\\s-]+gas|determinacao|motivacional|empowering|inspiracao|inspirador|autoajuda|motivador|uplifting|inspirar|motivar|garra'], "tags": {'inspirational': 1.0}},
    'expr: intense': {"padroes": ['visceral[\\s-]+e[\\s-]+intenso|pesado[\\s-]+e[\\s-]+intenso|nao[\\s-]+da[\\s-]+respiro|tirar[\\s-]+o[\\s-]+folego|cair[\\s-]+o[\\s-]+queixo|porrada[\\s-]+emocional|alta[\\s-]+voltagem|muito[\\s-]+intenso|sem[\\s-]+respiro|arrebatador|avassalador|eletrizante|intensidade|explosivo|frenetico|pulsante|intenso'], "tags": {'intense': 1.0}},
    'expr: justice': {"padroes": ['lutar[\\s-]+contra[\\s-]+o[\\s-]+sistema|justica[\\s-]+seja[\\s-]+feita|provar[\\s-]+a[\\s-]+inocencia|condenado[\\s-]+injustamente|lutar[\\s-]+por[\\s-]+justica|verdade[\\s-]+e[\\s-]+justica|preso[\\s-]+injustamente|julgamento[\\s-]+justo|lei[\\s-]+e[\\s-]+ordem|buscar[\\s-]+justica|inocente[\\s-]+preso|justica[\\s-]+social|fazer[\\s-]+justica|injusticado|julgamento|justiceiro|denunciar|reparacao|advogado|denuncia|justica|justice'], "tags": {'justice': 1.0}},
    'expr: kids and family': {"padroes": ['sessao[\\s-]+da[\\s-]+tarde[\\s-]+em[\\s-]+familia|com[\\s-]+as[\\s-]+criancas|kids[\\s-]+and[\\s-]+family|ver[\\s-]+com[\\s-]+crianca|toda[\\s-]+a[\\s-]+familia|animacao[\\s-]+infantil|desenho[\\s-]+animado|familia[\\s-]+inteira|familia[\\s-]+reunida|family[\\s-]+friendly|pras[\\s-]+criancas|familia[\\s-]+toda|criancada|molecada'], "tags": {'kids and family': 1.0}},
    'expr: life & death': {"padroes": ['pouco[\\s-]+tempo[\\s-]+de[\\s-]+vida|vem[\\s-]+depois[\\s-]+da[\\s-]+morte|aproveitar[\\s-]+a[\\s-]+vida|encarar[\\s-]+a[\\s-]+morte|life[\\s-]+and[\\s-]+death|sobre[\\s-]+a[\\s-]+morte|viver[\\s-]+intensamente|vida[\\s-]+e[\\s-]+morte|fim[\\s-]+da[\\s-]+vida|doenca[\\s-]+terminal|perder[\\s-]+alguem|ultimos[\\s-]+dias|despedida|finitude|funeral|velorio|cancer|perda'], "tags": {'life & death': 1.0}},
    'expr: light': {"padroes": ['descansar[\\s-]+a[\\s-]+cabeca|descansar[\\s-]+a[\\s-]+mente|easy[\\s-]+watching|descompromissado|nada[\\s-]+pesado|despretensioso|descontraido|tranquilinho|suavezinho|tranquilo|levinho|relaxar|chill|relax|suave|sussa'], "tags": {'light': 1.0}},
    'expr: loneliness': {"padroes": ['solidao[\\s-]+na[\\s-]+cidade[\\s-]+grande|ninguem[\\s-]+por[\\s-]+perto|saudade[\\s-]+de[\\s-]+alguem|nao[\\s-]+se[\\s-]+encaixar|velhice[\\s-]+solitaria|vida[\\s-]+solitaria|gente[\\s-]+sozinha|morar[\\s-]+sozinho|sem[\\s-]+amigos|abandonado|isolamento|loneliness|deslocado|solitario|solteirao|abandono|carencia|excluido|carente|isolado|solidao|sozinho|lonely'], "tags": {'loneliness': 1.0}},
    'expr: love story': {"padroes": ['amor[\\s-]+a[\\s-]+primeira[\\s-]+vista|amor[\\s-]+atraves[\\s-]+do[\\s-]+tempo|viver[\\s-]+um[\\s-]+grande[\\s-]+amor|casal[\\s-]+que[\\s-]+se[\\s-]+ama|historia[\\s-]+de[\\s-]+amor|romance[\\s-]+de[\\s-]+epoca|cartas[\\s-]+de[\\s-]+amor|paixao[\\s-]+avassaladora|amor[\\s-]+adolescente|casal[\\s-]+apaixonado|amor[\\s-]+verdadeiro|amor[\\s-]+proibido|romance[\\s-]+epico|amor[\\s-]+eterno|grande[\\s-]+amor|alma[\\s-]+gemea|love[\\s-]+story|reencontro'], "tags": {'love story': 1.0}},
    'expr: magic': {"padroes": ['escola[\\s-]+de[\\s-]+magia|mundo[\\s-]+magico|encantamento|ilusionismo|ilusionista|feiticeiro|alquimia|bruxaria|hogwarts|feitico|magicos|varinha|magico|wizard|bruxa|bruxo|magia|magos'], "tags": {'magic': 1.0}},
    'expr: meditative': {"padroes": ['natureza[\\s-]+contemplativa|quase[\\s-]+sem[\\s-]+dialogo|calmo[\\s-]+e[\\s-]+profundo|lento[\\s-]+e[\\s-]+bonito|cinema[\\s-]+lento|paz[\\s-]+interior|poucas[\\s-]+falas|sem[\\s-]+pressa|transcendental|contemplativo|contemplacao|hipnotizante|devagarinho|meditative|meditativo|serenidade|silencioso|hipnotico|sereno'], "tags": {'meditative': 1.0}},
    'expr: melancholic': {"padroes": ['aquela[\\s-]+vibe[\\s-]+de[\\s-]+domingo[\\s-]+a[\\s-]+noite|contemplativo[\\s-]+e[\\s-]+triste|introspectivo[\\s-]+e[\\s-]+triste|solitario[\\s-]+e[\\s-]+triste|sensacao[\\s-]+de[\\s-]+vazio|melancolia[\\s-]+bonita|nostalgia[\\s-]+triste|domingo[\\s-]+chuvoso|clima[\\s-]+cinzento|tristeza[\\s-]+mansa|clima[\\s-]+outonal|dia[\\s-]+cinza|desalentado|melancholic|melancolico|melancholy|tristonho|cinzento|saudoso|fossa'], "tags": {'melancholic': 1.0}},
    'expr: memory': {"padroes": ['nao[\\s-]+lembra[\\s-]+quem[\\s-]+e|acordar[\\s-]+sem[\\s-]+memoria|recuperar[\\s-]+a[\\s-]+memoria|lembrar[\\s-]+do[\\s-]+passado|perder[\\s-]+a[\\s-]+memoria|perdeu[\\s-]+a[\\s-]+memoria|memorias[\\s-]+implantadas|memoria[\\s-]+fragmentada|passado[\\s-]+esquecido|apagar[\\s-]+memorias|memoria[\\s-]+apagada|memoria[\\s-]+falsa|sem[\\s-]+memoria|recordacoes|flashbacks|alzheimer|demencia|esquecer|memoria'], "tags": {'memory': 1.0}},
    'expr: mental illness': {"padroes": ['internado[\\s-]+num[\\s-]+hospicio|sindrome[\\s-]+do[\\s-]+panico|crise[\\s-]+de[\\s-]+panico|dupla[\\s-]+personalidade|transtorno[\\s-]+mental|surto[\\s-]+psicotico|mental[\\s-]+illness|doenca[\\s-]+mental|saude[\\s-]+mental|esquizofrenia|bipolaridade|psiquiatria|transtorno|ansiedade|depressao|manicomio|sanatorio|hospicio|autismo|bipolar|loucura'], "tags": {'mental illness': 1.0}},
    'expr: mindfuck': {"padroes": ['porra[\\s-]+eu[\\s-]+acabei[\\s-]+de[\\s-]+ver|fazer[\\s-]+minha[\\s-]+cabeca[\\s-]+fritar|dar[\\s-]+um[\\s-]+no[\\s-]+na[\\s-]+cabeca|sair[\\s-]+do[\\s-]+filme[\\s-]+confuso|explodir[\\s-]+minha[\\s-]+mente|bugar[\\s-]+meu[\\s-]+cerebro|explodir[\\s-]+a[\\s-]+cabeca|fritar[\\s-]+a[\\s-]+cabeca|bugar[\\s-]+a[\\s-]+cabeca|bugar[\\s-]+a[\\s-]+mente|bugue[\\s-]+a[\\s-]+mente|fundir[\\s-]+a[\\s-]+cuca|cabeca[\\s-]+a[\\s-]+mil|no[\\s-]+na[\\s-]+cabeca|cabeca[\\s-]+explodir|cabeca[\\s-]+fritar|mind[\\s-]+blowing|mind[\\s-]+bender|mind[\\s-]+fuck|mindfuck'], "tags": {'mindfuck': 1.0}},
    'expr: monster': {"padroes": ['abominavel[\\s-]+homem[\\s-]+das[\\s-]+neves|criatura[\\s-]+das[\\s-]+profundezas|monstro[\\s-]+assustador|criatura[\\s-]+bizarra|monstro[\\s-]+gigante|monstro[\\s-]+marinho|mutante[\\s-]+gigante|bicho[\\s-]+estranho|bicho[\\s-]+gigante|pe[\\s-]+grande|monstrengo|criatura|monstrao|monstro|kaiju'], "tags": {'monster': 1.0}},
    'expr: multiple storylines': {"padroes": ['tudo[\\s-]+se[\\s-]+conecta[\\s-]+no[\\s-]+final|pontos[\\s-]+de[\\s-]+vista[\\s-]+diferentes|historias[\\s-]+que[\\s-]+se[\\s-]+cruzam|vidas[\\s-]+que[\\s-]+se[\\s-]+cruzam|mosaico[\\s-]+de[\\s-]+historias|historias[\\s-]+interligadas|historias[\\s-]+conectadas|historias[\\s-]+paralelas|multiple[\\s-]+storylines|varias[\\s-]+perspectivas|muitos[\\s-]+personagens|varios[\\s-]+personagens|tramas[\\s-]+paralelas|varias[\\s-]+historias|varios[\\s-]+nucleos|elenco[\\s-]+grande|varias[\\s-]+tramas|antologia|segmentos|coral'], "tags": {'multiple storylines': 1.0}},
    'expr: murder mystery': {"padroes": ['assassino[\\s-]+entre[\\s-]+os[\\s-]+convidados|investigacao[\\s-]+de[\\s-]+assassinato|misterio[\\s-]+de[\\s-]+assassinato|descobrir[\\s-]+quem[\\s-]+matou|misterio[\\s-]+de[\\s-]+detetive|assassino[\\s-]+entre[\\s-]+nos|caso[\\s-]+de[\\s-]+assassinato|descobrir[\\s-]+o[\\s-]+culpado|todos[\\s-]+sao[\\s-]+suspeitos|assassinato[\\s-]+misterioso|jogo[\\s-]+de[\\s-]+detetive|detetive[\\s-]+particular|crime[\\s-]+no[\\s-]+trem|crime[\\s-]+misterioso|morte[\\s-]+misteriosa|quem[\\s-]+matou|whodunit|cluedo|poirot'], "tags": {'murder mystery': 1.0}},
    'expr: music': {"padroes": ['vida[\\s-]+de[\\s-]+musico|rock[\\s-]+and[\\s-]+roll|trilha[\\s-]+sonora|hip[\\s-]+hop|orquestra|cantoria|concerto|musicais|karaoke|bandas|cantar|cantor|dancar|musica|banda|danca|music'], "tags": {'music': 1.0}},
    'expr: mythology': {"padroes": ['criaturas[\\s-]+mitologicas|criaturas[\\s-]+miticas|deuses[\\s-]+egipcios|mitologia[\\s-]+grega|deuses[\\s-]+gregos|herois[\\s-]+gregos|mitos[\\s-]+antigos|epico[\\s-]+grego|mitologico|semideuses|mitologia|mythology|semideus|deuses|lendas|lenda|mitos|titas'], "tags": {'mythology': 1.0}},
    'expr: neo-noir': {"padroes": ['luzes[\\s-]+de[\\s-]+neon[\\s-]+e[\\s-]+crime|cidade[\\s-]+chuvosa[\\s-]+a[\\s-]+noite|sombras[\\s-]+e[\\s-]+fumaca|anti[\\s-]+heroi[\\s-]+noir|crime[\\s-]+e[\\s-]+sombras|narracao[\\s-]+em[\\s-]+off|cinico[\\s-]+e[\\s-]+noir|jazz[\\s-]+e[\\s-]+crime|detetive[\\s-]+cansado|submundo[\\s-]+noturno|atmosfera[\\s-]+noir|detetive[\\s-]+noir|estetica[\\s-]+noir|policial[\\s-]+noir|thriller[\\s-]+noir|femme[\\s-]+fatale|mulher[\\s-]+fatal|noir[\\s-]+moderno|hard[\\s-]+boiled|film[\\s-]+noir|neo[\\s-]+noir'], "tags": {'neo-noir': 1.0}},
    'expr: nonlinear': {"padroes": ['contado[\\s-]+de[\\s-]+tras[\\s-]+pra[\\s-]+frente|idas[\\s-]+e[\\s-]+vindas[\\s-]+no[\\s-]+tempo|vai[\\s-]+e[\\s-]+volta[\\s-]+no[\\s-]+tempo|linha[\\s-]+do[\\s-]+tempo[\\s-]+baguncada|historia[\\s-]+fora[\\s-]+de[\\s-]+ordem|quebra[\\s-]+cabeca[\\s-]+temporal|cronologia[\\s-]+embaralhada|narrativa[\\s-]+fragmentada|montagem[\\s-]+fragmentada|tras[\\s-]+pra[\\s-]+frente|estrutura[\\s-]+diferente|fora[\\s-]+de[\\s-]+ordem|tempo[\\s-]+embaralhado|nao[\\s-]+linear|non[\\s-]+linear|flashback|nonlinear|mosaico'], "tags": {'nonlinear': 1.0}},
    'expr: nostalgic': {"padroes": ['classico[\\s-]+da[\\s-]+sessao[\\s-]+da[\\s-]+tarde|volta[\\s-]+no[\\s-]+tempo[\\s-]+da[\\s-]+infancia|memorias[\\s-]+de[\\s-]+infancia|clima[\\s-]+de[\\s-]+infancia|tempos[\\s-]+de[\\s-]+crianca|sessao[\\s-]+da[\\s-]+tarde|minha[\\s-]+infancia|bate[\\s-]+saudade|das[\\s-]+antigas|minha[\\s-]+epoca|fita[\\s-]+vhs|videocassete|nostalgico|saudosismo|nostalgia|nostalgic|relembrar|infancia|locadora|vintage|retro'], "tags": {'nostalgic': 1.0}},
    'expr: obsession': {"padroes": ['doenca[\\s-]+pela[\\s-]+perfeicao|perseguicao[\\s-]+obsessiva|loucura[\\s-]+de[\\s-]+amor|ciume[\\s-]+doentio|amor[\\s-]+doentio|fa[\\s-]+obcecado|ideia[\\s-]+fixa|perfeccionismo|perfeccionista|perseguidor|possessivo|compulsao|obsessivo|obcecada|fixacao|ciumes|fixado'], "tags": {'obsession': 1.0}},
    'expr: ominous': {"padroes": ['calmaria[\\s-]+antes[\\s-]+da[\\s-]+tempestade|crescendo[\\s-]+de[\\s-]+tensao|ruim[\\s-]+vai[\\s-]+acontecer|sensacao[\\s-]+de[\\s-]+perigo|clima[\\s-]+de[\\s-]+ameaca|pressentimento[\\s-]+ruim|tempestade[\\s-]+chegando|sombra[\\s-]+ameacadora|tensao[\\s-]+crescente|perigo[\\s-]+iminente|suspense[\\s-]+lento|nuvem[\\s-]+negra|agourento|ameacador|iminente|ominous|agouro'], "tags": {'ominous': 1.0}},
    'expr: organized crime': {"padroes": ['chefe[\\s-]+do[\\s-]+trafico|mundo[\\s-]+do[\\s-]+crime|faccao[\\s-]+criminosa|familia[\\s-]+mafiosa|organized[\\s-]+crime|narcotrafico|traficantes|gangsteres|gangster|carteis|milicia|trafico|cartel|chefao|faccao|triade|yakuza|mafia'], "tags": {'organized crime': 1.0}},
    'expr: paranoid': {"padroes": ['nao[\\s-]+confiar[\\s-]+em[\\s-]+ninguem|sera[\\s-]+que[\\s-]+estou[\\s-]+louco|mania[\\s-]+de[\\s-]+perseguicao|ninguem[\\s-]+e[\\s-]+confiavel|desconfiar[\\s-]+de[\\s-]+tudo|quem[\\s-]+esta[\\s-]+mentindo|tudo[\\s-]+e[\\s-]+suspeito|sendo[\\s-]+vigiado|enlouquecendo|desconfianca|gaslighting|perseguido|neurotico|paranoico|paranoid|delirio|neurose|vigiado'], "tags": {'paranoid': 1.0}},
    'expr: parenthood': {"padroes": ['pais[\\s-]+de[\\s-]+primeira[\\s-]+viagem|cuidar[\\s-]+dos[\\s-]+filhos|familia[\\s-]+com[\\s-]+bebe|relacao[\\s-]+de[\\s-]+mae|pais[\\s-]+e[\\s-]+filhos|filho[\\s-]+adotivo|criar[\\s-]+filhos|ter[\\s-]+filhos|virar[\\s-]+mae|virar[\\s-]+pai|mae[\\s-]+solo|pai[\\s-]+solo|ser[\\s-]+pai|maternidade|gravidez|adocao|bebes'], "tags": {'parenthood': 1.0}},
    'expr: parody': {"padroes": ['referencias[\\s-]+a[\\s-]+outros[\\s-]+filmes|zoeira[\\s-]+com[\\s-]+filmes[\\s-]+famosos|parodia[\\s-]+de[\\s-]+super[\\s-]+heroi|tirar[\\s-]+sarro[\\s-]+de[\\s-]+terror|tirar[\\s-]+sarro[\\s-]+de[\\s-]+filme|satira[\\s-]+de[\\s-]+genero|comedia[\\s-]+que[\\s-]+zoa|homenagem[\\s-]+engracada|besteirol[\\s-]+parodia|zoando[\\s-]+hollywood|imitar[\\s-]+filmes|zoar[\\s-]+cliches|zoa[\\s-]+cliches|zoar[\\s-]+filmes|metalinguagem|imitacao|parodias|parodia|parody|spoof'], "tags": {'parody': 1.0}},
    'expr: period piece': {"padroes": ['figurino[\\s-]+de[\\s-]+epoca|bailes[\\s-]+de[\\s-]+epoca|roupas[\\s-]+de[\\s-]+epoca|drama[\\s-]+de[\\s-]+epoca|reis[\\s-]+e[\\s-]+rainhas|era[\\s-]+vitoriana|epoca[\\s-]+antiga|period[\\s-]+piece|corte[\\s-]+real|seculo[\\s-]+xix|outra[\\s-]+era|seculo[\\s-]+19|antigamente|historico|vitoriano|medieval|realeza'], "tags": {'period piece': 1.0}},
    'expr: philosophical': {"padroes": ['qual[\\s-]+o[\\s-]+sentido[\\s-]+da[\\s-]+vida|questionar[\\s-]+a[\\s-]+realidade|pensar[\\s-]+a[\\s-]+existencia|questoes[\\s-]+existenciais|sentido[\\s-]+da[\\s-]+vida|perguntas[\\s-]+grandes|grandes[\\s-]+questoes|verdade[\\s-]+absoluta|livre[\\s-]+arbitrio|dilema[\\s-]+moral|onde[\\s-]+viemos|quem[\\s-]+somos|philosophical|consciencia|e[\\s-]+real|existencia|filosofico|metafisica|metafisico|filosofia|dilemas|etica'], "tags": {'philosophical': 1.0}},
    'expr: poignant': {"padroes": ['fica[\\s-]+na[\\s-]+cabeca[\\s-]+por[\\s-]+dias|honesto[\\s-]+e[\\s-]+doloroso|sincero[\\s-]+e[\\s-]+doloroso|dolorido[\\s-]+e[\\s-]+bonito|profundo[\\s-]+e[\\s-]+triste|cru[\\s-]+e[\\s-]+emocional|emocionalmente[\\s-]+forte|rasga[\\s-]+o[\\s-]+coracao|doi[\\s-]+de[\\s-]+verdade|doer[\\s-]+no[\\s-]+peito|verdade[\\s-]+dolorosa|soco[\\s-]+emocional|deixa[\\s-]+marcas|cortante|doloroso|marcante|poignant|pungente|comocao|machuca'], "tags": {'poignant': 1.0}},
    'expr: police investigation': {"padroes": ['crime[\\s-]+a[\\s-]+ser[\\s-]+resolvido|resolver[\\s-]+um[\\s-]+crime|investigacao[\\s-]+policial|police[\\s-]+investigation|resolver[\\s-]+o[\\s-]+caso|cena[\\s-]+do[\\s-]+crime|procurar[\\s-]+pistas|caso[\\s-]+policial|cold[\\s-]+case|interrogatorio|investigacao|investigador|procedural|detetives|delegado|detetive|forense|pericia|pistas'], "tags": {'police investigation': 1.0}},
    'expr: politics': {"padroes": ['bastidores[\\s-]+do[\\s-]+poder|esquerda[\\s-]+e[\\s-]+direita|golpe[\\s-]+de[\\s-]+estado|campanha[\\s-]+eleitoral|estado[\\s-]+autoritario|jogo[\\s-]+politico|casa[\\s-]+branca|democracia|diplomacia|militancia|congresso|ideologia|revolucao|ditadura|eleicoes|politica|politico|regime|senado'], "tags": {'politics': 1.0}},
    'expr: post-apocalyptic': {"padroes": ['depois[\\s-]+do[\\s-]+fim[\\s-]+do[\\s-]+mundo|deserto[\\s-]+pos[\\s-]+apocaliptico|sobreviventes[\\s-]+no[\\s-]+deserto|sociedade[\\s-]+em[\\s-]+ruinas|the[\\s-]+last[\\s-]+of[\\s-]+us|gangues[\\s-]+no[\\s-]+deserto|pos[\\s-]+guerra[\\s-]+nuclear|civilizacao[\\s-]+destruida|depois[\\s-]+da[\\s-]+bomba|mundo[\\s-]+em[\\s-]+ruinas|post[\\s-]+apocalyptic|inverno[\\s-]+nuclear|mundo[\\s-]+devastado|terra[\\s-]+arrasada|mundo[\\s-]+vazio|wasteland|mutantes|radiacao|ruinas'], "tags": {'post-apocalyptic': 1.0}},
    'expr: poverty': {"padroes": ['dificuldade[\\s-]+financeira|comunidade[\\s-]+carente|vida[\\s-]+de[\\s-]+pobre|familia[\\s-]+pobre|classe[\\s-]+baixa|sem[\\s-]+dinheiro|vida[\\s-]+dificil|passar[\\s-]+fome|desempregado|desemprego|periferia|barraco|cortico|despejo|pobreza|poverty|divida|favela'], "tags": {'poverty': 1.0}},
    'expr: prison escape': {"padroes": ['escapar[\\s-]+da[\\s-]+cadeia|escapar[\\s-]+da[\\s-]+prisao|fugir[\\s-]+da[\\s-]+prisao|cavar[\\s-]+um[\\s-]+tunel|fuga[\\s-]+da[\\s-]+cadeia|fuga[\\s-]+da[\\s-]+prisao|tunel[\\s-]+de[\\s-]+fuga|fuga[\\s-]+espetacular|seguranca[\\s-]+maxima|penitenciaria|presidiarios|presidiario|jailbreak|detentos|foragido|presidio|prisao'], "tags": {'prison escape': 1.0}},
    'expr: quirky': {"padroes": ['estranho[\\s-]+no[\\s-]+bom[\\s-]+sentido|estiloso[\\s-]+e[\\s-]+esquisito|criativo[\\s-]+e[\\s-]+estranho|personagens[\\s-]+excentricos|fofo[\\s-]+e[\\s-]+estranho|personagem[\\s-]+esquisito|fora[\\s-]+do[\\s-]+comum|cult[\\s-]+esquisito|alternativo|bizarrinho|diferentao|excentrico|esquisito|peculiar|singular|hipster|offbeat|quirky|indie'], "tags": {'quirky': 1.0}},
    'expr: racism': {"padroes": ['sul[\\s-]+dos[\\s-]+estados[\\s-]+unidos|representatividade[\\s-]+negra|preconceito[\\s-]+racial|racismo[\\s-]+estrutural|ku[\\s-]+klux[\\s-]+klan|luta[\\s-]+antirracista|supremacia[\\s-]+branca|injustica[\\s-]+racial|direitos[\\s-]+civis|black[\\s-]+power|discriminacao|antirracismo|preconceito|escravidao|segregacao|apartheid|negritude|escravos|racismo|racista|racism'], "tags": {'racism': 1.0}},
    'expr: redemption': {"padroes": ['se[\\s-]+tornar[\\s-]+alguem[\\s-]+melhor|voltar[\\s-]+ao[\\s-]+caminho[\\s-]+certo|ex[\\s-]+presidiario[\\s-]+recomecando|consertar[\\s-]+os[\\s-]+erros|transformacao[\\s-]+pessoal|reparar[\\s-]+o[\\s-]+erro|mudar[\\s-]+de[\\s-]+vida|pedir[\\s-]+perdao|nova[\\s-]+chance|se[\\s-]+redimir|arrependimento|arrependido|redemption|expiacao|recomeco|salvacao|perdoar|perdao'], "tags": {'redemption': 1.0}},
    'expr: reflective': {"padroes": ['refletir[\\s-]+sobre[\\s-]+a[\\s-]+vida|ficar[\\s-]+pensando[\\s-]+depois|olhar[\\s-]+pra[\\s-]+dentro|repensar[\\s-]+a[\\s-]+vida|crescimento[\\s-]+pessoal|pensar[\\s-]+na[\\s-]+vida|licao[\\s-]+de[\\s-]+vida|rever[\\s-]+a[\\s-]+vida|sobre[\\s-]+a[\\s-]+vida|fazer[\\s-]+refletir|sair[\\s-]+pensando|fazer[\\s-]+pensar|contemplativo|introspectivo|reflective|filosofar|reflexivo|refletir|reflexao|maduro'], "tags": {'reflective': 1.0}},
    'expr: religion': {"padroes": ['vida[\\s-]+de[\\s-]+santo|fe[\\s-]+em[\\s-]+deus|espiritualidade|cristianismo|espiritual|evangelico|religioso|catolico|convento|milagres|pregacao|religiao|biblico|cristao|milagre|biblia|crenca|igreja|jesus'], "tags": {'religion': 1.0}},
    'expr: revenge': {"padroes": ['justica[\\s-]+com[\\s-]+as[\\s-]+proprias[\\s-]+maos|matar[\\s-]+quem[\\s-]+fez[\\s-]+isso|acerto[\\s-]+de[\\s-]+contas|cacar[\\s-]+quem[\\s-]+matou|vai[\\s-]+pagar[\\s-]+caro|olho[\\s-]+por[\\s-]+olho|dar[\\s-]+o[\\s-]+troco|vinganca[\\s-]+fria|fazer[\\s-]+pagar|retaliacao|vingativo|revanche|vendetta|vingar'], "tags": {'revenge': 1.0}},
    'expr: road trip': {"padroes": ['atravessar[\\s-]+o[\\s-]+pais|viagem[\\s-]+pelo[\\s-]+pais|cair[\\s-]+na[\\s-]+estrada|viagem[\\s-]+de[\\s-]+carro|viagem[\\s-]+sem[\\s-]+rumo|viagem[\\s-]+de[\\s-]+moto|cruzar[\\s-]+o[\\s-]+pais|pe[\\s-]+na[\\s-]+estrada|estrada[\\s-]+afora|road[\\s-]+movie|route[\\s-]+66|rota[\\s-]+66|mochileiro|mochilao|estrada|carona|viajar'], "tags": {'road trip': 1.0}},
    'expr: romantic': {"padroes": ['borboletas[\\s-]+no[\\s-]+estomago|ver[\\s-]+com[\\s-]+o[\\s-]+crush|historia[\\s-]+de[\\s-]+amor|primeiro[\\s-]+encontro|meloso[\\s-]+romantico|clima[\\s-]+romantico|se[\\s-]+apaixonar|casal[\\s-]+fofo|rom[\\s-]+com|romancezinho|casalzinho|amorzinho|romantico|suspirar|namoro|paixao|beijo'], "tags": {'romantic': 1.0}},
    'expr: sacrifice': {"padroes": ['dar[\\s-]+a[\\s-]+vida[\\s-]+por[\\s-]+alguem|morrer[\\s-]+pelo[\\s-]+outro|proteger[\\s-]+quem[\\s-]+ama|tudo[\\s-]+pela[\\s-]+familia|despedida[\\s-]+heroica|sacrificio[\\s-]+final|dar[\\s-]+a[\\s-]+vida|self[\\s-]+sacrifice|entregar[\\s-]+tudo|morte[\\s-]+heroica|se[\\s-]+sacrificar|ato[\\s-]+heroico|ultimo[\\s-]+ato|abrir[\\s-]+mao|sacrificar|sacrificio|altruismo|altruista|renunciar|heroismo|renuncia'], "tags": {'sacrifice': 1.0}},
    'expr: sad': {"padroes": ['partir[\\s-]+o[\\s-]+coracao|triste[\\s-]+de[\\s-]+doer|dor[\\s-]+no[\\s-]+peito|historia[\\s-]+tragica|coracao[\\s-]+partido|final[\\s-]+triste|sofrer[\\s-]+junto|bad[\\s-]+vibe|na[\\s-]+bad|sofrencia|tristinho|tragedia|tristeza|sofrido|sofrer'], "tags": {'sad': 1.0}},
    'expr: satirical': {"padroes": ['tirar[\\s-]+sarro[\\s-]+do[\\s-]+sistema|critica[\\s-]+social[\\s-]+engracada|critica[\\s-]+com[\\s-]+humor|zoar[\\s-]+a[\\s-]+sociedade|rir[\\s-]+dos[\\s-]+ricos|zoar[\\s-]+os[\\s-]+ricos|comedia[\\s-]+politica|satira[\\s-]+politica|absurdo[\\s-]+social|parodia[\\s-]+social|critica[\\s-]+acida|ironia[\\s-]+social|zoar[\\s-]+politico|caricatura|debochado|satirical|satirizar|satirico|deboche|satira|satire'], "tags": {'satirical': 1.0}},
    'expr: scary': {"padroes": ['dormir[\\s-]+de[\\s-]+luz[\\s-]+acesa|cagar[\\s-]+nas[\\s-]+calcas|morrer[\\s-]+de[\\s-]+medo|tremer[\\s-]+de[\\s-]+medo|cagar[\\s-]+de[\\s-]+medo|pular[\\s-]+do[\\s-]+sofa|terror[\\s-]+pesado|sentir[\\s-]+medo|tomar[\\s-]+susto|jump[\\s-]+scare|dar[\\s-]+medo|horripilante|apavorante|assustador|jumpscare|assustar|sustos|pavor|scary|susto'], "tags": {'scary': 1.0}},
    'expr: sentimental': {"padroes": ['brega[\\s-]+no[\\s-]+bom[\\s-]+sentido|agua[\\s-]+com[\\s-]+acucar|cara[\\s-]+de[\\s-]+novela|romantico[\\s-]+meloso|coracao[\\s-]+mole|sentimentalismo|melodramatico|sentimental|choradeira|acucarado|derretido|melodrama|novelinha|novelao|melado|meloso|brega'], "tags": {'sentimental': 1.0}},
    'expr: serial killer': {"padroes": ['cacada[\\s-]+a[\\s-]+um[\\s-]+serial[\\s-]+killer|assassinatos[\\s-]+em[\\s-]+serie|assassino[\\s-]+em[\\s-]+serie|cacar[\\s-]+um[\\s-]+assassino|mente[\\s-]+de[\\s-]+assassino|jack[\\s-]+o[\\s-]+estripador|matanca[\\s-]+em[\\s-]+serie|assassino[\\s-]+mascarado|assassino[\\s-]+psicopata|maniaco[\\s-]+assassino|perfil[\\s-]+criminal|serial[\\s-]+killer|estripador|mindhunter|psicopatas|psicopata|matanca|slasher'], "tags": {'serial killer': 1.0}},
    'expr: silly': {"padroes": ['idiota[\\s-]+no[\\s-]+bom[\\s-]+sentido|sem[\\s-]+pe[\\s-]+nem[\\s-]+cabeca|desligar[\\s-]+o[\\s-]+cerebro|humor[\\s-]+de[\\s-]+tiozao|piada[\\s-]+de[\\s-]+tiozao|comedia[\\s-]+pastelao|tosco[\\s-]+engracado|comedia[\\s-]+idiota|pastelao[\\s-]+bobo|comedia[\\s-]+boba|humor[\\s-]+besta|sem[\\s-]+pensar|dumb[\\s-]+fun|besteirinha|palhacadas|palhacada|besteira|bobeira|bobinho'], "tags": {'silly': 1.0}},
    'expr: slapstick': {"padroes": ['escorregar[\\s-]+na[\\s-]+casca[\\s-]+de[\\s-]+banana|cartoon[\\s-]+de[\\s-]+verdade|comedia[\\s-]+de[\\s-]+tombo|quebradeira[\\s-]+engracada|torta[\\s-]+na[\\s-]+cara|pancadaria[\\s-]+comica|comedia[\\s-]+pastelao|tombo[\\s-]+engracado|comedia[\\s-]+muda|gags[\\s-]+visuais|humor[\\s-]+fisico|tres[\\s-]+patetas|trapalhadas|trapalhada|trapalhoes|palhacada|slapstick|pastelao|palhaco|quedas|tapas|tombo'], "tags": {'slapstick': 1.0}},
    'expr: slow paced': {"padroes": ['ritmo[\\s-]+de[\\s-]+cinema[\\s-]+de[\\s-]+arte|contemplativo[\\s-]+e[\\s-]+lento|tempo[\\s-]+pra[\\s-]+respirar|calmo[\\s-]+e[\\s-]+lento|lento[\\s-]+mas[\\s-]+bom|planos[\\s-]+longos|ritmo[\\s-]+devagar|ritmo[\\s-]+europeu|cenas[\\s-]+longas|ritmo[\\s-]+lento|vai[\\s-]+devagar|slow[\\s-]+paced|slow[\\s-]+burn|arrastado|enrolacao|sonolento|lentidao|lentinho|devagar|parado|lento'], "tags": {'slow paced': 1.0}},
    'expr: small town': {"padroes": ['cidade[\\s-]+do[\\s-]+interior[\\s-]+americano|todo[\\s-]+mundo[\\s-]+se[\\s-]+conhece|cidadezinha[\\s-]+do[\\s-]+interior|cidade[\\s-]+do[\\s-]+interior|cidadezinha[\\s-]+americana|comunidade[\\s-]+pequena|meio[\\s-]+do[\\s-]+nada|vida[\\s-]+na[\\s-]+roca|cidade[\\s-]+esquecida|cidade[\\s-]+pequena|cidade[\\s-]+pacata|lugar[\\s-]+isolado|small[\\s-]+town|cidadezinha|interior|vilarejo|caipira|fazenda|povoado|pacato'], "tags": {'small town': 1.0}},
    'expr: social commentary': {"padroes": ['critica[\\s-]+ao[\\s-]+capitalismo|critica[\\s-]+a[\\s-]+sociedade|luta[\\s-]+de[\\s-]+classes|desigualdade[\\s-]+social|ricos[\\s-]+e[\\s-]+pobres|comentario[\\s-]+social|social[\\s-]+commentary|questoes[\\s-]+sociais|sociedade[\\s-]+doente|denuncia[\\s-]+social|mensagem[\\s-]+social|critica[\\s-]+social|abismo[\\s-]+social|classe[\\s-]+social|marginalizados|desigualdade|capitalismo|privilegio|engajado|lacracao|opressao'], "tags": {'social commentary': 1.0}},
    'expr: space': {"padroes": ['exploracao[\\s-]+espacial|estacao[\\s-]+espacial|viagem[\\s-]+espacial|espaco[\\s-]+sideral|nave[\\s-]+espacial|outro[\\s-]+planeta|buraco[\\s-]+negro|astronautas|astronauta|espacial|planetas|universo|foguete|galaxia|sideral|espaco|naves|space'], "tags": {'space': 1.0}},
    'expr: sports': {"padroes": ['final[\\s-]+do[\\s-]+campeonato|time[\\s-]+de[\\s-]+futebol|futebol[\\s-]+americano|jogo[\\s-]+decisivo|campeonato|olimpiadas|treinador|basquete|esportes|atletas|corrida|esporte|futebol|atleta|sports|volei'], "tags": {'sports': 1.0}},
    'expr: stylized': {"padroes": ['cinema[\\s-]+de[\\s-]+autor[\\s-]+visual|estilo[\\s-]+visual[\\s-]+forte|estilo[\\s-]+de[\\s-]+diretor|cheio[\\s-]+de[\\s-]+estilo|estetica[\\s-]+marcante|visual[\\s-]+de[\\s-]+hq|direcao[\\s-]+estilosa|estetica[\\s-]+propria|visual[\\s-]+exagerado|visual[\\s-]+estiloso|camera[\\s-]+lenta|visual[\\s-]+unico|luz[\\s-]+neon|estilizado|moderninho|videoclipe|descolado|estetica|estiloso|stylized'], "tags": {'stylized': 1.0}},
    'expr: superhero': {"padroes": ['heroi[\\s-]+de[\\s-]+quadrinho|universo[\\s-]+de[\\s-]+herois|equipe[\\s-]+de[\\s-]+herois|capa[\\s-]+e[\\s-]+uniforme|liga[\\s-]+de[\\s-]+herois|vigilante[\\s-]+mascarado|poderes[\\s-]+especiais|superpoderes|quadrinhos|superpoder|mascarado|superhero'], "tags": {'superhero': 1.0}},
    'expr: supernatural': {"padroes": ['poderes[\\s-]+sobrenaturais|coisas[\\s-]+do[\\s-]+alem|fenomeno[\\s-]+paranormal|forcas[\\s-]+ocultas|supernatural|mediunidade|entidades|exorcismo|ocultismo|demonios|maldicao|possuido|medium'], "tags": {'supernatural': 1.0}},
    'expr: surreal': {"padroes": ['estranho[\\s-]+e[\\s-]+onirico|fora[\\s-]+da[\\s-]+realidade|realidade[\\s-]+distorcida|viagem[\\s-]+de[\\s-]+acido|pesadelo[\\s-]+estranho|onirico[\\s-]+estranho|viagem[\\s-]+lisergica|sonho[\\s-]+maluco|mind[\\s-]+trip|bad[\\s-]+trip|alucinogeno|psicodelico|surrealismo|surrealista|distorcido|psicodelia|delirante|lynchiano|kafkiano|surreal'], "tags": {'surreal': 1.0}},
    'expr: survival': {"padroes": ['instinto[\\s-]+de[\\s-]+sobrevivencia|lutar[\\s-]+pra[\\s-]+sobreviver|acidente[\\s-]+de[\\s-]+aviao|perdido[\\s-]+no[\\s-]+espaco|preso[\\s-]+na[\\s-]+montanha|perdido[\\s-]+na[\\s-]+selva|luta[\\s-]+pela[\\s-]+vida|perdido[\\s-]+no[\\s-]+mar|ultimo[\\s-]+sobrevivente|floresta[\\s-]+perigosa|ilha[\\s-]+deserta|sem[\\s-]+agua|sobrevivencia|sobreviventes|sobrevivendo|sobreviver|avalanche|naufragio|selva'], "tags": {'survival': 1.0}},
    'expr: suspenseful': {"padroes": ['nao[\\s-]+sei[\\s-]+o[\\s-]+que[\\s-]+vai[\\s-]+acontecer|prende[\\s-]+do[\\s-]+inicio[\\s-]+ao[\\s-]+fim|quem[\\s-]+sera[\\s-]+o[\\s-]+culpado|segurar[\\s-]+ate[\\s-]+o[\\s-]+fim|misterio[\\s-]+e[\\s-]+suspense|suspense[\\s-]+de[\\s-]+verdade|cheio[\\s-]+de[\\s-]+suspense|tensao[\\s-]+e[\\s-]+misterio|muito[\\s-]+suspense|suspense[\\s-]+raiz|hitchcockiano|suspensezinho|imprevisivel|expectativa|suspenseful|whodunit|gancho'], "tags": {'suspenseful': 1.0}},
    'expr: tear jerker': {"padroes": ['acabar[\\s-]+com[\\s-]+meu[\\s-]+estoque[\\s-]+de[\\s-]+lenco|desidratar[\\s-]+de[\\s-]+tanto[\\s-]+chorar|lavar[\\s-]+a[\\s-]+alma[\\s-]+chorando|debulhar[\\s-]+em[\\s-]+lagrimas|chorar[\\s-]+ate[\\s-]+solucar|chorar[\\s-]+no[\\s-]+final|caixa[\\s-]+de[\\s-]+lenco|cair[\\s-]+no[\\s-]+choro|derramar[\\s-]+lagrimas|chorar[\\s-]+horrores|chorar[\\s-]+litros|chorar[\\s-]+muito|fazer[\\s-]+chorar|chorar[\\s-]+rios|tear[\\s-]+jerker|faz[\\s-]+chorar|tearjerker|lagrimas|chororo'], "tags": {'tear jerker': 1.0}},
    'expr: technology': {"padroes": ['dependencia[\\s-]+de[\\s-]+tecnologia|vicio[\\s-]+em[\\s-]+tecnologia|vale[\\s-]+do[\\s-]+silicio|tecnologia[\\s-]+perigosa|futuro[\\s-]+tecnologico|realidade[\\s-]+virtual|mundo[\\s-]+digital|redes[\\s-]+sociais|computadores|ciberespaco|cibernetico|tecnologico|technology|tecnologia|engenhoca|metaverso|gadgets|startup'], "tags": {'technology': 1.0}},
    'expr: teen movie': {"padroes": ['primeiro[\\s-]+amor[\\s-]+adolescente|festa[\\s-]+de[\\s-]+adolescente|high[\\s-]+school[\\s-]+movie|galera[\\s-]+da[\\s-]+escola|crush[\\s-]+da[\\s-]+escola|besteirol[\\s-]+americano|romance[\\s-]+adolescente|sessao[\\s-]+adolescente|drama[\\s-]+adolescente|teen[\\s-]+movie|adolescentes|adolescente|colegial'], "tags": {'teen movie': 1.0}},
    'expr: tense': {"padroes": ['tensao[\\s-]+do[\\s-]+comeco[\\s-]+ao[\\s-]+fim|nervos[\\s-]+a[\\s-]+flor[\\s-]+da[\\s-]+pele|na[\\s-]+ponta[\\s-]+da[\\s-]+cadeira|edge[\\s-]+of[\\s-]+the[\\s-]+seat|prender[\\s-]+a[\\s-]+respiracao|comer[\\s-]+as[\\s-]+unhas|roer[\\s-]+as[\\s-]+unhas|pulso[\\s-]+acelerado|ficar[\\s-]+nervoso|sem[\\s-]+respirar|suando[\\s-]+frio|suar[\\s-]+frio|estressante|agoniante|aflitivo|aflicao|nervoso|agonia|tensao|tense|tenso'], "tags": {'tense': 1.0}},
    'expr: thought-provoking': {"padroes": ['mexer[\\s-]+com[\\s-]+a[\\s-]+cabeca|expandir[\\s-]+a[\\s-]+mente|cheio[\\s-]+de[\\s-]+ideias|pano[\\s-]+pra[\\s-]+manga|abrir[\\s-]+a[\\s-]+mente|fora[\\s-]+da[\\s-]+caixa|thought[\\s-]+provoking|provoca[\\s-]+reflexao|discutir[\\s-]+depois|questionar[\\s-]+tudo|deixa[\\s-]+pensando|fazer[\\s-]+pensar|pensar[\\s-]+muito|faz[\\s-]+pensar|inteligente|provocativo|desafiador|instigante|pensar'], "tags": {'thought-provoking': 1.0}},
    'expr: time loop': {"padroes": ['mesmo[\\s-]+dia[\\s-]+se[\\s-]+repetindo|preso[\\s-]+no[\\s-]+mesmo[\\s-]+dia|dia[\\s-]+que[\\s-]+se[\\s-]+repete|mesmo[\\s-]+dia[\\s-]+de[\\s-]+novo|morre[\\s-]+e[\\s-]+recomeca|morrer[\\s-]+e[\\s-]+voltar|preso[\\s-]+num[\\s-]+ciclo|reiniciar[\\s-]+o[\\s-]+dia|dia[\\s-]+da[\\s-]+marmota|preso[\\s-]+no[\\s-]+tempo|loop[\\s-]+no[\\s-]+tempo|ciclo[\\s-]+infinito|eterno[\\s-]+retorno|loop[\\s-]+infinito|loop[\\s-]+temporal|time[\\s-]+loop|looping'], "tags": {'time loop': 1.0}},
    'expr: time travel': {"padroes": ['viajantes[\\s-]+do[\\s-]+tempo|voltar[\\s-]+pro[\\s-]+passado|alterar[\\s-]+o[\\s-]+passado|viajante[\\s-]+do[\\s-]+tempo|voltar[\\s-]+ao[\\s-]+passado|maquina[\\s-]+do[\\s-]+tempo|mudar[\\s-]+o[\\s-]+passado|viagem[\\s-]+no[\\s-]+tempo|viajar[\\s-]+no[\\s-]+tempo|voltar[\\s-]+no[\\s-]+tempo|salto[\\s-]+no[\\s-]+tempo|ir[\\s-]+pro[\\s-]+futuro|ir[\\s-]+ao[\\s-]+futuro|paradoxo[\\s-]+temporal|viagem[\\s-]+temporal|time[\\s-]+machine|time[\\s-]+travel|delorean|paradoxo'], "tags": {'time travel': 1.0}},
    'expr: touching': {"padroes": ['historia[\\s-]+de[\\s-]+vida[\\s-]+emocionante|mexe[\\s-]+com[\\s-]+a[\\s-]+gente|emocionar[\\s-]+de[\\s-]+verdade|arrepiar[\\s-]+de[\\s-]+emocao|tocar[\\s-]+o[\\s-]+coracao|no[\\s-]+na[\\s-]+garganta|deixar[\\s-]+emocionado|toca[\\s-]+a[\\s-]+alma|olhos[\\s-]+marejados|emocao[\\s-]+forte|mexer[\\s-]+comigo|mexeu[\\s-]+comigo|emocao[\\s-]+pura|emocionante|comovente|emocionar|delicado|sensivel|tocante|moving|tocar'], "tags": {'touching': 1.0}},
    'expr: true story': {"padroes": ['based[\\s-]+on[\\s-]+a[\\s-]+true[\\s-]+story|baseado[\\s-]+em[\\s-]+historia[\\s-]+real|historia[\\s-]+real[\\s-]+impressionante|baseado[\\s-]+em[\\s-]+fatos[\\s-]+reais|aconteceu[\\s-]+de[\\s-]+verdade|inspirado[\\s-]+em[\\s-]+fatos|personagem[\\s-]+real|fato[\\s-]+historico|caso[\\s-]+veridico|historia[\\s-]+real|fatos[\\s-]+reais|caso[\\s-]+real|reconstituicao|vida[\\s-]+real|cinebiografia|biografia|veridico|biopic'], "tags": {'true story': 1.0}},
    'expr: twist ending': {"padroes": ['cair[\\s-]+o[\\s-]+queixo[\\s-]+no[\\s-]+final|final[\\s-]+de[\\s-]+cair[\\s-]+o[\\s-]+queixo|nao[\\s-]+esperava[\\s-]+esse[\\s-]+final|final[\\s-]+que[\\s-]+muda[\\s-]+tudo|final[\\s-]+com[\\s-]+reviravolta|reviravolta[\\s-]+no[\\s-]+final|surpresa[\\s-]+no[\\s-]+final|virada[\\s-]+no[\\s-]+final|final[\\s-]+surpreendente|final[\\s-]+bombastico|final[\\s-]+inesperado|final[\\s-]+enganador|revelacao[\\s-]+final|final[\\s-]+chocante|ninguem[\\s-]+espera|twist[\\s-]+ending|plot[\\s-]+twist|twistzinho|twist'], "tags": {'twist ending': 1.0}},
    'expr: twists & turns': {"padroes": ['ninguem[\\s-]+e[\\s-]+o[\\s-]+que[\\s-]+parece|jogo[\\s-]+de[\\s-]+gato[\\s-]+e[\\s-]+rato|nada[\\s-]+e[\\s-]+o[\\s-]+que[\\s-]+parece|trama[\\s-]+cheia[\\s-]+de[\\s-]+voltas|cheio[\\s-]+de[\\s-]+reviravoltas|mentiras[\\s-]+e[\\s-]+revelacoes|monte[\\s-]+de[\\s-]+reviravolta|cheio[\\s-]+de[\\s-]+camadas|twists[\\s-]+and[\\s-]+turns|muitas[\\s-]+reviravoltas|varias[\\s-]+reviravoltas|trama[\\s-]+imprevisivel|enredo[\\s-]+intrincado|gato[\\s-]+e[\\s-]+rato|muitas[\\s-]+surpresas|vira[\\s-]+e[\\s-]+mexe|trama[\\s-]+complexa|reviravoltas|intrigante|revelacoes|enganacao'], "tags": {'twists & turns': 1.0}},
    'expr: underdog': {"padroes": ['contra[\\s-]+todas[\\s-]+as[\\s-]+probabilidades|provar[\\s-]+que[\\s-]+estavam[\\s-]+errados|contra[\\s-]+tudo[\\s-]+e[\\s-]+todos|perdedores[\\s-]+que[\\s-]+vencem|davi[\\s-]+contra[\\s-]+golias|historia[\\s-]+de[\\s-]+azarao|vencer[\\s-]+contra[\\s-]+tudo|loser[\\s-]+que[\\s-]+vence|baixo[\\s-]+pra[\\s-]+cima|improvavel[\\s-]+vencedor|ninguem[\\s-]+acreditava|saiu[\\s-]+do[\\s-]+nada|zero[\\s-]+ao[\\s-]+topo|ultimo[\\s-]+colocado|virada[\\s-]+epica|desacreditado|rejeitados|azarao|virada|zebra'], "tags": {'underdog': 1.0}},
    'expr: unlikely friendships': {"padroes": ['amizade[\\s-]+entre[\\s-]+diferentes|rico[\\s-]+e[\\s-]+pobre[\\s-]+amigos|duas[\\s-]+pessoas[\\s-]+diferentes|amizade[\\s-]+com[\\s-]+alienigena|inimigos[\\s-]+viram[\\s-]+amigos|amizade[\\s-]+com[\\s-]+monstro|idoso[\\s-]+e[\\s-]+crianca|velho[\\s-]+e[\\s-]+crianca|unlikely[\\s-]+friendship|amizade[\\s-]+improvavel|amizade[\\s-]+inesperada|humano[\\s-]+e[\\s-]+robo|mundos[\\s-]+diferentes|amizade[\\s-]+estranha|buddy[\\s-]+improvavel|dupla[\\s-]+improvavel|cao[\\s-]+e[\\s-]+gato|dupla[\\s-]+inusitada|dupla[\\s-]+dinamica|odd[\\s-]+couple'], "tags": {'unlikely friendships': 1.0}},
    'expr: vampires': {"padroes": ['cacadores[\\s-]+de[\\s-]+vampiros|criaturas[\\s-]+da[\\s-]+noite|mordida[\\s-]+no[\\s-]+pescoco|bebedor[\\s-]+de[\\s-]+sangue|vampiro[\\s-]+romantico|vampiros[\\s-]+modernos|imortal[\\s-]+sedento|vampiro[\\s-]+gotico|chupar[\\s-]+sangue|conde[\\s-]+dracula|sugar[\\s-]+sangue|transilvania|sanguessuga|vampiresco|vampirismo|vampiros|vampira|vampiro'], "tags": {'vampires': 1.0}},
    'expr: visceral': {"padroes": ['embrulhar[\\s-]+o[\\s-]+estomago|embrulhe[\\s-]+o[\\s-]+estomago|pancada[\\s-]+no[\\s-]+estomago|soco[\\s-]+no[\\s-]+estomago|brutalmente[\\s-]+honesto|sentir[\\s-]+na[\\s-]+pele|intenso[\\s-]+e[\\s-]+cru|doi[\\s-]+no[\\s-]+corpo|estomago[\\s-]+revirado|angustia[\\s-]+fisica|gut[\\s-]+wrenching|sem[\\s-]+filtro|agressividade|na[\\s-]+carne|dilacerante|impactante|agressivo|atropelar|rasgante|visceral'], "tags": {'visceral': 1.0}},
    'expr: visually stunning': {"padroes": ['cada[\\s-]+cena[\\s-]+e[\\s-]+um[\\s-]+quadro|efeitos[\\s-]+visuais[\\s-]+incriveis|so[\\s-]+fotografia[\\s-]+bonita|beautiful[\\s-]+cinematography|quadro[\\s-]+em[\\s-]+movimento|colirio[\\s-]+pros[\\s-]+olhos|encher[\\s-]+os[\\s-]+olhos|visualmente[\\s-]+incrivel|foco[\\s-]+no[\\s-]+visual|fotografia[\\s-]+incrivel|bonito[\\s-]+de[\\s-]+ver|espetaculo[\\s-]+visual|visually[\\s-]+stunning|fotografia[\\s-]+linda|paisagens[\\s-]+lindas|efeitos[\\s-]+visuais|imagens[\\s-]+lindas|cenas[\\s-]+lindas|visual[\\s-]+lindo|cinematografia|eye[\\s-]+candy|deslumbrante|fotografia'], "tags": {'visually stunning': 1.0}},
    'expr: war': {"padroes": ['campo[\\s-]+de[\\s-]+batalha|guerra[\\s-]+do[\\s-]+vietna|primeira[\\s-]+guerra|segunda[\\s-]+guerra|trincheiras|bombardeio|trincheira|militares|batalhas|batalha|combate|invasao|militar|pelotao|soldado|tanques|front'], "tags": {'war': 1.0}},
    'expr: whimsical': {"padroes": ['crianca[\\s-]+por[\\s-]+dentro|cheio[\\s-]+de[\\s-]+fantasia|magico[\\s-]+e[\\s-]+colorido|cheio[\\s-]+de[\\s-]+magia|magico[\\s-]+e[\\s-]+fofo|fantasia[\\s-]+delicada|mundo[\\s-]+encantado|fantasia[\\s-]+leve|mundo[\\s-]+magico|fabula[\\s-]+fofa|encantamento|imaginativo|maravilhoso|caprichoso|encantador|fantasioso|imaginacao|encantado|whimsical|sonhador|fabula|ludico'], "tags": {'whimsical': 1.0}},
    'expr: witty': {"padroes": ['inteligente[\\s-]+e[\\s-]+engracado|escrito[\\s-]+e[\\s-]+engracado|comedia[\\s-]+de[\\s-]+dialogo|dialogos[\\s-]+espertos|humor[\\s-]+inteligente|respostas[\\s-]+rapidas|dialogos[\\s-]+afiados|humor[\\s-]+britanico|dialogo[\\s-]+afiado|humor[\\s-]+refinado|humor[\\s-]+esperto|lingua[\\s-]+afiada|sarcasmo[\\s-]+fino|boas[\\s-]+sacadas|ironia[\\s-]+fina|espirituoso|trocadilhos|trocadilho|banter|clever|sagaz|witty'], "tags": {'witty': 1.0}},
    'expr: zombies': {"padroes": ['pandemia[\\s-]+de[\\s-]+zumbi|ataque[\\s-]+de[\\s-]+zumbis|cidade[\\s-]+de[\\s-]+zumbis|the[\\s-]+walking[\\s-]+dead|horda[\\s-]+de[\\s-]+zumbis|morto[\\s-]+que[\\s-]+anda|cadaveres[\\s-]+andando|apocalipse[\\s-]+zumbi|epidemia[\\s-]+zumbi|zumbi[\\s-]+correndo|mortos[\\s-]+vivos|walking[\\s-]+dead|virus[\\s-]+zumbi|contaminados|infectados|undead|zumbis|horda|zumbi'], "tags": {'zombies': 1.0}},
}
# <<< EXTRAS_V8

def _juntar(antiga, nova):
    """Junta duas entradas com o mesmo nome: padrões somados (sem repetir) e o maior peso de cada etiqueta."""
    j = dict(antiga)
    j["padroes"] = list(antiga["padroes"]) + [p for p in nova["padroes"] if p not in antiga["padroes"]]
    for campo in ("tags", "evita"):
        if campo in antiga or campo in nova:
            d = dict(antiga.get(campo, {}))
            for t, w in nova.get(campo, {}).items():
                d[t] = max(d.get(t, 0), w)
            j[campo] = d
    for k, v in nova.items():
        if k not in ("padroes", "tags", "evita"):
            j[k] = v
    return j


def montar():
    """Junta temas e extras: nome -> {"padroes": [...], "tags": {etiqueta: peso}, ["evita"], [flags]}."""
    d = {}
    for tema, tags in MAPA_TEMAS.items():
        padroes = [p for p in DICIONARIO[tema]["padroes"] if p not in PADROES_REMOVIDOS.get(tema, [])]
        d[tema] = {"padroes": padroes, "tags": tags}
    d.update(EXTRAS)
    for nome, e in EXTRAS_V2.items():
        d[nome] = _juntar(d[nome], e) if nome in d else e
    for nome, e in EXTRAS_V8.items():  # v8: expressões em massa (expressoes.py)
        d[nome] = _juntar(d[nome], e) if nome in d else e
    return d


DICIONARIO_TAGS = montar()


def conferir():
    import pandas as pd
    vocab = set(pd.read_csv("vocabulario_piloto.csv").tag)
    problemas = []
    for nome, e in DICIONARIO_TAGS.items():
        for campo in ("tags", "evita"):
            for tag, peso in e.get(campo, {}).items():
                if tag not in vocab:
                    problemas.append(f"{nome}: etiqueta '{tag}' ({campo}) não está no vocabulário")
                # as expressões da rodada 2 usam pesos a partir de 0,4 ("amor próprio": social commentary 0,4)
                if not 0.3 <= peso <= 1:
                    problemas.append(f"{nome}: peso {peso} fora de 0,3-1 em '{tag}' ({campo})")
    for termo, tags in TAGS_POR_TERMO.items():
        for tag, peso in tags.items():
            if tag not in vocab:
                problemas.append(f"termo negável '{termo}': etiqueta '{tag}' não está no vocabulário")
            if not 0.5 <= peso <= 1:
                problemas.append(f"termo negável '{termo}': peso {peso} fora de 0,5-1")
    faltam_temas = [t for t in DICIONARIO if t not in MAPA_TEMAS]
    usadas = {t for e in DICIONARIO_TAGS.values() for t in e["tags"]}
    print(f"{len(DICIONARIO_TAGS)} entradas ({len(MAPA_TEMAS)} temas do dicionario.py + {len(EXTRAS)} extras "
          f"+ {len(EXTRAS_V2)} da rodada 2, uma delas juntada a um tema que já existia); "
          f"{len(usadas)} das {len(vocab)} etiquetas do vocabulário são usadas.")
    print("Temas do dicionario.py sem mapeamento:", faltam_temas or "nenhum")
    print("Problemas:", problemas or "nenhum")


if __name__ == "__main__":
    conferir()
