# Como atualizar os dados do site

**Por quê:** os Termos de Uso do TMDB permitem guardar dados em cache por **no máximo 6 meses**. A página `admin_local/admin.html` (fora do site publicado) mostra um **alerta vermelho** quando os dados do TMDB passam de **150 dias**. As datas ficam em `site/data/versao.json` (`dados_tmdb_baixados_em`, `posters_buscados_em`, `creditos_buscados_em`, `recomendados_buscados_em`; o alerta usa a mais antiga, `dado_tmdb_mais_antigo`). Os endereços das capas (`posters.csv`) e os créditos (`creditos.csv`: diretores, elenco, países, estúdios e coleções) e os recomendados (`recomendados_tmdb.csv`) também são dados do TMDB e seguem o mesmo limite.

Os dados do MovieLens (Tag Genome e ml-32m) não mudam e não precisam ser baixados de novo.

## Passo a passo

Rode tudo na pasta do projeto.

1. **Guardar uma cópia e começar um arquivo novo.** Renomeie `filmes_v2.csv` para `filmes_v2_AAAA-MM.csv` (ex.: `filmes_v2_2026-11.csv`).
   - O `fetch_filmes_v2.py` retoma de onde parou e **não atualiza** filmes que já estão no arquivo.
   - Para atualizar "onde assistir", notas e votos, ele precisa de um arquivo novo.
2. **Baixar do TMDB:** `python fetch_filmes_v2.py` (uns 15 minutos).
   - Precisa do arquivo `.env` com a chave do TMDB. Não abra nem mostre esse arquivo.
   - Com o Norton ligado, o script já usa os certificados do Windows (biblioteca `truststore`).
3. **Cruzar com o Tag Genome:** `python -I cruzar_tag_genome.py`, que gera o `etiquetas.csv`.
4. **Ver os filmes novos sem etiqueta:** `python -I ml32m_sinonimos.py`, que gera o `filmes_sem_fonte.csv`.
   - Opcional: etiquetar os filmes novos pela IA, offline, com `etiquetar_ia.py` (mesmo vocabulário, origem "ia").
   - **Capas:** renomeie `posters.csv` para `posters_AAAA-MM.csv` e rode `python buscar_posteres.py` (uns 20 a 30 minutos; retoma se parar). Ele guarda só o endereço da capa de cada filme, não as imagens.
   - **Créditos (pessoas, países, estúdios, coleções):** renomeie `creditos.csv` para `creditos_AAAA-MM.csv` e rode `python buscar_creditos.py` (uns 30 minutos; retoma se parar; andamento em `buscar_creditos.log`).
   - **Recomendados do TMDB (filmes parecidos):** renomeie `recomendados_tmdb.csv` para `recomendados_tmdb_AAAA-MM.csv` e rode `python buscar_recomendados.py` (cerca de 1 hora; retoma se parar; andamento em `buscar_recomendados.log`).
   - **Vizinhos do MovieLens ("quem gostou de X gostou de Y"):** `python -I similaridade_ml.py` (alguns minutos). Não é dado do TMDB e não vence em 6 meses, mas precisa ser refeito quando o catálogo muda.
5. **Juntar as etiquetas:** `python -I unificar_etiquetas.py`, que gera o `etiquetas_unificadas.csv`.
6. **Gerar os dados do site:** `python -I exportar_site.py`.
   - Atualiza `site/data/`, inclusive `versao.json` com a data nova.
7. **Conferir que o site continua igual ao motor Python:** `python -I site_teste/validar_site.py`.
   - Deve dar todos idênticos (pedidos 91 a 140, frases do estresse e frases inventadas da v4). É só conferência da tradução, não é medição.
8. **Testar no computador:** na pasta do projeto, `python -m http.server 8765 --bind 127.0.0.1`.
   - Abra http://127.0.0.1:8765/site/ e http://127.0.0.1:8765/admin_local/admin.html.
   - Na `admin.html`, confira se a data dos dados ficou nova e sem alerta.
   - Depois, publique de novo a pasta `site/` (a `admin_local/` nunca vai para o site).
9. **Apagar as cópias antigas** (`filmes_v2_AAAA-MM.csv`, `posters_AAAA-MM.csv`, `creditos_AAAA-MM.csv`, `recomendados_tmdb_AAAA-MM.csv`) com mais de 6 meses. Os dados do TMDB também não devem ficar guardados além do limite.

## Lembretes

- Os arquivos de dados (`site/data/`, `filmes*.csv`, `dados_externos/`) não vão para repositório público: só o código (ver `.gitignore`).
- Com a lista de filmes nova, os resultados dos motores podem mudar. Os pedidos 111 a 140 continuam proibidos para qualquer ajuste.
