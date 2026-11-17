"""
Diagnóstico de ESTRESSE do motor T (o mesmo do site), nas frases de pedidos_estresse.csv.

pedidos_estresse.csv é um conjunto de DESCOBERTA DE FALHAS, nunca de medição (não tem gabarito).
Este script NÃO altera dicionário, pesos nem código do motor: só roda, confere e escreve o relatório.

Uso:  python -I rodar_estresse.py        (motor T atual, o mesmo do site)
      python -I rodar_estresse.py v3     (motor T v3 congelado, para o "antes" com as mesmas regras de conferência)
Gera: resultados_estresse_T.csv e relatorio_estresse.txt (ou resultados_estresse_T_v3.csv e relatorio_estresse_v3.txt)

Rodada v4: as conferências de país (a), negação de "americano"/estúdio (f) e pessoas (h) passaram a usar o
creditos.csv (países de produção, estúdios, diretores e elenco do TMDB), lido aqui de forma independente do motor.

As verificações automáticas (a-h) usam regras próprias deste script, independentes do motor,
para conferir se o top 5 respeita o que a frase pediu. Os cortes usados estão escritos no relatório.
"""
import collections
import importlib
import os
import re
import statistics
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # com "python -I" a pasta do script não entra sozinha

import motor as m
import motor_t as mt
from dicionario import DICIONARIO, GENEROS

VERSAO = sys.argv[1] if len(sys.argv) > 1 else ""
if VERSAO not in ("", "v3"):
    sys.exit("Uso: python -I rodar_estresse.py [v3]")
MOTOR_MOD = importlib.import_module("motor_t_v3_congelado" if VERSAO == "v3" else "motor_t")
DIC_MOD = importlib.import_module("dicionario_tags_v3_congelado" if VERSAO == "v3" else "dicionario_tags")
DICIONARIO_TAGS, IDIOMAS_T, TAGS_POR_TERMO = DIC_MOD.DICIONARIO_TAGS, DIC_MOD.IDIOMAS_T, DIC_MOD.TAGS_POR_TERMO
ROTULO_MOTOR = "motor T v3 (congelado)" if VERSAO == "v3" else "motor T v4 (atual, o mesmo do site)"

ARQ_PEDIDOS = "pedidos_estresse.csv"
ARQ_CREDITOS = "creditos.csv"
SAIDA_CSV = f"resultados_estresse_T{'_' + VERSAO if VERSAO else ''}.csv"
SAIDA_TXT = f"relatorio_estresse{'_' + VERSAO if VERSAO else ''}.txt"
MODOS = ["etiquetas", "filtros", "aleatorio", "sinopse", "reserva_populares"]
sa = m.sem_acento

# Palavras que não dizem nada sobre o filme (as mesmas listas que o motor já usa) + negações
VAZIAS = m.PALAVRAS_VAZIAS | mt.PALAVRAS_DE_PEDIDO | mt.NEGACOES | mt.VOLTA_POSITIVO
# Palavras de preenchimento que as listas do motor não têm (só para o ranking de palavras não reconhecidas):
# fala informal ("tô", "vc"), verbos de pedido ("esteja", "passe") e gatilhos de referência ("parecido", "estilo").
PREENCHIMENTO = set("""
to tou ta estou preciso precisando vc vcs qro quer esteja passe passa goste bastante verdade sentir
parecido parecida similar igual estilo ca
""".split())
IGNORAR_RANKING = VAZIAS | PREENCHIMENTO

# ---------------------------------------------------------------------------
# Cortes das verificações (regras deste diagnóstico, não do motor)
# ---------------------------------------------------------------------------
ANO_HOJE = 2026
CORTE_RECENTE = 2024          # "lançamento recente" = 2024 em diante
CORTE_ANTIGO = 1979           # "antigo" = até 1979
CORTE_MUDO = 1929             # "filme mudo" = até 1929 ou palavra-chave "silent film"
CORTE_CURTO = m.DURACAO_CURTO_PADRAO   # "curto" = menos de 100 min (mesmo número que o motor usa)
CORTE_NAO_LONGO = 120         # "não seja muito longo" = até 2h
CORTE_BEM_AVALIADO = 7.5      # "bem avaliado" = nota TMDB 7,5 ou mais (o motor não tem filtro de nota)
CORTE_ETIQUETA = 0.5          # filme "forte" numa etiqueta = metade de cima da escala que o motor usa

# a) país pedido -> países de produção aceitos (creditos.csv). Regra deste diagnóstico: pelo menos um dos países
#    de produção é do país pedido. "Asiático" continua conferido pelo idioma original (não é país).
IDIOMA_PEDIDO = [
    (r"frances\w*|franca\b", "francês", {"FR"}),
    (r"italian\w*|italia\b", "italiano", {"IT"}),
    (r"japon\w*|japao\b", "japonês", {"JP"}),
    (r"espanho\w*|espanha\b", "espanhol", {"ES"}),
    (r"alema\w*|alemanha\b", "alemão", {"DE", "AT"}),
    (r"indian\w*|india\b|bollywood", "indiano", {"IN"}),
    (r"corean\w*|coreia\b", "coreano", {"KR"}),
    (r"chines\w*|china\b", "chinês", {"CN", "HK", "TW"}),
    (r"argentin\w*", "argentino", {"AR"}),
    (r"mexican\w*|mexico\b", "mexicano", {"MX"}),
    (r"nordic\w*|escandinav\w*", "nórdico", {"SE", "DK", "NO", "FI", "IS"}),
    (r"brasileir\w*|nacional\b", "brasileiro", {"BR"}),
    (r"asiatic\w*|do oriente|oriental\w*", "asiático (conferido pelo idioma original)", None),
]
IDIOMAS_ASIATICOS = set(IDIOMAS_T[0][1])

# d) streaming pedido -> texto procurado em streaming_assinatura_br
STREAMING_PEDIDO = [
    (r"netflix", "Netflix", "netflix"),
    (r"prime video|amazon", "Prime Video", "amazon prime video"),
    (r"\bmax\b|hbo", "Max (HBO Max)", "hbo max"),
    (r"disney", "Disney+", "disney plus"),
    (r"globoplay", "Globoplay", "globoplay"),
    (r"apple tv", "Apple TV+", "apple tv"),
    (r"paramount", "Paramount+", "paramount"),
]

# f) alvos de negação: regex do termo -> (rótulo, função que diz se o filme TEM o que foi negado)
NEG_ALVOS = []          # preenchido em montar_alvos(), porque precisa do motor carregado

# g) gatilhos de referência (mais amplos que os do motor, para achar referências que ele perde)
REF_GATILHOS = r"(?:tipo|parecid[oa] com|similar a|igual a|algo como|como|no estilo d[eoa]|no estilo|estilo d[eoa])\s+(.+)"

# g) mesmo universo com outro título (o motor só exclui pelo título-base; aqui só para conferir)
UNIVERSO = {"o senhor dos aneis": ["hobbit"], "matrix": ["animatrix"], "toy story": ["lightyear"]}

# h) nomes próprios que não são pessoas
NAO_PESSOA = {"netflix", "prime", "prime video", "video", "max", "disney", "marvel", "dc", "vietna", "natal",
              "studio ghibli", "ghibli", "hollywood", "oi", "teste", "aaaa"}

# erros de digitação comuns, só para descobrir o gênero esperado no critério de "resposta estranha"
TYPOS_GENERO = [(r"\baks?ao\b|\bacsao\b", "Ação"), (r"\bsuspence\b", "Thriller"), (r"\bfics?ao cientifica\b", "Ficção científica"),
                (r"\bterro\b", "Terror"), (r"\bcomedia\b", "Comédia")]


# ---------------------------------------------------------------------------
def negado_aqui(t, pos, janela=4):
    """Regra deste diagnóstico: o termo está negado se uma de 'sem/não/nada/nem' aparece até 4 palavras antes."""
    antes = re.split(r"[,.;!?]", t[:pos])[-1].split()[-janela:]
    return any(p in ("sem", "nao", "nada", "nem") for p in antes)


def carregar_creditos(f):
    """Países, estúdios e pessoas por filme (creditos.csv), lidos aqui de forma independente do motor."""
    c = pd.read_csv(ARQ_CREDITOS, dtype=str, keep_default_na=False).drop_duplicates("id", keep="last")
    c.index = c.id.astype(int)
    c = c.reindex(f.id.astype(int).values).fillna("")
    sp = lambda s: [x for x in s.split("|") if x]
    paises = {i: set(sp(v)) for i, v in zip(f.index, c.paises_producao)}
    estudios = {i: [sa(x) for x in sp(v)] for i, v in zip(f.index, c.estudios)}
    pessoas = collections.defaultdict(set)   # nome normalizado -> filmes (diretor ou 8 primeiros do elenco)
    for i, d, e in zip(f.index, c.diretores, c.elenco):
        for nome in sp(d) + sp(e):
            pessoas[" ".join(re.findall(r"[a-z0-9]+", sa(nome)))].add(i)
    sobrenomes = collections.defaultdict(list)
    for nome in pessoas:
        if len(nome.split()) >= 2:
            sobrenomes[nome.split()[-1]].append(nome)
    return paises, estudios, pessoas, sobrenomes


def achar_pessoa_creditos(seq, pessoas, sobrenomes):
    """Regra deste diagnóstico: nome completo; ou sobrenome sozinho (se houver mais de uma pessoa com ele,
    fica a que tem mais filmes no catálogo). Devolve (nome, filmes) ou (None, set())."""
    k = " ".join(re.findall(r"[a-z0-9]+", sa(seq)))
    if k in pessoas:
        return k, pessoas[k]
    if len(k.split()) == 1 and k in sobrenomes:
        nome = max(sobrenomes[k], key=lambda n: (len(pessoas[n]), n))
        return nome, pessoas[nome]
    return None, set()


def achar_ref_catalogo(nome, f):
    exato = f.index[(f._tit == nome) | (f._tit_orig == nome) | (f._tit_curto == nome)]
    if len(exato):
        return list(exato)
    fr = f.index[f._tit.str.startswith(nome + " ") | f._tit_orig.str.startswith(nome + " ")]
    return list(fr)


def main():
    print(f"Carregando o {ROTULO_MOTOR}...")
    motor = MOTOR_MOD.MotorT()
    f = motor.filmes
    paises_de, estudios_de, pessoas_cred, sobrenomes_cred = carregar_creditos(f)
    vidx = {t: j for j, t in enumerate(motor.vocab)}
    pos_de = {i: f.index.get_loc(i) for i in f.index}

    def forte(i, tag):
        return tag in vidx and motor.M[pos_de[i], vidx[tag]] >= CORTE_ETIQUETA

    def tem_kw(i, *trechos):
        return any(any(tr in k for tr in trechos) for k in f.at[i, "_kw"])

    # f) alvos de negação: gêneros, termos de TAGS_POR_TERMO e alguns temas concretos
    alvos = []
    for g, padroes in GENEROS.items():
        alvos.append(("|".join(padroes), f"gênero {g}", lambda i, g=g: g in f.at[i, "_generos"]))
    for padrao, tags in TAGS_POR_TERMO.items():
        fortes = [t for t, w in tags.items() if w >= 0.8]
        alvos.append((padrao, "etiquetas " + "/".join(fortes), lambda i, ts=fortes: any(forte(i, t) for t in ts)))
    alvos += [
        (r"super-?\s?hero\w*|super-?\s?heroi\w*", "super-herói (palavra-chave superhero ou etiqueta)",
         lambda i: tem_kw(i, "superhero") or forte(i, "superhero")),
        (r"fantasma\w*", "fantasma (palavra-chave ghost ou etiqueta ghosts)", lambda i: tem_kw(i, "ghost") or forte(i, "ghosts")),
        (r"alienigena\w*|extraterrestre\w*|\bets?\b", "alienígena (palavra-chave alien ou etiqueta alien invasion)",
         lambda i: tem_kw(i, "alien") or forte(i, "alien invasion")),
        (r"sust[oa]s?\b", "sustos (etiquetas scary/creepy)", lambda i: forte(i, "scary") or forte(i, "creepy")),
        (r"marvel", "Marvel (estúdio Marvel no TMDB ou palavra-chave marvel cinematic universe)",
         lambda i: tem_kw(i, "marvel cinematic universe") or any("marvel" in e for e in estudios_de[i])),
        (r"american\w*|estadunidense\w*|hollywood", "americano (EUA é o único país de produção)",
         lambda i: paises_de[i] == {"US"}),
        (r"palavr[aã]o\w*|palavroes", "palavrão (palavra-chave swear/profanity; quase nenhum filme tem)",
         lambda i: tem_kw(i, "swear", "profanity")),
        (r"disney", "Disney (estúdio com 'disney' no nome, no TMDB)",
         lambda i: any("disney" in e for e in estudios_de[i])),
    ]

    ped = pd.read_csv(ARQ_PEDIDOS)
    linhas, tempos = [], []
    viol_por_tipo = collections.defaultdict(list)
    palavras_cat = collections.defaultdict(collections.Counter)
    expressoes = collections.Counter()
    parciais, estranhas, top5_vistos = [], [], collections.defaultdict(list)

    # padrões que o motor reconhece (para achar as palavras que não casaram com nada)
    padroes_motor = []
    for e in DICIONARIO_TAGS.values():
        padroes_motor += e["padroes"]
    padroes_motor += list(TAGS_POR_TERMO)
    for d in DICIONARIO.values():
        padroes_motor += d["padroes"]
    for ps in GENEROS.values():
        padroes_motor += ps
    padroes_motor += list(m.IDIOMAS) + [p for p, _ in IDIOMAS_T] + [r"\b" + s + r"\b" for s in m.SERVICOS]
    filtros_motor = [r"menos de \d+\s*h\s*\d*", r"menos de \d+\s*min\w*", r"\bcurt[oa]\b", r"\banos \d{2,4}\b",
                     r"\bde (19\d\d|20\d\d)\b"]

    for _, p in ped.iterrows():
        pedido, numero, cat = str(p.pedido), int(p.numero), p.categoria
        t0 = time.perf_counter()
        top, info = motor.recomendar(pedido)
        dt = (time.perf_counter() - t0) * 1000
        tempos.append(dt)
        c = motor._cache[pedido]
        t = sa(pedido)
        idx5 = list(top.index)
        nome5 = [f"{f.at[i, 'titulo']} ({f.at[i, 'ano']})" for i in idx5]
        top5_vistos[tuple(idx5)].append(numero)
        viol = []

        def add(tipo, texto):
            viol.append(f"{tipo}) {texto}")
            viol_por_tipo[tipo].append((numero, pedido, texto, nome5))

        filtros = info["filtros"]

        # a) idioma / país
        for rx, rot, cods in IDIOMA_PEDIDO:
            mm = re.search(r"\b(?:" + rx + ")", t)
            if mm and not negado_aqui(t, mm.start()):
                if cods is None:
                    fora = [f"{f.at[i, 'titulo']} [{f.at[i, 'idioma_original']}]" for i in idx5
                            if f.at[i, "idioma_original"] not in IDIOMAS_ASIATICOS]
                    det = "" if "idiomas" in filtros else " (o motor NÃO detectou o filtro)"
                else:
                    fora = [f"{f.at[i, 'titulo']} [{'/'.join(sorted(paises_de[i])) or 'sem país'}]" for i in idx5
                            if not (paises_de[i] & cods)]
                    det = "" if ("idiomas" in filtros or "paises" in filtros) else " (o motor NÃO detectou o filtro)"
                if fora:
                    add("a", f"pediu {rot}: {len(fora)} de 5 sem o país entre os de produção{det}: " + ", ".join(fora))
                break

        # b) duração
        lim, rot = None, ""
        if mm := re.search(r"menos de (\d+)\s*h\s*(\d+)?", t):
            lim, rot = int(mm.group(1)) * 60 + int(mm.group(2) or 0) - 1, mm.group(0)
        elif mm := re.search(r"menos de (\d+)\s*min", t):
            lim, rot = int(mm.group(1)) - 1, mm.group(0)
        elif mm := re.search(r"\bate (\d+)\s*h\s*(\d+)?", t):
            lim, rot = int(mm.group(1)) * 60 + int(mm.group(2) or 0), mm.group(0)
        elif mm := re.search(r"\bate (\d+)\s*min", t):
            lim, rot = int(mm.group(1)), mm.group(0)
        elif re.search(r"\bcurt[oa]s?\b", t):
            lim, rot = CORTE_CURTO - 1, f"curto (menos de {CORTE_CURTO} min)"
        elif re.search(r"nao (seja )?muito long|nao (seja )?long", t):
            lim, rot = CORTE_NAO_LONGO, f"não muito longo (até {CORTE_NAO_LONGO} min)"
        if lim:
            fora = [f"{f.at[i, 'titulo']} [{f.at[i, 'duracao_min']} min]" for i in idx5 if not (0 < f.at[i, "duracao_min"] <= lim)]
            det = "" if "duracao_max" in filtros else " (o motor NÃO detectou o filtro de duração)"
            if fora:
                add("b", f"pediu '{rot}': {len(fora)} de 5 fora{det}: " + ", ".join(fora))

        # c) ano / década / época
        regra = None
        if mm := re.search(r"\banos (\d{2,4})\b", t):
            d = int(mm.group(1)); d = d + (1900 if d >= 30 else 2000) if d < 100 else d
            regra = (f"anos {mm.group(1)} ({d}-{d + 9})", lambda i, d=d: d <= f.at[i, "ano"] <= d + 9, "ano_min")
        elif mm := re.search(r"\b(?:de|desde) ((?:19|20)\d\d) (?:pra|para) ca\b|\bdesde ((?:19|20)\d\d)\b", t):
            y = int(mm.group(1) or mm.group(2))
            regra = (f"de {y} pra cá", lambda i, y=y: f.at[i, "ano"] >= y, "ano_min")
        elif mm := re.search(r"\b(?:de|em) ((?:19|20)\d\d)\b", t):
            y = int(mm.group(1))
            regra = (f"de {y}", lambda i, y=y: f.at[i, "ano"] == y, "ano_min")
        elif re.search(r"\brecente|\blancamento", t):
            regra = (f"recente ({CORTE_RECENTE}+)", lambda i: f.at[i, "ano"] >= CORTE_RECENTE, "ano_min")
        elif re.search(r"\bantig[oa]s?\b", t):
            regra = (f"antigo (até {CORTE_ANTIGO})", lambda i: f.at[i, "ano"] <= CORTE_ANTIGO, "ano_min")
        elif re.search(r"\bmud[oa]s?\b", t):
            regra = (f"filme mudo (até {CORTE_MUDO} ou palavra-chave silent film)",
                     lambda i: f.at[i, "ano"] <= CORTE_MUDO or tem_kw(i, "silent film"), None)
        elif re.search(r"preto e branco", t):
            regra = ("preto e branco (palavra-chave black and white)", lambda i: tem_kw(i, "black and white"), None)
        if regra:
            rot, ok, chave = regra
            fora = [f"{f.at[i, 'titulo']} [{f.at[i, 'ano']}]" for i in idx5 if not ok(i)]
            det = "" if (chave is None or chave in filtros) else " (o motor NÃO detectou o filtro de ano)"
            if chave is None:
                det = " (conferido pela palavra-chave ou pelo ano)"
            if fora:
                add("c", f"pediu '{rot}': {len(fora)} de 5 fora{det}: " + ", ".join(fora))

        # d) streaming
        for rx, rot, txt in STREAMING_PEDIDO:
            if re.search(rx, t):
                fora = [f.at[i, "titulo"] for i in idx5
                        if txt not in str(f.at[i, "streaming_assinatura_br"]).lower()]
                det = "" if "streaming" in filtros else " (o motor NÃO detectou o filtro de streaming)"
                if fora:
                    add("d", f"pediu {rot}: {len(fora)} de 5 não estão nesse serviço por assinatura{det}: " + ", ".join(fora))
                break

        # e) nota
        corte = None
        if mm := re.search(r"nota (?:acima|maior|mais alta|superior) (?:de|que|a) (\d+(?:[.,]\d+)?)", t):
            corte, estrito = float(mm.group(1).replace(",", ".")), True
        elif re.search(r"bem avaliad|nota alta|aclamad", t):
            corte, estrito = CORTE_BEM_AVALIADO, False
        if corte is not None:
            fora = [f"{f.at[i, 'titulo']} [{f.at[i, 'nota']:.1f}]" for i in idx5
                    if (f.at[i, "nota"] <= corte if estrito else f.at[i, "nota"] < corte)]
            if fora:
                add("e", f"pediu nota {'acima de' if estrito else 'a partir de'} {corte:g}{'' if 'nota_min' in filtros else ' (o motor NÃO detectou o filtro de nota)'}: "
                    f"{len(fora)} de 5 fora: " + ", ".join(fora))

        # f) negações
        for rx, rot, tem in alvos:
            for mm in re.finditer(r"\b(?:" + rx + ")", t):
                if negado_aqui(t, mm.start()):
                    if tem is None:
                        add("f", f"negou '{mm.group(0)}' -> {rot}")
                    else:
                        com = [f.at[i, "titulo"] for i in idx5 if tem(i)]
                        if com:
                            add("f", f"negou '{mm.group(0)}' -> {rot}: {len(com)} de 5 têm: " + ", ".join(com))
                    break

        # g) referência
        ref_motor = info.get("referencia", "")
        for mm in re.finditer(REF_GATILHOS, t):
            nome = re.split(r",| mas | so que | porem | e que ", mm.group(1))[0].strip(" .!?")
            if not nome:
                continue
            achados = achar_ref_catalogo(nome, f)
            if not achados:
                add("g", f"referência '{nome}' não achada no catálogo")
                break
            proibidos = set(achados)
            for i in achados:
                for col in ("_serie_pt", "_serie_orig"):
                    k = f.at[i, col]
                    proibidos |= set(f.index[f[col].map(lambda x: mt.mesma_familia(x, k))])
            proibidos |= set(f.index[f._tit.str.contains(re.escape(nome)) | f._tit_orig.str.contains(re.escape(nome))])
            for chave_u, outros in UNIVERSO.items():
                if chave_u in nome or nome in chave_u:
                    for o in outros:
                        proibidos |= set(f.index[f._tit.str.contains(o)])
            if not ref_motor:
                add("g", f"referência '{nome}' existe no catálogo, mas o motor NÃO a detectou")
            ruins = [f.at[i, "titulo"] for i in idx5 if i in proibidos]
            if ruins:
                add("g", f"referência '{nome}': o filme citado, a série ou o mesmo universo apareceu: " + ", ".join(ruins))
            break

        # h) nomes de pessoas
        for seq in re.findall(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ'-]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ'-]+)*", pedido):
            s_ = sa(seq)
            if s_ in NAO_PESSOA or s_ in VAZIAS or s_ in m.PESSOAS:
                continue
            # título de filme só é ignorado quando a frase pede uma referência ("tipo X", "parecido com X")
            if (ref_motor and s_ in ref_motor) or (re.search(REF_GATILHOS, t) and achar_ref_catalogo(s_, f)):
                continue
            nome_p, filmes_p = achar_pessoa_creditos(seq, pessoas_cred, sobrenomes_cred)
            if not filmes_p:
                if not any(sa(seq) in sa(av) for av in info.get("avisos", [])):
                    add("h", f"'{seq}' não é diretor nem ator do catálogo, e o motor não avisou")
                continue
            dela = sum(1 for i in idx5 if i in filmes_p)
            precisa = min(5, len(filmes_p))
            if dela < precisa:
                add("h", f"'{seq}' ({nome_p}, {len(filmes_p)} filmes no catálogo): só {dela} de 5 são dessa pessoa")

        # palavras que não casaram com nada que o motor reconhece
        cobertos = []
        for padrao in padroes_motor:
            cobertos += [(x.start(), x.end()) for x in re.finditer(r"\b(?:" + padrao + ")", t)]
        for padrao in filtros_motor:
            cobertos += [(x.start(), x.end()) for x in re.finditer(padrao, t)]
        if ref_motor and ref_motor in t:
            k = t.index(ref_motor)
            cobertos.append((k, k + len(ref_motor)))
        reconhecidas, ignoradas, corrida = [], [], []
        for w in re.finditer(r"[a-z0-9]+", t):
            if any(a < w.end() and w.start() < b for a, b in cobertos):
                if w.group(0) not in IGNORAR_RANKING:
                    reconhecidas.append(w.group(0))
                if len(corrida) >= 2:
                    expressoes[" ".join(corrida)] += 1
                corrida = []
            elif w.group(0) not in IGNORAR_RANKING:
                ignoradas.append(w.group(0))
                corrida.append(w.group(0))
            else:
                if len(corrida) >= 2:
                    expressoes[" ".join(corrida)] += 1
                corrida = []
        if len(corrida) >= 2:
            expressoes[" ".join(corrida)] += 1
        for w in ignoradas:
            palavras_cat[cat][w] += 1
        if reconhecidas and ignoradas:
            parciais.append((numero, pedido, reconhecidas, ignoradas))

        # critério de "resposta estranha": gênero esperado x gêneros dos 5
        esperado = set()
        for g, padroes in GENEROS.items():
            for x in re.finditer(r"\b(?:" + "|".join(padroes) + ")", t):
                if not negado_aqui(t, x.start()):
                    esperado.add(g)
        for rx, g in TYPOS_GENERO:
            if re.search(rx, t):
                esperado.add(g)
        origem = "gênero pedido"
        if not esperado and ref_motor and info.get("excluidos"):
            ref_idx = c["a"]["ref_idx"]
            esperado = set().union(*[f.at[i, "_generos"] for i in ref_idx]) if ref_idx else set()
            origem = "gêneros do filme citado"
        # Três critérios objetivos, nesta ordem de prioridade:
        # 1) 2+ dos 5 sem nenhum gênero esperado (escrito no pedido, mesmo com erro de digitação comum,
        #    ou os gêneros do filme citado);
        # 2) o pedido tem palavra de conteúdo, mas a resposta é a lista fixa de populares;
        # 3) caminho "sinopse" e 2+ títulos repetem uma palavra do pedido (casou pelo título, não pelo tema).
        if esperado:
            sem_nada = [f.at[i, "titulo"] for i in idx5 if not (f.at[i, "_generos"] & esperado)]
            if len(sem_nada) >= 2:
                estranhas.append((1, -len(sem_nada), numero, pedido,
                                  f"{len(sem_nada)} de 5 sem {origem} ({', '.join(sorted(esperado))})", nome5))
        conteudo = [x for x in ignoradas if len(x) >= 3 and len(set(x)) > 1]  # tira "oi", "aaaa"
        if info["modo_resposta"] == "reserva_populares" and conteudo:
            estranhas.append((2, 0, numero, pedido, f"tinha conteúdo ({', '.join(conteudo)}), mas veio a lista fixa de populares", nome5))
        if info["modo_resposta"] == "sinopse":
            palavras_ped = {x for x in re.findall(r"[a-z0-9]+", t) if len(x) >= 3 and x not in IGNORAR_RANKING}
            no_titulo = [f.at[i, "titulo"] for i in idx5 if palavras_ped & set(re.findall(r"[a-z0-9]+", f.at[i, "_tit"]))]
            if len(no_titulo) >= 2:
                estranhas.append((3, -len(no_titulo), numero, pedido,
                                  f"casou pela palavra no título, não pelo tema: {', '.join(no_titulo)}", nome5))

        # colunas do CSV
        rec = list(c["temas"])
        if c["pos"]:
            rec.append("etiquetas: " + ", ".join(f"{k}({v:g})" for k, v in sorted(c["pos"].items(), key=lambda kv: -kv[1])))
        if c["temas_a"]:
            rec.append("temas do motor A: " + ", ".join(c["temas_a"]))
        fd = []
        for k, v in filtros.items():
            fd.append(f"{k}={'/'.join(map(str, v)) if isinstance(v, (list, tuple)) else v}")
        if c["temas_neg"]:
            fd.append("temas negados=" + "/".join(c["temas_neg"]))
        if c["termos_negados"]:
            fd.append("termos negados=" + "/".join(c["termos_negados"]))
        if c["neg"]:
            fd.append("etiquetas penalizadas=" + "/".join(sorted(c["neg"])))
        for chave, rot in (("pessoas", "pessoas"), ("sem_pessoas", "sem pessoas"), ("paises", "países"),
                           ("sem_paises", "sem países"), ("estudios", "estúdios"), ("sem_estudios", "sem estúdios")):
            if info.get(chave):
                fd.append(f"{rot}=" + "/".join(info[chave]))
        ref_txt = ""
        if ref_motor:
            ref_txt = f"{ref_motor} (excluídos: {len(c['excluir'])} filmes da série)"
        linhas.append({
            "numero": numero, "categoria": cat, "pedido": pedido, "modo_resposta": info["modo_resposta"],
            "etiquetas_e_temas_reconhecidos": " | ".join(rec), "filtros_detectados": "; ".join(fd),
            "referencia_detectada": ref_txt, "top5": "; ".join(nome5), "aviso": info.get("aviso", ""),
            "violacoes": " || ".join(viol), "avisos_motor": " | ".join(info.get("avisos", [])), "tempo_ms": round(dt, 1),
        })

    res = pd.DataFrame(linhas)
    res.to_csv(SAIDA_CSV, index=False, encoding="utf-8-sig")
    escrever_relatorio(res, viol_por_tipo, palavras_cat, expressoes, parciais, estranhas, top5_vistos, tempos)
    print(f"Gerados {SAIDA_CSV} e {SAIDA_TXT}")


def escrever_relatorio(res, viol, palavras_cat, expressoes, parciais, estranhas, top5_vistos, tempos):
    L = []
    w = L.append
    w(f"RELATÓRIO DE ESTRESSE: {ROTULO_MOTOR.upper()}")
    w("=" * 70)
    w("pedidos_estresse.csv é conjunto de DESCOBERTA DE FALHAS, nunca de medição (não tem gabarito).")
    w("Regras de conferência da rodada v4: país (a), 'americano'/Disney/Marvel (f) e pessoas (h) conferidos pelo")
    w("creditos.csv (TMDB), lido por este script de forma independente do motor. As outras regras não mudaram.")
    w("Antes x depois: ver relatorio_estresse_v3_v4.txt (python -I comparar_estresse.py).")
    w(f"Frases: {len(res)}\n")

    w("1) MODO DE RESPOSTA")
    w("-" * 70)
    tot = res.modo_resposta.value_counts()
    for k in MODOS:
        w(f"  {k:<18} {tot.get(k, 0):>4}")
    w("\n  Por categoria:")
    tab = pd.crosstab(res.categoria, res.modo_resposta).reindex(columns=MODOS, fill_value=0)
    w("  " + tab.to_string().replace("\n", "\n  "))

    w("\n2) FRASES QUE CAÍRAM EM SINOPSE OU RESERVA_POPULARES")
    w("-" * 70)
    for _, r in res[res.modo_resposta.isin(["sinopse", "reserva_populares"])].iterrows():
        w(f"  #{r.numero} [{r.categoria}] {r.modo_resposta}: \"{r.pedido}\"")
        w(f"      -> {r.top5}")

    w("\n3) VIOLAÇÕES POR TIPO")
    w("-" * 70)
    w(f"  Cortes usados: curto = menos de {CORTE_CURTO} min (o mesmo número do motor); \"não muito longo\" = até {CORTE_NAO_LONGO} min;")
    w(f"  recente = {CORTE_RECENTE}+; antigo = até {CORTE_ANTIGO}; filme mudo = até {CORTE_MUDO} ou palavra-chave \"silent film\";")
    w(f"  bem avaliado = nota TMDB {CORTE_BEM_AVALIADO:g}+ (regra deste diagnóstico; o motor v3 usa o mesmo corte");
    w(f"  filme \"forte\" numa etiqueta = nota >= {CORTE_ETIQUETA:g} na escala do motor;")
    w("  país = pelo menos um país de produção é o pedido; 'não seja americano' = EUA não pode ser o único país;")
    w("  pessoa = nome completo ou sobrenome (o de mais filmes) entre diretores e 8 primeiros do elenco; o top 5 precisa")
    w("  ter min(5, filmes da pessoa) filmes dela; nome que não é do catálogo precisa gerar aviso do motor.")
    nomes = {"a": "idioma/país", "b": "duração", "c": "ano/década/época", "d": "streaming", "e": "nota",
             "f": "negações", "g": "referência", "h": "nome de pessoa"}
    for k in "abcdefgh":
        itens = viol.get(k, [])
        w(f"\n  {k}) {nomes[k]}: {len(itens)}")
        for numero, pedido, texto, nome5 in itens:
            w(f"     #{numero} \"{pedido}\"")
            w(f"        {texto}")
            if k != "h":
                w(f"        top 5: {'; '.join(nome5)}")

    w("\n4) PALAVRAS DOS PEDIDOS QUE NÃO CASARAM COM NADA")
    w("-" * 70)
    w("  (sem etiqueta, tema, gênero, filtro ou referência; ignorando as palavras vazias que o motor já usa")
    w("   e mais estas de preenchimento: " + ", ".join(sorted(PREENCHIMENTO)) + ")")
    geral = collections.Counter()
    for cnt in palavras_cat.values():
        geral.update(cnt)
    w("\n  Ranking geral (palavra: vezes):")
    w("  " + ", ".join(f"{p}: {n}" for p, n in geral.most_common(60)))
    w("\n  Expressões (2+ palavras seguidas não reconhecidas):")
    w("  " + ", ".join(f"\"{p}\": {n}" for p, n in expressoes.most_common(40)))
    w("\n  Por categoria:")
    for cat in sorted(palavras_cat):
        w(f"   {cat}: " + ", ".join(f"{p} ({n})" for p, n in palavras_cat[cat].most_common(25)))

    w("\n5) FRASES ENTENDIDAS SÓ EM PARTE (reconheceu um termo e ignorou outro)")
    w("-" * 70)
    for numero, pedido, rec, ign in parciais:
        w(f"  #{numero} \"{pedido}\"  | reconheceu: {', '.join(rec)}  | ignorou: {', '.join(ign)}")

    w("\n6) 10 RESPOSTAS QUE PARECEM ESTRANHAS")
    w("-" * 70)
    w("  Critérios objetivos, por prioridade (não julga gosto):")
    w("   1) 2+ dos 5 sem nenhum gênero esperado (o gênero escrito no pedido, mesmo com erro de digitação comum,")
    w("      ou os gêneros do filme citado);")
    w("   2) o pedido tem palavra de conteúdo, mas a resposta é a lista fixa de populares;")
    w("   3) caminho \"sinopse\" e 2+ títulos repetem uma palavra do pedido (casou pelo título, não pelo tema).")
    estranhas.sort(key=lambda x: (x[0], x[1], x[2]))
    cont = collections.Counter(x[0] for x in estranhas)
    w(f"  Frases que caem em cada critério: 1) {cont[1]}  2) {cont[2]}  3) {cont[3]}. As 10 primeiras:")
    vistos = set()
    for crit, _, numero, pedido, motivo, nome5 in estranhas:
        if numero in vistos:
            continue
        vistos.add(numero)
        w(f"  #{numero} \"{pedido}\" [critério {crit}]: {motivo}")
        w(f"      top 5: {'; '.join(nome5)}")
        if len(vistos) == 10:
            break
    w("\n  Também objetivo: o mesmo top 5 repetido em 3+ frases diferentes:")
    for chave, nums in sorted(top5_vistos.items(), key=lambda kv: -len(kv[1])):
        if len(nums) >= 3:
            w(f"   {len(nums)} frases ({', '.join('#' + str(x) for x in nums)}) devolveram o mesmo top 5:")
            w("      " + res[res.numero == nums[0]].top5.iloc[0])

    w("\n7) TEMPO DO MOTOR POR PEDIDO (Python)")
    w("-" * 70)
    w(f"  média {statistics.mean(tempos):.0f} ms | mediana {statistics.median(tempos):.0f} ms | máximo {max(tempos):.0f} ms "
      f"| mínimo {min(tempos):.0f} ms")
    lentos = res.sort_values("tempo_ms", ascending=False).head(3)
    w("  mais lentos: " + "; ".join(f"#{r.numero} {r.tempo_ms} ms" for _, r in lentos.iterrows()))
    w("  (no site, em JavaScript, a medição anterior era de cerca de 10 ms por pedido)")
    open(SAIDA_TXT, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
