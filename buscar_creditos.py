"""
Busca no TMDB, para cada filme do filmes_v2.csv, diretores, os 8 primeiros do elenco, países de produção,
estúdios e coleção (franquia). Uma chamada por filme: /movie/{id}?append_to_response=credits.

Saída: creditos.csv com as colunas
    id, diretores, diretores_ids, elenco, elenco_ids, paises_producao, estudios, estudios_ids,
    colecao_id, colecao, data_busca
Listas separadas por "|". Os ids das pessoas e estúdios servem para separar homônimos.

Como usar:
    (o arquivo .env precisa ter a linha TMDB_KEY=sua_chave; a chave nunca é mostrada)
    python buscar_creditos.py

Se parar no meio, rode de novo: pula os filmes que já estão no creditos.csv. O andamento fica em
buscar_creditos.log.
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
ARQUIVO = "creditos.csv"
ARQ_LOG = "buscar_creditos.log"
BASE = "https://api.themoviedb.org/3"
N_ELENCO = 8
CAMPOS = ["id", "diretores", "diretores_ids", "elenco", "elenco_ids", "paises_producao", "estudios",
          "estudios_ids", "colecao_id", "colecao", "data_busca"]

logging.basicConfig(filename=ARQ_LOG, level=logging.INFO, encoding="utf-8",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("creditos")

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


def limpar(texto):
    return str(texto or "").replace("|", "/").strip()


def linha(filme_id, d, hoje):
    d = d or {}
    cred = d.get("credits") or {}
    diretores = [p for p in cred.get("crew") or [] if p.get("job") == "Director"]
    elenco = sorted(cred.get("cast") or [], key=lambda p: p.get("order", 999))[:N_ELENCO]
    estudios = d.get("production_companies") or []
    col = d.get("belongs_to_collection") or {}
    return {
        "id": filme_id,
        "diretores": "|".join(limpar(p.get("name")) for p in diretores),
        "diretores_ids": "|".join(str(p.get("id")) for p in diretores),
        "elenco": "|".join(limpar(p.get("name")) for p in elenco),
        "elenco_ids": "|".join(str(p.get("id")) for p in elenco),
        "paises_producao": "|".join(c.get("iso_3166_1", "") for c in d.get("production_countries") or []),
        "estudios": "|".join(limpar(c.get("name")) for c in estudios),
        "estudios_ids": "|".join(str(c.get("id")) for c in estudios),
        "colecao_id": col.get("id") or "",
        "colecao": limpar(col.get("name")),
        "data_busca": hoje,
    }


def main():
    ids = pd.read_csv(ARQ_FILMES, usecols=["id"]).id.astype(int).tolist()
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
    nao_achados = 0
    with open(ARQUIVO, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for n, filme_id in enumerate(faltam, start=1):
            d = chamar(f"/movie/{filme_id}", language="pt-BR", append_to_response="credits")
            if d is None:
                nao_achados += 1
            w.writerow(linha(filme_id, d, hoje))
            f.flush()
            if n % 250 == 0:
                print(f"  {n}/{len(faltam)}")
                log.info("andamento %d/%d", n, len(faltam))
            time.sleep(0.03)  # bem abaixo do limite do TMDB (~40-50 pedidos por segundo)
    tab = pd.read_csv(ARQUIVO, dtype=str, keep_default_na=False)
    resumo = (f"creditos.csv: {len(tab)} filmes; com diretor: {(tab.diretores != '').sum()}; "
              f"com elenco: {(tab.elenco != '').sum()}; com país: {(tab.paises_producao != '').sum()}; "
              f"com estúdio: {(tab.estudios != '').sum()}; em coleção: {(tab.colecao_id != '').sum()}; "
              f"não encontrados nesta rodada: {nao_achados}")
    print("\n" + resumo)
    log.info(resumo)


if __name__ == "__main__":
    main()
