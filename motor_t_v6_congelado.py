"""
Motor T (etiquetas): usa etiquetas_unificadas.csv (Tag Genome + ml-32m + IA) e combina com os motores A
(palavras-chave) e B (sinopse). Catálogo: filmes_v2.csv (6.000 filmes). Sem IA rodando: só cruzamento de dados.

Usado pelo motor.py:  python motor.py T  |  python motor.py T <arquivo>  |  python motor.py T ajustar
"""
import collections
import datetime
import json
import os
import re
import unicodedata

import numpy as np
import pandas as pd

import motor as m
from dicionario import DICIONARIO, GENEROS
from dicionario_tags_v6_congelado import (  # versão congelada v6 (antes do teste cego da referência)
    ANTES_IDIOMA, CORRECOES_DIGITACAO, DICIONARIO_TAGS, ESTUDIOS, GIRIAS_BEM_AVALIADO,
                             IDIOMAS_T, NAO_SOBRENOME, PAISES, PALAVRAS_CHAVE_TMDB, PALAVRAS_VAZIAS_EXTRA, PARTICULAS_NOME,
                             PESSOA_CONTEXTO, SEM_DADOS, TAGS_POR_TERMO)

ARQ_FILMES_T = "filmes_v2.csv"
# Quando nada é reconhecido: primeiro a sinopse (similaridade mínima de 0,15, o mesmo limite escolhido
# no treino para o motor H); se nem isso, os filmes mais bem avaliados com o aviso leve abaixo.
LIMIAR_SINOPSE = m.LIMIAR_SIMILARIDADE
AVISO_LEVE = "Não entendi bem seu pedido, mas estes são filmes que agradam a quase todo mundo"
# Palavras de pedido que não dizem nada sobre o filme; ficam de fora da reserva por sinopse
PALAVRAS_DE_PEDIDO = set("""
sei la qualquer quaisquer coisa coisas recomenda recomende recomendar recomendacao sugere sugira sugerir sugestao
indica indique indicar indicacao dica dicas bom boa bons boas legal legais otimo otima assistir ver olhar agora
algum alguma alguns algumas algo filme filmes filminho quero queria gostaria pode poderia me mim voce voces
hoje noite dia tarde manda mande tanto faz nenhum nenhuma talvez sabe ai entao
""".split()) | set(PALAVRAS_VAZIAS_EXTRA)
ARQ_UNIFICADAS = "etiquetas_unificadas.csv"
ARQ_PESOS = "pesos_t.json"
PESOS_PADRAO = {"tags": 0.5, "a": 0.3, "b": 0.2}
TOP_N = m.TOP_N

# ---------------------------------------------------------------------------
# Negação do motor T (alcança listas separadas por vírgula; para em palavras que voltam ao positivo)
# ---------------------------------------------------------------------------
NEGACOES = {"nao", "sem", "nada", "nem"}
VOLTA_POSITIVO = {"tenha", "tem", "ter", "com", "mas", "porem", "quero", "queremos", "prefiro", "pode", "gosto"}


def negacao_t(texto, pos, janela=10):
    trecho = re.split(r"[.;!?]", texto[:pos])[-1]
    palavras = trecho.replace(",", " ").split()[-janela:]
    for i in range(len(palavras) - 1, -1, -1):
        p = palavras[i]
        if p in VOLTA_POSITIVO:
            return None
        if p in NEGACOES:
            return "nao_so" if any(q in ("so", "apenas", "somente") for q in palavras[i + 1:i + 3]) else "nao"
    return None


def achar_t(texto, padroes):
    """'sim' se algum padrão aparece sem negação; 'nao' se só aparece negado; None se não aparece."""
    sim = nao = False
    for padrao in padroes:
        for mt in re.finditer(r"\b(?:" + padrao + ")", texto):
            n = negacao_t(texto, mt.start())
            if n is None:
                sim = True
            elif n == "nao":
                nao = True
    return "sim" if sim else ("nao" if nao else None)


# ---------------------------------------------------------------------------
# Séries (para excluir a série do filme citado e para a diversidade do top 5)
# ---------------------------------------------------------------------------
ARTIGOS = r"^(the|a|an|o|a|os|as|le|la|les|el|los|il)\s+"


def chave_serie(titulo):
    t = m.sem_acento(titulo).strip()
    t = re.split(r"\s*[:(–]\s*|\s+-\s+", t)[0]
    t = re.sub(ARTIGOS, "", t)
    t = re.sub(r"[^a-z0-9 ]", "", t)
    t = re.sub(r"\s+(\d+|[ivx]+|parte? \w+|chapter \w+|capitulo \w+|vol \w+)$", "", t).strip()
    return t


def mesma_familia(k1, k2):
    if not k1 or not k2:
        return False
    if k1 == k2:
        return True
    curta, longa = sorted((k1, k2), key=len)
    return len(curta) >= 5 and longa.startswith(curta + " ")


# ===========================================================================
# Rodada de correções v3 (a partir do diagnóstico de estresse). Só o motor T; o motor A não muda.
# Todas as regras abaixo também existem em site/motor.js (exportadas em config.json).
# ===========================================================================
ANO_ATUAL = datetime.date.today().year
ANOS_RECENTE = 2            # "lançamento recente", "novo", "atual" = ano atual - 2 em diante
ANO_ANTIGO_MAX = 1979       # "antigo", "filme velho" = até 1979
ANO_MODERNO_MIN = 2010      # "moderno", "contemporâneo" = 2010 em diante
NOTA_BEM_AVALIADO = 7.5     # "bem avaliado", "nota alta", gírias ("topzera")
NOTA_ALEATORIO = 7.5        # "aleatório / surpreenda-me": sorteio entre os filmes com nota 7,5+
NOTA_POUCO_CONHECIDO = 7.0  # "pouco conhecido / obscuro": nota 7+ e votos abaixo da mediana do catálogo
DURACAO_NAO_LONGO = 120     # "não seja muito longo" = até 120 min
DURACAO_LONGO = 150         # "longo" = a partir de 150 min
PESO_PALAVRA_DO_TITULO = 0.1  # reserva por sinopse: palavra do pedido que está no título do filme vale 10%
MIN_LETRAS_CORRECAO = 6     # erro de digitação: só palavras de 6+ letras, distância de edição 1

# e) Referência: gatilhos ("como" e os outros só valem se vier um título conhecido depois)
GATILHOS_REFERENCIA_T = (r"\b(?:misturar|misturando|mistura de|mix de|cruzamento de|tipo|parecid[oa]s? com|similar(?:es)? (?:a|ao|com)|semelhantes? (?:a|ao)|igual (?:a|ao)"
                         r"|ao estilo d[eoa]s?|no estilo d[eoa]s?|no estilo|estilo d[eoa]s?|estilo|na vibe d[eoa]s?"
                         r"|na vibe|vibe d[eoa]s?|que lembr[ae]|lembra|lembrando|como)\s+")
ARTIGOS_REF = ["o", "a", "os", "as"]
# v6: referência dupla ("misturar Matrix com Titanic", "tipo Toy Story e Shrek"): só quando os dois lados são títulos
SEPARA_REF_DUPLA = r" e | com | mais | \+ "

# d) Streaming: nomes que valem sozinhos e apelidos que só valem depois de "na/no/tem na/que passe na..."
SERVICOS_T = [
    ["netflix", "netflix"], ["prime video", "prime video"], ["amazon", "amazon prime"],
    ["disney\\s*(?:\\+|plus)", "disney"], ["hbo", "hbo"], ["globoplay", "globoplay"], ["apple tv", "apple tv"],
    ["paramount", "paramount"], ["mubi", "mubi"], ["crunchyroll", "crunchyroll"],
]
APELIDOS_SERVICO = [["max", "hbo"], ["prime", "prime video"], ["disney", "disney"], ["globo", "globoplay"],
                    ["apple", "apple tv"]]
CONTEXTO_SERVICO = (r"(?:tem na|tem no|passe na|passe no|passa na|passa no|passando na|passando no|esteja na|esteja no"
                    r"|ta na|ta no|esta na|esta no|catalogo d[ao]|assinatura d[ao]|streaming d[ao]|na|no|pela|pelo|via)\s+")

# a) Nota
NOTA_REGRAS = [  # [regex, estrita?]  (o número é o grupo 1)
    [r"\b(?:nota|notas|avaliacao)\s+(?:acima|maior|mais|superior)\s+(?:de|que|a|do que)\s+(\d+(?:[.,]\d+)?)", True],
    [r"\b(?:nota|avaliacao)\s+(?:minima\s+(?:de\s+)?)?(\d+(?:[.,]\d+)?)\s*(?:\+|ou mais|para cima)", False],
    [r"\b(?:acima|mais) de (\d+(?:[.,]\d+)?)(?!\s*(?:h|min|ano|filme|vot|mil|pessoa|\d|[.,]\d|%))", True],
    [r"(?<![\w.,])(\d+(?:[.,]\d+)?)\s*\+", False],
]
BEM_AVALIADO = ["bem avaliad", "melhor(?:es)? avaliad", "nota alta", "notas altas", "nota boa", "boa nota",
                "bem votad"] + GIRIAS_BEM_AVALIADO

# b) Duração (minutos). Números explícitos primeiro; depois "não seja muito longo" e "longo".
DURACAO_ATE = [  # até N (inclusive)
    r"\b(?:ate|no maximo|maximo de)\s+(\d+)\s*(?:horas?|hrs?|h)\s*(?:e\s+(meia)|(?:e\s+)?(\d{1,2}))?",
    r"\b(?:ate|no maximo|maximo de)\s+(\d+)\s*(?:minutos|mins?)\b",
    r"(?<![\w.,])(\d)\s*(?:horas?|h)\s*(?:e\s+(meia)|(?:e\s+)?(\d{2}))?(?!\w)",
]
DURACAO_MAIS_DE = [
    r"\bmais de (\d+)\s*(?:horas?|hrs?|h)\s*(?:e\s+(meia)|(?:e\s+)?(\d{1,2}))?",
    r"\bmais de (\d+)\s*(?:minutos|mins?)\b",
]
HORA_E_MEIA = r"\b(?:uma )?hora e meia\b"
NAO_LONGO_ANTES = {"um", "uns", "uma", "umas", "de", "do", "da", "num", "numa", "o", "os"}
NAO_LONGO_DEPOIS = {"metragem", "metragens", "data", "vida", "distancia"}
LONGO_REFORCO = {"muito", "bem", "mais", "beem", "bem"}

# c) Época
EPOCA_RECENTE = [r"\b(?:lancamentos?|recentes?|novidades?|atua(?:l|is)|do momento|recem[- ]lancad\w*)\b",
                 r"\b(?:filmes?|algo|coisa|lancamento|bem|mais)\s+nov(?:inh)?[oa]s?\b", r"\bnovinh[oa]s?\b"]
EPOCA_ANTIGO = r"\bantig[oa]s?\b"
EPOCA_VELHO = r"\b(?:filmes?|algo|coisa|cinema|bem|mais|meio)\s+velh[oa]s?\b"
ANTIGO_NAO_ANTES = {"roma", "grecia", "egito", "mundo", "china", "india", "japao", "civilizacao", "testamento",
                    "oriente", "mesopotamia"}
ANTIGO_NAO_DEPOIS = {"egito", "testamento", "roma", "grecia", "mundo", "amigo", "amiga", "amigos", "amigas",
                     "namorado", "namorada"}
EPOCA_MODERNO = r"\b(?:modern[oa]s?|contemporane[oa]s?)\b"

# h) e j)
ALEATORIO = r"\b(?:aleatori\w*|surpreend\w*[ -]me|me surpreend\w*|sortei\w*|qualquer um|random)\b"
POUCO_CONHECIDO = (r"\b(?:pouco conhecid\w*|desconhecid\w*|obscur\w*|ninguem (?:conhece|viu)|pouca gente (?:conhece|viu)"
                   r"|poucos (?:conhecem|viram)|fora do radar)")

# f) Erros de digitação: correções da tabela (palavra inteira, maiores primeiro) + distância de edição 1
CORRECOES_ORDENADAS = sorted(CORRECOES_DIGITACAO.items(), key=lambda kv: (-len(kv[0]), kv[0]))


def _literais(padroes):
    return {w for p in padroes for w in re.findall(r"[a-z]{5,}", p)}


_PADROES_VOCAB = ([p for e in DICIONARIO_TAGS.values() for p in e["padroes"]] + list(TAGS_POR_TERMO)
                  + [p for d in DICIONARIO.values() for p in d["padroes"]] + [p for ps in GENEROS.values() for p in ps])
# Vocabulário do dicionário e dos gêneros (pedaços literais de 5+ letras dos padrões)
VOCAB_CORRECAO = sorted(_literais(_PADROES_VOCAB), key=lambda w: (-len(w), w))
# Tudo o que o motor reconhece: uma palavra coberta por algum destes padrões não é "desconhecida"
PADROES_COBERTURA = (_PADROES_VOCAB + list(m.IDIOMAS) + [p for p, _ in IDIOMAS_T]
                     + [p for p, _ in PALAVRAS_CHAVE_TMDB] + [p for p, _ in SEM_DADOS] + BEM_AVALIADO
                     + [p for p, _ in SERVICOS_T] + [p for p, _ in APELIDOS_SERVICO]
                     + EPOCA_RECENTE + [EPOCA_ANTIGO, EPOCA_VELHO, EPOCA_MODERNO, ALEATORIO, POUCO_CONHECIDO,
                                        r"long[oa]s?", r"curt[oa]s?"]
                     + [p[0] for p in PAISES] + [e[0] for e in ESTUDIOS])  # v4: países e estúdios


def distancia_1(a, b):
    """True se a e b diferem por no máximo 1 edição (troca, inclusão, exclusão ou inversão de 2 letras vizinhas)."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        dif = [i for i in range(la) if a[i] != b[i]]
        if len(dif) == 1:
            return True
        return len(dif) == 2 and dif[1] == dif[0] + 1 and a[dif[0]] == b[dif[1]] and a[dif[1]] == b[dif[0]]
    curta, longa = (a, b) if la < lb else (b, a)
    i = 0
    while i < len(curta) and curta[i] == longa[i]:
        i += 1
    return curta[i:] == longa[i + 1:]


def palavra_antes(texto, pos):
    p = re.findall(r"[a-z0-9]+", texto[:pos])
    return p[-1] if p else ""


def palavra_depois(texto, fim):
    p = re.findall(r"[a-z0-9]+", texto[fim:])
    return p[0] if p else ""


def numero(txt):
    return float(txt.replace(",", "."))


def subir_nota(filtros, valor, estrita):
    """Junta filtros de nota: fica o mais exigente."""
    atual = filtros.get("nota_min")
    if atual is None or valor > atual or (valor == atual and estrita):
        filtros["nota_min"] = valor
        filtros["nota_estrita"] = estrita


def resolver_ref(nome, f):
    """Índices do filme (ou franquia / lista à mão de pessoa) com esse nome; [] se não achar."""
    for alvo in [nome] + [a + " " + nome for a in ARTIGOS_REF]:
        exato = f.index[(f._tit == alvo) | (f._tit_orig == alvo) | (f._tit_curto == alvo)]
        if len(exato):
            return list(exato)
        if alvo in m.PESSOAS:
            return list(f.index[f.titulo.isin(m.PESSOAS[alvo])])
        franquia = f.index[f._tit.str.startswith(alvo + " ") | f._tit_orig.str.startswith(alvo + " ")]
        if len(franquia):
            return list(franquia)
    return []


def achar_referencia_t(t, f):
    """Como achar_referencia do motor A, com os gatilhos novos e o artigo opcional ("no estilo do Senhor dos Anéis").
    v6: se o nome não for um título, tenta dois títulos ("Matrix com Titanic") -> referência dupla.
    Devolve (nome digitado, índices dos filmes citados, grupos de índices: um por filme/franquia citado)."""
    for mt in re.finditer(GATILHOS_REFERENCIA_T, t):
        nome = re.split(r",| mas | so que | porem | e que ", t[mt.end():])[0].strip(" .!?")
        if not nome:
            continue
        idx = resolver_ref(nome, f)
        if idx:
            return nome, idx, [idx]
        for sep in re.finditer(SEPARA_REF_DUPLA, nome):
            n1, n2 = nome[:sep.start()].strip(), nome[sep.end():].strip()
            if n1 and n2:
                g1, g2 = resolver_ref(n1, f), resolver_ref(n2, f)
                if g1 and g2:
                    return nome, list(dict.fromkeys(g1 + g2)), [g1, g2]
    return None, [], []


def achar_streaming_t(t):
    for padrao, servico in SERVICOS_T:
        for mt in re.finditer(r"\b(?:" + padrao + r")(?!\w)", t):
            if negacao_t(t, mt.start()) != "nao":
                return servico
    for apelido, servico in APELIDOS_SERVICO:
        for mt in re.finditer(r"\b" + CONTEXTO_SERVICO + r"(?:" + apelido + r")(?!\w)", t):
            if negacao_t(t, mt.start()) != "nao":
                return servico
    return None


def achar_duracao_t(t):
    """Devolve {"duracao_ate": N} ou {"duracao_minima": N} (minutos) ou {}."""
    def minutos(mt):
        g = mt.groups()
        if len(g) == 1:  # só minutos
            return int(g[0])
        return int(g[0]) * 60 + (30 if g[1] else int(g[2] or 0))
    for padrao in DURACAO_MAIS_DE:
        if mt := re.search(padrao, t):
            return {"duracao_minima": minutos(mt) + 1}
    for padrao in DURACAO_ATE:
        if mt := re.search(padrao, t):
            return {"duracao_ate": minutos(mt)}
    if re.search(HORA_E_MEIA, t):
        return {"duracao_ate": 90}
    for mt in re.finditer(r"\blong[oa]s?\b", t):
        antes, depois = palavra_antes(t, mt.start()), palavra_depois(t, mt.end())
        if antes in NAO_LONGO_ANTES or depois in NAO_LONGO_DEPOIS:
            continue
        if negacao_t(t, mt.start()) == "nao":
            return {"duracao_ate": DURACAO_NAO_LONGO}
        if mt.group(0) in ("longo", "longos") or antes in LONGO_REFORCO:
            return {"duracao_minima": DURACAO_LONGO}
    return {}


def achar_epoca_t(t):
    """Devolve (ano_min, ano_max) para recente / antigo / moderno (o que aparecer primeiro), ou None."""
    achados = []
    for padrao in EPOCA_RECENTE:
        for mt in re.finditer(padrao, t):
            if negacao_t(t, mt.start()) != "nao":
                achados.append((mt.start(), (ANO_ATUAL - ANOS_RECENTE, 9999)))
    for mt in re.finditer(EPOCA_ANTIGO, t):
        if (palavra_antes(t, mt.start()) not in ANTIGO_NAO_ANTES and palavra_depois(t, mt.end()) not in ANTIGO_NAO_DEPOIS
                and negacao_t(t, mt.start()) != "nao"):
            achados.append((mt.start(), (0, ANO_ANTIGO_MAX)))
    for mt in re.finditer(EPOCA_VELHO, t):
        if negacao_t(t, mt.start()) != "nao":
            achados.append((mt.start(), (0, ANO_ANTIGO_MAX)))
    for mt in re.finditer(EPOCA_MODERNO, t):
        if palavra_antes(t, mt.start()) != "arte" and negacao_t(t, mt.start()) != "nao":
            achados.append((mt.start(), (ANO_MODERNO_MIN, 9999)))
    return min(achados, key=lambda x: x[0])[1] if achados else None


def achar_nota_t(t, filtros):
    for padrao, estrita in NOTA_REGRAS:
        for mt in re.finditer(padrao, t):
            v = numero(mt.group(1))
            if v <= 10 and negacao_t(t, mt.start()) != "nao":
                subir_nota(filtros, v, estrita)
                return
    for padrao in BEM_AVALIADO:
        for mt in re.finditer(r"\b(?:" + padrao + ")", t):
            if negacao_t(t, mt.start()) != "nao":
                subir_nota(filtros, NOTA_BEM_AVALIADO, False)
                return


def aplicar_filtros_t(f, filtros):
    """aplicar_filtros do motor A + os filtros novos (nota, duração "até"/"a partir de", palavras-chave, pouco conhecido).
    Os gêneros continuam por último, com a mesma regra de "poucos filmes com todos os gêneros"."""
    ok = pd.Series(True, index=f.index)
    if "duracao_max" in filtros:
        ok &= (f.duracao_min > 0) & (f.duracao_min < filtros["duracao_max"])
    if "duracao_ate" in filtros:
        ok &= (f.duracao_min > 0) & (f.duracao_min <= filtros["duracao_ate"])
    if "duracao_minima" in filtros:
        ok &= f.duracao_min >= filtros["duracao_minima"]
    if "streaming" in filtros:
        ok &= f.streaming_assinatura_br.fillna("").str.lower().str.contains(filtros["streaming"], regex=False)
    if "ano_min" in filtros:
        ok &= f.ano.between(filtros["ano_min"], filtros["ano_max"])
    if "idiomas" in filtros:
        ok &= f.idioma_original.isin(filtros["idiomas"])
    if "nota_min" in filtros:
        ok &= (f.nota > filtros["nota_min"]) if filtros["nota_estrita"] else (f.nota >= filtros["nota_min"])
    if "votos_max" in filtros:
        ok &= f.votos < filtros["votos_max"]
    for kw in filtros.get("palavras_chave", []):
        ok &= f._kw.map(lambda s, kw=kw: kw in s)
    for kw in filtros.get("sem_palavras_chave", []):
        ok &= ~f._kw.map(lambda s, kw=kw: kw in s)
    # v4: pessoas (todas as citadas), países e estúdios (qualquer um dos citados); negados excluem
    if "_pessoas" in f.columns:
        for grupo in filtros.get("pessoas", []):
            ok &= f._pessoas.map(lambda s, g=grupo: any(i in s for i in g))
        if filtros.get("pessoas_alguma"):
            alguma = set(i for g in filtros["pessoas_alguma"] for i in g)
            ok &= f._pessoas.map(lambda s: bool(s & alguma))
        if filtros.get("sem_pessoas"):
            sem = set(filtros["sem_pessoas"])
            ok &= ~f._pessoas.map(lambda s: bool(s & sem))
        if filtros.get("paises"):
            gs = [PAISES[g][3] for g in filtros["paises"]]
            ok &= pd.Series([any(pais_ok(p, idi, g) for g in gs) for p, idi in zip(f._paises, f.idioma_original)],
                            index=f.index)
        for g in filtros.get("sem_paises", []):
            grupo = PAISES[g][3]
            ok &= ~f._paises.map(lambda p, gr=grupo: sai_no_negado(p, gr))
        if filtros.get("estudios"):
            quer = set(filtros["estudios"])
            ok &= f._estudios.map(lambda s: bool(s & quer))
        for g in filtros.get("sem_estudios", []):
            ok &= ~f._estudios.map(lambda s, g=g: g in s)
    for g in filtros.get("sem_generos", []):
        ok &= ~f._generos.map(lambda gs, g=g: g in gs)
    if "generos" in filtros:
        quer = set(filtros["generos"])
        todos = ok & f._generos.map(lambda gs: quer <= gs)
        if todos.sum() >= TOP_N or len(quer) == 1:
            ok = todos
        else:
            ok &= f._generos.map(lambda gs: bool(quer & gs))
    return ok


# h) Sorteio igual no Python e no JavaScript (mulberry32), com semente tirada do pedido (FNV-1a)
_M32 = 0xFFFFFFFF


def semente_do_texto(s):
    h = 0x811C9DC5
    b = s.encode("utf-16-le")
    for i in range(0, len(b), 2):
        h ^= b[i] | (b[i + 1] << 8)
        h = (h * 16777619) & _M32
    return h


def mulberry32(a):
    a &= _M32

    def proximo():
        nonlocal a
        a = (a + 0x6D2B79F5) & _M32
        t = ((a ^ (a >> 15)) * (1 | a)) & _M32
        t = ((t + (((t ^ (t >> 7)) * (61 | t)) & _M32)) & _M32) ^ t
        return ((t ^ (t >> 14)) & _M32) / 4294967296
    return proximo


def embaralhar(lista, semente):
    lst = list(lista)
    rnd = mulberry32(semente)
    for i in range(len(lst) - 1, 0, -1):
        j = int(rnd() * (i + 1))
        lst[i], lst[j] = lst[j], lst[i]
    return lst


# ===========================================================================
# Rodada v4: pessoas, países, estúdios e franquias (creditos.csv, do TMDB). Também em site/motor.js.
# ===========================================================================
ARQ_CREDITOS = "creditos.csv"
# v6: recomendação por referência
ARQ_VIZINHOS = "vizinhos_ml.csv"          # similaridade_ml.py (notas do MovieLens 32M)
ARQ_RECOMENDADOS = "recomendados_tmdb.csv"  # buscar_recomendados.py (TMDB, cache de 6 meses)
MIN_FILMES_PESSOA = 2      # para manter o site leve, só pessoas com 2+ filmes no catálogo são reconhecidas
MIN_LETRAS_SOBRENOME = 4   # sobrenome sozinho ("Nolan") só com 4+ letras
MAX_PALAVRAS_NOME = 5
# Sobrenome com mais de uma pessoa: vale para a que tem pelo menos 3x mais filmes que as outras somadas
FATOR_DOMINANTE = 3
AVISO_PESSOA_DESCONHECIDA = ('Não achei filmes de "{}" no catálogo. Se for o nome de uma pessoa, ela não tem 2 ou mais '
                             'filmes entre os 6.000 do catálogo (só esses diretores e atores são reconhecidos).')
AVISO_SOBRENOME_AMBIGUO = 'Há mais de uma pessoa com o sobrenome "{}" no catálogo ({}). Escreva o nome completo.'
AVISO_PESSOA_SEM_COMBINAR = ("Não achei filmes de {} que combinem com todo o resto do pedido. "
                             "Estes são os filmes de {} no catálogo.")
RE_NOME_MAIUSCULO = r"\b[A-Z][a-zA-Z'-]+(?:\s+[A-Z][a-zA-Z'-]+)+"


def sem_acento_mantendo_maiusculas(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in texto if not unicodedata.combining(c))


def normalizar_nome(s):
    return " ".join(re.findall(r"[a-z0-9]+", m.sem_acento(s)))


def pais_ok(paises, idioma, grupo):
    """Filme é do país/grupo pedido? (regra explicada em dicionario_tags.PAISES)"""
    if not paises:
        return False
    if all(p in grupo for p in paises):
        return True
    if idioma == "en" and "US" in paises and "US" not in grupo:
        return False
    return any(p in grupo and idioma in grupo[p] for p in paises)


def so_do_grupo(paises, grupo):
    return bool(paises) and all(p in grupo for p in paises)


def sai_no_negado(paises, grupo):
    """País negado: "não seja americano" tira todo filme com EUA na produção; os outros, só os feitos só no grupo."""
    if "US" in grupo:
        return "US" in paises
    return so_do_grupo(paises, grupo)


_RE_COBERTURA = None


def coberto(texto):
    """True se algum padrão que o motor já reconhece (dicionário, gêneros, filtros, países...) aparece no texto."""
    global _RE_COBERTURA
    if _RE_COBERTURA is None:
        _RE_COBERTURA = re.compile("|".join(r"(?:\b(?:" + p + "))" for p in PADROES_COBERTURA))
    return bool(_RE_COBERTURA.search(texto))


def montar_creditos(f, vocab_tfidf):
    """Lê creditos.csv e monta o índice de pessoas, países, estúdios e coleções na ordem das linhas de f.
    O mesmo índice vai para o site (exportar_site.py), então Python e JavaScript usam exatamente os mesmos dados."""
    if not os.path.exists(ARQ_CREDITOS):
        return None
    c = pd.read_csv(ARQ_CREDITOS, dtype=str, keep_default_na=False).drop_duplicates("id", keep="last")
    c.index = c.id.astype(int)
    c = c.reindex(f.id.astype(int).values).fillna("")

    def lista(s):
        return [x for x in s.split("|") if x] if s else []

    dir_ids, cast_ids = [], []
    contagem, nome_de = collections.Counter(), {}
    for r in c.itertuples():
        d = list(zip(lista(r.diretores_ids), lista(r.diretores)))
        e = list(zip(lista(r.elenco_ids), lista(r.elenco)))
        dir_ids.append([int(p) for p, _ in d])
        cast_ids.append([int(p) for p, _ in e])
        for p, nome in d + e:
            nome_de[int(p)] = nome
        for p in {int(p) for p, _ in d + e}:
            contagem[p] += 1
    indexadas = sorted((p for p, n in contagem.items() if n >= MIN_FILMES_PESSOA),
                       key=lambda p: (-contagem[p], nome_de[p], p))
    pidx = {p: i for i, p in enumerate(indexadas)}
    nomes = [nome_de[p] for p in indexadas]

    def so_indexadas(ids):
        vistos, out = set(), []
        for p in ids:
            if p in pidx and p not in vistos:
                vistos.add(p)
                out.append(pidx[p])
        return out

    filmes_dir = [so_indexadas(x) for x in dir_ids]
    filmes_elenco = [so_indexadas(x) for x in cast_ids]

    # Formas do nome: completo, primeiro + último (para nomes com 3+ palavras) e sobrenome sozinho quando é seguro
    n_filmes = [contagem[p] for p in indexadas]
    completos, sobrenomes = collections.defaultdict(set), collections.defaultdict(set)
    primeiros = collections.Counter()  # primeiro nome -> maior número de filmes de quem tem esse primeiro nome
    for i, nome in enumerate(nomes):
        toks = normalizar_nome(nome).split()
        if not toks:
            continue
        completos[" ".join(toks)].add(i)
        if len(toks) >= 3:
            completos[toks[0] + " " + toks[-1]].add(i)
        if len(toks) >= 2:
            primeiros[toks[0]] = max(primeiros[toks[0]], n_filmes[i])
            sob = toks[-1]
            if len(toks) >= 3 and toks[-2] in PARTICULAS_NOME:
                sob = toks[-2] + " " + sob
            sobrenomes[sob].add(i)
    bloqueadas = m.PALAVRAS_VAZIAS | PALAVRAS_DE_PEDIDO | NEGACOES | VOLTA_POSITIVO | set(NAO_SOBRENOME)
    # Palavras que aparecem em minúscula em alguma sinopse são palavras comuns do português ("paz", "rock", "costa");
    # nomes de pessoas aparecem com maiúscula.
    minusculas = set()
    for s in f.sinopse.fillna(""):
        minusculas.update(re.findall(r"(?<![A-Za-z])[a-z]+(?![A-Za-z])", sem_acento_mantendo_maiusculas(s)))

    def seguro(s, ids):
        """Sobrenome sozinho só se não for palavra comum (minúscula nas sinopses, palavra de pedido, padrão do motor)
        nem primeiro nome de alguém com tantos filmes quanto o dono do sobrenome."""
        palavras = s.split()
        if len(s.replace(" ", "")) < MIN_LETRAS_SOBRENOME:
            return False
        if any(p in bloqueadas or p in minusculas or p.isdigit() for p in palavras):
            return False
        if any(primeiros.get(p, 0) >= max(n_filmes[i] for i in ids) for p in palavras):
            return False
        return not coberto(s)

    variantes = {k: sorted(v) for k, v in completos.items()}
    ambiguos = {}
    for s, ids in sobrenomes.items():
        if s in variantes or not seguro(s, ids):
            continue
        ordem = sorted(ids, key=lambda i: (-n_filmes[i], i))
        if len(ordem) == 1 or n_filmes[ordem[0]] >= FATOR_DOMINANTE * sum(n_filmes[i] for i in ordem[1:]):
            variantes[s] = [ordem[0]]  # único, ou dominante ("Nolan" = Christopher Nolan, não Jeanette Nolan)
        else:
            ambiguos[s] = ordem

    paises = [lista(x) for x in c.paises_producao]
    estudios = []
    for s in c.estudios:
        nomes_est = [m.sem_acento(x) for x in lista(s)]
        estudios.append([g for g, e in enumerate(ESTUDIOS) if any(tr in n for n in nomes_est for tr in e[2])])
    colecao = [int(x) if x else 0 for x in c.colecao_id]
    datas = sorted(set(d for d in c.data_busca if d))
    return {"nomes": nomes, "variantes": variantes, "ambiguos": ambiguos, "dir": filmes_dir, "elenco": filmes_elenco,
            "paises": paises, "estudios": estudios, "colecao": colecao, "data_busca": datas[0] if datas else None,
            "n_filmes_pessoa": n_filmes, "sem_dados": int((c.data_busca == "").sum())}


def achar_pessoas(t, cred):
    """Procura nomes do índice no texto, do mais longo para o mais curto. Devolve [(forma, ids, ini, fim, ambíguo)]."""
    toks = [(x.group(0), x.start(), x.end()) for x in re.finditer(r"[a-z0-9]+", t)]
    achados, i = [], 0
    while i < len(toks):
        achou = False
        for n in range(min(MAX_PALAVRAS_NOME, len(toks) - i), 0, -1):
            k = " ".join(w for w, _, _ in toks[i:i + n])
            if k in cred["variantes"] or k in cred["ambiguos"]:
                amb = k not in cred["variantes"]
                ids = cred["ambiguos"][k] if amb else cred["variantes"][k]
                achados.append((k, ids, toks[i][1], toks[i + n - 1][2], amb))
                i += n
                achou = True
                break
        if not achou:
            i += 1
    return achados


def achar_estudios(t):
    """Devolve (positivos, negados, trechos) dos estúdios citados."""
    sim, nao, trechos = [], [], []
    for g, (padrao, _, _, conflita) in enumerate(ESTUDIOS):
        for x in re.finditer(r"\b(?:" + padrao + r")(?!\w)", t):
            if conflita and (re.match(r"\s*(?:\+|plus\b)", t[x.end():])
                             or re.search(r"\b" + CONTEXTO_SERVICO + "$", t[:x.start()])):
                continue
            neg = negacao_t(t, x.start())
            if neg == "nao":
                if g not in nao:
                    nao.append(g)
            elif neg is None and g not in sim:
                sim.append(g)
            trechos.append((x.start(), x.end()))
    return [g for g in sim if g not in nao], nao, trechos


def achar_paises(t):
    """Devolve (positivos, negados) dos países citados ("não seja americano" = negado)."""
    sim, nao = [], []
    for g, p in enumerate(PAISES):
        for x in re.finditer(r"\b(?:" + p[0] + ")", t):
            if palavra_antes(t, x.start()) in ANTES_IDIOMA:
                continue
            neg = negacao_t(t, x.start())
            if neg == "nao":
                if g not in nao:
                    nao.append(g)
            elif neg is None and g not in sim:
                sim.append(g)
    return [g for g in sim if g not in nao], nao


def tirar_trechos(t, trechos):
    for ini, fim in sorted(trechos, reverse=True):
        t = t[:ini] + " " + t[fim:]
    return t


def achar_pessoa_desconhecida(original, t, f):
    """Nome que parece de pessoa e não foi reconhecido: depois de "dirigido por / com o ator..." ou 2+ palavras
    com maiúscula no pedido original. Devolve o nome (minúsculo, sem acento) ou None.
    t = texto já sem a referência, as pessoas e os estúdios reconhecidos."""
    bloqueadas = m.PALAVRAS_VAZIAS | PALAVRAS_DE_PEDIDO | NEGACOES | VOLTA_POSITIVO
    palavras_t = " " + " ".join(re.findall(r"[a-z0-9]+", t)) + " "

    def desconhecido(nome):
        if not nome or (" " + nome + " ") not in palavras_t or coberto(nome):
            return False
        return not ((f._tit == nome) | (f._tit_orig == nome) | (f._tit_curto == nome)
                    | f._tit.str.startswith(nome + " ") | f._tit_orig.str.startswith(nome + " ")).any()

    for x in re.finditer(PESSOA_CONTEXTO, t):
        nome = []
        for w in re.findall(r"[a-z0-9]+|[,.;!?]", t[x.end():])[:3]:
            if w in bloqueadas or not w.isalpha():
                break
            nome.append(w)
        if desconhecido(" ".join(nome)):
            return " ".join(nome)
    for x in re.finditer(RE_NOME_MAIUSCULO, sem_acento_mantendo_maiusculas(original)):
        toks = normalizar_nome(x.group(0)).split()
        corrida = []
        for w in toks + [""]:
            if w and w not in bloqueadas:
                corrida.append(w)
                continue
            if len(corrida) >= 2 and desconhecido(" ".join(corrida)):
                return " ".join(corrida)
            corrida = []
    return None


def montar_referencias(f):
    """v6: por posição do filme no catálogo, vizinhos do MovieLens [(posição, pontos)] e recomendados do TMDB
    [posição]. Mesmo índice no motor Python e no exportador do site. None se os dois arquivos faltarem."""
    if not (os.path.exists(ARQ_VIZINHOS) or os.path.exists(ARQ_RECOMENDADOS)):
        return None
    pos = {int(i): k for k, i in enumerate(f.id)}
    viz, rec = [[] for _ in range(len(f))], [[] for _ in range(len(f))]
    data = None
    if os.path.exists(ARQ_VIZINHOS):
        v = pd.read_csv(ARQ_VIZINHOS).sort_values(["id", "posicao"], kind="stable")
        for i, j, p in zip(v.id, v.vizinho_id, v.pontos):
            if i in pos and j in pos:
                viz[pos[i]].append((pos[j], int(p)))
    if os.path.exists(ARQ_RECOMENDADOS):
        r = pd.read_csv(ARQ_RECOMENDADOS, dtype=str, keep_default_na=False).drop_duplicates("id", keep="last")
        for i, lista in zip(r.id, r.recomendados):
            if int(i) in pos:
                rec[pos[int(i)]] = [pos[int(x)] for x in lista.split("|") if x and int(x) in pos]
        datas = [d for d in r.data_busca if d]
        data = min(datas) if datas else None
    return {"viz": viz, "rec": rec, "data_busca": data}


# ---------------------------------------------------------------------------

class MotorT:
    def __init__(self, pesos=None, nome="T"):
        self.nome = nome
        self.motor_a = m.MotorA(ARQ_FILMES_T)
        self.filmes = self.motor_a.filmes
        self.motor_b = m.MotorB(filmes=self.filmes)
        if pesos is None and os.path.exists(ARQ_PESOS):
            pesos = json.load(open(ARQ_PESOS, encoding="utf-8"))
        self.pesos = pesos or dict(PESOS_PADRAO)
        self.vocab = list(pd.read_csv("vocabulario_piloto.csv").tag)
        self._cache = {}
        f = self.filmes
        f["_serie_pt"] = f.titulo.map(chave_serie)
        f["_serie_orig"] = f.titulo_original.map(chave_serie)

        # Matriz filme x etiqueta: maior nota entre as fontes, contando só a metade de cima da posição
        # (posição 0,5 = 0; posição 1 = 1), para filmes "medianos" numa etiqueta não ganharem pontos.
        u = pd.read_csv(ARQ_UNIFICADAS, dtype={"imdb_id": str}, usecols=["imdb_id", "tag", "score"])
        u["s"] = ((u.score - 0.5) / 0.5).clip(lower=0)
        piv = u.groupby(["imdb_id", "tag"]).s.max().unstack(fill_value=0).reindex(columns=self.vocab, fill_value=0)
        M = piv.reindex(f.imdb_id.fillna("").values).fillna(0).to_numpy(dtype=np.float32)
        self.M = M
        normas = np.linalg.norm(M, axis=1)
        self.normas = np.where(normas > 0, normas, 1)
        self.tem_etiqueta = (M.sum(axis=1) > 0)

        # v3: raízes do índice da sinopse (palavra que existe nas sinopses não é tratada como erro de digitação)
        self.vocab_tfidf = self.motor_b.vetorizador.vocabulary_
        # v3: para cada raiz do índice, os filmes que têm essa raiz no título (português ou original)
        self.titulo_termo = {}
        for i, (t1, t2) in enumerate(zip(f.titulo.fillna(""), f.titulo_original.fillna(""))):
            for r in set(m.preparar_texto(t1 + " " + t2).split()):
                j = self.vocab_tfidf.get(r)
                if j is not None:
                    self.titulo_termo.setdefault(j, []).append(i)
        self.mediana_votos = float(f.votos.median())

        # v4: pessoas, países, estúdios e coleções (creditos.csv). Sem o arquivo, o motor funciona como a v3.
        self.cred = montar_creditos(f, self.vocab_tfidf)
        if self.cred:
            f["_pessoas"] = [set(d) | set(e) for d, e in zip(self.cred["dir"], self.cred["elenco"])]
            f["_paises"] = [tuple(p) for p in self.cred["paises"]]
            f["_estudios"] = [set(e) for e in self.cred["estudios"]]
            f["_colecao"] = self.cred["colecao"]
        # v6: vizinhos do MovieLens e recomendados do TMDB (sem os arquivos, a referência usa só etiquetas)
        self.refs = montar_referencias(f)

    # --- v3: corrige erros de digitação (tabela + distância de edição 1)
    def corrigir(self, texto):
        correcoes = []
        for errado, certo in CORRECOES_ORDENADAS:
            novo = re.sub(r"\b" + re.escape(errado) + r"\b", certo, texto)
            if novo != texto:
                correcoes.append([errado, certo])
                texto = novo
        ignorar = m.PALAVRAS_VAZIAS | PALAVRAS_DE_PEDIDO | NEGACOES | VOLTA_POSITIVO
        suspeitas = [w for w in re.finditer(r"[a-z]+", texto)
                     if len(w.group(0)) >= MIN_LETRAS_CORRECAO and w.group(0) not in ignorar
                     and m.preparar_texto(w.group(0)) not in self.vocab_tfidf]
        if not suspeitas:
            return texto, correcoes
        cobertos = []
        for padrao in PADROES_COBERTURA:
            cobertos += [(x.start(), x.end()) for x in re.finditer(r"\b(?:" + padrao + ")", texto)]
        trocas = []
        for w in suspeitas:
            p = w.group(0)
            if any(a < w.end() and w.start() < b for a, b in cobertos):
                continue
            for lit in VOCAB_CORRECAO:
                feito = False
                for k in (len(lit), len(lit) + 1, len(lit) - 1):
                    if 1 <= k <= len(p) and distancia_1(p[:k], lit):
                        trocas.append((w.start(), w.end(), lit + p[k:]))
                        correcoes.append([p, lit + p[k:]])
                        feito = True
                        break
                if feito:
                    break
        for ini, fim, novo in reversed(trocas):
            texto = texto[:ini] + novo + texto[fim:]
        return texto, correcoes

    # --- v3: análise do pedido só do motor T (o motor A continua com m.analisar, como ele é)
    def analisar_t(self, pedido):
        f = self.filmes
        t = m.sem_acento(pedido)
        ref_nome, ref_idx, ref_grupos = achar_referencia_t(t, f)
        if ref_nome:  # tira o nome citado para ele não ativar tema, gênero, filtro nem correção
            t = t.replace(ref_nome, " ")
        avisos = []
        # v4: pessoas e estúdios antes da correção de digitação (nomes próprios não são "erros"); saem do texto
        pessoas, sem_pessoas, estudios, sem_estudios = [], [], [], []
        if self.cred:
            trechos = []
            for forma, ids, ini, fim, amb in achar_pessoas(t, self.cred):
                trechos.append((ini, fim))
                if amb:
                    avisos.append(AVISO_SOBRENOME_AMBIGUO.format(forma, ", ".join(self.cred["nomes"][i] for i in ids)))
                    continue
                neg = negacao_t(t, ini)
                if neg == "nao":
                    sem_pessoas += [i for i in ids if i not in sem_pessoas]
                elif neg is None and list(ids) not in pessoas:
                    pessoas.append(list(ids))
            estudios, sem_estudios, tr_est = achar_estudios(t)
            t = tirar_trechos(t, trechos + tr_est)
            desconhecida = achar_pessoa_desconhecida(pedido, t, f)
            if desconhecida:
                avisos.append(AVISO_PESSOA_DESCONHECIDA.format(desconhecida))
        t, correcoes = self.corrigir(t)
        aleatorio = bool(re.search(ALEATORIO, t))
        if aleatorio:
            t = re.sub(ALEATORIO, " ", t)
        for padrao, aviso in SEM_DADOS:
            if any(negacao_t(t, x.start()) != "nao" for x in re.finditer(r"\b(?:" + padrao + ")", t)):
                avisos.append(aviso)
                t = re.sub(r"\b(?:" + padrao + ")", " ", t)

        filtros = m.achar_filtros(t)  # gênero (recalculado depois), "menos de", "curto", ano, idioma
        filtros.pop("streaming", None)
        servico = achar_streaming_t(t)
        if servico:
            filtros["streaming"] = servico
        if "duracao_max" not in filtros:
            filtros.update(achar_duracao_t(t))
        if "ano_min" not in filtros:
            epoca = achar_epoca_t(t)
            if epoca:
                filtros["ano_min"], filtros["ano_max"] = epoca
        achar_nota_t(t, filtros)
        kw_sim, kw_nao = [], []
        for padrao, kw in PALAVRAS_CHAVE_TMDB:
            r = achar_t(t, [padrao])
            if r == "sim":
                kw_sim.append(kw)
            elif r == "nao":
                kw_nao.append(kw)
        if kw_sim:
            filtros["palavras_chave"] = kw_sim
        if kw_nao:
            filtros["sem_palavras_chave"] = kw_nao
        if any(negacao_t(t, x.start()) != "nao" for x in re.finditer(POUCO_CONHECIDO, t)):
            filtros["votos_max"] = self.mediana_votos
            subir_nota(filtros, NOTA_POUCO_CONHECIDO, False)
        if aleatorio:
            filtros["aleatorio"] = True
            subir_nota(filtros, NOTA_ALEATORIO, False)
        # v4: pessoas, estúdios e países viram filtros
        if self.cred:
            if pessoas:
                filtros["pessoas"] = pessoas
            if sem_pessoas:
                filtros["sem_pessoas"] = sem_pessoas
            if estudios:
                filtros["estudios"] = estudios
            if sem_estudios:
                filtros["sem_estudios"] = sem_estudios
            paises, sem_paises = achar_paises(t)
            if paises:
                filtros["paises"] = paises
            if sem_paises:
                filtros["sem_paises"] = sem_paises
            # "filme francês" agora é país de produção; o idioma só vale com "em francês / idioma francês"
            if (paises or sem_paises) and "idiomas" in filtros:
                explicito = any(palavra_antes(t, x.start()) in ANTES_IDIOMA
                                for p in m.IDIOMAS for x in re.finditer(r"\b(" + p + r")\b", t))
                if not explicito:
                    filtros.pop("idiomas")
        return {"texto": t, "filtros": filtros, "referencia": ref_nome or "", "ref_idx": ref_idx, "ref_grupos": ref_grupos,
                "correcoes": correcoes, "avisos": avisos}

    # --- v3: similaridade da reserva por sinopse, com peso menor para palavras que estão no título do filme
    def similaridade_reserva(self, palavras):
        from sklearn.preprocessing import normalize
        n = len(self.filmes)
        vet = normalize(self.motor_b.vetorizador.transform([m.preparar_texto(" ".join(palavras))]))
        sim = np.zeros(n)
        if vet.nnz == 0:
            return pd.Series(sim, index=self.filmes.index)
        if not hasattr(self, "_matriz_csc"):
            self._matriz_csc = normalize(self.motor_b.matriz).tocsc()
        for j, q in sorted(zip(vet.indices, vet.data)):
            col = self._matriz_csc[:, j].toarray().ravel() * q
            no_titulo = self.titulo_termo.get(j)
            if no_titulo:
                col[no_titulo] *= PESO_PALAVRA_DO_TITULO
            sim += col
        return pd.Series(sim, index=self.filmes.index)

    # --- partes do pedido que não dependem dos pesos (guardadas em cache)
    def componentes(self, pedido):
        if pedido in self._cache:
            return self._cache[pedido]
        f = self.filmes
        a = self.analisar_t(pedido)
        texto = a["texto"]

        # Etiquetas ativadas (positivas e negadas), com o maior peso de cada etiqueta.
        # Primeiro as expressões de "companhia" ("com meu pai"): ativam suas etiquetas e saem do texto,
        # para "pai" não virar tema de pais e filhos nem "família" virar filtro de gênero.
        pos, neg, temas, temas_neg = {}, {}, [], []
        evita = {}
        usa_nota = False
        entradas = sorted(DICIONARIO_TAGS.items(), key=lambda kv: not kv[1].get("companhia", False))
        for nome, e in entradas:
            r = achar_t(texto, e["padroes"])
            if r == "sim":
                temas.append(nome)
                usa_nota |= e.get("nota", False)
                for t, w in e["tags"].items():
                    pos[t] = max(pos.get(t, 0), w)
                for t, w in e.get("evita", {}).items():  # v3: "estressado" evita tense, intense...
                    evita[t] = max(evita.get(t, 0), w)
                if e.get("companhia"):
                    for padrao in e["padroes"]:
                        texto = re.sub(r"\b(?:" + padrao + ")", " ", texto)
            elif r == "nao":
                temas_neg.append(nome)
                for t, w in e["tags"].items():
                    neg[t] = max(neg.get(t, 0), w)
        neg = {t: w for t, w in neg.items() if t not in pos}
        # v3: etiquetas que a expressão "evita": mesmo mecanismo da negação por termo (penaliza e sai do positivo)
        for t, w in evita.items():
            neg[t] = max(neg.get(t, 0), w)
            pos.pop(t, None)

        # Negação de termos específicos ("sem ser triste", "nada pesado"): penaliza as etiquetas do termo
        # e tira essas etiquetas do positivo, mesmo que outro termo do mesmo tema esteja positivo.
        termos_negados = []
        for padrao, tags in TAGS_POR_TERMO.items():
            for mt in re.finditer(r"\b(?:" + padrao + ")", texto):
                if negacao_t(texto, mt.start()) == "nao":
                    termos_negados.append(mt.group(0))
                    for t, w in tags.items():
                        neg[t] = max(neg.get(t, 0), w)
                        pos.pop(t, None)
                    break

        # Gêneros recalculados com a negação do motor T (ex.: "não seja só pra criança" não liga Família)
        filtros = dict(a["filtros"])
        filtros.pop("generos", None)
        filtros.pop("sem_generos", None)
        incluir, excluir_g = [], []
        for genero, padroes in m.GENEROS.items():
            r = achar_t(texto, padroes)
            if r == "sim":
                incluir.append(genero)
            elif r == "nao":
                excluir_g.append(genero)
        if incluir:
            filtros["generos"] = incluir
        if excluir_g:
            filtros["sem_generos"] = excluir_g
        # Idiomas só do motor T ("asiático"), quando o pedido não citou um idioma específico
        if "idiomas" not in filtros:
            for padrao, codigos in IDIOMAS_T:
                if re.search(r"\b(" + padrao + r")\b", texto):
                    filtros["idiomas"] = codigos
                    break
        a = dict(a, filtros=filtros, texto=texto)

        idx = {t: j for j, t in enumerate(self.vocab)}
        dict_score = np.zeros(len(f), dtype=np.float32)
        for t, w in pos.items():
            dict_score += w * self.M[:, idx[t]]
        for t, w in neg.items():
            dict_score -= w * self.M[:, idx[t]]

        # Referência: perfil de etiquetas do(s) filme(s) citado(s) -> cosseno
        ref_idx = a["ref_idx"]
        ref_cos = None
        excluir = set(ref_idx)
        if ref_idx:
            ref_cos = self.cos_perfil(ref_idx)
            for i in ref_idx:
                for col in ("_serie_orig", "_serie_pt"):
                    k = f.at[i, col]
                    mesmas = f.index[f[col].map(lambda x: mesma_familia(x, k))]
                    excluir |= set(mesmas)
            # v4: filme citado que pertence a uma coleção do TMDB (franquia): sai a coleção inteira
            if self.cred:
                colecoes = {f.at[i, "_colecao"] for i in ref_idx} - {0}
                if colecoes:
                    excluir |= set(f.index[f._colecao.isin(colecoes)])

        candidatos = aplicar_filtros_t(f, a["filtros"])
        candidatos[list(excluir)] = False
        # v4: nenhum filme da pessoa combina com o resto do pedido -> mostra os filmes dela (de qualquer uma das citadas)
        if a["filtros"].get("pessoas") and not candidatos.any():
            grupos = a["filtros"]["pessoas"]
            so_pessoa = aplicar_filtros_t(f, {"pessoas_alguma": grupos})
            so_pessoa[list(excluir)] = False
            if so_pessoa.any():
                candidatos = so_pessoa
                nomes = " e ".join(self.cred["nomes"][g[0]] for g in grupos)
                a = dict(a, avisos=a["avisos"] + [AVISO_PESSOA_SEM_COMBINAR.format(nomes, nomes)])

        # v6: referência com vizinhos do MovieLens e recomendados do TMDB (pesos em pesos_t.json, chave "ref").
        # Sem pesos de ML/TMDB (ou sem os arquivos), fica como antes: só o perfil de etiquetas.
        ref_serie = None if ref_cos is None else pd.Series(ref_cos, index=f.index)
        pr = self.pesos.get("ref")
        if a["ref_grupos"] and pr and (pr["ml"] or pr["tmdb"]) and self.refs:
            ref_serie, candidatos = self.pontuar_referencia(a["ref_grupos"], candidatos, pr)

        pontos_a, temas_a, neg_a = self.motor_a.pontuar(m.analisar(pedido, f))  # motor A como ele é
        sim_b = pd.Series(self.motor_b.pontuar(a), index=f.index)
        # Sinopse para a reserva: só com as palavras que dizem algo sobre o filme
        # (v3: palavra do pedido que está no título do filme vale só 10%)
        palavras = [w for w in re.findall(r"[a-z0-9]+", texto) if w not in PALAVRAS_DE_PEDIDO and w not in m.PALAVRAS_VAZIAS]
        if palavras:
            sim_reserva = self.similaridade_reserva(palavras)
        else:
            sim_reserva = pd.Series(0.0, index=f.index)

        # Só avisa "não entendi" se nem as etiquetas do T, nem os temas do motor A (dicionario.py),
        # nem gênero, filtro ou referência reconheceram algo.
        entendeu = bool(pos or neg or temas_a or neg_a or a["filtros"] or ref_idx)
        comp = {
            "a": a, "candidatos": candidatos, "dict": pd.Series(dict_score, index=f.index),
            "ref": ref_serie,
            "A": pontos_a, "B": sim_b, "pos": pos, "neg": neg, "temas": temas, "temas_neg": temas_neg,
            "temas_a": temas_a, "excluir": excluir, "entendeu": entendeu, "usa_tags": bool(pos or neg),
            "usa_nota": usa_nota, "termos_negados": termos_negados, "B_reserva": sim_reserva,
        }
        self._cache[pedido] = comp
        return comp

    def cos_perfil(self, idx):
        """Cosseno entre o perfil de etiquetas (média) dos filmes idx e cada filme do catálogo; None sem etiquetas."""
        perfil = self.M[[self.filmes.index.get_loc(i) for i in idx]].mean(axis=0)
        if perfil.sum() > 0:
            return (self.M @ perfil) / (self.normas * np.linalg.norm(perfil))
        return None

    def pontuar_referencia(self, grupos, candidatos, pr):
        """v6: pontuação da referência = ML x vizinhos do MovieLens + TMDB x "está nos recomendados"
        + etiquetas x cosseno do perfil, cada parte na escala 0-1 dentro dos candidatos. Referência dupla: soma.
        Se o filme citado tem vizinhos no ML, os candidatos viram a união vizinhos + recomendados (se sobrarem 5+).
        Sem vizinhos no ML: o peso do ML é dividido entre TMDB e etiquetas, e o catálogo todo continua valendo."""
        f, n = self.filmes, len(self.filmes)
        ml, tm, tag = np.zeros(n), np.zeros(n), np.zeros(n)
        tem_ml = False
        for g in grupos:
            mlg, tmg = np.zeros(n), np.zeros(n)
            for r in g:
                for j, p in self.refs["viz"][r]:
                    if p > mlg[j]:
                        mlg[j] = p
                for j in self.refs["rec"][r]:
                    tmg[j] = 1
                tem_ml |= bool(self.refs["viz"][r])
            ml += mlg
            tm += tmg
            cg = self.cos_perfil(g)
            if cg is not None:
                tag += cg.astype(np.float64)
        w_ml, w_tm, w_tag = pr["ml"], pr["tmdb"], pr["tags"]
        if not tem_ml:
            soma = w_tm + w_tag
            w_ml, w_tm, w_tag = 0.0, (w_tm / soma if soma else 0.0), (w_tag / soma if soma else 0.0)
        else:
            uniao = candidatos & pd.Series((ml > 0) | (tm > 0), index=f.index)
            if uniao.sum() >= TOP_N:
                candidatos = uniao
        cand = candidatos

        def esc(v):
            return m.escala_0_1(pd.Series(v, index=f.index)[cand])

        pontos = w_ml * esc(ml) + w_tm * esc(tm) + w_tag * esc(tag)
        return pontos.reindex(f.index, fill_value=0.0), candidatos

    def recomendar(self, pedido, n=TOP_N, semente=None):
        f = self.filmes
        c = self.componentes(pedido)
        info = m.montar_info(f, c["a"], c["temas"], c["temas_neg"])
        info["excluidos"] = f.loc[sorted(c["excluir"]), "titulo"].tolist()
        info["tags_ativadas"] = c["pos"]
        info["tags_negadas"] = c["neg"]
        info["temas_motor_a"] = c["temas_a"]
        info["termos_negados"] = c["termos_negados"]
        info["correcoes"] = c["a"]["correcoes"]
        info["avisos"] = c["a"]["avisos"]
        if self.cred:  # v4: nomes legíveis de pessoas, países e estúdios reconhecidos
            fl, nomes = c["a"]["filtros"], self.cred["nomes"]
            info["pessoas"] = [nomes[g[0]] for g in fl.get("pessoas", [])]
            info["sem_pessoas"] = [nomes[i] for i in fl.get("sem_pessoas", [])]
            info["paises"] = [PAISES[g][1] for g in fl.get("paises", [])]
            info["sem_paises"] = [PAISES[g][2] for g in fl.get("sem_paises", [])]
            info["estudios"] = [ESTUDIOS[g][1] for g in fl.get("estudios", [])]
            info["sem_estudios"] = [ESTUDIOS[g][1] for g in fl.get("sem_estudios", [])]
        cand = c["candidatos"]
        so_filtros = not (c["usa_tags"] or c["a"]["ref_idx"] or c["temas_a"] or c["usa_nota"])

        if c["a"]["filtros"].get("aleatorio"):
            # v3: "aleatório / surpreenda-me": sorteio entre os candidatos (já com nota 7,5+). Sem semente,
            # ela sai do próprio pedido (mesmo resultado no Python e no site); o site manda uma semente nova a cada busca.
            info["modo_resposta"] = "aleatorio"
            ordem = embaralhar(list(f.index[cand]), semente_do_texto(m.sem_acento(pedido)) if semente is None else semente)
            total = len(ordem)
            final = pd.Series({i: (total - k) / total for k, i in enumerate(ordem)}, dtype=float)
        elif c["entendeu"] and so_filtros:
            # v3: só filtros (nota, duração, época, streaming, gênero...): o catálogo filtrado pela nota ajustada
            info["modo_resposta"] = "filtros"
            final = m.escala_0_1(f.loc[cand, "_nota_ajustada"])
        elif c["entendeu"]:
            # Caminho normal: etiquetas (+ palavras-chave e sinopse pelos pesos)
            info["modo_resposta"] = "etiquetas"
            partes_t = []
            if c["usa_tags"]:
                partes_t.append(m.escala_0_1(c["dict"][cand]))
            if c["ref"] is not None:
                partes_t.append(m.escala_0_1(c["ref"][cand]))
            if c["usa_nota"]:  # "clássico": empurrão para os filmes mais bem avaliados
                partes_t.append(m.escala_0_1(f.loc[cand, "_nota_ajustada"]))
            tags = sum(partes_t) / len(partes_t) if partes_t else c["dict"][cand] * 0.0
            p = self.pesos
            final = (p["tags"] * m.escala_0_1(tags) + p["a"] * m.escala_0_1(c["A"][cand])
                     + p["b"] * m.escala_0_1(c["B"][cand]))
        elif c["B_reserva"][cand].max() >= LIMIAR_SINOPSE:
            # Reserva 1: nada reconhecido, mas a sinopse de algum filme é parecida o bastante com o pedido
            info["modo_resposta"] = "sinopse"
            final = m.escala_0_1(c["B_reserva"][cand])
        else:
            # Reserva 2: filmes mais bem avaliados (nota ajustada pelos votos), com aviso leve
            info["modo_resposta"] = "reserva_populares"
            info["aviso"] = AVISO_LEVE
            final = m.escala_0_1(f.loc[cand, "_nota_ajustada"])

        if not cand.any():
            final = pd.Series(dtype=float)
        res = f.loc[cand,["titulo", "ano", "nota", "votos", "_nota_ajustada", "_serie_pt", "_serie_orig"]].copy()
        res["pontos"] = final.round(4)
        res = res.sort_values(["pontos", "_nota_ajustada"], ascending=False)
        # Diversidade: no máximo 1 filme por série no top 5
        escolhidos, chaves = [], []
        for i, r in res.iterrows():
            if any(mesma_familia(r._serie_orig, k1) or mesma_familia(r._serie_pt, k2) for k1, k2 in chaves):
                continue
            escolhidos.append(i)
            chaves.append((r._serie_orig, r._serie_pt))
            if len(escolhidos) == n:
                break
        top = res.loc[escolhidos, ["titulo", "ano", "nota", "votos", "pontos"]]
        return top, info
