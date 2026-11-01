# Capturas reais do Renamix

Pasta reservada para imagens do aplicativo em execução. Nenhum PNG está presente
neste checkout; a legibilidade e a privacidade das cinco capturas ainda não puderam
ser avaliadas. Não crie imagens vazias, montagens ou capturas fictícias.

| Arquivo previsto | Conteúdo |
| --- | --- |
| `main-window.png` | Aba Renomear, com três arquivos de exemplo e prévia. |
| `themes.png` | Aba Temas com as oito opções. |
| `dark-beach.png` | Prévia no tema Dark Beach. |
| `vampire.png` | Prévia no tema Vampire. |
| `conflict.png` | Destino ocupado, com status e mensagem legíveis. |

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
