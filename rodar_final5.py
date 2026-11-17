"""
Teste cego da recomendação por REFERÊNCIA: roda o motor T nos pedidos 171 a 200 (pedidos_final5.csv) em dois cenários
e salva o top 5 de cada. NÃO calcula métrica nem compara com gabarito: a avaliação será feita com as notas do autor.
Os pedidos 171 a 200 não podem ser usados para ajustar dicionário, pesos ou código.

Cenários (definidos antes; o código do motor é o mesmo, muda só o arquivo de pesos):
  atual -> pesos_t.json     (referência só com etiquetas, a configuração ligada hoje)
  ml    -> pesos_t_ml.json  (referência com vizinhos do MovieLens 0,5 + recomendados do TMDB 0,2 + etiquetas 0,3)

Uso: python -I rodar_final5.py
Gera resultados_T_final5_atual_top5.csv e resultados_T_final5_ml_top5.csv.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

ARQ_PEDIDOS = "pedidos_final5.csv"
CENARIOS = [("atual", "pesos_t.json"), ("ml", "pesos_t_ml.json")]
COLS = ["numero", "pedido", "posicao", "titulo", "ano", "onde_assistir_BR", "temas_ou_etiquetas_reconhecidos",
        "modo_resposta", "aviso", "filtros_detectados", "fonte_referencia"]


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


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    from motor_t import GATILHOS_REFERENCIA_T, MotorT
    import motor as m
    # Só as colunas necessárias (observacoes não é lida)
    pedidos = pd.read_csv(ARQ_PEDIDOS, usecols=["numero", "estilo", "pedido"], dtype=str, keep_default_na=False)
    controle = set(pedidos.numero[~pedidos.estilo.str.startswith("refer")])
    tops, caminhos, refs_detectadas, refs_nao_achadas = {}, {}, {}, {}
    mt = MotorT(pesos=json.load(open(CENARIOS[0][1], encoding="utf-8")))  # mesmo motor; troca só os pesos
    f = mt.filmes
    for nome, arq_pesos in CENARIOS:
        mt.pesos = json.load(open(arq_pesos, encoding="utf-8"))
        mt._cache = {}
        usa_ml = bool(mt.pesos.get("ref") and (mt.pesos["ref"]["ml"] or mt.pesos["ref"]["tmdb"]))
        linhas, caminhos[nome], tops[nome] = [], {}, {}
        for p in pedidos.itertuples():
            top, info = mt.recomendar(p.pedido)
            grupos = mt.componentes(p.pedido)["a"]["ref_grupos"]
            modo, aviso = info.get("modo_resposta", ""), info.get("aviso", "") or ""
            caminho = modo
            if grupos:
                tem_viz = any(mt.refs and mt.refs["viz"][r] for g in grupos for r in g)
                caminho = "referência com vizinhos" if tem_viz else "referência sem vizinhos"
                refs_detectadas[p.numero] = (p.pedido, info["referencia"],
                                             [", ".join(f.at[i, "titulo"] for i in g[:3]) + (" ..." if len(g) > 3 else "")
                                              for g in grupos], tem_viz)
            elif nome == "atual":
                t = m.sem_acento(p.pedido)
                gat = [t[x.end():].split(",")[0].strip(" .!?") for x in re.finditer(GATILHOS_REFERENCIA_T, t)]
                if gat and p.numero not in controle:
                    refs_nao_achadas[p.numero] = (p.pedido, gat)
            caminhos[nome][caminho] = caminhos[nome].get(caminho, 0) + 1
            tops[nome][p.numero] = list(top.index)
            base = {"numero": p.numero, "pedido": p.pedido, "temas_ou_etiquetas_reconhecidos": reconhecidos(info),
                    "modo_resposta": modo, "aviso": aviso, "filtros_detectados": filtros_legiveis(info)}
            if top.empty:
                linhas.append({**base, "posicao": "", "titulo": "", "ano": "", "onde_assistir_BR": "",
                               "fonte_referencia": "", "aviso": aviso or "nenhum filme devolvido"})
            for pos, (i, r) in enumerate(top.iterrows(), start=1):
                fonte = ""
                if grupos:
                    if usa_ml and mt.refs:
                        no_ml = any(any(j == i for j, _ in mt.refs["viz"][x]) for g in grupos for x in g)
                        no_tm = any(i in mt.refs["rec"][x] for g in grupos for x in g)
                        fonte = ("mistura" if no_ml and no_tm else "vizinhos_ml" if no_ml
                                 else "recomendados_tmdb" if no_tm else "etiquetas")
                    else:
                        fonte = "etiquetas"
                    fonte += f" (referência: {info['referencia']})"
                sb = f.at[i, "streaming_assinatura_br"]
                linhas.append({**base, "posicao": pos, "titulo": r.titulo, "ano": r.ano,
                               "onde_assistir_BR": sb if pd.notna(sb) else "", "fonte_referencia": fonte})
        saida = f"resultados_T_final5_{nome}_top5.csv"
        pd.DataFrame(linhas, columns=COLS).to_csv(saida, index=False, encoding="utf-8")
        print(f"{nome}: {len(linhas)} linhas -> {saida}")

    print(f"\nCaminho de resposta em {len(pedidos)} pedidos (sem medir desempenho):")
    for nome, _ in CENARIOS:
        print(f"  {nome}: " + ", ".join(f"{k}: {v}" for k, v in sorted(caminhos[nome].items())))
    print(f"\nReferências detectadas ({len(refs_detectadas)}):")
    for n, (ped, ref, grupos, tem_viz) in refs_detectadas.items():
        print(f"  #{n} \"{ped}\" -> \"{ref}\" = {' + '.join(grupos)} [{'com' if tem_viz else 'sem'} vizinhos no MovieLens]")
    print(f"\nPedidos de referência com gatilho mas sem título achado no catálogo ({len(refs_nao_achadas)}):")
    for n, (ped, gat) in refs_nao_achadas.items():
        print(f"  #{n} \"{ped}\" (texto depois do gatilho: {' / '.join(gat)})")
    mudou = [n for n in sorted(controle, key=int) if tops["atual"][n] != tops["ml"][n]]
    print(f"\nPedidos de controle ({len(controle)}: {', '.join(sorted(controle, key=int))}): "
          f"{len(mudou)} mudaram de top 5 entre os cenários" + (f": {', '.join(mudou)}" if mudou else " (idênticos)."))


if __name__ == "__main__":
    main()
