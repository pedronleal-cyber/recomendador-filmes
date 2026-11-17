"""
Conferência (NÃO é medição): compara o top 5 do motor T congelado v2 (motor_t_v2_congelado.py) com o motor T atual (v3)
nos pedidos 91 a 110, para o autor avaliar se mudou para melhor ou pior. Não usa gabarito nem calcula acerto.
Os pedidos 111 a 140 NÃO entram aqui (teste cego, proibidos para ajuste).

Uso:  python -I comparar_v2_v3.py
Gera: comparacao_91_110_v2_v3.txt
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd

import motor_t as novo
import motor_t_v2_congelado as velho

SAIDA = "comparacao_91_110_v2_v3.txt"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ped = pd.read_csv("pedidos_final2.csv", usecols=["numero", "pedido"], dtype=str, keep_default_na=False)
    v2, v3 = velho.MotorT(), novo.MotorT()
    L, mudaram = [], []
    for p in ped.itertuples():
        t2, i2 = v2.recomendar(p.pedido)
        t3, i3 = v3.recomendar(p.pedido)
        a = [f"{r.titulo} ({r.ano})" for r in t2.itertuples()]
        b = [f"{r.titulo} ({r.ano})" for r in t3.itertuples()]
        if a != b or i2.get("modo_resposta") != i3.get("modo_resposta"):
            mudaram.append(int(p.numero))
            L.append(f"#{p.numero} \"{p.pedido}\"")
            L.append(f"   ANTES (v2, {i2.get('modo_resposta')}): " + "; ".join(a))
            L.append(f"   DEPOIS (v3, {i3.get('modo_resposta')}): " + "; ".join(b))
            novos_temas = [x for x in i3["temas"] if x not in i2["temas"]]
            fl = {k: v for k, v in i3["filtros"].items() if i2["filtros"].get(k) != v}
            L.append(f"   o que mudou no entendimento: temas novos={novos_temas or '-'}; filtros novos/alterados={fl or '-'}; "
                     f"correções={i3.get('correcoes') or '-'}")
            if set(a) == set(b) and a != b:
                L.append("   (mesmos filmes, outra ordem)")
            L.append("")
    cab = [f"Pedidos 91 a 110: {len(mudaram)} de {len(ped)} mudaram de top 5 ou de caminho de resposta: "
           + (", ".join(f"#{x}" for x in mudaram) or "nenhum"), ""]
    open(SAIDA, "w", encoding="utf-8").write("\n".join(cab + L) + "\n")
    print("\n".join(cab + L))


if __name__ == "__main__":
    main()
