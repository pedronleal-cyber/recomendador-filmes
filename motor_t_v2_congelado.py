"""
Motor T (etiquetas): usa etiquetas_unificadas.csv (Tag Genome + ml-32m + IA) e combina com os motores A
(palavras-chave) e B (sinopse). Catálogo: filmes_v2.csv (6.000 filmes). Sem IA rodando: só cruzamento de dados.

Usado pelo motor.py:  python motor.py T  |  python motor.py T <arquivo>  |  python motor.py T ajustar
"""
import json
import os
import re

import numpy as np
import pandas as pd

import motor as m
from dicionario_tags_v2_congelado import DICIONARIO_TAGS, IDIOMAS_T, TAGS_POR_TERMO  # versão congelada v2 (antes da rodada de correções do estresse)

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
""".split())
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

    # --- partes do pedido que não dependem dos pesos (guardadas em cache)
    def componentes(self, pedido):
        if pedido in self._cache:
            return self._cache[pedido]
        f = self.filmes
        a = m.analisar(pedido, f)
        texto = a["texto"]

        # Etiquetas ativadas (positivas e negadas), com o maior peso de cada etiqueta.
        # Primeiro as expressões de "companhia" ("com meu pai"): ativam suas etiquetas e saem do texto,
        # para "pai" não virar tema de pais e filhos nem "família" virar filtro de gênero.
        pos, neg, temas, temas_neg = {}, {}, [], []
        usa_nota = False
        entradas = sorted(DICIONARIO_TAGS.items(), key=lambda kv: not kv[1].get("companhia", False))
        for nome, e in entradas:
            r = achar_t(texto, e["padroes"])
            if r == "sim":
                temas.append(nome)
                usa_nota |= e.get("nota", False)
                for t, w in e["tags"].items():
                    pos[t] = max(pos.get(t, 0), w)
                if e.get("companhia"):
                    for padrao in e["padroes"]:
                        texto = re.sub(r"\b(?:" + padrao + ")", " ", texto)
            elif r == "nao":
                temas_neg.append(nome)
                for t, w in e["tags"].items():
                    neg[t] = max(neg.get(t, 0), w)
        neg = {t: w for t, w in neg.items() if t not in pos}

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
            pos_ref = [f.index.get_loc(i) for i in ref_idx]
            perfil = self.M[pos_ref].mean(axis=0)
            if perfil.sum() > 0:
                ref_cos = (self.M @ perfil) / (self.normas * np.linalg.norm(perfil))
            for i in ref_idx:
                for col in ("_serie_orig", "_serie_pt"):
                    k = f.at[i, col]
                    mesmas = f.index[f[col].map(lambda x: mesma_familia(x, k))]
                    excluir |= set(mesmas)

        candidatos = m.aplicar_filtros(f, a["filtros"])
        candidatos[list(excluir)] = False

        pontos_a, temas_a, neg_a = self.motor_a.pontuar(m.analisar(pedido, f))  # motor A como ele é
        sim_b = pd.Series(self.motor_b.pontuar(a), index=f.index)
        # Sinopse para a reserva: só com as palavras que dizem algo sobre o filme
        palavras = [w for w in re.findall(r"[a-z0-9]+", texto) if w not in PALAVRAS_DE_PEDIDO and w not in m.PALAVRAS_VAZIAS]
        if palavras:
            vet = self.motor_b.vetorizador.transform([m.preparar_texto(" ".join(palavras))])
            sim_reserva = pd.Series(m.cosine_similarity(vet, self.motor_b.matriz).ravel(), index=f.index)
        else:
            sim_reserva = pd.Series(0.0, index=f.index)

        # Só avisa "não entendi" se nem as etiquetas do T, nem os temas do motor A (dicionario.py),
        # nem gênero, filtro ou referência reconheceram algo.
        entendeu = bool(pos or neg or temas_a or neg_a or a["filtros"] or ref_idx)
        comp = {
            "a": a, "candidatos": candidatos, "dict": pd.Series(dict_score, index=f.index),
            "ref": None if ref_cos is None else pd.Series(ref_cos, index=f.index),
            "A": pontos_a, "B": sim_b, "pos": pos, "neg": neg, "temas": temas, "temas_neg": temas_neg,
            "temas_a": temas_a, "excluir": excluir, "entendeu": entendeu, "usa_tags": bool(pos or neg),
            "usa_nota": usa_nota, "termos_negados": termos_negados, "B_reserva": sim_reserva,
        }
        self._cache[pedido] = comp
        return comp

    def recomendar(self, pedido, n=TOP_N):
        f = self.filmes
        c = self.componentes(pedido)
        info = m.montar_info(f, c["a"], c["temas"], c["temas_neg"])
        info["excluidos"] = f.loc[sorted(c["excluir"]), "titulo"].tolist()
        info["tags_ativadas"] = c["pos"]
        info["tags_negadas"] = c["neg"]
        info["temas_motor_a"] = c["temas_a"]
        info["termos_negados"] = c["termos_negados"]
        cand = c["candidatos"]

        if c["entendeu"]:
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

        res = f.loc[cand, ["titulo", "ano", "nota", "votos", "_nota_ajustada", "_serie_pt", "_serie_orig"]].copy()
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
