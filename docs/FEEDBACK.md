# Como configurar o feedback 👍/👎 (opcional)

O site tem um bloco "Gostou dos resultados?" com 👍 / 👎 e uma caixinha de comentário opcional. Quando a pessoa clica, a página manda para uma planilha do Google:

- a frase pesquisada;
- os 5 títulos mostrados;
- a avaliação (`bom` ou `ruim`);
- o comentário opcional;
- o caminho de resposta do motor (`etiquetas`, `filtros`, `sinopse`...).

Nenhum dado pessoal é enviado pela página. (O Google, como qualquer servidor, vê o endereço IP de quem clica.)

**Neste repositório o receptor vem desligado.** Em `site/app.js` a constante está assim:

```js
const FEEDBACK_URL = "COLE_AQUI_A_URL_DO_SEU_APPS_SCRIPT";
```

Enquanto ela não começar com `https://script.google.com/`, os botões de feedback **não aparecem** e nada é enviado.

## Passo a passo

1. Crie uma planilha nova no Google Planilhas.
2. Menu **Extensões → Apps Script**. Apague o que estiver lá e cole:

```js
function doPost(e) {
  const dados = JSON.parse(e.postData.contents || "{}");
  const corta = (x, n) => String(x || "").slice(0, n);
  const planilha = SpreadsheetApp.getActiveSpreadsheet();
  const aba = planilha.getSheetByName("feedback") || planilha.insertSheet("feedback");
  if (aba.getLastRow() === 0) {
    aba.appendRow(["quando", "frase", "filmes", "avaliacao", "comentario", "modo"]);
  }
  aba.appendRow([
    new Date(),
    corta(dados.frase, 300),
    corta(dados.filmes, 600),
    dados.avaliacao === "bom" ? "bom" : "ruim",
    corta(dados.comentario, 500),
    corta(dados.modo, 40),
  ]);
  return ContentService.createTextOutput("ok");
}
```

3. Clique em **Implantar → Nova implantação**, tipo **App da Web**:
   - Executar como: **Eu**;
   - Quem pode acessar: **Qualquer pessoa**.
4. Autorize o acesso à planilha e copie a URL que termina em `/exec`.
5. Em `site/app.js`, troque `COLE_AQUI_A_URL_DO_SEU_APPS_SCRIPT` por essa URL.
6. Teste: rode o site local, faça uma busca e clique em 👍. Uma linha nova deve aparecer na aba `feedback`.

## Cuidados

- Qualquer pessoa que tiver a URL pode mandar linhas para a planilha. Por isso o script corta o tamanho de cada campo. Se começar a receber lixo, crie uma implantação nova (a URL muda) e apague a antiga.
- **Não coloque a sua URL num repositório público** se não quiser receber envios de fora do seu site. Uma saída é manter a URL só na cópia publicada do site.
- A página usa `mode: "no-cors"`, então não consegue ler a resposta do Google; ela só sabe se a requisição saiu.
