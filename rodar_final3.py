"""
Teste cego final: roda os motores A e T nos pedidos 111 a 140 (pedidos_final3.csv) e salva o top 5 de cada um.
NÃO calcula nenhuma métrica e NÃO lê a coluna boas_respostas: a avaliação será feita com as notas humanas do autor.
Os pedidos 111 a 140 não podem ser usados para ajustar dicionário, pesos ou código.

Uso:
    python -I rodar_final3.py
    (opcional, só para conferir o formato com outro arquivo:  python -I rodar_final3.py <arquivo> <pasta_saida>)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

import motor as m
from motor_t import MotorT

ARQ_PEDIDOS = "pedidos_final3.csv"
CATALOGO = "filmes_v2.csv"


def reconhecidos_a(info):
    partes = list(info["temas"]) + [f"não: {t}" for t in info["temas_negados"]]
    partes += [f"{k}={v}" for k, v in info["filtros"].items()]
    if info["referencia"]:
        partes.append(f"referência: {info['referencia']}")
    return " | ".join(partes)


def reconhecidos_t(info):
    partes = list(info["temas"])
    partes += [f"tema do A: {t}" for t in info.get("temas_motor_a", []) if t not in info["temas"]]
    partes += [f"não: {t}" for t in info["temas_negados"]]
    partes += [f"termo negado: {t}" for t in info.get("termos_negados", [])]
    partes += [f"{k}={v}" for k, v in info["filtros"].items()]
    if info["referencia"]:
        partes.append(f"referência: {info['referencia']}")
    return " | ".join(partes)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    arq = sys.argv[1] if len(sys.argv) > 1 else ARQ_PEDIDOS
    pasta = sys.argv[2] if len(sys.argv) > 2 else "."
    if not os.path.exists(arq):
        sys.exit(f"Não achei {arq}. Coloque o arquivo na pasta do projeto e rode de novo.")
    # Só as colunas necessárias: o gabarito (boas_respostas) não é lido aqui
    pedidos = pd.read_csv(arq, usecols=["numero", "estilo", "pedido"], dtype=str, keep_default_na=False)

    motores = {"A": m.MotorA(CATALOGO), "T": MotorT()}
    caminhos = {nome: {} for nome in motores}
    reservas = {nome: [] for nome in motores}
    for nome, motor in motores.items():
        f = motor.filmes
        linhas = []
        for p in pedidos.itertuples():
            top, info = motor.recomendar(p.pedido)
            if nome == "A":
                reconhecido = reconhecidos_a(info)
                # O motor A não tem caminho por sinopse: ou reconhece temas/filtros/referência, ou cai na
                # lista de filmes mais bem avaliados (reserva)
                modo = "temas" if (info["temas"] or info["temas_negados"] or info["filtros"] or info["referencia"]) \
                    else "reserva_populares"
                aviso = ""
            else:
                reconhecido = reconhecidos_t(info)
                modo = info.get("modo_resposta", "")
                aviso = info.get("aviso", "")
            caminhos[nome][modo] = caminhos[nome].get(modo, 0) + 1
            if modo == "reserva_populares":
                reservas[nome].append((p.numero, p.pedido))
            if top.empty:
                linhas.append({"numero": p.numero, "pedido": p.pedido, "posicao": "", "titulo": "", "ano": "",
                               "onde_assistir_BR": "", "temas_ou_etiquetas_reconhecidos": reconhecido,
                               "modo_resposta": modo, "aviso": aviso or "nenhum filme devolvido"})
            for pos, (i, r) in enumerate(top.iterrows(), start=1):
                linhas.append({
                    "numero": p.numero, "pedido": p.pedido, "posicao": pos, "titulo": r.titulo, "ano": r.ano,
                    "onde_assistir_BR": f.at[i, "streaming_assinatura_br"] if pd.notna(f.at[i, "streaming_assinatura_br"]) else "",
                    "temas_ou_etiquetas_reconhecidos": reconhecido, "modo_resposta": modo, "aviso": aviso,
                })
        cols = ["numero", "pedido", "posicao", "titulo", "ano", "onde_assistir_BR",
                "temas_ou_etiquetas_reconhecidos", "modo_resposta", "aviso"]
        saida = os.path.join(pasta, f"resultados_{nome}_final3_top5.csv")
        pd.DataFrame(linhas, columns=cols).to_csv(saida, index=False, encoding="utf-8")
        print(f"{nome}: {len(linhas)} linhas -> {saida}")

    print(f"\nCaminho de resposta em {len(pedidos)} pedidos (sem medir desempenho):")
    for nome in motores:
        print(f"  {nome}: " + ", ".join(f"{k}: {v}" for k, v in sorted(caminhos[nome].items())))
    for nome in motores:
        lista = reservas[nome]
        print(f"  {nome} caiu em reserva_populares em {len(lista)} pedido(s)"
              + (":" if lista else "."))
        for n, ped in lista:
            print(f"     #{n} {ped}")


if __name__ == "__main__":
    main()
