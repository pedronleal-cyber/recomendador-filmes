# Recomendador de filmes — instruções para assistentes de código

A pessoa descreve em português o filme que quer ver e recebe 5 sugestões, com onde assistir no Brasil. Projeto de portfólio de dados, sem fins lucrativos.

## Regras do projeto

- **Custo zero:** nada de serviços pagos.
- **Sem IA rodando no site:** a recomendação só cruza dados. As etiquetas de origem `ia` foram geradas uma vez, offline, e ficam sempre marcadas com essa origem.
- **Sem login, sem anúncios, sem rastreamento.** O feedback 👍/👎 só envia a frase pesquisada (e os filmes sugeridos) se a pessoa clicar.
- **Nunca abra, mostre nem versione o `.env`** (guarda a chave do TMDB, na linha `TMDB_KEY=...`).
- **Dados de terceiros não vão para o repositório** (ver `.gitignore`): `site/data/`, `filmes*.csv`, etiquetas, créditos, pôsteres, recomendados, vizinhos, `dados_externos/`, planilhas de avaliação.
- **TMDB:** cache de no máximo 6 meses (ver `ATUALIZAR_DADOS.md`); aviso oficial exato no site: "This website uses TMDB and the TMDB APIs but is not endorsed, certified, or otherwise approved by TMDB.", com o logo do TMDB menor que o nome do site.
- **MovieLens 32M e Tag Genome 2021:** uso não comercial, citar as fontes, não sugerir endosso da Universidade de Minnesota / GroupLens. Textos em `site/LICENCAS.md`.

## Regras de medição

- A medida principal é a **precisão@5** com notas humanas, sempre num conjunto de pedidos **nunca visto**.
- **Conjuntos consumidos** (não usar para ajustar dicionário, pesos ou código): pedidos 111–140, 141–170 e 171–200.
- `pedidos_estresse.csv` (201–361) serve só para descobrir falhas, nunca para medir.
- Antes de mudar o motor, guarde uma cópia congelada (`motor_t_vN_congelado.py`, `dicionario_tags_vN_congelado.py`) e confira que o site (JS) e o Python dão o mesmo top 5: `python -I site_teste/validar_site.py`.

## Arquivos principais

- `motor_t.py` + `dicionario_tags.py`: motor T (etiquetas + palavras-chave + regras de leitura do pedido).
- `site/motor.js`: o mesmo motor em JavaScript; `site/app.js`: a página.
- `motor.py` + `dicionario.py`: motores antigos A, B e H.
- `exportar_site.py`: gera `site/data/` a partir dos CSV locais.
