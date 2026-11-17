"""
Conferência (não é medição): compara o top 5 do motor T congelado v5 com o motor T atual (v6, referência por
ML/TMDB) nos pedidos 91 a 170 e nas 161 frases do estresse. Só informa o que mudou; nada é desfeito por causa disso.

Uso: python -I comparar_v5_v6.py [saida.txt]
Os pedidos 111 a 170 são conjuntos consumidos: aqui só se lista o que mudou, sem ajustar nada.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd


def pedidos():
    ps = []
    for arq in ["pedidos_final2.csv", "pedidos_final3.csv", "pedidos_final4.csv", "pedidos_estresse.csv"]:
        d = pd.read_csv(arq, usecols=["numero", "pedido"], dtype=str, keep_default_na=False)
        ps += list(d.itertuples(index=False))
    return ps


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    saida = sys.argv[1] if len(sys.argv) > 1 else "comparacao_v5_v6.txt"
    from motor_t import MotorT
    from motor_t_v5_congelado import MotorT as MotorT5
    antes, depois = MotorT5(), MotorT()
    L, mudou = [], 0
    for p in pedidos():
        ta, ia = antes.recomendar(p.pedido)
        td, idd = depois.recomendar(p.pedido)
        if list(ta.index) != list(td.index) or ia.get("modo_resposta") != idd.get("modo_resposta"):
            mudou += 1
            L.append(f"#{p.numero} \"{p.pedido}\"  [{ia.get('modo_resposta')} -> {idd.get('modo_resposta')}]"
                     f"  referência: {idd.get('referencia') or '-'}\n"
                     f"   antes:  {' | '.join(ta.titulo)}\n   depois: {' | '.join(td.titulo)}")
    cab = f"Top 5 v5 (congelado) x v6 (atual): mudou em {mudou} de {len(pedidos())} pedidos (91-170 + estresse 201-361)"
    open(saida, "w", encoding="utf-8").write(cab + "\n\n" + "\n".join(L) + "\n")
    print(cab)
    print("\n".join(L))


if __name__ == "__main__":
    main()
