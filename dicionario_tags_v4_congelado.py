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
# Negado ("não seja americano"): sai o filme cujos países de produção são todos do grupo (ex.: só EUA).
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
     "|hollywood\\w*", "produção americana", "não é produção só americana", {"US": ["en"]}],
    ["frances\\w*", "filme francês", "não é produção só francesa", {"FR": ["fr"]}],
    ["italian\\w*", "filme italiano", "não é produção só italiana", {"IT": ["it"]}],
    ["alema\\w*", "filme alemão", "não é produção só alemã", {"DE": ["de"], "AT": ["de"]}],
    ["espanho\\w*", "filme espanhol", "não é produção só espanhola", {"ES": ["es", "ca"]}],
    ["japon\\w*", "filme japonês", "não é produção só japonesa", {"JP": ["ja"]}],
    ["sul-corean\\w*|corean\\w*", "filme coreano", "não é produção só coreana", {"KR": ["ko"]}],
    ["chines\\w*|hong kong", "filme chinês", "não é produção só chinesa", {"CN": ["zh", "cn"], "HK": ["cn", "zh"], "TW": ["zh"]}],
    ["indian\\w*|bollywood", "filme indiano", "não é produção só indiana",
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
""".split()
# Partículas de sobrenome ("Guillermo del Toro" -> sobrenome "del toro")
PARTICULAS_NOME = ["de", "del", "da", "di", "do", "dos", "das", "van", "von", "le", "la", "du", "der", "den", "mac", "st"]


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
