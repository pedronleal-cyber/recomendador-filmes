"""
Validação do porte Python -> JavaScript do motor T (NÃO é medição de desempenho).
1) Raízes das palavras: Python (snowballstemmer) x JS, para todas as palavras das sinopses.
2) Top 5 dos pedidos 91 a 170, das 161 frases do estresse (201 a 361) e de frases inventadas (v4 e v6, referência)
   (900+): motor_t.py x site/motor.js, incluindo o caminho de resposta e os avisos.
Não calcula acerto nem compara com gabarito.

Uso (na pasta do projeto):
    python -I site_teste/validar_site.py
"""
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

import pandas as pd

import motor as m
from motor_t import MotorT

PASTA = os.path.join(RAIZ, "site_teste")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    f = pd.read_csv("filmes_v2.csv", usecols=["sinopse"])
    palavras = sorted({p for s in f.sinopse.fillna("") for p in re.findall(r"[a-z0-9]+", m.sem_acento(s))})
    raizes = dict(zip(palavras, m._stemmer.stemWords(palavras)))
    json.dump(raizes, open(os.path.join(PASTA, "raizes_python.json"), "w", encoding="utf-8"), ensure_ascii=False)

    t = MotorT()
    pedidos = pd.concat([pd.read_csv(a, usecols=["numero", "pedido"], dtype=str, keep_default_na=False)
                         for a in ("pedidos_final2.csv", "pedidos_final3.csv", "pedidos_final4.csv", "pedidos_estresse.csv")])
    # v4: frases inventadas (não vêm de nenhum conjunto de pedidos) para exercitar pessoas, países, estúdios e franquias
    extras = ["comédia com Adam Sandler", "filme do Nolan", "dirigido por Steven Spielberg", "sem o Adam Sandler, comédia",
              "terror com Tom Hanks", "filme com Wagner Moura", "dirigido por Fulano Beltrano", "filme do Miyazaki",
              "filme coreano de suspense", "falado em francês", "filme argentino", "algo que não seja americano, drama",
              "filme nórdico", "animação que não seja da Disney", "filme da Pixar", "algo do Studio Ghibli",
              "tipo Harry Potter", "parecido com Velozes e Furiosos", "filme europeu antigo", "comédia britânica",
              "na Disney, animação", "filme com Tom Hanks e Meg Ryan", "Keanu Reeves ação", "filme latino-americano",
              "filme de ação que não seja americano", "comédia sem ser americana",
              "misturar Matrix com Titanic", "tipo Toy Story e Shrek", "parecido com Parasita, mas mais leve",
              "tipo Interestelar dos anos 2000", "mistura de Up com Divertida Mente", "como Duna, na Netflix",
              "romance que se passa em Paris", "algo entre Jurassic Park e Indiana Jones", "no estilo de Corra!",
              "meio Matrix meio Titanic", "um Shrek com cara de Toy Story", "comédia indiana", "filme entre amigos e família",
              "tipo Duna", "quero algo que vá fazer minha cabeça fritar", "um filme mind-blowing", "nada de chorar, quero rir",
              "algo bem trash pra rir", "sem fritar a cabeça, algo leve"]
    pedidos = pd.concat([pedidos, pd.DataFrame({"numero": [str(900 + k) for k in range(len(extras))], "pedido": extras})])
    ref = []
    for p in pedidos.itertuples():
        top, info = t.recomendar(p.pedido)
        ref.append({"numero": int(p.numero), "pedido": p.pedido, "modo": info.get("modo_resposta"), "avisos": info.get("avisos", []),
                    "top": [int(i) for i in top.index], "pontos": [float(x) for x in top.pontos]})
    json.dump(ref, open(os.path.join(PASTA, "referencia_python.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"Python: {len(raizes)} palavras e {len(ref)} pedidos exportados. Rodando o motor JS...\n")
    subprocess.run(["node", os.path.join(PASTA, "validar.js")], check=True)


if __name__ == "__main__":
    main()
