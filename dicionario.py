"""
Dicionário feito à mão para o motor de recomendação.

Como ler:
- Os "padroes" são começos de palavras em português, sem acento e em minúsculas.
  Ex.: "chor" casa com "chorar", "choro", "chorando".
  Um "\\b" no fim quer dizer "a palavra termina aqui" (ex.: "rir\\b" não casa com "rirmos").
- As "palavras_chave" são termos em inglês que existem na coluna palavras_chave do filmes.csv.

Para conferir quantos filmes têm cada termo (e se algum não existe):
    python dicionario.py
"""

# ---------------------------------------------------------------------------
# 1) Gêneros: palavras do pedido -> nome do gênero na coluna "generos" (filtro nos dados)
# ---------------------------------------------------------------------------

GENEROS = {
    "Terror": ["terror", "horror"],
    "Comédia": ["comedia", "engracad", "rir\\b", "risada", "humor", "zoeira", "zueira", "besteirol"],
    "Animação": ["animac", "animad", "desenho", "anime\\b"],
    "Guerra": ["guerra"],
    "Romance": ["romance", "romantic"],
    "Ficção científica": ["ficcao cientifica", "sci-?fi"],
    "Ação": ["acao\\b", "porrada", "pancadaria"],
    "Thriller": ["suspense", "thriller"],
    "Drama": ["drama"],
    "Aventura": ["aventura"],
    "Fantasia": ["fantasia"],
    "Crime": ["policial", "crime\\b"],
    "Mistério": ["misterio"],
    "Família": ["familia", "crianc", "infantil"],
    "História": ["historic", "de epoca"],
    "Música": ["musical"],
    "Faroeste": ["faroeste", "velho oeste", "western"],
    "Documentário": ["documentario"],
}

# ---------------------------------------------------------------------------
# 2) Temas e sentimentos: palavras do pedido -> palavras-chave em inglês
# ---------------------------------------------------------------------------

DICIONARIO = {
    "chorar / emocionante": {
        "padroes": ["chor", "emocion", "triste", "comovent", "lagrima"],
        "palavras_chave": ["tearjerker", "tears", "sadness", "tragic", "tragedy", "heartbreak", "sentimental",
                           "melancholy", "melodramatic", "depressing", "grief", "dying and death", "loss of loved one"],
    },
    "tenso": {
        "padroes": ["tens", "prende", "agonia", "angusti", "nervos", "adrenalina"],
        "palavras_chave": ["tense", "intense", "suspenseful", "anxious", "race against time", "psychological thriller",
                           "paranoia", "frantic", "desperate"],
    },
    "maluco / confuso": {
        "padroes": ["maluc", "louc", "doid", "bizarr", "estranh", "surreal", "confus", "confund"],
        "palavras_chave": ["surrealism", "surreal", "absurd", "madness", "insanity", "hallucination",
                           "alternative reality", "dream world", "nonlinear timeline", "unreliable narrator",
                           "split personality", "mind game", "complex", "reality vs fantasy"],
    },
    "pensar / reflexivo": {
        "padroes": ["pensa", "reflex", "filosof", "profund"],
        "palavras_chave": ["philosophical", "thoughtful", "reflective", "introspective", "existentialism",
                           "ambiguous", "complex", "philosophy", "existential crisis"],
    },
    "leve / alto astral": {
        "padroes": ["leve\\b", "levinho", "descontra", "relaxa", "alto astral", "fofo", "feel good"],
        "palavras_chave": ["lighthearted", "feelgood", "cheerful", "playful", "comforting", "joyful", "joyous",
                           "whimsical", "heart warming", "hopeful"],
    },
    "rir / engraçado": {
        "padroes": ["rir\\b", "risada", "engracad", "hilari", "zoeira", "zueira", "besteirol", "comedia", "humor"],
        "palavras_chave": ["hilarious", "amused", "absurd", "slapstick comedy", "buddy comedy", "parody", "satire",
                           "witty", "ridiculous", "prank", "teen comedy"],
    },
    "amizade": {
        "padroes": ["amizade", "amigo", "amiga", "parceri", "parceiro", "companheir"],
        "palavras_chave": ["friendship", "friends", "best friend", "male friendship", "female friendship",
                           "unlikely friendship", "buddy", "buddy cop", "buddy comedy", "group of friends"],
    },
    "pessoas diferentes": {
        "padroes": ["diferente", "oposto", "improvav"],
        "palavras_chave": ["unlikely friendship", "culture clash", "fish out of water", "interracial friendship",
                           "odd one out"],
    },
    "solidão": {
        "padroes": ["solid", "sozinh", "isolad", "isolament", "solitari"],
        "palavras_chave": ["loneliness", "isolation", "social isolation", "alone", "stranded", "castaway",
                           "trapped in space"],
    },
    "trauma": {
        "padroes": ["trauma", "traumat"],
        "palavras_chave": ["trauma", "post-traumatic stress disorder (ptsd)", "childhood trauma", "war trauma",
                           "traumatic past", "mental illness", "psychological drama", "survivor's guilt",
                           "healing", "psychological healing"],
    },
    "superação": {
        "padroes": ["supera", "volta por cima", "vencer", "inspira"],
        "palavras_chave": ["inspirational", "inspiring story", "underdog", "comeback", "against the odds",
                           "beating the odds", "determination", "overcoming fears", "hopeful"],
    },
    "perda / luto": {
        "padroes": ["perd", "luto", "faleci", "viuv", "seguir em frente", "ente querido"],
        "palavras_chave": ["loss of loved one", "grief", "mourning", "widow", "widower", "dying and death",
                           "death", "loss"],
    },
    "reviravolta / final inesperado": {
        "padroes": ["reviravolt", "plot twist", "final inesperad", "ninguem espera", "surpreend", "inesperad", "twist"],
        "palavras_chave": ["plot twist", "twist ending", "twist", "surprise-ending", "unreliable narrator", "shocking",
                           "mind game", "deception", "split personality", "dissociative identity disorder"],
    },
    "máfia": {
        "padroes": ["mafi", "gangster", "crime organizado", "chefao"],
        "palavras_chave": ["mafia", "gangster", "organized crime", "mobster", "crime boss", "mafia boss",
                           "sicilian mafia", "mob boss", "crime family", "godfather"],
    },
    "assalto / golpe": {
        "padroes": ["assalt", "roubo", "golpe", "ladra", "ladro", "furto", "planejad"],
        "palavras_chave": ["heist", "robbery", "bank robbery", "thief", "con artist", "con man", "heist gone wrong",
                           "bank heist", "casino heist", "diamond heist", "criminal mastermind"],
    },
    "viagem no tempo": {
        "padroes": ["viage\\w* no tempo", "viajar no tempo", "volta no tempo", "loop temporal"],
        "palavras_chave": ["time travel", "time loop", "time machine", "time paradox", "time warp",
                           "alternate timeline", "time-manipulation"],
    },
    "sobrevivência": {
        "padroes": ["sobreviv", "naufrag"],
        "palavras_chave": ["survival", "struggle for survival", "wilderness survival", "survival thriller",
                           "fight for survival", "stranded", "castaway", "man vs nature", "human vs nature",
                           "plane crash", "airplane crash", "stranded at sea"],
    },
    "natureza": {
        "padroes": ["natureza", "selva", "floresta", "montanha", "oceano", "deserto", "ilha\\b", "neve\\b"],
        "palavras_chave": ["nature", "wilderness", "jungle", "forest", "mountain", "ocean", "sea", "desert",
                           "island", "snow", "mountain climbing", "wild animal"],
    },
    "inteligência artificial": {
        "padroes": ["inteligencia artificial", "ia\\b", "robo", "androide", "maquina"],
        "palavras_chave": ["artificial intelligence (a.i.)", "robot", "android", "humanoid robot", "cyborg",
                           "man vs machine", "transhumanism", "sentient robot", "human android relationship"],
    },
    "o que é ser humano": {
        "padroes": ["humano", "humanidade", "consciencia", "identidade"],
        "palavras_chave": ["humanity", "transhumanism", "identity", "consciousness", "existentialism",
                           "human clone", "quest for identity", "compassionate", "empathetic"],
    },
    "carros / corrida": {
        "padroes": ["carro", "corrida", "racha", "velocidade"],
        "palavras_chave": ["car race", "street race", "cars", "car crash", "race car driver", "racing", "sports car",
                           "getaway driver", "chase", "police chase", "car racing", "street racing", "motorsport"],
    },
    "mulheres fortes": {
        "padroes": ["mulher\\w* fort", "protagonista feminina", "heroina", "guerreira"],
        "palavras_chave": ["strong woman", "female protagonist", "female hero", "warrior woman", "female empowerment",
                           "female warrior", "female assassin", "female soldier"],
    },
    "guerra / soldados": {
        "padroes": ["soldad", "guerra", "batalha", "combate", "exercito", "militar"],
        "palavras_chave": ["war", "world war ii", "world war i", "soldier", "soldiers", "battlefield", "vietnam war",
                           "army", "military", "anti war", "war veteran", "combat", "prisoner of war", "battle"],
    },
    "esporte": {
        "padroes": ["esport", "futebol", "basquete", "boxe", "lutador", "atleta", "campeo", "treinador", "olimpi"],
        "palavras_chave": ["sports", "boxing", "basketball", "american football", "football (soccer)", "baseball",
                           "racing", "world champion", "boxing champion", "olympic games", "underdog",
                           "sport competition", "coaching", "head coach", "rivalry"],
    },
    "história real": {
        "padroes": ["historia real", "historias reais", "fatos reais", "baseado em fatos", "biografi"],
        "palavras_chave": ["based on true story", "biography", "true crime", "biographical", "biographical drama"],
    },
    "super-herói": {
        "padroes": ["super.?heroi", "quadrinho", "hq\\b"],
        "palavras_chave": ["superhero", "based on comic", "super power", "superhero team", "masked superhero",
                           "vigilante", "secret identity", "supervillain", "super villain",
                           "marvel cinematic universe (mcu)", "dc extended universe (dceu)"],
    },
    "sombrio / pesado": {
        "padroes": ["sombri", "obscur", "dark\\b", "pesad", "perturbad"],
        "palavras_chave": ["dark", "grimdark", "darkness", "dark hero", "neo-noir", "brutality", "violence",
                           "disturbed", "bleak", "depressing", "tragic hero", "tragic villain", "anti hero"],
    },
    "vilão": {
        "padroes": ["vilao", "viloes", "vila\\b", "vilan"],
        "palavras_chave": ["villain", "super villain", "supervillain", "female villain", "psychopath",
                           "criminal mastermind", "evil mastermind", "archvillain"],
    },
    "luta / porrada": {
        "padroes": ["porrada", "pancadaria", "luta", "briga", "artes marciais", "kung fu", "soco"],
        "palavras_chave": ["martial arts", "fight", "hand to hand combat", "fistfight", "kung fu", "shootout",
                           "gunfight", "action hero", "bar fight", "underground fighting", "sword fight",
                           "mixed martial arts (mma)"],
    },
    "medo": {
        "padroes": ["medo", "assust", "apavor", "arrepi", "sinistr", "macabr"],
        "palavras_chave": ["frightened", "horrified", "fear", "supernatural horror", "psychological horror",
                           "sinister", "macabre", "dread", "creepy", "haunted house", "demonic possession",
                           "possession", "demon", "ghost", "ominous"],
    },
    "susto": {
        "padroes": ["susto"],
        "palavras_chave": ["jump scare", "slasher"],
    },
    "sangue / violência": {
        "padroes": ["sangue", "sangrent", "gore\\b", "violent", "violenc", "brutal", "nojent"],
        "palavras_chave": ["gore", "blood and gore", "bloody", "violence", "extreme violence", "brutality",
                           "brutal violence", "torture", "sadistic horror", "body horror", "extreme gore"],
    },
    "criança / família": {
        "padroes": ["crianc", "infantil", "familia", "filhos", "pequenos"],
        "palavras_chave": ["kids", "family", "children's adventure", "based on children's book", "talking animal",
                           "cartoon", "anthropomorphism", "animals", "pets", "fairy tale"],
    },
    "romance / amor": {
        "padroes": ["romance", "romantic", "amor\\b", "amoros", "paixao", "namor", "apaixon"],
        "palavras_chave": ["romance", "love", "falling in love", "romantic", "romcom", "love of one's life",
                           "first love", "true love", "love at first sight", "love triangle", "forbidden love",
                           "new love", "wedding"],
    },
    "aventura": {
        "padroes": ["aventur", "explorac", "tesouro", "jornada", "expedic"],
        "palavras_chave": ["adventurer", "adventure", "treasure hunt", "treasure", "quest", "journey",
                           "swashbuckler", "pirate", "jungle adventure", "expedition"],
    },
    "espaço": {
        "padroes": ["espac", "astronaut", "planeta", "galaxi", "nave\\b", "naves\\b"],
        "palavras_chave": ["space", "space travel", "spacecraft", "astronaut", "space station", "spaceship",
                           "space mission", "space adventure", "alien planet", "planet", "space opera",
                           "trapped in space", "moon", "planet mars"],
    },
    "alienígena": {
        "padroes": ["alien", "extraterrest", "et\\b"],
        "palavras_chave": ["alien", "alien invasion", "alien life-form", "alien contact"],
    },
    "zumbi": {
        "padroes": ["zumbi", "zombie", "morto.vivo", "mortos.vivos"],
        "palavras_chave": ["zombie", "zombie apocalypse"],
    },
    "vampiro": {
        "padroes": ["vampir"],
        "palavras_chave": ["vampire", "vampire hunter (slayer)"],
    },
    "fantasma / espírito": {
        "padroes": ["fantasm", "espirito", "assombr", "casa mal"],
        "palavras_chave": ["ghost", "haunted house", "haunting", "possession", "demonic possession", "demon"],
    },
    "serial killer": {
        "padroes": ["serial killer", "assassino em serie", "psicopata"],
        "palavras_chave": ["serial killer", "psychopath", "killer", "slasher"],
    },
    "vingança": {
        "padroes": ["vinga"],
        "palavras_chave": ["revenge", "vigilante", "vigilante justice", "rape and revenge", "revenge thriller"],
    },
    "espionagem": {
        "padroes": ["espia\\b", "espiao", "espioes", "espionagem", "agente secreto"],
        "palavras_chave": ["spy", "secret agent", "central intelligence agency (cia)", "mi6", "undercover"],
    },
    "prisão / fuga": {
        "padroes": ["prisao", "presidio", "cadeia", "fuga\\b", "escapar"],
        "palavras_chave": ["prison", "prison escape", "escape", "prisoner", "imprisonment"],
    },
    "escola / adolescência": {
        "padroes": ["escola", "colegio", "adolescen", "ensino medio", "faculdade"],
        "palavras_chave": ["high school", "school", "teenager", "coming of age", "teen movie", "high school student",
                           "college", "teen comedy", "teen drama"],
    },
    "natal": {
        "padroes": ["natal\\b", "natalin"],
        "palavras_chave": ["christmas", "christmas eve", "christmas party", "holiday"],
    },
    "cachorro / animais": {
        "padroes": ["cachorr", "cao\\b", "caes\\b", "animais", "bichinho"],
        "palavras_chave": ["dog", "animals", "talking animal", "pets", "human animal relationship"],
    },
    "magia / bruxaria": {
        "padroes": ["magia", "magic", "bruxa", "bruxo", "feitic", "mago\\b"],
        "palavras_chave": ["magic", "witch", "wizard", "school of witchcraft", "magical creature", "wizardry",
                           "black magic"],
    },
    "medieval / dragões": {
        "padroes": ["dragao", "dragoes", "medieval", "reino", "cavaleir", "espada"],
        "palavras_chave": ["dragon", "kingdom", "castle", "sword fight", "sword", "fantasy world", "dark fantasy",
                           "quest"],
    },
    "fim do mundo / distopia": {
        "padroes": ["apocalip", "fim do mundo", "distopi", "pos.apocal"],
        "palavras_chave": ["dystopia", "post-apocalyptic future", "end of the world", "apocalypse",
                           "zombie apocalypse", "dark future"],
    },
    "futuro / tecnologia": {
        "padroes": ["futur", "tecnolog", "cyberpunk", "virtual"],
        "palavras_chave": ["future", "technology", "cyberpunk", "virtual reality", "tech noir"],
    },
    "sonho / realidade / memória": {
        "padroes": ["sonho", "realidade", "mente\\b", "memoria", "lembranc"],
        "palavras_chave": ["dreams", "dream world", "alternative reality", "virtual reality",
                           "memory", "memory loss", "false memory", "implanted memory", "amnesia"],
    },
    "investigação": {
        "padroes": ["detetive", "investiga", "quem matou", "assassinato"],
        "palavras_chave": ["detective", "investigation", "murder", "whodunit", "murder mystery", "police", "fbi",
                           "crime scene", "crime investigation"],
    },
    "conspiração / política": {
        "padroes": ["conspira", "politic", "governo", "presidente"],
        "palavras_chave": ["conspiracy", "conspiracy thriller", "political thriller", "corruption", "usa president",
                           "surveillance"],
    },
    "drogas": {
        "padroes": ["droga", "traficant", "cartel", "viciad"],
        "palavras_chave": ["drugs", "drug dealer", "drug addiction", "drug cartel", "alcoholism", "drug crime"],
    },
    "música / dança": {
        "padroes": ["music", "danc", "cantor", "cantora"],
        "palavras_chave": ["musical", "singer", "dancing", "concert"],
    },
    "pais e filhos": {
        "padroes": ["pai e filh", "mae e filh", "pai\\b", "mae\\b"],
        "palavras_chave": ["father son relationship", "father daughter relationship", "mother son relationship",
                           "mother daughter relationship", "parent child relationship", "single father",
                           "single mother"],
    },
    "viagem / estrada": {
        "padroes": ["road trip", "pe na estrada", "viagem de carro"],
        "palavras_chave": ["road trip", "journey", "travel"],
    },
    "dinossauros": {
        "padroes": ["dinossaur"],
        "palavras_chave": ["dinosaur"],
    },
    "monstros": {
        "padroes": ["tubara", "monstro", "criatura"],
        "palavras_chave": ["shark", "shark attack", "creature", "monster", "giant monster", "kaiju", "animal attack",
                           "animal horror"],
    },
    "desastre": {
        "padroes": ["desastre", "catastrof", "terremoto", "tsunami", "furacao", "tempestade"],
        "palavras_chave": ["disaster", "disaster movie"],
    },
    "psicológico": {
        "padroes": ["psicolog", "mental\\b", "loucura"],
        "palavras_chave": ["psychological thriller", "psychological horror", "psychological drama", "mental illness",
                           "madness", "insanity", "paranoia", "obsession"],
    },
    "traição / ciúme": {
        "padroes": ["traic", "trai\\b", "ciume", "infiel"],
        "palavras_chave": ["betrayal", "infidelity", "jealousy", "deception"],
    },
    "casamento": {
        "padroes": ["casament", "noiv", "casad"],
        "palavras_chave": ["wedding", "marriage", "husband wife relationship", "married couple", "marriage crisis"],
    },
}

# Palavras-chave que descrevem o "formato" do filme e não o conteúdo. Ficam de fora quando
# o motor compara um filme citado ("tipo Matrix") com os outros.
PALAVRAS_META = ("stinger", "woman director", "sequel", "prequel", "remake", "reboot", "spin off", "based on ")


def conferir(arq_filmes="filmes.csv"):
    """Mostra quantos filmes têm cada termo do dicionário e avisa se algum não existe."""
    import collections
    import pandas as pd

    filmes = pd.read_csv(arq_filmes)
    contagem = collections.Counter(t for s in filmes.palavras_chave.dropna() for t in s.split("|"))
    faltando = []
    for tema, d in DICIONARIO.items():
        partes = []
        for termo in d["palavras_chave"]:
            n = contagem.get(termo, 0)
            partes.append(f"{termo} ({n})")
            if n == 0:
                faltando.append((tema, termo))
        print(f"- {tema}: " + ", ".join(partes))
    generos = set(g for s in filmes.generos for g in s.split("|"))
    for g in GENEROS:
        if g not in generos:
            faltando.append(("GENEROS", g))
    print(f"\n{len(DICIONARIO)} temas, {sum(len(d['palavras_chave']) for d in DICIONARIO.values())} termos.")
    print("Termos que NÃO existem nos dados:", faltando if faltando else "nenhum")
    return faltando


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    conferir()
