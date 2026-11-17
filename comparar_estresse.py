"""
Quadro ANTES x DEPOIS do diagnóstico de estresse (pedidos_estresse.csv, 161 frases).
É só conferência de DESCOBERTA DE FALHAS: não é medição e não tem gabarito.

Padrão (rodada v4): antes = resultados_estresse_T_v3.csv (motor T v3 congelado), depois = resultados_estresse_T.csv
(motor T v4). Os dois lados precisam ter sido gerados com as MESMAS regras de conferência (a-h) do rodar_estresse.py:
    python -I rodar_estresse.py v3
    python -I rodar_estresse.py
    python -I comparar_estresse.py
Gera: relatorio_estresse_v3_v4.txt

Também aceita outros arquivos: python -I comparar_estresse.py <antes.csv> <depois.csv> <saida.txt> [rótulo antes] [rótulo depois]
"""
import re
import sys

import pandas as pd

args = sys.argv[1:]
ANTES = args[0] if len(args) > 0 else "resultados_estresse_T_v3.csv"
DEPOIS = args[1] if len(args) > 1 else "resultados_estresse_T.csv"
SAIDA = args[2] if len(args) > 2 else "relatorio_estresse_v3_v4.txt"
ROT_A = args[3] if len(args) > 3 else "v3"
ROT_D = args[4] if len(args) > 4 else "v4"
TIPOS = {"a": "idioma/país", "b": "duração", "c": "ano/época", "d": "streaming", "e": "nota", "f": "negação",
         "g": "referência", "h": "nome de pessoa"}
MODOS = ["etiquetas", "filtros", "aleatorio", "sinopse", "reserva_populares"]
FOCO = ["pessoas", "pais_epoca", "negacao_filtro"]


def tipos(v):
    return set(re.findall(r"(?:^|\|\| )([a-h])\)", v)) if isinstance(v, str) else set()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    a = pd.read_csv(ANTES, keep_default_na=False)
    d = pd.read_csv(DEPOIS, keep_default_na=False)
    for df in (a, d):
        if "avisos_motor" not in df.columns:
            df["avisos_motor"] = ""
    j = a.merge(d, on=["numero", "categoria", "pedido"], suffixes=("_a", "_d"))
    j["ta"], j["td"] = j.violacoes_a.map(tipos), j.violacoes_d.map(tipos)
    L = []
    w = L.append
    w(f"ESTRESSE DO MOTOR T: ANTES ({ROT_A}) x DEPOIS ({ROT_D})")
    w("=" * 70)
    w("pedidos_estresse.csv é conjunto de DESCOBERTA DE FALHAS, nunca de medição. Os pedidos 111 a 140 não foram usados.")
    w("As regras de conferência (a-h) são as mesmas nos dois lados (rodar_estresse.py da rodada v4).")
    w(f"Frases: {len(j)}\n")
    w(f"1) MODO DE RESPOSTA            {ROT_A:>5}  {ROT_D:>6}")
    for mo in MODOS:
        w(f"   {mo:<26} {(a.modo_resposta == mo).sum():>5}  {(d.modo_resposta == mo).sum():>6}")
    w(f"\n2) FRASES COM VIOLAÇÃO, POR TIPO   {ROT_A:>5}  {ROT_D:>6}")
    for k, nome in TIPOS.items():
        w(f"   {k}) {nome:<26} {j.ta.map(lambda s: k in s).sum():>5}  {j.td.map(lambda s: k in s).sum():>6}")
    w(f"   {'com alguma violação':<29} {(j.ta.map(len) > 0).sum():>5}  {(j.td.map(len) > 0).sum():>6}")
    w(f"   {'sem contar pessoas (a-g)':<29} {j.ta.map(lambda s: bool(s - {'h'})).sum():>5}  "
      f"{j.td.map(lambda s: bool(s - {'h'})).sum():>6}")
    w(f"\n   Por categoria (frases com alguma violação)   {ROT_A:>5}  {ROT_D:>6}")
    for cat in sorted(j.categoria.unique()):
        s = j[j.categoria == cat]
        w(f"   {cat:<44} {(s.ta.map(len) > 0).sum():>5}  {(s.td.map(len) > 0).sum():>6}   (de {len(s)})")
    same = (j.top5_a == j.top5_d).sum()
    w(f"\n   Top 5 igual ao de antes em {same} de {len(j)} frases.")

    def linha(r):
        txt = (f"   #{r.numero} [{r.categoria}] \"{r.pedido}\"\n"
               f"      modo: {r.modo_resposta_a} -> {r.modo_resposta_d} | violações: "
               f"{','.join(sorted(r.ta)) or '-'} -> {','.join(sorted(r.td)) or '-'}\n"
               f"      antes:  {r.top5_a}\n      depois: {r.top5_d}")
        if r.filtros_detectados_d:
            txt += f"\n      filtros depois: {r.filtros_detectados_d}"
        if r.avisos_motor_d:
            txt += f"\n      aviso depois: {r.avisos_motor_d}"
        if r.violacoes_d:
            txt += f"\n      violação depois: {r.violacoes_d}"
        return txt

    w("\n3) FOCO: PESSOAS, PAÍS/ÉPOCA E NEGAÇÃO/FILTRO (todas as frases dessas categorias)")
    for cat in FOCO:
        s = j[j.categoria == cat]
        w(f"\n   --- {cat}: com violação {ROT_A} {(s.ta.map(len) > 0).sum()} -> {ROT_D} {(s.td.map(len) > 0).sum()} (de {len(s)}) ---")
        for _, r in s.iterrows():
            w(linha(r))

    resto = j[~j.categoria.isin(FOCO)]
    melhor = resto[resto.apply(lambda r: bool(r.ta - r.td) or (r.modo_resposta_a == "reserva_populares" and r.modo_resposta_d != "reserva_populares")
                               or (r.modo_resposta_a == "sinopse" and r.modo_resposta_d in ("etiquetas", "filtros", "aleatorio")), axis=1)]
    pior = resto[resto.apply(lambda r: bool(r.td - r.ta) or (r.modo_resposta_a in ("etiquetas", "filtros") and r.modo_resposta_d in ("sinopse", "reserva_populares")), axis=1)]
    w(f"\n4) OUTRAS CATEGORIAS: FRASES QUE MELHORARAM ({len(melhor)})")
    for _, r in melhor.iterrows():
        w(linha(r))
    w(f"\n5) OUTRAS CATEGORIAS: FRASES QUE PIORARAM ({len(pior)})")
    for _, r in pior.iterrows():
        w(linha(r))
    outros = resto[(resto.top5_a != resto.top5_d) & ~resto.numero.isin(melhor.numero) & ~resto.numero.isin(pior.numero)]
    w(f"\n6) OUTRAS CATEGORIAS: TOP 5 MUDOU SEM MUDAR VIOLAÇÃO ({len(outros)}) — para olhar à mão")
    for _, r in outros.iterrows():
        w(linha(r))
    fica = resto[(resto.td.map(len) > 0) & ~resto.numero.isin(melhor.numero) & ~resto.numero.isin(pior.numero)]
    w(f"\n7) OUTRAS CATEGORIAS: VIOLAÇÕES QUE CONTINUAM IGUAIS ({len(fica)})")
    for _, r in fica.iterrows():
        w(f"   #{r.numero} \"{r.pedido}\": {r.violacoes_d}")
    open(SAIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:32]))
    print(f"... relatório completo em {SAIDA}")


if __name__ == "__main__":
    main()
