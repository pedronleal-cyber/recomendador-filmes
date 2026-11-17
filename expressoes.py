"""
Expressões e sinônimos para as 150 etiquetas (rodada v8). Tudo calculado antes e guardado em tabelas: o site não usa IA.
As expressões foram escritas uma única vez pelo Claude (offline), em expressoes_lotes/ ("!" = frase de negação).

Comandos (rodar com python -I, na ordem):
  juntar      -> expressoes_etiquetas.csv (etiqueta, expressao, polaridade) + conferência (150 etiquetas, 30-50 cada)
  dividir     -> expressoes_teste.csv (20%, sorteado dentro de cada etiqueta e polaridade) e expressoes_treino.csv (80%).
                 Recusa rodar de novo se o teste já existir (o teste nunca muda).
  medir ROT [v7]  -> mede no conjunto de TESTE; "v7" usa o motor congelado v7 (antes). Gera medicao_expressoes_ROT.csv
  construir   -> transforma SÓ o treino em padrões (um por etiqueta) e grava o bloco EXTRAS_V8 no dicionario_tags.py
  comparar A B -> quadro antes x depois (medicao_expressoes_A.csv x medicao_expressoes_B.csv)

Como medir uma expressão de teste (o pedido é a própria expressão):
  positiva: "entendida" = a etiqueta foi ativada; "no topo" = está entre as de maior peso ativadas;
  negação:  "entendida" = a etiqueta foi penalizada (negada).
  Também: em quantos dos 5 filmes sugeridos a etiqueta é forte (posição >= 0,8 em alguma fonte).
CUIDADO: treino e teste foram escritos pelo mesmo autor ao mesmo tempo; o resultado no teste tende a ser otimista
em relação a pedidos de pessoas reais.
"""
import glob
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

ARQ_TODAS = "expressoes_etiquetas.csv"
ARQ_TESTE = "expressoes_teste.csv"
ARQ_TREINO = "expressoes_treino.csv"
SEMENTE = 2026
FRACAO_TESTE = 0.2
PESO = 1.0
INICIO_BLOCO = "# >>> EXTRAS_V8 (gerado por expressoes.py construir; não editar à mão)"
FIM_BLOCO = "# <<< EXTRAS_V8"

# Palavras que sozinhas não dizem nada sobre o filme (não viram padrão sozinhas)
GENERICAS = set("""
clima vibe forte filme filmes coisa mundo gente sobre muito legal humano poder poderes real sistema elite crime epoca
historia vida morte amor tempo time show luta texto papo livre campo rosa cool neon cara final fim noite manha tarde
coracao cabeca mente alma pessoa pessoas homem mulher crianca criancas jovem jovens velho nova novo grande pequeno
bonito bonita lindo linda bom boa melhor pior antigo antiga moderno atual dark light leve chorar triste pesado
sentir sentido vence pesada paciente menina inocente
""".split())
FILLERS_POS = set("quero queria um uma uns umas filme filmes algo alguma algum coisa que pra para me de do da dos das o a os as bem".split())
FILLERS_NEG = set("sem nao nada nem quero que seja ser de do da um uma filme filmes algo coisa nenhum nenhuma tanto tao me faca pra o a os as muito".split())


def norm(s):
    import motor as m
    return re.sub(r"[^a-z0-9\s-]", " ", m.sem_acento(s)).strip()


def nucleo(expr, negacao):
    toks = [t for t in re.split(r"[\s-]+", norm(expr)) if t]
    fill = FILLERS_NEG if negacao else FILLERS_POS
    while toks and toks[0] in fill:
        toks.pop(0)
    while toks and toks[-1] in ("demais",):
        toks.pop()
    return toks


def juntar():
    vocab = list(pd.read_csv("vocabulario_piloto.csv").tag)
    linhas = []
    for arq in sorted(glob.glob("expressoes_lotes/lote*.txt")):
        for ln in open(arq, encoding="utf-8"):
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            tag, resto = ln.split("|", 1)
            vistos = set()
            for e in resto.split(";"):
                e = e.strip()
                if not e:
                    continue
                neg = e.startswith("!")
                e = e.lstrip("!").strip()
                if (e, neg) in vistos:
                    continue
                vistos.add((e, neg))
                linhas.append({"etiqueta": tag, "expressao": e, "polaridade": "negacao" if neg else "positiva"})
    d = pd.DataFrame(linhas)
    fora = set(d.etiqueta) - set(vocab)
    faltam = set(vocab) - set(d.etiqueta)
    cont = d.groupby("etiqueta").size()
    print(f"{len(d)} expressões, {d.etiqueta.nunique()} etiquetas; por etiqueta: mín {cont.min()}, máx {cont.max()}, "
          f"média {cont.mean():.1f}; negação: {(d.polaridade == 'negacao').sum()}")
    if fora or faltam or cont.min() < 30 or cont.max() > 50:
        sys.exit(f"PROBLEMA: fora do vocabulário {fora}; faltam {faltam}; abaixo de 30: {list(cont[cont < 30].index)}")
    d.to_csv(ARQ_TODAS, index=False, encoding="utf-8")
    print(f"-> {ARQ_TODAS}")


def dividir():
    if os.path.exists(ARQ_TESTE):
        sys.exit(f"{ARQ_TESTE} já existe: o conjunto de teste não pode ser refeito.")
    d = pd.read_csv(ARQ_TODAS, keep_default_na=False)
    rnd = random.Random(SEMENTE)
    teste = []
    for (_, _), g in d.groupby(["etiqueta", "polaridade"], sort=True):
        idx = list(g.index)
        rnd.shuffle(idx)
        teste += idx[:max(1, round(FRACAO_TESTE * len(idx)))]
    d["conjunto"] = "treino"
    d.loc[teste, "conjunto"] = "teste"
    d[d.conjunto == "teste"].drop(columns="conjunto").to_csv(ARQ_TESTE, index=False, encoding="utf-8")
    d[d.conjunto == "treino"].drop(columns="conjunto").to_csv(ARQ_TREINO, index=False, encoding="utf-8")
    print(f"teste: {len(teste)} ({len(teste) / len(d):.0%}) | treino: {len(d) - len(teste)} -> {ARQ_TESTE}, {ARQ_TREINO}")


def medir(rotulo, versao=None):
    if versao == "v7":
        from motor_t_v7_congelado import MotorT
    else:
        from motor_t import MotorT
    mt = MotorT()
    col = {t: j for j, t in enumerate(mt.vocab)}
    forte = mt.M >= 0.6  # posição >= 0,8 em alguma fonte (metade de cima reescalada: (0,8-0,5)/0,5 = 0,6)
    d = pd.read_csv(ARQ_TESTE, keep_default_na=False)
    linhas = []
    for r in d.itertuples():
        c = mt.componentes(r.expressao)
        top, info = mt.recomendar(r.expressao)
        alvo = c["neg"] if r.polaridade == "negacao" else c["pos"]
        ativou = r.etiqueta in alvo
        topo = ativou and alvo[r.etiqueta] >= max(alvo.values())
        n_forte = int(sum(forte[mt.filmes.index.get_loc(i), col[r.etiqueta]] for i in top.index))
        linhas.append({"etiqueta": r.etiqueta, "expressao": r.expressao, "polaridade": r.polaridade,
                       "entendida": int(ativou), "no_topo": int(topo), "nenhuma_etiqueta": int(not (c["pos"] or c["neg"])),
                       "filmes_fortes_top5": n_forte, "modo": info.get("modo_resposta", ""),
                       "etiquetas_ativadas": "; ".join(f"{k}={v:g}" for k, v in sorted(c["pos"].items(), key=lambda kv: -kv[1])[:6]),
                       "etiquetas_negadas": "; ".join(sorted(c["neg"])[:6]), "top5": " | ".join(top.titulo)})
    out = pd.DataFrame(linhas)
    out.to_csv(f"medicao_expressoes_{rotulo}.csv", index=False, encoding="utf-8")
    resumo(out, rotulo)


def resumo(out, rotulo):
    pos, neg = out[out.polaridade == "positiva"], out[out.polaridade == "negacao"]
    print(f"[{rotulo}] {len(out)} expressões de teste ({len(pos)} positivas, {len(neg)} de negação)")
    print(f"  positivas entendidas: {pos.entendida.mean():.1%} | no topo: {pos.no_topo.mean():.1%} | "
          f"sem nenhuma etiqueta: {pos.nenhuma_etiqueta.mean():.1%} | filmes fortes no top 5: {pos.filmes_fortes_top5.mean():.2f}")
    print(f"  negações entendidas (etiqueta penalizada): {neg.entendida.mean():.1%}")


def construir():
    import motor as m
    import motor_t as mtm
    tr = pd.read_csv(ARQ_TREINO, keep_default_na=False)
    f = m.MotorA(mtm.ARQ_FILMES_T).filmes
    for c in ("_tit", "_tit_orig", "_tit_curto"):
        f[c + "_sl"] = f[c].map(mtm.so_letras)
    titulos = set(f._tit_sl) | set(f._tit_orig_sl) | set(f._tit_curto_sl)
    cred = mtm.montar_creditos(f, m.MotorB(filmes=f).vetorizador.vocabulary_)
    pessoas = set(cred["variantes"]) if cred else set()
    re_generos = [re.compile(r"\b(?:" + p + ")") for ps in m.GENEROS.values() for p in ps]
    re_outros = [re.compile(r"\b(?:" + p + ")") for p in
                 [p for p, _ in mtm.SERVICOS_T] + [e[0] for e in mtm.ESTUDIOS] + [p[0] for p in mtm.PAISES]]
    vazias = m.PALAVRAS_VAZIAS | mtm.PALAVRAS_DE_PEDIDO
    padroes, motivos = {}, {}
    for r in tr.itertuples():
        toks = nucleo(r.expressao, r.polaridade == "negacao")
        frase = " ".join(toks)
        motivo = None
        if not toks or len(frase) < 4:
            motivo = "curta demais"
        elif len(toks) == 1 and (len(toks[0]) < 5 or toks[0] in GENERICAS or toks[0] in vazias):
            motivo = "palavra genérica"
        elif mtm.so_letras(frase) in titulos:
            motivo = "título de filme"
        elif frase in pessoas:
            motivo = "nome de pessoa"
        elif any(rg.fullmatch(frase) for rg in re_generos):
            motivo = "gênero (já tratado)"
        elif any(rg.fullmatch(frase) for rg in re_outros):
            motivo = "serviço, estúdio ou país (já tratado)"
        if motivo:
            motivos[motivo] = motivos.get(motivo, 0) + 1
            continue
        padroes.setdefault(r.etiqueta, set()).add(r"[\s-]+".join(re.escape(t) for t in toks))
    bloco = [INICIO_BLOCO,
             "# Uma entrada por etiqueta, com os jeitos de pedir do conjunto de TREINO (80%) de expressoes_etiquetas.csv,",
             "# escritos pelo Claude (offline). Os padrões de cada etiqueta vão juntos numa só expressão regular.",
             "EXTRAS_V8 = {"]
    for tag in sorted(padroes):
        alt = "|".join(sorted(padroes[tag], key=lambda p: (-len(p), p)))
        bloco.append(f"    {('expr: ' + tag)!r}: {{\"padroes\": [{alt!r}], \"tags\": {{{tag!r}: {PESO}}}}},")
    bloco += ["}", FIM_BLOCO]
    s = open("dicionario_tags.py", encoding="utf-8").read()
    if INICIO_BLOCO in s:
        ini, fim = s.index(INICIO_BLOCO), s.index(FIM_BLOCO) + len(FIM_BLOCO)
        s = s[:ini] + "\n".join(bloco) + s[fim:]
    else:
        ancora = "\n\ndef _juntar(antiga, nova):"
        assert s.count(ancora) == 1
        s = s.replace(ancora, "\n\n" + "\n".join(bloco) + ancora)
    chamada = "    for nome, e in EXTRAS_V8.items():  # v8: expressões em massa (expressoes.py)\n        d[nome] = _juntar(d[nome], e) if nome in d else e\n"
    if chamada not in s:
        ancora = "    for nome, e in EXTRAS_V2.items():\n        d[nome] = _juntar(d[nome], e) if nome in d else e\n"
        assert s.count(ancora) == 1
        s = s.replace(ancora, ancora + chamada)
    open("dicionario_tags.py", "w", encoding="utf-8").write(s)
    n = sum(len(v) for v in padroes.values())
    print(f"EXTRAS_V8: {len(padroes)} etiquetas, {n} padrões a partir de {len(tr)} expressões de treino.")
    print("Descartadas: " + ", ".join(f"{k}: {v}" for k, v in sorted(motivos.items())))


def comparar(a, b):
    A = pd.read_csv(f"medicao_expressoes_{a}.csv", keep_default_na=False)
    B = pd.read_csv(f"medicao_expressoes_{b}.csv", keep_default_na=False)
    grupos = pd.read_csv("vocabulario_piloto.csv").set_index("tag").grupo
    L = [f"EXPRESSÕES DE TESTE (20% guardados antes de mexer no dicionário): {a} x {b}", ""]
    for pol, rot in (("positiva", "positivas"), ("negacao", "de negação")):
        x, y = A[A.polaridade == pol], B[B.polaridade == pol]
        L.append(f"{rot} ({len(x)}): entendidas {x.entendida.mean():.1%} -> {y.entendida.mean():.1%}"
                 + (f" | no topo {x.no_topo.mean():.1%} -> {y.no_topo.mean():.1%} | sem nenhuma etiqueta "
                    f"{x.nenhuma_etiqueta.mean():.1%} -> {y.nenhuma_etiqueta.mean():.1%} | filmes fortes no top 5 "
                    f"{x.filmes_fortes_top5.mean():.2f} -> {y.filmes_fortes_top5.mean():.2f}" if pol == "positiva" else ""))
    L.append("\nPositivas entendidas por grupo de etiqueta:")
    for g in sorted(grupos.unique()):
        x = A[(A.polaridade == "positiva") & A.etiqueta.map(grupos).eq(g)]
        y = B[(B.polaridade == "positiva") & B.etiqueta.map(grupos).eq(g)]
        L.append(f"  {g:<8} ({len(x):>3}): {x.entendida.mean():.1%} -> {y.entendida.mean():.1%}")
    j = A.merge(B, on=["etiqueta", "expressao", "polaridade"], suffixes=("_a", "_d"))
    piorou = j[(j.entendida_a == 1) & (j.entendida_d == 0)]
    L.append(f"\nPioraram (entendida antes, não depois): {len(piorou)}")
    for r in piorou.itertuples():
        L.append(f"  [{r.etiqueta}] \"{r.expressao}\" ({r.polaridade})")
    nao = j[(j.entendida_d == 0)]
    L.append(f"\nAinda não entendidas depois ({len(nao)}):")
    for r in nao.itertuples():
        L.append(f"  [{r.etiqueta}] \"{r.expressao}\" ({r.polaridade}) -> ativou: {r.etiquetas_ativadas_d or '-'}")
    saida = f"relatorio_expressoes_{a}_{b}.txt"
    open(saida, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:12]))
    print(f"... relatório completo em {saida}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cmd, args = (sys.argv[1] if len(sys.argv) > 1 else ""), sys.argv[2:]
    {"juntar": juntar, "dividir": dividir, "construir": construir}.get(cmd, lambda: None)() if cmd in (
        "juntar", "dividir", "construir") else (medir(*args) if cmd == "medir" else comparar(*args) if cmd == "comparar"
                                                 else print(__doc__))
