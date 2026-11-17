"""
Motor de recomendação de filmes (Etapa 3).

Abordagem A: traduz os termos do pedido para palavras-chave em inglês (dicionario.py)
             e soma quantas palavras-chave de cada filme batem.
Abordagem B: compara o pedido com a sinopse em português (TF-IDF + similaridade de cosseno).

As duas usam os mesmos filtros nos dados: gênero, duração, streaming, ano e idioma.

Uso:
    python motor.py A                 -> roda os 40 pedidos de teste e salva resultados_A.csv
    python motor.py B                 -> roda os 40 pedidos de teste e salva resultados_B.csv
    python motor.py comparar          -> mostra A e B lado a lado (lê os dois arquivos de resultado)
    python motor.py A validacao       -> roda nos pedidos de pedidos_validacao.csv e salva resultados_A_validacao.csv
    python motor.py comparar validacao
    python motor.py A "meu pedido"    -> mostra o top 5 para um pedido qualquer

Sem IA: só cruzamento de dados.
"""

import collections
import os
import re
import sys
import unicodedata

import numpy as np
import pandas as pd
import snowballstemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from dicionario import DICIONARIO, GENEROS, PALAVRAS_META

ARQ_FILMES = "filmes.csv"
ARQ_PEDIDOS = "pedidos_teste.csv"
TOP_N = 5

# ---------------------------------------------------------------------------
# Limpeza de texto
# ---------------------------------------------------------------------------

# Palavras que não ajudam a diferenciar filmes (já sem acento).
PALAVRAS_VAZIAS = set("""
a o e as os um uma uns umas de da do das dos em na no nas nos num numa por pelo pela pelos pelas
para pra pro pras pros com sem que se ao aos ou mas mais menos muito muita muitos muitas bem
ja tem ter ser esta esse essa isso isto aquele aquela eu me mim meu minha voce ele ela eles elas
nos nosso nossa seu sua seus suas lhe sobre entre ate apos quando onde como qual quais quem
porque pois tambem so nao sim nada algo alguem coisa tipo uns quero queremos filme filmes
ver assistir hoje noite pra la aqui vai vou foi era sao estao seja sejam tenha dar deixe
""".split())

_stemmer = snowballstemmer.stemmer("portuguese")


def sem_acento(texto):
    texto = unicodedata.normalize("NFKD", str(texto).lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def preparar_texto(texto):
    """Minúsculas, sem acento, sem palavras vazias e com cada palavra reduzida à raiz."""
    palavras = re.findall(r"[a-z0-9]+", sem_acento(texto))
    palavras = [p for p in palavras if p not in PALAVRAS_VAZIAS and len(p) > 1]
    return " ".join(_stemmer.stemWords(palavras))


# ---------------------------------------------------------------------------
# Negação: "sem muito sangue", "nada de susto", "que não seja pesado"
# ---------------------------------------------------------------------------

def tipo_negacao(texto, pos):
    """Olha as 3 palavras antes de `pos` (na mesma frase).
    Devolve "nao" (negado), "nao_so" ("não seja só X" = X pode, mas não só ele) ou None."""
    antes = re.split(r"[,.;!?]", texto[:pos])[-1].split()[-3:]
    for i, p in enumerate(antes):
        if p in ("nao", "sem", "nada", "nem"):
            return "nao_so" if any(q in ("so", "apenas", "somente") for q in antes[i + 1:]) else "nao"
    return None


def achar_padroes(texto, padroes):
    """Procura os padrões no texto. Devolve "sim", "nao" (só aparece negado) ou None."""
    achou_sim = achou_nao = False
    for padrao in padroes:
        for m in re.finditer(r"\b(?:" + padrao + ")", texto):
            neg = tipo_negacao(texto, m.start())
            if neg is None:
                achou_sim = True
            elif neg == "nao":
                achou_nao = True
    return "sim" if achou_sim else ("nao" if achou_nao else None)


# ---------------------------------------------------------------------------
# Filtros aplicados direto nos dados
# ---------------------------------------------------------------------------

SERVICOS = {  # palavra no pedido -> texto procurado em streaming_assinatura_br
    "netflix": "netflix",
    "prime video": "prime video",
    "amazon": "amazon prime",
    "disney": "disney",
    "hbo": "hbo",
    "globoplay": "globoplay",
    "apple tv": "apple tv",
    "paramount": "paramount",
    "mubi": "mubi",
    "crunchyroll": "crunchyroll",
}

IDIOMAS = {  # palavra no pedido -> códigos de idioma_original
    r"japon\w*": ["ja"],
    r"corean\w*": ["ko"],
    r"frances\w*": ["fr"],
    r"espanho\w*": ["es"],
    r"italian\w*": ["it"],
    r"alema\w*": ["de"],
    r"brasileir\w*|nacional": ["pt"],
    r"chines\w*": ["cn", "zh"],
    r"indian\w*": ["hi"],
}

DURACAO_CURTO_PADRAO = 100  # "filme curto" sem número = menos de 100 min


def achar_filtros(t):
    """Lê o pedido (já sem acento) e devolve os filtros explícitos."""
    filtros = {}

    # Gênero: "terror", "comédia romântica"...
    incluir, excluir = [], []
    for genero, padroes in GENEROS.items():
        r = achar_padroes(t, padroes)
        if r == "sim":
            incluir.append(genero)
        elif r == "nao":
            excluir.append(genero)
    if incluir:
        filtros["generos"] = incluir
    if excluir:
        filtros["sem_generos"] = excluir

    # Duração: "menos de 1h40", "menos de 90 min", "curto"
    m = re.search(r"menos de (\d+)\s*h\s*(\d+)?", t)
    if m:
        filtros["duracao_max"] = int(m.group(1)) * 60 + int(m.group(2) or 0)
    else:
        m = re.search(r"menos de (\d+)\s*min", t)
        if m:
            filtros["duracao_max"] = int(m.group(1))
        elif re.search(r"\bcurt[oa]\b", t):
            filtros["duracao_max"] = DURACAO_CURTO_PADRAO

    # Streaming
    for palavra, servico in SERVICOS.items():
        if re.search(r"\b" + palavra + r"\b", t):
            filtros["streaming"] = servico
            break

    # Ano: "anos 80", "anos 2000", "de 1994"
    m = re.search(r"\banos (\d{2,4})\b", t)
    if m:
        d = int(m.group(1))
        if d < 100:
            d += 1900 if d >= 30 else 2000
        filtros["ano_min"], filtros["ano_max"] = d, d + 9
    else:
        m = re.search(r"\bde (19\d\d|20\d\d)\b", t)
        if m:
            filtros["ano_min"] = filtros["ano_max"] = int(m.group(1))

    # Idioma original
    for padrao, codigos in IDIOMAS.items():
        if re.search(r"\b(" + padrao + r")\b", t):
            filtros["idiomas"] = codigos
            break

    return filtros


def aplicar_filtros(filmes, filtros):
    ok = pd.Series(True, index=filmes.index)
    if "duracao_max" in filtros:
        ok &= (filmes.duracao_min > 0) & (filmes.duracao_min < filtros["duracao_max"])
    if "streaming" in filtros:
        ok &= filmes.streaming_assinatura_br.fillna("").str.lower().str.contains(filtros["streaming"], regex=False)
    if "ano_min" in filtros:
        ok &= filmes.ano.between(filtros["ano_min"], filtros["ano_max"])
    if "idiomas" in filtros:
        ok &= filmes.idioma_original.isin(filtros["idiomas"])
    for g in filtros.get("sem_generos", []):
        ok &= ~filmes._generos.map(lambda gs: g in gs)
    if "generos" in filtros:
        quer = set(filtros["generos"])
        todos = ok & filmes._generos.map(lambda gs: quer <= gs)
        if todos.sum() >= TOP_N or len(quer) == 1:
            ok = todos
        else:  # poucos filmes com todos os gêneros juntos -> aceita qualquer um deles
            ok &= filmes._generos.map(lambda gs: bool(quer & gs))
    return ok


# ---------------------------------------------------------------------------
# Pedidos de referência ("tipo Matrix")
# ---------------------------------------------------------------------------

# Pessoas citadas como referência -> filmes delas no filmes.csv (lista feita à mão,
# porque o filmes.csv não tem coluna de diretor). Só filmes dirigidos pela pessoa.
PESSOAS = {
    "tarantino": [
        "Cães de Aluguel", "Pulp Fiction: Tempo de Violência", "Jackie Brown",
        "Kill Bill: Volume 1", "Kill Bill: Volume 2", "À Prova de Morte",
        "Bastardos Inglórios", "Django Livre", "Os Oito Odiados", "Era Uma Vez em… Hollywood",
    ],
}

GATILHOS_REFERENCIA = r"(?:tipo|parecid[oa] com|como|no estilo d[eoa]|no estilo|estilo d[eoa]|estilo)\s+(.+)"


def achar_referencia(t, filmes):
    """Se o pedido cita um filme/franquia/pessoa, devolve (nome citado, índices dos filmes citados)."""
    for m in re.finditer(GATILHOS_REFERENCIA, t):
        nome = re.split(r",| mas | so que | porem | e que ", m.group(1))[0].strip(" .!?")
        if not nome:
            continue
        # 1) Título exato (ou a parte antes dos dois-pontos)
        exato = filmes.index[(filmes._tit == nome) | (filmes._tit_orig == nome) | (filmes._tit_curto == nome)]
        if len(exato):
            return nome, list(exato)
        # 2) Pessoa conhecida
        if nome in PESSOAS:
            return nome, list(filmes.index[filmes.titulo.isin(PESSOAS[nome])])
        # 3) Franquia: títulos que começam com o nome ("harry potter e ...")
        franquia = filmes.index[filmes._tit.str.startswith(nome + " ") | filmes._tit_orig.str.startswith(nome + " ")]
        if len(franquia):
            return nome, list(franquia)
    return None, []


# ---------------------------------------------------------------------------
# Parte comum às duas abordagens
# ---------------------------------------------------------------------------

def carregar_filmes(arq=ARQ_FILMES):
    f = pd.read_csv(arq)
    f["sinopse"] = f.sinopse.fillna("")
    f["_tit"] = f.titulo.map(sem_acento).str.strip()
    f["_tit_orig"] = f.titulo_original.map(sem_acento).str.strip()
    f["_tit_curto"] = f._tit.str.split(":").str[0].str.strip()
    f["_generos"] = f.generos.str.split("|").map(set)
    f["_kw"] = f.palavras_chave.fillna("").str.split("|").map(lambda l: set(x for x in l if x))
    # Nota ajustada pelos votos (filmes com poucos votos puxados para a média). Só para desempate.
    m, c = f.votos.median(), f.nota.mean()
    f["_nota_ajustada"] = (f.votos / (f.votos + m)) * f.nota + (m / (f.votos + m)) * c
    return f


def analisar(pedido, filmes):
    """Tudo que os dois motores precisam saber do pedido."""
    t = sem_acento(pedido)
    ref_nome, ref_idx = achar_referencia(t, filmes)
    if ref_nome:  # tira o nome citado ("clube da luta") para ele não ativar gênero/tema ("luta")
        t = t.replace(ref_nome, " ")
    return {"texto": t, "filtros": achar_filtros(t), "referencia": ref_nome or "", "ref_idx": ref_idx}


def montar_info(filmes, a, temas=None, temas_negados=None):
    return {
        "filtros": a["filtros"],
        "referencia": a["referencia"],
        "excluidos": filmes.loc[a["ref_idx"], "titulo"].tolist(),
        "temas": temas or [],
        "temas_negados": temas_negados or [],
    }


# ---------------------------------------------------------------------------
# Abordagem A: dicionário -> palavras-chave em inglês
# ---------------------------------------------------------------------------

class MotorA:
    nome = "A"

    def __init__(self, arq_filmes=ARQ_FILMES):
        self.filmes = carregar_filmes(arq_filmes)

    def recomendar(self, pedido, n=TOP_N):
        f = self.filmes
        a = analisar(pedido, f)
        pontos, temas, negados = self.pontuar(a)

        candidatos = aplicar_filtros(f, a["filtros"])
        candidatos[a["ref_idx"]] = False  # o filme citado não pode aparecer

        res = f.loc[candidatos, ["titulo", "ano", "nota", "votos", "_nota_ajustada"]].copy()
        res["pontos"] = pontos[candidatos].round(3)
        res = res.sort_values(["pontos", "_nota_ajustada"], ascending=False).head(n)
        return res.drop(columns="_nota_ajustada"), montar_info(f, a, temas, negados)

    def pontuar(self, a):
        """Pontos de todos os filmes para um pedido já analisado. Devolve (pontos, temas, temas negados)."""
        f = self.filmes

        # 1) Quais temas do dicionário o pedido ativa (e quais aparecem negados)
        temas, negados = [], []
        for tema, d in DICIONARIO.items():
            r = achar_padroes(a["texto"], d["padroes"])
            if r == "sim":
                temas.append(tema)
            elif r == "nao":
                negados.append(tema)

        # 2) Pontos: cada tema vale 1 ponto se o filme tiver alguma palavra-chave dele,
        #    +0,1 por palavra-chave extra do mesmo tema. Tema negado tira 1 ponto.
        pontos = pd.Series(0.0, index=f.index)
        for tema in temas:
            termos = set(DICIONARIO[tema]["palavras_chave"])
            batidas = f._kw.map(lambda kw: len(kw & termos))
            pontos += (batidas > 0) + 0.1 * (batidas - 1).clip(lower=0)
        for tema in negados:
            termos = set(DICIONARIO[tema]["palavras_chave"])
            pontos -= f._kw.map(lambda kw: bool(kw & termos)).astype(float)

        # 3) Referência: cada palavra-chave em comum com o filme citado soma pontos
        #    (com vários filmes citados, pesa pela fração deles que têm a palavra).
        if a["ref_idx"]:
            cont = collections.Counter(
                k for i in a["ref_idx"] for k in f.at[i, "_kw"]
                if not any(meta in k for meta in PALAVRAS_META)
            )
            pesos = {k: v / len(a["ref_idx"]) for k, v in cont.items()}
            pontos += f._kw.map(lambda kw: sum(pesos.get(k, 0) for k in kw))

        return pontos, temas, negados


# ---------------------------------------------------------------------------
# Abordagem B: texto da sinopse (TF-IDF + cosseno)
# ---------------------------------------------------------------------------

class MotorB:
    nome = "B"

    def __init__(self, arq_filmes=ARQ_FILMES, filmes=None):
        self.filmes = carregar_filmes(arq_filmes) if filmes is None else filmes
        self.vetorizador = TfidfVectorizer(sublinear_tf=True)
        self.matriz = self.vetorizador.fit_transform(self.filmes.sinopse.map(preparar_texto))

    def pontuar(self, a):
        """Similaridade (0 a 1) entre o pedido já analisado e a sinopse de cada filme."""
        f = self.filmes
        # Texto de busca: o pedido + (se for referência) a sinopse dos filmes citados
        busca = a["texto"]
        if a["ref_idx"]:
            busca += " " + " ".join(f.loc[a["ref_idx"], "sinopse"])
        vetor = self.vetorizador.transform([preparar_texto(busca)])
        return cosine_similarity(vetor, self.matriz).ravel()

    def recomendar(self, pedido, n=TOP_N):
        f = self.filmes
        a = analisar(pedido, f)
        sim = self.pontuar(a)

        candidatos = aplicar_filtros(f, a["filtros"])
        candidatos[a["ref_idx"]] = False  # o filme citado não pode aparecer

        res = f.loc[candidatos, ["titulo", "ano", "nota", "votos"]].copy()
        res["pontos"] = sim[candidatos.values]
        # Empate (ex.: nenhuma palavra em comum) -> o mais popular primeiro
        res = res.sort_values(["pontos", "votos"], ascending=False).head(n)
        return res, montar_info(f, a)


# ---------------------------------------------------------------------------
# Abordagem H (híbrida): pontos da A + similaridade da B, na mesma escala
# ---------------------------------------------------------------------------

AVISO_NAO_ENTENDI = "Não entendi bem o pedido. Tente descrever o gênero, o clima ou o tema."
# Similaridade mínima com alguma sinopse para um pedido sem tema/gênero/filtro/referência.
# Escolhido olhando só os 40 pedidos de treino: o menor valor de um pedido real foi 0,156.
LIMIAR_SIMILARIDADE = 0.15
PESOS_H = {"H50": 0.5, "H70": 0.7}  # peso da A (o resto vai para a B)


def escala_0_1(valores):
    """Coloca os valores entre 0 (pior) e 1 (melhor). Se todos forem iguais, todos viram 0."""
    menor, maior = valores.min(), valores.max()
    if maior == menor:
        return valores * 0.0
    return (valores - menor) / (maior - menor)


class MotorH:
    def __init__(self, peso_a=0.5, nome="H", arq_filmes=ARQ_FILMES):
        self.nome = nome
        self.peso_a = peso_a
        self.motor_a = MotorA(arq_filmes)
        self.filmes = self.motor_a.filmes
        self.motor_b = MotorB(filmes=self.filmes)

    def recomendar(self, pedido, n=TOP_N):
        f = self.filmes
        a = analisar(pedido, f)
        pontos_a, temas, negados = self.motor_a.pontuar(a)
        sim_b = pd.Series(self.motor_b.pontuar(a), index=f.index)
        info = montar_info(f, a, temas, negados)
        info["similaridade_max"] = round(float(sim_b.max()), 3)

        # O pedido foi entendido se ativou algum tema, gênero, filtro ou referência,
        # ou se a sinopse de algum filme é parecida o bastante com ele.
        entendeu = bool(temas or negados or a["filtros"] or a["ref_idx"]) or sim_b.max() >= LIMIAR_SIMILARIDADE
        if not entendeu:
            info["aviso"] = AVISO_NAO_ENTENDI
            return pd.DataFrame(columns=["titulo", "ano", "nota", "votos", "pontos"]), info

        candidatos = aplicar_filtros(f, a["filtros"])
        candidatos[a["ref_idx"]] = False  # o filme citado não pode aparecer

        res = f.loc[candidatos, ["titulo", "ano", "nota", "votos", "_nota_ajustada"]].copy()
        res["pontos"] = (self.peso_a * escala_0_1(pontos_a[candidatos])
                         + (1 - self.peso_a) * escala_0_1(sim_b[candidatos])).round(4)
        res = res.sort_values(["pontos", "_nota_ajustada"], ascending=False).head(n)
        return res.drop(columns="_nota_ajustada"), info


# ---------------------------------------------------------------------------
# Avaliação nos pedidos de teste
# ---------------------------------------------------------------------------

def _tem(col, texto):
    return col.fillna("").str.contains(texto, regex=False)


# Regras escritas nas observações da planilha (pedidos de filtro): um filme que cumpre a regra
# também conta como acerto, mesmo que não esteja na lista de boas respostas.
REGRAS = {
    36: lambda f: (f.duracao_min < 100) & f.generos.str.contains("Comédia|Animação|Família|Romance"),
    37: lambda f: _tem(f.generos, "Comédia") & _tem(f.streaming_assinatura_br, "Netflix"),
    38: lambda f: f.ano.between(1980, 1989) & (f.nota >= 7.3),
    39: lambda f: _tem(f.generos, "Animação") & (f.idioma_original == "ja"),
}


# Conjunto de desenvolvimento do motor T: pedidos 1 a 90 (treino + validação + final do autor).
# Os pedidos 91 a 110 (pedidos_final2.csv) ficam guardados para o teste final.
ARQS_DESENVOLVIMENTO = ["pedidos_teste.csv", "pedidos_validacao.csv", "pedidos_final.csv"]


def ler_pedidos(arq_pedidos):
    arqs = arq_pedidos if isinstance(arq_pedidos, (list, tuple)) else [arq_pedidos]
    d = pd.concat([pd.read_csv(a, encoding="utf-8", dtype=str, keep_default_na=False) for a in arqs],
                  ignore_index=True).fillna("")
    d["numero"] = d.numero.astype(int)
    return d


def avaliar(motor, arq_pedidos=ARQ_PEDIDOS):
    pedidos = ler_pedidos(arq_pedidos)
    f = motor.filmes
    titulos_catalogo = set(f.titulo)
    linhas = []
    for p in pedidos.itertuples():
        top, info = motor.recomendar(p.pedido)
        gabarito = {t.strip() for t in p.boas_respostas.split("|") if t.strip()}
        certos_gab = [t for t in top.titulo if t in gabarito]
        certos_regra = []
        regra = REGRAS[p.numero](f) if p.numero in REGRAS else None
        if regra is not None:
            certos_regra = [f.at[i, "titulo"] for i in top.index if regra.at[i]]
        certos = list(dict.fromkeys(certos_gab + certos_regra))
        # Relevância posição a posição (gabarito ou regra) -> precisão e NDCG@5
        rel = [(t in gabarito) or (regra is not None and bool(regra.at[i])) for i, t in zip(top.index, top.titulo)]
        n_ideal = TOP_N if regra is not None else min(TOP_N, len(gabarito & titulos_catalogo))
        dcg = sum(1 / np.log2(k + 2) for k, r in enumerate(rel) if r)
        idcg = sum(1 / np.log2(k + 2) for k in range(n_ideal))
        linha = {
            "numero": p.numero,
            "estilo": p.estilo,
            "pedido": p.pedido,
            "acertou": "sim" if certos else "não",
            "qtd_boas_no_top5": len(certos_gab),  # quantos dos 5 estão em boas_respostas
            "n_bons": int(sum(rel)),              # gabarito ou regra
            "precisao": sum(rel) / TOP_N,
            "ndcg5": round(dcg / idcg, 4) if idcg else 0.0,
            "top_titulos": " | ".join(top.titulo),
        }
        # Nota estrita: só os filmes que o próprio autor citou (quando o arquivo tem essa coluna)
        if "filmes_do_autor" in pedidos.columns and p.filmes_do_autor:
            do_autor = {t.strip() for t in p.filmes_do_autor.split("|") if t.strip()}
            certos_autor = [t for t in top.titulo if t in do_autor]
            linha["acertou_estrito"] = "sim" if certos_autor else "não"
            linha["filmes_do_autor_no_top5"] = " | ".join(certos_autor)
        linha |= {
            "filmes_certos": " | ".join(certos),
            "acerto_pelo_gabarito": "sim" if certos_gab else "não",
            "acerto_pela_regra": ("sim" if certos_regra else "não") if p.numero in REGRAS else "",
            **{f"top{i + 1}": f"{r.titulo} ({r.ano})" for i, r in enumerate(top.itertuples())},
            "pontos_top1": round(float(top.pontos.iloc[0]), 3) if len(top) else 0,
            "filtros_aplicados": "; ".join(f"{k}={v}" for k, v in info["filtros"].items()),
            "referencia": info["referencia"],
            "excluidos": " | ".join(info["excluidos"]),
        }
        if motor.nome != "B":
            linha["temas"] = " | ".join(info["temas"])
            linha["temas_negados"] = " | ".join(info["temas_negados"])
        if "similaridade_max" in info:
            linha["similaridade_max"] = info["similaridade_max"]
        if "similaridade_max" in info or "aviso" in info or motor.nome.startswith("T"):
            linha["aviso"] = info.get("aviso", "")  # "não entendi" conta como erro
        if "modo_resposta" in info:  # motor T: etiquetas, sinopse ou reserva_populares
            linha["modo_resposta"] = info["modo_resposta"]
        linhas.append(linha)
    return pd.DataFrame(linhas)


def txt_acerto(r):
    return f"{r['acertos']}/{r['n']} ({r['acerto']:.0%})"


def resumo_metricas(res):
    """Nota de acerto, precisão média, NDCG@5 médio e cobertura (filmes diferentes nos tops 5)."""
    titulos = {t for s in res.top_titulos for t in s.split(" | ") if t}
    return {"acerto": (res.acertou == "sim").mean(), "precisao": res.precisao.mean(),
            "ndcg5": res.ndcg5.mean(), "cobertura": len(titulos), "n": len(res),
            "acertos": int((res.acertou == "sim").sum()),
            "avisos": int((res.get("aviso", pd.Series(dtype=str)).fillna("") != "").sum())}


def comparar_dev():
    """A, B, H70 (catálogo de 2.000), H70 no catálogo de 6.000 e T, nos pedidos 1 a 90."""
    from motor_t import MotorT
    motores = [MotorA(), MotorB(), MotorH(0.7, "H70"), MotorH(0.7, "H70-v2", arq_filmes="filmes_v2.csv"), MotorT()]
    resultados = {}
    for mt in motores:
        res = avaliar(mt, ARQS_DESENVOLVIMENTO)
        res.to_csv(f"resultados_{mt.nome}_desenvolvimento.csv", index=False, encoding="utf-8")
        resultados[mt.nome] = res
    out = []
    p = lambda s="": (print(s), out.append(s))
    p("=" * 78)
    p("DESENVOLVIMENTO (pedidos 1 a 90): A, B, H70, H70 no catálogo de 6.000 e T")
    p("=" * 78)
    p(f"Pesos do motor T: {motores[-1].pesos}")
    p(f"{'motor':<10}{'catálogo':>9}{'acerto':>14}{'precisão':>10}{'NDCG@5':>8}{'cobertura':>11}{'avisos':>8}")
    for nome, res in resultados.items():
        r = resumo_metricas(res)
        cat = "6.000" if nome in ("H70-v2", "T") else "2.000"
        p(f"{nome:<10}{cat:>9}{txt_acerto(r):>14}"
          f"{r['precisao']:>10.2f}{r['ndcg5']:>8.3f}{r['cobertura']:>11}{r['avisos']:>8}")
    p("(precisão = média de filmes bons entre os 5; NDCG@5 = 1 se os bons estão todos no topo; "
      "cobertura = filmes diferentes nos tops 5 dos 90 pedidos)")
    estilos = list(dict.fromkeys(resultados["A"].estilo))
    for metrica, rotulo in (("acerto", "Acerto por estilo"), ("ndcg5", "NDCG@5 por estilo"), ("precisao", "Precisão por estilo")):
        p(f"\n{rotulo}:")
        p(f"{'estilo':<12}{'n':>4}" + "".join(f"{n:>9}" for n in resultados))
        for e in estilos:
            linha = f"{e:<12}{(resultados['A'].estilo == e).sum():>4}"
            for res in resultados.values():
                g = res[res.estilo == e]
                v = (g.acertou == "sim").mean() if metrica == "acerto" else g[metrica].mean()
                linha += f"{v:>9.0%}" if metrica == "acerto" else f"{v:>9.2f}"
            p(linha)
    with open("relatorio_motor_t.txt", "w", encoding="utf-8") as arq:
        arq.write("\n".join(out) + "\n")
    print("\nSalvo em relatorio_motor_t.txt")


PESOS_TESTE_T = [
    {"tags": 1.0, "a": 0.0, "b": 0.0},
    {"tags": 0.7, "a": 0.3, "b": 0.0},
    {"tags": 0.6, "a": 0.2, "b": 0.2},
    {"tags": 0.5, "a": 0.3, "b": 0.2},
    {"tags": 0.4, "a": 0.4, "b": 0.2},
    {"tags": 0.3, "a": 0.5, "b": 0.2},
]


def ajustar_t():
    """Testa os conjuntos de pesos do motor T só nos pedidos 1 a 90 e guarda o melhor em pesos_t.json."""
    import json
    from motor_t import MotorT, ARQ_PESOS
    mt = MotorT(pesos=PESOS_TESTE_T[0])
    out = []
    p = lambda s="": (print(s), out.append(s))
    p("Ajuste de pesos do motor T (pedidos 1 a 90). Escolha: maior NDCG@5; empate -> maior acerto.")
    p(f"{'tags':>6}{'A':>6}{'B':>6}{'acerto':>14}{'precisão':>10}{'NDCG@5':>8}{'cobertura':>11}")
    melhores = []
    for pesos in PESOS_TESTE_T:
        mt.pesos = pesos
        r = resumo_metricas(avaliar(mt, ARQS_DESENVOLVIMENTO))
        melhores.append((r["ndcg5"], r["acerto"], pesos))
        p(f"{pesos['tags']:>6}{pesos['a']:>6}{pesos['b']:>6}{txt_acerto(r):>14}"
          f"{r['precisao']:>10.2f}{r['ndcg5']:>8.3f}{r['cobertura']:>11}")
    escolhido = max(melhores, key=lambda x: (x[0], x[1]))[2]
    json.dump(escolhido, open(ARQ_PESOS, "w", encoding="utf-8"))
    p(f"\nPesos escolhidos: {escolhido} -> salvos em {ARQ_PESOS}")
    with open("relatorio_pesos_t.txt", "w", encoding="utf-8") as arq:
        arq.write("\n".join(out) + "\n")


def mostrar_relatorio(res, nome):
    total = len(res)
    acertos = (res.acertou == "sim").sum()
    print(f"\n=== Abordagem {nome}: nota de acerto ===")
    print(f"{acertos} de {total} pedidos com pelo menos 1 filme bom no top {TOP_N} ({acertos / total:.0%})")
    if "acertou_estrito" in res:
        e = (res.acertou_estrito == "sim").sum()
        print(f"Nota estrita (filmes do autor): {e} de {total} ({e / total:.0%})")
    print(f"Média de filmes bons no top {TOP_N}: {res.qtd_boas_no_top5.mean():.2f}")

    print("\nPor estilo:")
    for estilo, g in res.groupby("estilo", sort=False):
        a = (g.acertou == "sim").sum()
        print(f"  {estilo:<11} {a}/{len(g)}  ({a / len(g):.0%})")

    if "aviso" in res:
        avisos = res[res.aviso.fillna("") != ""]
        print(f"\nPedidos que caíram no aviso \"não entendi\": {len(avisos)} {avisos.numero.tolist()}")

    print("\nPedidos que erraram:")
    for r in res[res.acertou == "não"].itertuples():
        print(f"\n  #{r.numero} [{r.estilo}] {r.pedido}")
        aviso = getattr(r, "aviso", "")
        if isinstance(aviso, str) and aviso:
            print(f"     AVISO: {aviso}")
            continue
        if r.filtros_aplicados:
            print(f"     filtros: {r.filtros_aplicados}")
        if getattr(r, "temas", ""):
            print(f"     temas: {r.temas}")
        if getattr(r, "temas_negados", ""):
            print(f"     temas negados: {r.temas_negados}")
        for i in range(1, TOP_N + 1):
            v = getattr(r, f"top{i}", "")
            if isinstance(v, str) and v:
                print(f"     {i}. {v}")


def tabela_por_estilo(sufixo=""):
    """Tabela de acertos por estilo para todas as abordagens que já têm arquivo de resultado."""
    res = {}
    for nome in ["A", "B", *PESOS_H]:
        arq = f"resultados_{nome}{sufixo}.csv"
        if os.path.exists(arq):
            res[nome] = pd.read_csv(arq, encoding="utf-8")
    base = next(iter(res.values()))
    print(f"\n=== Acertos por estilo {sufixo.strip('_') or 'treino'} ===")
    print(f"{'':<12}" + "".join(f"{n:>8}" for n in res))
    for estilo in base.estilo.unique():
        n = (base.estilo == estilo).sum()
        print(f"{estilo:<12}" + "".join(f"{f'{(r[r.estilo == estilo].acertou == 'sim').sum()}/{n}':>8}"
                                        for r in res.values()))
    print(f"{'TOTAL':<12}" + "".join(f"{f'{(r.acertou == 'sim').sum()}/{len(r)}':>8}" for r in res.values()))
    print(f"{'%':<12}" + "".join(f"{(r.acertou == 'sim').mean():>8.0%}" for r in res.values()))
    if all("acertou_estrito" in r for r in res.values()):
        print(f"{'estrita':<12}" + "".join(f"{f'{(r.acertou_estrito == 'sim').sum()}/{len(r)}':>8}"
                                           for r in res.values()))
        print(f"{'estrita %':<12}" + "".join(f"{(r.acertou_estrito == 'sim').mean():>8.0%}" for r in res.values()))
    if all("qtd_boas_no_top5" in r for r in res.values()):
        print(f"{'média boas':<12}" + "".join(f"{r.qtd_boas_no_top5.mean():>8.2f}" for r in res.values()))
    if all("acertou_estrito" in r for r in res.values()):
        print("\nNota estrita por estilo:")
        print(f"{'':<12}" + "".join(f"{n:>8}" for n in res))
        for estilo in base.estilo.unique():
            n = (base.estilo == estilo).sum()
            print(f"{estilo:<12}" + "".join(
                f"{f'{(r[r.estilo == estilo].acertou_estrito == 'sim').sum()}/{n}':>8}" for r in res.values()))


def comparar(sufixo=""):
    a = pd.read_csv(f"resultados_A{sufixo}.csv", encoding="utf-8")
    b = pd.read_csv(f"resultados_B{sufixo}.csv", encoding="utf-8")
    print(f"\n=== A contra B {sufixo.strip('_')} ===")
    print(f"{'':<12}{'A':>8}{'B':>8}")
    for estilo in a.estilo.unique():
        na = (a[a.estilo == estilo].acertou == "sim").sum()
        nb = (b[b.estilo == estilo].acertou == "sim").sum()
        n = (a.estilo == estilo).sum()
        print(f"{estilo:<12}{f'{na}/{n}':>8}{f'{nb}/{n}':>8}")
    na, nb = (a.acertou == "sim").sum(), (b.acertou == "sim").sum()
    print(f"{'TOTAL':<12}{f'{na}/{len(a)}':>8}{f'{nb}/{len(b)}':>8}")
    print(f"{'%':<12}{na / len(a):>8.0%}{nb / len(b):>8.0%}")

    m = a[["numero", "estilo", "pedido", "acertou"]].merge(b[["numero", "acertou"]], on="numero", suffixes=("_A", "_B"))
    print("\nPedido a pedido:")
    for r in m.itertuples():
        print(f"  #{r.numero:<3} {r.estilo:<11} A:{r.acertou_A:<4} B:{r.acertou_B:<4} {r.pedido[:60]}")
    so_a = m[(m.acertou_A == "sim") & (m.acertou_B == "não")].numero.tolist()
    so_b = m[(m.acertou_A == "não") & (m.acertou_B == "sim")].numero.tolist()
    nenhum = m[(m.acertou_A == "não") & (m.acertou_B == "não")].numero.tolist()
    print(f"\nSó A acertou: {so_a}\nSó B acertou: {so_b}\nNenhum acertou: {nenhum}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    opcao = (sys.argv[1] if len(sys.argv) > 1 else "B").upper()
    resto = [r for r in sys.argv[2:] if r != "--teste-final"]
    teste_final_autorizado = "--teste-final" in sys.argv

    # Outro conjunto de pedidos: "python motor.py A validacao" lê pedidos_validacao.csv
    arq_pedidos, sufixo = ARQ_PEDIDOS, ""
    if resto == ["desenvolvimento"]:
        arq_pedidos, sufixo, resto = ARQS_DESENVOLVIMENTO, "_desenvolvimento", []
    elif len(resto) == 1 and os.path.exists(f"pedidos_{resto[0]}.csv"):
        arq_pedidos, sufixo = f"pedidos_{resto[0]}.csv", f"_{resto[0]}"
        resto = []

    # Trava: os pedidos 91 a 110 são o teste final e só rodam uma vez, quando o autor autorizar.
    if sufixo == "_final2" and not teste_final_autorizado:
        print("Os pedidos 91 a 110 (final2) estão guardados para o teste final. "
              "Para rodar, acrescente --teste-final (só quando o autor autorizar).")
        return

    if opcao == "COMPARAR_DEV":
        comparar_dev()
        return
    if opcao == "T" and resto == ["ajustar"]:
        ajustar_t()
        return
    if opcao == "COMPARAR":
        comparar(sufixo)
        return
    if opcao == "TABELA":
        tabela_por_estilo(sufixo)
        return
    if opcao == "A":
        motores = [MotorA()]
    elif opcao == "B":
        motores = [MotorB()]
    elif opcao == "H":  # roda os dois pesos
        motores = [MotorH(peso, nome) for nome, peso in PESOS_H.items()]
    elif opcao in PESOS_H:
        motores = [MotorH(PESOS_H[opcao], opcao)]
    elif opcao == "T":
        from motor_t import MotorT
        motores = [MotorT()]
    else:
        print("Use: python motor.py A | B | H | H50 | H70 | T | comparar | tabela | comparar_dev  [arquivo]\n"
              "     python motor.py T ajustar   (testa os pesos do motor T nos pedidos 1 a 90)")
        return

    if resto:  # pedido avulso
        top, info = motores[0].recomendar(" ".join(resto))
        print(info)
        print(top.to_string(index=False))
        return

    for motor in motores:
        res = avaliar(motor, arq_pedidos)
        saida = f"resultados_{motor.nome}{sufixo}.csv"
        res.to_csv(saida, index=False, encoding="utf-8")
        mostrar_relatorio(res, f"{motor.nome}{' (' + sufixo.strip('_') + ')' if sufixo else ''}")
        print(f"\nResultados salvos em {saida}")


if __name__ == "__main__":
    main()
