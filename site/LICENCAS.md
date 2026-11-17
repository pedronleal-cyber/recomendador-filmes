# Licenças, créditos e citações

Este site é um projeto de portfólio, **sem fins lucrativos**: sem anúncios, sem doações, sem plano pago e sem qualquer receita.

## Avisos

- **Dados derivados redistribuídos sob as mesmas condições.** O arquivo `data/etiquetas.json` contém notas de etiquetas derivadas do MovieLens Tag Genome 2021 e do MovieLens 32M (ml-32m). Esses dados transformados são redistribuídos sob as mesmas condições das licenças originais, transcritas abaixo.
- **Filmes parecidos ("quem gostou de X também gostou de Y").** O arquivo `data/referencias.json` contém pontuações de similaridade entre filmes calculadas a partir das notas (ratings) do MovieLens 32M (ml-32m). São dados derivados, redistribuídos sob as mesmas condições: uso só não comercial, sem endosso da Universidade de Minnesota nem do GroupLens. O mesmo arquivo traz os filmes recomendados pelo TMDB para cada filme (dados do TMDB, guardados por no máximo 6 meses).
- **Uso não comercial.** Os dados do MovieLens não podem ser usados para fins comerciais ou que gerem receita sem permissão prévia do GroupLens Research Project (Universidade de Minnesota). O Tag Genome 2021 é licenciado como CC BY-NC 3.0 (atribuição, uso não comercial).
- **Sem endosso.** Este site não é endossado pela Universidade de Minnesota nem pelo GroupLens Research Group. Aviso do TMDB: "This website uses TMDB and the TMDB APIs but is not endorsed, certified, or otherwise approved by TMDB."
- **Etiquetas estimadas por IA.** Parte das etiquetas (marcadas como "etiqueta estimada" no site) foi estimada por IA (Claude, da Anthropic) uma única vez, offline. O site não usa IA ao funcionar: só cruza dados.

## Créditos

![TMDB](img/tmdb-logo.svg)

Data dos dados: ver `data/versao.json` (campos `dados_tmdb_baixados_em`, `posters_buscados_em`, `creditos_buscados_em`, `recomendados_buscados_em` e `dado_tmdb_mais_antigo`). As capas são exibidas direto dos servidores do TMDB (não são hospedadas aqui); os botões "Onde assistir" levam à página do filme no TMDB, com dados de streaming do JustWatch. O TMDB permite guardar esses dados por no máximo 6 meses; para atualizar, ver `ATUALIZAR_DADOS.md` na raiz do projeto.

- Dados de filmes: TMDB (The Movie Database). This website uses TMDB and the TMDB APIs but is not endorsed, certified, or otherwise approved by TMDB.
- Onde assistir: JustWatch (via TMDB).
- Etiquetas: MovieLens (GroupLens, Universidade de Minnesota): Tag Genome 2021 e MovieLens 32M.
- Filmes parecidos: similaridade calculada a partir das notas do MovieLens 32M (GroupLens) e filmes recomendados pelo TMDB.

## Citações

- F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4: 19:1–19:19. https://doi.org/10.1145/2827872
- Vig, J., Sen, S., and Riedl, J. (2012). The tag genome: Encoding community knowledge to support novel interaction. ACM Trans. Interact. Intell. Syst., 2(3):13:1–13:44. https://doi.org/10.1145/2362394.2362395
- Kotkov, D., Maslov, A., and Neovius, M. (2021). Revisiting the tag relevance prediction problem. In Proceedings of the 44th International ACM SIGIR conference on Research and Development in Information Retrieval. https://doi.org/10.1145/3404835.3463019

## Texto das licenças (como está nos README originais)

### MovieLens 32M (ml-32m) — trecho "Usage License" do README.txt

> Neither the University of Minnesota nor any of the researchers involved can guarantee the correctness of the data, its suitability for any particular purpose, or the validity of results based on the use of the data set. The data set may be used for any research purposes under the following conditions:
>
> * The user may not state or imply any endorsement from the University of Minnesota or the GroupLens Research Group.
> * The user must acknowledge the use of the data set in publications resulting from the use of the data set (see below for citation information).
> * The user may redistribute the data set, including transformations, so long as it is distributed under these same license conditions.
> * The user may not use this information for any commercial or revenue-bearing purposes without first obtaining permission from a faculty member of the GroupLens Research Project at the University of Minnesota.
> * The executable software scripts are provided "as is" without warranty of any kind, either expressed or implied, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. The entire risk as to the quality and performance of them is with you. Should the program prove defective, you assume the cost of all necessary servicing, repair or correction.
>
> In no event shall the University of Minnesota, its affiliates or employees be liable to you for any damages arising out of the use or inability to use these programs (including but not limited to loss of data or data being rendered inaccurate).
>
> If you have any further questions or comments, please email <grouplens-info@umn.edu>

Citação pedida no README: "To acknowledge use of the dataset in publications, please cite the following paper: F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4: 19:1–19:19. https://doi.org/10.1145/2827872"

### MovieLens Tag Genome 2021 — trecho "Usage License" do genome_2021_readme.txt

> This work is licensed under the Creative Commons Attribution-NonCommercial 3.0 License.

Licença completa: https://creativecommons.org/licenses/by-nc/3.0/

Citação pedida no README: "To acknowledge use of the dataset in publications, please cite both of the following papers:" Kotkov et al. (2021) e Vig et al. (2012), listados acima.

## Resumo em português simples

- **ml-32m:** pode ser usado para pesquisa e redistribuído, inclusive transformado, desde que nas mesmas condições: sem uso comercial ou com receita sem permissão do GroupLens, citando Harper & Konstan (2015) e sem sugerir endosso da Universidade de Minnesota. Os dados vêm "como estão", sem garantia.
- **Tag Genome 2021 (CC BY-NC 3.0):** pode ser compartilhado e adaptado, com crédito aos autores, sem uso comercial.
