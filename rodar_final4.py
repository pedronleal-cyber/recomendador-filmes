"""
Teste cego final da v4: roda o motor T atual e o motor T v1 congelado nos pedidos 141 a 170 (pedidos_final4.csv)
e salva o top 5 de cada um. NÃO calcula nenhuma métrica e NÃO compara os motores: a avaliação será feita com as
notas humanas do autor. Os pedidos 141 a 170 não podem ser usados para ajustar dicionário, pesos ou código.

Os dois motores usam os mesmos dados (filmes_v2.csv, etiquetas_unificadas.csv, pesos_t.json, vocabulario_piloto.csv
e o motor A de motor.py). Diferença: só o código e o dicionário. A v1 não usa creditos.csv (não existia).

Uso:
    python -I rodar_final4.py            -> gera resultados_T_final4_top5.csv e resultados_T1_final4_top5.csv
    python -I rodar_final4.py v1check    -> só confere se a v1 de hoje repete site_teste/referencia_v1.json (91 a 140)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

ARQ_PEDIDOS = "pedidos_final4.csv"
COLS = ["numero", "pedido", "posicao", "titulo", "ano", "onde_assistir_BR", "temas_ou_etiquetas_reconhecidos",
        "modo_resposta", "aviso", "filtros_detectados"]


def reconhecidos(info):
    partes = list(info["temas"])
    partes += [f"tema do A: {t}" for t in info.get("temas_motor_a", []) if t not in info["temas"]]
    partes += [f"não: {t}" for t in info["temas_negados"]]
    partes += [f"termo negado: {t}" for t in info.get("termos_negados", [])]
    if info.get("referencia"):
        partes.append(f"referência: {info['referencia']}")
    return " | ".join(partes)


def filtros_legiveis(info):
    fd = [f"{k}={'/'.join(map(str, v)) if isinstance(v, (list, tuple)) else v}" for k, v in info["filtros"].items()]
    for chave, rot in (("pessoas", "pessoas"), ("sem_pessoas", "sem pessoas"), ("paises", "países"),
                       ("sem_paises", "sem países"), ("estudios", "estúdios"), ("sem_estudios", "sem estúdios")):
        if info.get(chave):
            fd.append(f"{rot}=" + "/".join(map(str, info[chave])))
    return "; ".join(fd)


def v1check():
    from motor_t_v1_congelado import MotorT as MotorT1
    ref = json.load(open("site_teste/referencia_v1.json", encoding="utf-8"))
    mt = MotorT1()
    iguais = 0
    for r in ref:
        top, info = mt.recomendar(r["pedido"])
        ids = [int(i) for i in top.index]
        iguais += ids == r["top"] and info.get("modo_resposta") == r["modo"]
    print(f"v1 congelada hoje x referência guardada (pedidos 91 a 140): {iguais} de {len(ref)} iguais")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1:] == ["v1check"]:
        return v1check()
    from motor_t import MotorT
    from motor_t_v1_congelado import MotorT as MotorT1
    # Só as colunas necessárias (observacoes não é lida)
    pedidos = pd.read_csv(ARQ_PEDIDOS, usecols=["numero", "estilo", "pedido"], dtype=str, keep_default_na=False)
    motores = {"T": MotorT(), "T1": MotorT1()}
    caminhos = {nome: {} for nome in motores}
    reservas = {nome: [] for nome in motores}
    for nome, motor in motores.items():
        f = motor.filmes
        linhas = []
        for p in pedidos.itertuples():
            top, info = motor.recomendar(p.pedido)
            modo, aviso = info.get("modo_resposta", ""), info.get("aviso", "") or ""
            rec, fd = reconhecidos(info), filtros_legiveis(info)
            caminhos[nome][modo] = caminhos[nome].get(modo, 0) + 1
            if modo == "reserva_populares":
                reservas[nome].append((p.numero, p.pedido))
            base = {"numero": p.numero, "pedido": p.pedido, "temas_ou_etiquetas_reconhecidos": rec,
                    "modo_resposta": modo, "aviso": aviso, "filtros_detectados": fd}
            if top.empty:
                linhas.append({**base, "posicao": "", "titulo": "", "ano": "", "onde_assistir_BR": "",
                               "aviso": aviso or "nenhum filme devolvido"})
            for pos, (i, r) in enumerate(top.iterrows(), start=1):
                sb = f.at[i, "streaming_assinatura_br"]
                linhas.append({**base, "posicao": pos, "titulo": r.titulo, "ano": r.ano,
                               "onde_assistir_BR": sb if pd.notna(sb) else ""})
        saida = f"resultados_{nome}_final4_top5.csv"
        pd.DataFrame(linhas, columns=COLS).to_csv(saida, index=False, encoding="utf-8")
        print(f"{nome}: {len(linhas)} linhas -> {saida}")

    print(f"\nCaminho de resposta em {len(pedidos)} pedidos (sem medir desempenho):")
    for nome in motores:
        print(f"  {nome}: " + ", ".join(f"{k}: {v}" for k, v in sorted(caminhos[nome].items())))
    for nome in motores:
        lista = reservas[nome]
        print(f"  {nome} caiu em reserva_populares em {len(lista)} pedido(s)" + (":" if lista else "."))
        for n, ped in lista:
            print(f"     #{n} {ped}")


if __name__ == "__main__":
    main()
