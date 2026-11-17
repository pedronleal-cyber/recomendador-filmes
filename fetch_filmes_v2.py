"""
Base maior: baixa até 6000 filmes do TMDB (dados em pt-BR) e salva em filmes_v2.csv.
Igual ao fetch_filmes.py, mais a coluna imdb_id (usada para cruzar com o MovieLens Tag Genome).

Como usar:
    (o arquivo .env precisa ter a linha TMDB_KEY=sua_chave)
    python fetch_filmes_v2.py

Se parar no meio (Ctrl+C, internet caiu), rode de novo:
o script pula os filmes que já estão no filmes_v2.csv e continua de onde parou.

Não mexe no fetch_filmes.py nem no filmes.csv.
"""
import csv
import os
import sys
import time

try:
    # Usa os certificados do Windows. Necessário quando um antivírus (ex.: Norton)
    # inspeciona as conexões: o Windows confia nele, mas o Python sozinho não.
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import requests
from dotenv import load_dotenv

QTD_FILMES = 6000            # quantos filmes baixar
FILMES_POR_PAGINA = 20       # o TMDB entrega 20 filmes por página
MAX_PAGINAS = 500            # limite do TMDB na busca (500 páginas = 10.000 filmes)
ARQUIVO = "filmes_v2.csv"
BASE = "https://api.themoviedb.org/3"
MIN_VOTOS = 300              # preferência: filmes com pelo menos 300 votos
MIN_VOTOS_PISO = 100         # se não houver filmes suficientes com 300, aceita até este mínimo

CAMPOS = [
    "id", "titulo", "titulo_original", "ano", "idioma_original",
    "generos", "palavras_chave", "sinopse", "nota", "votos", "duracao_min",
    "streaming_assinatura_br", "streaming_aluguel_br", "streaming_compra_br",
    "imdb_id",
]

load_dotenv()
CHAVE = os.getenv("TMDB_KEY", "").strip()
if not CHAVE:
    sys.exit("Não achei a chave. Crie o arquivo .env com a linha TMDB_KEY=sua_chave")

sessao = requests.Session()
params_base = {}
if CHAVE.startswith("eyJ"):
    # token de acesso de leitura (é um texto longo que começa com eyJ)
    sessao.headers["Authorization"] = f"Bearer {CHAVE}"
else:
    # chave de API comum (v3)
    params_base["api_key"] = CHAVE


class FilmeNaoExiste(Exception):
    pass


def chamar(caminho, **params):
    """Faz uma chamada à API. Espera e tenta de novo se for rápido demais (429),
    se a internet falhar ou se o servidor do TMDB der erro."""
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
            sys.exit("A chave foi recusada. Confira se copiou inteira no arquivo .env")
        if resp.status_code == 404:
            raise FilmeNaoExiste(caminho)
        if resp.status_code >= 500:
            time.sleep(2 * (tentativa + 1))
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Muitas tentativas falharam em {caminho}")


def listar_ids(quantidade):
    """Pega os ids dos filmes com mais votos. Devolve [(id, votos), ...] em ordem de votos."""
    vistos, lista = set(), []
    paginas = min(quantidade // FILMES_POR_PAGINA + 1, MAX_PAGINAS)
    for pagina in range(1, paginas + 1):
        dados = chamar(
            "/discover/movie",
            language="pt-BR",
            sort_by="vote_count.desc",
            include_adult="false",
            page=pagina,
        )
        resultados = dados.get("results", [])
        if not resultados:
            break
        for filme in resultados:
            votos = filme.get("vote_count", 0)
            if votos >= MIN_VOTOS_PISO and filme["id"] not in vistos:
                vistos.add(filme["id"])
                lista.append((filme["id"], votos))
        if pagina % 50 == 0:
            print(f"  lista: página {pagina}/{paginas}")
        time.sleep(0.05)
    lista = lista[:quantidade]
    com_300 = sum(1 for _, v in lista if v >= MIN_VOTOS)
    if com_300 < quantidade:
        print(f"Atenção: só {com_300} filmes têm {MIN_VOTOS}+ votos; "
              f"completando com filmes de {MIN_VOTOS_PISO}+ votos.")
    return lista


def montar_linha(d):
    """Transforma a resposta do TMDB numa linha da tabela."""
    br = d.get("watch/providers", {}).get("results", {}).get("BR", {})

    def nomes(tipo):
        return "|".join(p["provider_name"] for p in br.get(tipo, []))

    palavras = d.get("keywords", {}).get("keywords", [])
    return {
        "id": d["id"],
        "titulo": d.get("title", ""),
        "titulo_original": d.get("original_title", ""),
        "ano": (d.get("release_date") or "")[:4],
        "idioma_original": d.get("original_language", ""),
        "generos": "|".join(g["name"] for g in d.get("genres", [])),
        "palavras_chave": "|".join(k["name"] for k in palavras),
        "sinopse": (d.get("overview") or "").replace("\n", " "),
        "nota": d.get("vote_average", ""),
        "votos": d.get("vote_count", ""),
        "duracao_min": d.get("runtime", ""),
        "streaming_assinatura_br": nomes("flatrate"),
        "streaming_aluguel_br": nomes("rent"),
        "streaming_compra_br": nomes("buy"),
        "imdb_id": d.get("imdb_id") or "",
    }


def ids_ja_baixados():
    if not os.path.exists(ARQUIVO):
        return set()
    with open(ARQUIVO, newline="", encoding="utf-8") as f:
        return {int(linha["id"]) for linha in csv.DictReader(f)}


def resumo():
    """Mostra os números que dizem se os dados servem."""
    with open(ARQUIVO, newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    total = len(linhas)
    if total == 0:
        print("Tabela vazia.")
        return

    def pct(n):
        return f"{n} ({100 * n / total:.0f}%)"

    qtd_palavras = [len([p for p in l["palavras_chave"].split("|") if p]) for l in linhas]
    votos = [int(l["votos"] or 0) for l in linhas]
    anos = [int(l["ano"]) for l in linhas if l["ano"].isdigit()]
    print("\n===== RESUMO =====")
    print("Filmes na tabela:", total)
    print("Com imdb_id:", pct(sum(1 for l in linhas if l["imdb_id"])))
    print("Menor número de votos:", min(votos))
    print(f"Com {MIN_VOTOS} ou mais votos:", pct(sum(1 for v in votos if v >= MIN_VOTOS)))
    print("Lançados de 2022 em diante:", pct(sum(1 for a in anos if a >= 2022)))
    print("Com 5 ou mais palavras-chave:", pct(sum(1 for q in qtd_palavras if q >= 5)))
    print("Com 1 a 4 palavras-chave:", pct(sum(1 for q in qtd_palavras if 1 <= q <= 4)))
    print("Sem nenhuma palavra-chave:", pct(sum(1 for q in qtd_palavras if q == 0)))
    print("Média de palavras-chave por filme:", round(sum(qtd_palavras) / total, 1))
    print("Com streaming por assinatura no Brasil:",
          pct(sum(1 for l in linhas if l["streaming_assinatura_br"])))
    print("Com algum streaming no Brasil (assinar, alugar ou comprar):",
          pct(sum(1 for l in linhas if l["streaming_assinatura_br"]
                  or l["streaming_aluguel_br"] or l["streaming_compra_br"])))
    print("Com sinopse em português:", pct(sum(1 for l in linhas if l["sinopse"])))


def main():
    print("Buscando a lista de filmes...")
    lista = listar_ids(QTD_FILMES)
    ja_tem = ids_ja_baixados()
    faltam = [i for i, _ in lista if i not in ja_tem]
    print(f"{len(lista)} filmes na lista, {len(ja_tem)} já baixados, {len(faltam)} para baixar.")

    arquivo_novo = not os.path.exists(ARQUIVO)
    pulados = 0
    with open(ARQUIVO, "a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        if arquivo_novo:
            escritor.writeheader()
        for n, filme_id in enumerate(faltam, start=1):
            try:
                detalhes = chamar(
                    f"/movie/{filme_id}",
                    language="pt-BR",
                    append_to_response="keywords,watch/providers",
                )
            except FilmeNaoExiste:
                pulados += 1
                continue
            escritor.writerow(montar_linha(detalhes))
            f.flush()
            if n % 250 == 0:
                print(f"  {n}/{len(faltam)} baixados")
            time.sleep(0.03)
    if pulados:
        print(f"{pulados} filmes não existem mais no TMDB e foram pulados.")

    resumo()
    print("\nDados: TMDB. Onde assistir: JustWatch (via TMDB). Credite os dois quando publicar.")


if __name__ == "__main__":
    main()
