"""
Busca o endereço da capa (poster_path) de cada filme do filmes_v2.csv no TMDB e salva em posters.csv
(id, poster_path, data_busca). NÃO baixa as imagens: o site carrega as capas direto do TMDB.

Como usar:
    (o arquivo .env precisa ter a linha TMDB_KEY=sua_chave; a chave nunca é mostrada)
    python buscar_posteres.py

Se parar no meio, rode de novo: pula os filmes que já estão no posters.csv.
Termos do TMDB: os endereços das capas também são cache e valem por no máximo 6 meses (ver ATUALIZAR_DADOS.md).
"""
import csv
import datetime
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
ARQUIVO = "posters.csv"
BASE = "https://api.themoviedb.org/3"
CAMPOS = ["id", "poster_path", "data_busca"]

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
    Devolve None se o filme não existe mais (404)."""
    params = {**params_base, **params}
    for tentativa in range(8):
        try:
            resp = sessao.get(f"{BASE}{caminho}", params=params, timeout=20)
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(2 * (tentativa + 1))
            continue
        if resp.status_code == 429:
            try:
                espera = int(resp.headers.get("Retry-After", 2))
            except ValueError:
                espera = 2
            time.sleep(espera)
            continue
        if resp.status_code == 401:
            sys.exit("A chave foi recusada. Confira o arquivo .env (sem mostrar a chave).")
        if resp.status_code == 404:
            return None
        if resp.status_code >= 500:
            time.sleep(2 * (tentativa + 1))
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Muitas tentativas falharam em {caminho}")


def main():
    ids = pd.read_csv(ARQ_FILMES, usecols=["id"]).id.astype(int).tolist()
    ja_tem = set()
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, newline="", encoding="utf-8") as f:
            ja_tem = {int(l["id"]) for l in csv.DictReader(f)}
    faltam = [i for i in ids if i not in ja_tem]
    print(f"{len(ids)} filmes no catálogo, {len(ja_tem)} já buscados, {len(faltam)} para buscar.")
    hoje = datetime.date.today().isoformat()
    novo = not os.path.exists(ARQUIVO)
    sem_capa = 0
    with open(ARQUIVO, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for n, filme_id in enumerate(faltam, start=1):
            d = chamar(f"/movie/{filme_id}", language="pt-BR")
            caminho = (d or {}).get("poster_path") or ""
            if not caminho:
                sem_capa += 1
            w.writerow({"id": filme_id, "poster_path": caminho, "data_busca": hoje})
            f.flush()
            if n % 500 == 0:
                print(f"  {n}/{len(faltam)}")
            time.sleep(0.03)
    tab = pd.read_csv(ARQUIVO, dtype={"poster_path": str}, keep_default_na=False)
    print(f"\nposters.csv: {len(tab)} filmes; com capa: {(tab.poster_path != '').sum()}; "
          f"sem capa: {(tab.poster_path == '').sum()}; nesta rodada sem capa: {sem_capa}")


if __name__ == "__main__":
    main()
