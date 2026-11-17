# Revisão das expressões novas do motor T (rodada 2 / v3)

Para o autor revisar. Fonte: `adicoes_dicionario_v2.py` (do diagnóstico de estresse e do teste no site).
Os pedidos 111 a 140 NÃO foram usados. Isto não é medição.

- **Filmes fortes** = filmes entre os 20% mais fortes em pelo menos uma etiqueta da expressão.
- **Exemplos** = os 3 filmes com a maior soma peso × nota nas etiquetas da expressão, menos as que ela evita.
- "pais e filhos" já existia: as duas versões foram juntadas (padrões somados, maior peso de cada etiqueta).

| Expressão | Padrões (sem acento) | Etiquetas (peso) | Evita | Filmes fortes | 3 exemplos |
|---|---|---|---|---|---|
| abraço / acolher | `abrac`, `acolh`, `consol`, `me anim` | heartwarming (1), feel-good (0.8), touching (0.7), light (0.6) | – | 1642 | Up: Altas Aventuras (2009); Um Grande Garoto (2002); Intocáveis (2011) |
| estressado / cansado | `estress`, `cansad`, `exaust`, `sobrecarreg`, `esgotad` | light (1), feel-good (0.8), funny (0.6), cute (0.5) | tense (0.8), intense (0.8), brutal (0.6), disturbing (0.6) | 2025 | Simplesmente Amor (2003); Megamente (2010); Legalmente Loira (2001) |
| motivado / inspirar | `motiva`, `inspira`, `dar uma forca`, `dar um animo`, `volta por cima` | inspirational (1), underdog (0.8), feel-good (0.7), redemption (0.5) | – | 1668 | Guerreiro (2011); Um Sonho de Liberdade (1994); A Luta pela Esperança (2005) |
| saudade | `saudade`, `saudos`, `lembranc` | nostalgic (1), bittersweet (0.7), heartwarming (0.6), coming of age (0.5) | – | 1723 | Cinema Paradiso (1988); Divertida Mente (2015); Forrest Gump: O Contador de Histórias (1994) |
| calmo / tranquilo | `calm[oa]`, `calmin`, `tranquil`, `sossego`, `sereno`, `serena`, `suave` | light (1), meditative (0.8), feel-good (0.7), whimsical (0.5), atmospheric (0.5) | tense (0.9), intense (0.9), scary (0.8), brutal (0.7), suspenseful (0.6) | 2187 | Meu Amigo Totoro (1988); O Serviço de Entregas da Kiki (1989); O Castelo Animado (2004) |
| ansioso | `ansios` | light (1), feel-good (0.8), meditative (0.6), cute (0.5) | tense (0.9), intense (0.9), suspenseful (0.8), scary (0.8) | 2040 | Meu Amigo Totoro (1988); O Serviço de Entregas da Kiki (1989); Moonrise Kingdom (2012) |
| coração partido | `coracao partido`, `coracao quebrado`, `terminei`, `fim de namoro`, `desilusao amorosa`, `sofrendo de amor` | sad (1), romantic (0.8), bittersweet (0.8), tear jerker (0.7), love story (0.7), emotional (0.7) | – | 1937 | Titanic (1997); (500) Dias com Ela (2009); Não Me Abandone Jamais (2010) |
| raiva / intenso | `raiva`, `odio\b`, `revoltad`, `intens[oa]\b` | intense (1), brutal (0.7), revenge (0.7), visceral (0.7), action packed (0.6), gritty (0.5) | – | 2125 | Kill Bill: Volume 1 (2003); Django Livre (2012); Kill Bill: Volume 2 (2004) |
| sem energia / preguiça | `sem energia`, `sem animo`, `preguic`, `moleza` | light (1), feel-good (0.8), funny (0.6), cute (0.5) | tense (0.7), intense (0.7), complex (0.6) | 2025 | Simplesmente Amor (2003); Megamente (2010); Legalmente Loira (2001) |
| esperança | `esperanc`, `otimis`, `dias melhores` | inspirational (1), heartwarming (0.8), feel-good (0.7), redemption (0.7), survival (0.5) | – | 2200 | Um Sonho de Liberdade (1994); Guerreiro (2011); Quem Quer Ser um Milionário? (2008) |
| primeiro encontro / dia dos namorados | `primeiro encontro`, `encontro romantic`, `dia dos namorados` | romantic (1), love story (0.8), feel-good (0.7), light (0.7), funny (0.6) | – | 2313 | Simplesmente Amor (2003); Um Lugar Chamado Notting Hill (1999); Afinado no Amor (1998) |
| galera / bagunça | `galera`, `com (os )?amigos`, `turma`, `bagunc`, `zoeira`, `festa\b` | funny (1), hilarious (0.8), silly (0.7), goofy (0.6), light (0.6), action packed (0.5) | – | 2375 | Austin Powers: 000, um Agente Nada Discreto (1997); American Pie: A Primeira Vez é Inesquecível (1999); Austin Powers: O Agente ‘Bond’ Cama (1999) |
| festa do pijama | `festa do pijama`, `pijama` | teen movie (0.9), funny (0.8), silly (0.6), coming of age (0.5), cute (0.5) | – | 2563 | A Mentira (2010); American Pie: A Primeira Vez é Inesquecível (1999); As Patricinhas de Beverly Hills (1995) |
| viagem / algo que prenda | `aviao`, `viagem longa`, `que prenda`, `prender`, `prenda` | fast paced (0.9), suspenseful (0.8), twists & turns (0.8), action packed (0.7), intense (0.6) | – | 1973 | Pulp Fiction: Tempo de Violência (1994); A Origem (2010); O Fugitivo (1993) |
| chuva / frio | `chuv`, `friozinho`, `dia frio`, `noite fria` | heartwarming (0.8), feel-good (0.7), atmospheric (0.6), romantic (0.5), melancholic (0.5) | – | 2346 | O Fabuloso Destino de Amélie Poulain (2001); Brilho Eterno de uma Mente sem Lembranças (2004); As Vantagens de Ser Invisível (2012) |
| de fundo / sem prestar atenção | `cozinhand`, `de fundo`, `fazendo outra coisa`, `sem prestar atencao`, `passando roupa` | light (1), funny (0.8), feel-good (0.7) | complex (0.8), nonlinear (0.8), dialogue driven (0.6), mindfuck (0.8) | 1843 | Megamente (2010); Um Lugar Chamado Notting Hill (1999); Afinado no Amor (1998) |
| agrada a todos | `todo mundo`, `todos gostem`, `todos goste`, `agrad\w* a todos`, `unanimidade` | feel-good (0.8), funny (0.6), epic (0.5), kids and family (0.5) + empurrão pela nota | – | 2342 | Toy Story: Um Mundo de Aventuras (1995); A Princesa Prometida (1987); Guerra nas Estrelas (1977) |
| épico | `epic[oa]s?\b`, `grandios` | epic (1), visually stunning (0.6), mythology (0.5) | – | 1540 | Guerra nas Estrelas: O Império Contra-Ataca (1980); Guerra nas Estrelas (1977); Avatar (2009) |
| divertido | `divertid`, `diversao` | funny (0.9), light (0.9), feel-good (0.8), fast paced (0.5) | – | 2257 | A Princesa Prometida (1987); Austin Powers: O Agente ‘Bond’ Cama (1999); Up: Altas Aventuras (2009) |
| ambição / poder | `ambic`, `poder\b`, `poderos`, `ganancia`, `cobica` | greed (1), corruption (0.7), politics (0.7), betrayal (0.5), dark (0.5) | – | 1863 | Rede de Intrigas (1976); Syriana: A Indústria do Petróleo (2005); A Montanha dos Sete Abutres (1951) |
| liberdade | `liberdade`, `livre\b`, `libertar`, `libertac` | inspirational (0.7), prison escape (0.6), underdog (0.5), redemption (0.5), survival (0.5) | – | 2000 | Um Sonho de Liberdade (1994); Expedição Kon Tiki (2012); Guerreiro (2011) |
| fé / religião | `\bfe\b`, `religi`, `\bdeus\b`, `espiritu`, `crenca` | religion (1), philosophical (0.6), existentialism (0.5), reflective (0.5) | – | 1545 | O Sétimo Selo (1957); Um Homem Sério (2009); Stalker (1979) |
| vícios | `vicio`, `viciad`, `drog`, `alcool`, `dependenc` | addiction (1), bleak (0.6), disturbing (0.5), depressing (0.5) | – | 1485 | Réquiem para um Sonho (2000); Shame (2011); O Operário (2004) |
| inteligência / loucura | `inteligenc(?!\w* artificial)`, `brilhante`, `mente brilhante` | cerebral (1), mental illness (0.5), complex (0.6), witty (0.5) | – | 1570 | Amnésia (2000); Clube da Luta (1999); Holy Motors (2012) |
| juventude / rebeldia | `juventud`, `rebeld` | coming of age (1), teen movie (0.6), social commentary (0.5), high school (0.5) | – | 1993 | Clube dos Cinco (1985); As Vantagens de Ser Invisível (2012); Eu, Você e a Garota Que Vai Morrer (2015) |
| pais e filhos | `pai e filh`, `mae e filh`, `pai\b`, `mae\b`, `pais e filhos`, `pai e filho`, `paternidade`, `maternidade`, `pai solo`, `mae solo` | parenthood (1), father daughter relationship (0.8), family drama (0.8), emotional (0.5) | – | 1769 | Os Descendentes (2011); Beleza Americana (1999); Magnólia (1999) |
| mentira / traição | `mentir`, `mentira`, `enganad`, `farsa`, `hipocris` | betrayal (0.9), twists & turns (0.6), conspiracy (0.5), twist ending (0.5) | – | 1779 | Los Angeles: Cidade Proibida (1997); Os Suspeitos (1995); Xeque-Mate (2006) |
| justiça | `justica`, `injustic`, `justiceir` | justice (1), courtroom (0.5), revenge (0.5), corruption (0.5) | – | 1650 | Millennium III: A Rainha do Castelo de Ar (2009); Cabo do Medo (1991); O Segredo dos seus Olhos (2009) |
| situação extrema | `situacao extrema`, `no limite`, `contra o tempo` | survival (1), intense (0.7), tense (0.6) | – | 1423 | Capitão Phillips (2013); Sem Saída (2008); Dunkirk (2017) |
| cidade grande | `cidade grande`, `metropole`, `vida urbana` | loneliness (0.7), melancholic (0.5), character study (0.5) | – | 1091 | O Agente da Estação (2003); Mary e Max: Uma Amizade Diferente (2009); Ela (2013) |
| amor próprio / ser diferente | `amor proprio`, `autoestima`, `se aceitar`, `aceitacao`, `ser diferente` | identity (1), coming of age (0.7), inspirational (0.7), social commentary (0.4) | – | 1895 | Gênio Indomável (1997); Beleza Americana (1999); Donnie Darko (2001) |
| morte / mortalidade | `sobre (a )?morte`, `mortalidade`, `luto\b`, `finitude` | life & death (1), existentialism (0.8), reflective (0.8), sad (0.6) | – | 1451 | A Chegada (2016); Na Natureza Selvagem (2007); Ela (2013) |

## Palavras-chave do TMDB (só entram com 20+ filmes)

| Expressão | Palavra-chave | Filmes no catálogo | Situação | 3 exemplos (mais bem avaliados) |
|---|---|---|---|---|
| `vietna` | vietnam war | 21 | ativa (filtro; negada = exclui) | Forrest Gump: O Contador de Histórias (1994); Apocalypse Now (1979); Nascido Para Matar (1987) |
| `segunda guerra / nazis` | world war ii | 103 | ativa (filtro; negada = exclui) | A Lista de Schindler (1993); A Vida é Bela (1997); O Pianista (2002) |
| `preto e branco` | black and white | 138 | ativa (filtro; negada = exclui) | A Lista de Schindler (1993); 12 Homens e uma Sentença (1957); Psicose (1960) |
| `filme mudo / cinema mudo` | silent film | 19 | NÃO ativa (menos de 20 filmes) | Tempos Modernos (1936); Luzes da Cidade (1931); Metrópolis (1927) |
| `marvel` | marvel cinematic universe | 0 | NÃO ativa (menos de 20 filmes) | – |
| `alienigen / alien\b` | alien | 146 | ativa (filtro; negada = exclui) | Devoradores de Estrelas (2026); Alien: O Oitavo Passageiro (1979); O Enigma de Outro Mundo (1982) |

"filme mudo" (silent film, 19 filmes) não virou filtro: o site avisa que não consegue filtrar filmes mudos.
"marvel" (marvel cinematic universe) não existe como palavra-chave no catálogo; "não é da Marvel" continua sem filtro.

## Regras novas do motor (resumo)

- **Nota:** "nota acima de N", "mais de N", "N+", "bem avaliado", "nota alta" (7,5+) e gírias: `topzera`, `top\b`, `show de bola`, `da hora`, `dahora`, `massa\b`, `brabo`, `foda`, `muito bom`, `excelente`, `obra.?prima`, `aclamad`, `premiad`.
- **Duração:** "até 1h30", "1h30", "no máximo 2 horas", "mais de 2h", "uma hora e meia"; "não seja muito longo" = até 120 min; "longo" = a partir de 150 min ("um longa" e "longa-metragem" não contam).
- **Época:** recente / lançamento / atual / "filme novo" = 2024+; antigo / "filme velho" = até 1979 ("Roma antiga", "Egito antigo" não contam); moderno / contemporâneo = 2010+; preto e branco = palavra-chave.
- **Streaming:** "max", "prime", "disney", "globo", "apple" só contam depois de "na/no/tem na/que passe na..."; "da Disney" (estúdio) não liga o filtro.
- **Referência:** também "similar a", "semelhante a", "igual a", "no estilo de", "na vibe de", "lembra" e "como" (só antes de título conhecido), com artigo opcional.
- **Digitação:** tabela de correções + distância de edição 1 para palavras de 6+ letras que não existem nas sinopses (ex.: "aventrua" → "aventura").
- **Só filtros:** catálogo filtrado ordenado pela nota ajustada pelos votos (caminho "filtros").
- **Aleatório / surpreenda-me:** sorteio entre os filmes com nota 7.5+ (caminho "aleatorio").
- **Pouco conhecido / obscuro:** nota 7+ e menos votos que a mediana (1892).
- **Reserva por sinopse:** palavra do pedido que está no título do filme vale 10%.
