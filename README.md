# Renamix

**Safe batch file renaming for local workflows**

Renomeie arquivos em lote com uma prévia clara e confirmação antes de alterar a pasta.
O Renamix é um aplicativo desktop em Python, com interface em português brasileiro,
feito para tarefas locais: organizar documentos, ajustar nomes de fotos ou identificar
uma versão final de arquivos. Funciona offline, sem contas, telemetria ou serviços externos.

Versão **0.1.0** · Python **3.11+** · Licença **MIT**

## Preview

A aparência padrão usa fundo escuro, painéis discretos e destaque vermelho na ação de renomear.
Pasta, regra, prévia e relatório ficam na mesma janela. O tema `clam` oferece uma base
comum; fontes, seletores nativos e escala podem variar conforme o sistema operacional.

A interface, incluindo Dark Beach e Vampire, foi validada manualmente no Windows
pelo autor. As capturas reais ainda não foram adicionadas. Veja as instruções e os
nomes previstos em [docs/assets/README.md](docs/assets/README.md).

## Funcionalidades

- Prefixo, sufixo ou substituição literal de texto: uma regra por operação.
- Prévia automática ao editar a regra, sem escrever nos arquivos.
- Tabela com nomes, status, detalhes e rolagem nos dois eixos.
- Detecção conservadora de colisões, inclusive por caixa e normalização Unicode.
- Revalidação de identidade, tamanho e datas dos arquivos antes da execução.
- Renomeação nativa sem substituição do destino, com falhas reportadas por arquivo.
- Relatório com totais e exportação CSV opcional, sem sobrescrever relatórios existentes.
- Oito temas visuais, com troca imediata e preferência salva localmente.

Somente arquivos regulares diretamente na pasta são elegíveis. Subpastas, links,
pontos de nova análise do Windows e ocultos são exibidos como ignorados. A contagem
de analisados inclui todas as entradas da tabela, inclusive essas entradas ignoradas.

## Temas

Na aba **Temas**, escolha uma das oito paletas: **Renamix Original**, **ChatGPT Dark**,
**ChatGPT Light**, **Codex Dark**, **Codex Light**, **Sakura**, **Dark Beach** e **Vampire**.
As amostras mostram as cores; a escolha atual aparece no rodapé. Para voltar à aparência
padrão, use **Restaurar tema original**. Mouse e teclado funcionam nos controles;
`Ctrl+Tab` alterna entre **Renomear** e **Temas**.

A mudança é imediata e preserva pasta, regra, prévia e relatório da sessão. A preferência
é restaurada na próxima abertura e fica em um pequeno `settings.json` no diretório
de configurações do usuário: `%APPDATA%\Renamix` no Windows, `~/Library/Application Support/Renamix`
no macOS e `${XDG_CONFIG_HOME:-~/.config}/renamix` no Linux. Configurações ausentes ou
inválidas recuperam o tema original; se não houver permissão para salvar, o tema continua
ativo apenas na sessão, com aviso na aba. Esse caminho não é derivado da pasta escolhida
para renomear; evite selecionar o próprio diretório de configurações como pasta de trabalho.
Tudo funciona offline.

Os temas ChatGPT e Codex são interpretações cromáticas, sem vínculo oficial com os
produtos. Dark Beach usa apenas cores originais inspiradas em uma atmosfera noturna;
não inclui capas, imagens ou logotipos. Seletores de arquivo, mensagens e a barra de
título podem seguir o tema do sistema operacional.

## Instalação

É possível executar a partir do código, sem instalar pacotes externos:

```console
cd renamix
python --version
python -m renamix
```

Use Python 3.11 ou superior com Tkinter. Dependendo do sistema, o comando pode ser
`python3`. No Windows, a instalação oficial do Python oferece o componente Tcl/Tk.
No Ubuntu/Debian, o suporte gráfico normalmente é instalado com:

```console
sudo apt install python3-tk
```

No macOS, use uma distribuição de Python que inclua Tcl/Tk (por exemplo, o instalador
do python.org). É necessário estar em uma sessão gráfica; a interface não abre em
servidores sem display. Para diagnosticar a instalação do Tkinter:

```console
python -m tkinter
```

Para instalar o projeto em um ambiente virtual no Windows, sem precisar ativá-lo:

```console
python -m venv .venv
.venv\Scripts\python -m pip install .
.venv\Scripts\python -m renamix
```

No Linux/macOS:

```console
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -m renamix
```

A instalação usa setuptools como ferramenta de empacotamento e pode precisar de acesso
ao índice de pacotes para obtê-lo. O aplicativo instalado não tem dependências de
execução externas e funciona sem rede. Com o ambiente ativado, `renamix` também abre
a interface. Não há argumentos de linha de comando para executar renomeações.

## Utilização

1. Clique em **Selecionar pasta…** ou informe o caminho.
2. Escolha **Prefixo**, **Sufixo** ou **Substituição** e preencha o texto.
3. Confira o nome proposto, o status e os detalhes de cada entrada.
4. Use **Analisar novamente** se a pasta tiver mudado.
5. Clique em **Renomear arquivos** e confirme a quantidade e a pasta.
6. Confira o relatório e, se desejar, escolha **Exportar CSV…** usando um nome novo.

O botão de renomear só fica disponível com uma prévia válida e pelo menos um arquivo
pronto. Arquivos em conflito ou inválidos não são executados e aparecem como falhas
no relatório; os demais podem ser renomeados. Não há atomicidade do lote nem desfazer
automático. Após a operação, uma nova prévia é necessária para executar outro lote.

| Status da prévia | Significado |
| --- | --- |
| Pronto | Operação elegível; será revalidada antes de executar. |
| Sem alterações | A regra manteve o nome. |
| Ignorado | Entrada oculta, link, subpasta ou outro tipo não regular. |
| Conflito | Destino ocupado, equivalente ou compartilhado por propostas. |
| Inválido | Nome não permitido ou erro de leitura. |

## Exemplos

| Regra | Entrada | Parâmetro | Resultado |
| --- | --- | --- | --- |
| Prefixo | `documento.pdf` | `2026_` | `2026_documento.pdf` |
| Sufixo | `relatorio.xlsx` | `_final` | `relatorio_final.xlsx` |
| Substituição | `IMG_001.jpg` | `IMG_` → `Foto_` | `Foto_001.jpg` |
| Sufixo | `backup.tar.gz` | `_novo` | `backup_novo.tar.gz` |
| Prefixo | `anotações` | `projeto_` | `projeto_anotações` |

Tudo a partir do primeiro ponto que inicia uma extensão é preservado: `relatorio.v1.csv`
recebe o sufixo como `relatorio_final.v1.csv`. A substituição é literal, distingue
maiúsculas/minúsculas e atua apenas na parte anterior às extensões. Todas as ocorrências
são substituídas. Busca vazia é inválida; substituição por texto vazio é permitida,
desde que o nome final seja válido. Nomes que começam por ponto são ignorados.

O CSV usa UTF-8 com BOM e ponto e vírgula, com as colunas **Nome anterior**,
**Nome proposto**, **Resultado** e **Mensagem de erro**. Valores que poderiam ser
interpretados como fórmulas por planilhas recebem um apóstrofo inicial na exportação.

## Segurança e compatibilidade

O aplicativo não altera o conteúdo dos arquivos, não executa comandos derivados de
nomes e não cria destinos fora da pasta. A prévia apenas lista entradas e metadados.
Nenhum nome existente é liberado para outro arquivo no mesmo lote: trocas, ciclos e
cadeias que dependam de desocupar destinos são recusados.

Uma verificação de existência seguida de `Path.rename()` seria insuficiente em sistemas
que substituem o destino. Por isso, a execução usa uma chamada nativa de exclusão:

| Plataforma | Operação sem substituição |
| --- | --- |
| Windows | `MoveFileExW` com flags zero, sem `MOVEFILE_REPLACE_EXISTING`. |
| Linux | `renameat2` com `RENAME_NOREPLACE`, usando descritor da pasta. |
| macOS | `renamex_np` com `RENAME_EXCL`. |

Se a API, kernel ou sistema de arquivos não suportar a operação, a renomeação falha.
Não há fallback para substituição, cópia/exclusão ou uma transação por links.
Referências: [Microsoft](https://learn.microsoft.com/pt-br/windows/win32/api/winbase/nf-winbase-movefileexw),
[manual Linux](https://man7.org/linux/man-pages/man2/rename.2.html) e
[Apple](https://developer.apple.com/documentation/foundation/urlresourcekey/volumesupportsexclusiverenamingkey).

### Limitações conhecidas

- A proteção nativa impede sobrescrita se outro processo criar o destino exato
  entre a validação e a chamada de renomeação. Colisões por caixa e Unicode são
  verificadas de forma conservadora na prévia e imediatamente antes da chamada;
  em volumes sensíveis a caixa, não há trava global contra a criação concorrente
  de outro nome apenas equivalente.
- As verificações de origem detectam mudanças observáveis entre prévia e execução.
  Não são uma trava contra processos hostis que troquem a origem ou a pasta no
  intervalo final antes da chamada nativa. Use pastas locais sob seu controle e
  suspenda outros organizadores/sincronizadores durante o lote. Não use como
  fronteira de segurança em pastas controladas por outros usuários.
- Não há garantia de atomicidade global, rollback ou persistência contra quedas de
  energia. Uma falha pode deixar parte do lote concluída; o relatório mostra isso.
- Nomes reservados do Windows, separadores, controles, nomes finais ocultos e pontos
  ou espaços finais são recusados em todos os sistemas. Renomeações que mudem apenas
  caixa ou forma Unicode também são recusadas, mesmo se o volume as permitir.
- Há um limite conservador de 255 bytes UTF-8 e 255 unidades UTF-16 por nome. No
  Windows, caminhos de destino com 260 ou mais unidades UTF-16 são bloqueados.
  Limites menores do volume e permissões são reportados pelo sistema operacional.
- Arquivos bloqueados podem falhar no Windows. No POSIX, arquivos abertos podem ser
  renomeados. Diretórios de rede, FUSE e volumes sincronizados exigem validação
  específica; prefira sistemas de arquivos locais com semântica nativa.
- Identidade e datas não equivalem a um hash de conteúdo. Uma alteração que preserve
  todos os metadados pode não ser detectada. O Renamix não lê o conteúdo para planejar.
- A listagem e a execução rodam em uma thread de trabalho; a inserção da tabela ocorre
  na interface. Pastas com dezenas de milhares de entradas podem ter atualização lenta.
- Não há recursão, monitoramento, instaladores, perfis, plugins ou desfazer automático.

## Estrutura

```text
renamix/
├── renamix/
│   ├── __init__.py       # versão
│   ├── __main__.py       # inicialização
│   ├── gui.py            # tema, eventos e apresentação
│   ├── planner.py        # regras, validação e prévia sem escrita
│   ├── executor.py       # revalidação, chamada nativa e relatório CSV
│   └── themes.py         # paletas, estilos e preferência visual local
├── tests/
│   ├── test_planner.py
│   ├── test_executor.py
│   └── test_themes.py
├── .github/workflows/tests.yml
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── pyproject.toml
```

`dataclasses` imutáveis guardam a regra e o planejamento que o usuário confirmou.
Separar a interface do núcleo permite testar a segurança sem abrir janelas.
A lógica usa somente a biblioteca padrão; `ctypes` acessa as operações do sistema.

## Testes

Na raiz do projeto:

```console
python -m compileall -q renamix tests
python -m unittest discover -s tests -v
```

Os testes usam `tempfile` e não alteram arquivos pessoais. Cobrem as três regras,
extensões, Unicode, ignorados, conflitos, nomes inválidos, alterações após a prévia,
falhas parciais, CSV e ausência de sobrescrita. A condição de corrida do destino é
simulada criando o arquivo imediatamente antes da chamada nativa real.
Os dois testes de links só são ignorados no Windows quando a criação retorna erro
1314 (privilégio ausente); outros erros fazem o teste falhar. O teste de FIFO é
exclusivo de POSIX. Ignorados não são contabilizados como aprovados.

O GitHub Actions executa a suíte sem interface em Ubuntu, Windows e macOS com Python
3.11, além de conferir sintaxe e instalação. Criar o workflow localmente não significa
que ele já tenha sido executado no GitHub.

Consulte [o registro de validação local](docs/VALIDATION.md) para resultados reais
e verificações manuais ainda pendentes.

Antes de publicar, confira manualmente seleção de pasta, confirmação/cancelamento,
rolagem, escala de tela, acentos, exportação e mensagens de arquivos bloqueados nas
plataformas de distribuição. O diálogo de arquivo é nativo e pode usar outro tema.

## Roadmap

Possíveis melhorias para 0.2.0, sujeitas a discussão:

- Filtrar arquivos por extensão e permitir seleção individual na prévia.
- Ordenar e filtrar a tabela sem alterar o planejamento confirmado.
- Tornar a inserção de tabelas grandes incremental e cancelável.
- Ampliar a validação manual de acessibilidade e escala em Linux e macOS.

## Contribuições

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para configurar o ambiente e propor mudanças.
Prefira melhorias pequenas, com comportamento reproduzível e testes para regras ou
garantias de arquivos. Não é necessário adicionar dependências para contribuir.

## Licença

[MIT](LICENSE) · Copyright © 2026 [Amoz Santos](https://github.com/amzsants).
