# Capturas reais do Renamix

Capturas reais do Renamix 0.1.1 no Windows, fornecidas pelo autor. Não crie imagens
vazias, montagens ou capturas fictícias.

| Arquivo | Conteúdo | Estado |
| --- | --- | --- |
| `main-window.png` | Substituição IMG → Foto: três propostas prontas e um CSV sem alterações, no Dark Beach. | Integrada |
| `themes.png` | Aba Temas com as oito opções. | Pendente |
| `dark-beach.png` | Tema Dark Beach, sem regra preenchida e com tabela vazia. | Integrada |
| `vampire.png` | Tema Vampire, sem regra preenchida e com tabela vazia. | Integrada |
| `conflict.png` | Destino ocupado, com status e mensagem legíveis. | Pendente |

As três imagens foram revisadas em tamanho original e em largura de 960 pixels.
Os PNGs mantêm suas dimensões originais: 1365 × 720 para a prévia e 1365 × 722
para os temas. A escala de tela não foi informada. O README permite ampliar cada
imagem; os dois exemplos de temas ficam em uma seção expansível.

Com autorização do autor, somente o caminho pessoal no campo de pasta foi coberto
com `[caminho ocultado]`, usando Python. Os demais pixels foram preservados e os
PNGs publicados não carregam metadados adicionais. Os originais foram guardados
localmente em `build/screenshots-originals-v011/`, ignorado pelo Git, com hashes
registrados para conferência. Não versione esses originais nem a pasta de build.

Use uma pasta descartável com nomes fictícios, como `IMG_001.jpg`, `IMG_002.jpg` e
`IMG_003.jpg`, e configure a substituição `IMG_` → `Foto_`. Para a captura de conflito,
adicione `Foto_001.jpg` antes de analisar; a proposta de `IMG_001.jpg` deve aparecer
em conflito. Use arquivos de teste, sem dados pessoais.

Escolha manualmente cada tema e capture somente a janela. Não exiba documentos,
caminhos pessoais, relatórios reais ou outras janelas. Não é necessário alterar a
resolução do sistema. Não use capas, imagens de artistas ou logotipos de terceiros.

Confira nomes, status, detalhes e botões antes de salvar. Prefira PNG, mantenha
dimensões consistentes e anote versão do aplicativo, sistema, resolução e escala
para a legenda. Preserve a captura original quando não houver necessidade de edição.

## Revisão e integração

Antes de incorporar cada PNG:

1. Abra a imagem em tamanho original e confira nomes, propostas, status e botões.
2. Confirme que ela corresponde à tela ou ao tema indicado pelo nome do arquivo.
3. Confira se o campo de pasta, nomes de arquivos e outras áreas não expõem dados
   pessoais desnecessários. Se expuserem, prefira uma nova captura com dados de teste.
4. Confira também em largura reduzida: textos importantes devem continuar legíveis.

Exiba uma captura por linha, com largura de até 960 pixels e preservando a proporção.
Evite colocar telas completas em colunas estreitas. Use uma legenda curta e um link
para a imagem original, permitindo ampliá-la. Descreva no texto alternativo o estado
visível, incluindo conflito ou tema quando relevante.

Depois da revisão, substitua somente a entrada correspondente na tabela de pendências
do README pela imagem disponível. Mantenha as demais como ausentes; não inclua tags de
imagem para arquivos que ainda não existem. Atualize também o estado das capturas em
`docs/assets/README.md` e preserve os dois blocos Mermaid do README principal.

Exemplo para o README principal, para usar somente quando o arquivo existir:

```markdown
<p align="center">
  <a href="docs/assets/screenshots/main-window.png">
    <img src="docs/assets/screenshots/main-window.png" width="960" alt="Tela principal do Renamix com três propostas de renomeação">
  </a>
</p>

Tela principal · Renamix 0.1.1 · Windows [versão] · [resolução] · escala [valor].
```

Substitua os campos entre colchetes pelos dados reais da captura. Não afirme que o
EXE foi validado em uma máquina sem Python se essa verificação não foi realizada.
