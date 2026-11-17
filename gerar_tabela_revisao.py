"""
Gera tabela_revisao.md: para cada expressão nova da rodada 2 (EXTRAS_V2), as etiquetas (e o que ela "evita"),
quantos filmes ficam entre os 20% mais fortes em pelo menos uma etiqueta e 3 filmes de exemplo do topo da expressão.
Também lista as palavras-chave do TMDB (com contagem) e as regras novas do motor. Não é medição.

"20% mais fortes" = posição >= 0,8 em alguma fonte (nota >= 0,6 na escala do motor), o mesmo método das contagens antigas.
Exemplos = filmes com a maior soma peso x nota nas etiquetas da expressão (menos as que ela evita); desempate pela nota ajustada.

Uso:  python -I gerar_tabela_revisao.py
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

import motor_t as mt
from adicoes_dicionario_v2 import PALAVRAS_CHAVE_TMDB as PROPOSTA_KW
from dicionario_tags import DICIONARIO_TAGS, EXTRAS_V2, GIRIAS_BEM_AVALIADO

SAIDA = "tabela_revisao.md"


def main():
    t = mt.MotorT()
    f = t.filmes
    idx = {x: j for j, x in enumerate(t.vocab)}
    L = ["# Revisão das expressões novas do motor T (rodada 2 / v3)", "",
         "Para o autor revisar. Fonte: `adicoes_dicionario_v2.py` (do diagnóstico de estresse e do teste no site).",
         "Os pedidos 111 a 140 NÃO foram usados. Isto não é medição.", "",
         "- **Filmes fortes** = filmes entre os 20% mais fortes em pelo menos uma etiqueta da expressão.",
         "- **Exemplos** = os 3 filmes com a maior soma peso × nota nas etiquetas da expressão, menos as que ela evita.",
         "- \"pais e filhos\" já existia: as duas versões foram juntadas (padrões somados, maior peso de cada etiqueta).", "",
         "| Expressão | Padrões (sem acento) | Etiquetas (peso) | Evita | Filmes fortes | 3 exemplos |",
         "|---|---|---|---|---|---|"]
    for nome in EXTRAS_V2:
        e = DICIONARIO_TAGS[nome]
        forte = np.zeros(len(f), bool)
        nota = np.zeros(len(f))
        for tg, w in e["tags"].items():
            forte |= t.M[:, idx[tg]] >= 0.6 - 1e-6
            nota += w * t.M[:, idx[tg]]
        for tg, w in e.get("evita", {}).items():
            nota -= w * t.M[:, idx[tg]]
        ordem = sorted(range(len(f)), key=lambda i: (-round(nota[i], 6), -f._nota_ajustada.iat[i]))[:3]
        ex = "; ".join(f"{f.titulo.iat[i]} ({f.ano.iat[i]})" for i in ordem)
        tags = ", ".join(f"{k} ({v:g})" for k, v in e["tags"].items())
        evita = ", ".join(f"{k} ({v:g})" for k, v in e.get("evita", {}).items()) or "–"
        extra = " + empurrão pela nota" if e.get("nota") else ""
        pad = ", ".join(f"`{p}`" for p in e["padroes"]).replace("|", r"\|")
        L.append(f"| {nome} | {pad} | {tags}{extra} | {evita} | {forte.sum()} | {ex} |")

    kw = collections.Counter(k for s in f._kw for k in s)
    L += ["", "## Palavras-chave do TMDB (só entram com 20+ filmes)", "",
          "| Expressão | Palavra-chave | Filmes no catálogo | Situação | 3 exemplos (mais bem avaliados) |", "|---|---|---|---|---|"]
    for exp, k in PROPOSTA_KW.items():
        n = kw.get(k, 0)
        tem = f[f._kw.map(lambda s, k=k: k in s)].sort_values("_nota_ajustada", ascending=False).head(3)
        ex = "; ".join(f"{r.titulo} ({r.ano})" for r in tem.itertuples()) or "–"
        sit = "ativa (filtro; negada = exclui)" if n >= 20 else "NÃO ativa (menos de 20 filmes)"
        L.append(f"| `{exp.replace('|', ' / ')}` | {k} | {n} | {sit} | {ex} |")
    L += ["", "\"filme mudo\" (silent film, 19 filmes) não virou filtro: o site avisa que não consegue filtrar filmes mudos.",
          "\"marvel\" (marvel cinematic universe) não existe como palavra-chave no catálogo; \"não é da Marvel\" continua sem filtro.", "",
          "## Regras novas do motor (resumo)", "",
          f"- **Nota:** \"nota acima de N\", \"mais de N\", \"N+\", \"bem avaliado\", \"nota alta\" (7,5+) e gírias: "
          + ", ".join(f"`{g}`" for g in GIRIAS_BEM_AVALIADO) + ".",
          f"- **Duração:** \"até 1h30\", \"1h30\", \"no máximo 2 horas\", \"mais de 2h\", \"uma hora e meia\"; "
          f"\"não seja muito longo\" = até {mt.DURACAO_NAO_LONGO} min; \"longo\" = a partir de {mt.DURACAO_LONGO} min "
          "(\"um longa\" e \"longa-metragem\" não contam).",
          f"- **Época:** recente / lançamento / atual / \"filme novo\" = {mt.ANO_ATUAL - mt.ANOS_RECENTE}+; "
          f"antigo / \"filme velho\" = até {mt.ANO_ANTIGO_MAX} (\"Roma antiga\", \"Egito antigo\" não contam); "
          f"moderno / contemporâneo = {mt.ANO_MODERNO_MIN}+; preto e branco = palavra-chave.",
          "- **Streaming:** \"max\", \"prime\", \"disney\", \"globo\", \"apple\" só contam depois de \"na/no/tem na/que passe na...\"; "
          "\"da Disney\" (estúdio) não liga o filtro.",
          "- **Referência:** também \"similar a\", \"semelhante a\", \"igual a\", \"no estilo de\", \"na vibe de\", \"lembra\" e "
          "\"como\" (só antes de título conhecido), com artigo opcional.",
          f"- **Digitação:** tabela de correções + distância de edição 1 para palavras de {mt.MIN_LETRAS_CORRECAO}+ letras que não "
          "existem nas sinopses (ex.: \"aventrua\" → \"aventura\").",
          "- **Só filtros:** catálogo filtrado ordenado pela nota ajustada pelos votos (caminho \"filtros\").",
          f"- **Aleatório / surpreenda-me:** sorteio entre os filmes com nota {mt.NOTA_ALEATORIO:g}+ (caminho \"aleatorio\").",
          f"- **Pouco conhecido / obscuro:** nota {mt.NOTA_POUCO_CONHECIDO:g}+ e menos votos que a mediana ({t.mediana_votos:.0f}).",
          f"- **Reserva por sinopse:** palavra do pedido que está no título do filme vale {mt.PESO_PALAVRA_DO_TITULO:.0%}."]
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"Gerado {SAIDA}")


if __name__ == "__main__":
    main()
