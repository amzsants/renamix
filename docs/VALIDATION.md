# Validação local da versão 0.1.0

Data: 31 de outubro de 2026 (America/Sao_Paulo).

Ambiente observado: Windows, Python 3.14.7, Tkinter disponível.

## Resultados executados

| Verificação | Resultado |
| --- | --- |
| `python -m compileall -q renamix tests` | Sem erros de sintaxe. |
| `python -m unittest discover -s tests -v` | 45 testes descobertos: 42 passaram, 3 ignorados, nenhuma falha. |
| Build e instalação local com `pip install --no-deps --upgrade --target .validation-install .` | Wheel 0.1.0 gerado e instalado com sucesso. |
| Suíte carregando o pacote instalado, com Python em modo isolado (`-I`) | 45 testes: 42 passaram, 3 ignorados, nenhuma falha. |
| `python -m renamix` | Janela abriu sem erro de inicialização. |
| Inspeção da janela com captura real | Tema, cabeçalho, campos, tabela e botões observados. Revisão visual completa pendente. |

Os testes ignorados foram dois cenários que exigem criar links simbólicos, sem
permissão nesta sessão do Windows, e um cenário de FIFO exclusivo de POSIX.
O teste de arquivo bloqueado utilizou um handle exclusivo real do Windows e passou.
A corrida de criação do destino foi simulada imediatamente antes de chamar a API
nativa real: origem e destino foram preservados, e a operação foi reportada como falha.

A primeira captura mostrou a região inferior fora da área visível. O tamanho e a
posição inicial foram ajustados para respeitar a altura da tela. A inspeção seguinte
foi interrompida por janela minimizada/entrada do usuário no controle de janelas;
por isso não há captura definitiva incluída no README.

As ações do workflow foram conferidas nas instruções oficiais de
[checkout](https://github.com/actions/checkout) e
[setup-python](https://github.com/actions/setup-python). A configuração local possui
três jobs de plataforma, Python 3.11, permissões somente de leitura e nenhuma
publicação automática. O workflow ainda não foi executado no GitHub.

## Validação manual pendente

- Confirmar o layout após o ajuste de tamanho, inclusive em 1366 × 768 e escala de 125%/150%.
- Percorrer o fluxo pela interface: selecionar pasta descartável, editar cada regra,
  analisar, cancelar confirmação, confirmar, conferir detalhes e exportar CSV.
- Conferir navegação por teclado, rolagem e nomes extensos na tabela.
- Obter uma captura real com arquivos de exemplo e sem caminhos pessoais.
- Executar a suíte e revisar a interface em Linux e macOS; esses sistemas não foram
  executados neste ambiente. Os backends nativos têm cobertura planejada pelo CI.

Esta validação não representa um teste de estresse nem uma garantia para volumes de
rede, processos hostis concorrentes ou falhas de energia. Consulte as limitações do README.
