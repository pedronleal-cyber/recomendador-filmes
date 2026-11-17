"""
Busca no TMDB, para cada filme do filmes_v2.csv, os filmes recomendados (/movie/{id}/recommendations).
Pede a página 1 e, se ainda faltar, a página 2. Guarda só os recomendados que estão no catálogo, até 20 por filme,
na ordem do TMDB.

Saída: recomendados_tmdb.csv com as colunas
    id, recomendados (ids separados por "|"), n_tmdb (quantos o TMDB devolveu, dentro ou fora do catálogo), data_busca

Como usar:
    (o arquivo .env precisa ter a linha TMDB_KEY=sua_chave; a chave nunca é mostrada)
    python buscar_recomendados.py

Se parar no meio, rode de novo: pula os filmes que já estão no recomendados_tmdb.csv. O andamento fica em
buscar_recomendados.log.
Termos do TMDB: estes dados também são cache e valem por no máximo 6 meses (ver ATUALIZAR_DADOS.md).
"""
import csv
import datetime
import logging
import os
import sys
import time

try:
    # Usa os certificados do Windows (necessário com antivírus que inspeciona conexões, como o Norton)
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import pandas as pd
import requests
from dotenv import load_dotenv

ARQ_FILMES = "filmes_v2.csv"
ARQUIVO = "recomendados_tmdb.csv"
ARQ_LOG = "buscar_recomendados.log"
BASE = "https://api.themoviedb.org/3"
MAX_REC = 20
PAGINAS = 2
CAMPOS = ["id", "recomendados", "n_tmdb", "data_busca"]

logging.basicConfig(filename=ARQ_LOG, level=logging.INFO, encoding="utf-8",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("recomendados")

load_dotenv()
CHAVE = os.getenv("TMDB_KEY", "").strip()
if not CHAVE:
    sys.exit("Não achei a chave. O arquivo .env precisa ter a linha TMDB_KEY=sua_chave")

sessao = requests.Session()
params_base = {}
if CHAVE.startswith("eyJ"):
    sessao.headers["Authorization"] = f"Bearer {CHAVE}"
else:
    params_base["api_key"] = CHAVE


def chamar(caminho, **params):
    """Chamada à API com nova tentativa em caso de 429 (rápido demais), falha de rede ou erro do servidor.
    Devolve None se o filme não existe mais (404). Nunca registra a chave no log."""
    params = {**params_base, **params}
    for tentativa in range(8):
        try:
            resp = sessao.get(f"{BASE}{caminho}", params=params, timeout=20)
        except (requests.ConnectionError, requests.Timeout) as e:
            log.warning("rede %s (tentativa %d): %s", caminho, tentativa + 1, type(e).__name__)
            time.sleep(2 * (tentativa + 1))
            continue
        if resp.status_code == 429:
            try:
                espera = int(resp.headers.get("Retry-After", 2))
            except ValueError:
                espera = 2
            log.warning("429 em %s, esperando %ds", caminho, espera)
            time.sleep(espera)
            continue
        if resp.status_code == 401:
            log.error("chave recusada (401)")
            sys.exit("A chave foi recusada. Confira o arquivo .env (sem mostrar a chave).")
        if resp.status_code == 404:
            log.warning("404 em %s", caminho)
            return None
        if resp.status_code >= 500:
            log.warning("erro %d em %s (tentativa %d)", resp.status_code, caminho, tentativa + 1)
            time.sleep(2 * (tentativa + 1))
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Muitas tentativas falharam em {caminho}")


def buscar(filme_id, catalogo):
    achados, n_tmdb = [], 0
    for pagina in range(1, PAGINAS + 1):
        d = chamar(f"/movie/{filme_id}/recommendations", language="pt-BR", page=pagina)
        if not d:
            break
        res = d.get("results") or []
        n_tmdb += len(res)
        for r in res:
            rid = r.get("id")
            if rid in catalogo and rid != filme_id and rid not in achados:
                achados.append(rid)
        if len(achados) >= MAX_REC or pagina >= (d.get("total_pages") or 1):
            break
        time.sleep(0.03)
    return achados[:MAX_REC], n_tmdb


def main():
    ids = pd.read_csv(ARQ_FILMES, usecols=["id"]).id.astype(int).tolist()
    catalogo = set(ids)
    ja_tem = set()
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, newline="", encoding="utf-8") as f:
            ja_tem = {int(l["id"]) for l in csv.DictReader(f)}
    faltam = [i for i in ids if i not in ja_tem]
    msg = f"{len(ids)} filmes no catálogo, {len(ja_tem)} já buscados, {len(faltam)} para buscar."
    print(msg)
    log.info(msg)
    hoje = datetime.date.today().isoformat()
    novo = not os.path.exists(ARQUIVO)
    with open(ARQUIVO, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for n, filme_id in enumerate(faltam, start=1):
            rec, n_tmdb = buscar(filme_id, catalogo)
            w.writerow({"id": filme_id, "recomendados": "|".join(map(str, rec)), "n_tmdb": n_tmdb, "data_busca": hoje})
            f.flush()
            if n % 250 == 0:
                print(f"  {n}/{len(faltam)}", flush=True)
                log.info("andamento %d/%d", n, len(faltam))
            time.sleep(0.03)  # bem abaixo do limite do TMDB (~40-50 pedidos por segundo)
    tab = pd.read_csv(ARQUIVO, dtype=str, keep_default_na=False)
    n_rec = tab.recomendados.map(lambda x: len(x.split("|")) if x else 0)
    resumo = (f"recomendados_tmdb.csv: {len(tab)} filmes; com algum recomendado no catálogo: {(n_rec > 0).sum()}; "
              f"média de recomendados no catálogo: {n_rec.mean():.1f}; sem nenhum do TMDB: {(tab.n_tmdb == '0').sum()}")
    print("\n" + resumo)
    log.info(resumo)


if __name__ == "__main__":
    main()
