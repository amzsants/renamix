# Validação de pré-publicação — Renamix 0.1.0

Data: 1 de novembro de 2026 (America/Sao_Paulo). Ambiente local: Windows, Python 3.14.7.
Base auditada: `307a0c8`; as alterações posteriores desta auditoria limitam-se a testes e documentação.

## Resultado

Código apto à revisão pública como MVP para pastas locais sob controle do usuário,
com as limitações do README. Não há evidência de homologação multiplataforma nem de
execução remota do CI. A inspeção não é uma garantia de ausência de vulnerabilidades.
A interface no Windows, incluindo Dark Beach e Vampire, foi validada manualmente
pelo autor, conforme informado nesta revisão; não houve automação de mouse/teclado
nem nova inspeção visual realizada pelo agente nesta rodada.

## Verificações executadas

| Verificação | Resultado real |
| --- | --- |
| `python -m unittest discover -s tests -v` | 62 descobertos: 59 aprovados, 3 ignorados, zero falhas/erros. |
| `python -m compileall -q renamix tests` | Sem erros de sintaxe. |
| `python -m pip install --no-deps --target .validation-install .` | Wheel 0.1.0 gerado e instalado. |
| Suíte com Python `-I`, carregando o pacote instalado | 62 descobertos: 59 aprovados, 3 ignorados, zero falhas/erros. |
| Falha simulada de I/O na criação de links nos dois testes | Os dois reportam erro, sem ignorá-lo. |
| Revisão estática do código e revisão independente de segurança | Nenhuma vulnerabilidade reportável estabelecida no uso local documentado. |
| Histórico local anterior às correções | 7 commits alcançáveis; 23 blobs armazenados, incluindo os eventualmente não alcançáveis; nenhum blob binário. |
| Busca de padrões de credenciais e caminhos pessoais nos blobs | Nenhuma ocorrência; complementada pela leitura do código atual. Não equivale a prova universal de ausência de segredos. |

O teste de arquivo bloqueado no Windows e o teste de criação concorrente do destino
executaram a API nativa real e passaram. O diretório de instalação usado na conferência
é ignorado pelo Git e foi removido após a validação.

## Os três testes ignorados

- `test_symlink_ignored_even_when_dangling`: exige criar link simbólico.
- `test_source_becomes_symlink_after_preview`: exige trocar uma origem por link simbólico.
- `test_fifo_is_ignored`: exige `os.mkfifo`, disponível em POSIX e ausente no Windows.

A tentativa real de criação de link nesta sessão retornou Windows `winerror=1314`
(privilégio ausente). Isso explica os dois primeiros casos. O tratamento foi restringido
a esse erro no Windows: outro `OSError` agora falha em vez de ocultar um defeito.
Não foram alterados privilégios ou configurações do Windows.

O FIFO ignorado é esperado nesta plataforma. Os dois links representam uma lacuna
de validação local, não resultados aprovados. Devem executar no CI Ubuntu/macOS;
no Windows, execute-os futuramente em um ambiente já autorizado a criar links.
Em POSIX, os dois testes específicos de bloqueio/atributo oculto do Windows serão
ignorados; compare os motivos, não apenas o total de aprovados.

## Revisão técnica

- Planejamento, execução, GUI e temas permanecem separados; nenhuma mudança no núcleo foi necessária.
- Destinos existentes e equivalentes são recusados. A chamada nativa exclui substituição;
  APIs ou volumes sem suporte falham sem fallback inseguro.
- A origem e a pasta são revalidadas. Continua a limitação documentada contra trocas
  hostis no intervalo final; não há atomicidade do lote, rollback ou garantia de durabilidade.
- Falhas são apresentadas por entrada; o lote pode concluir parcialmente.
- CSV usa criação exclusiva, UTF-8 com BOM, delimitador `;` e proteção de prefixos de
  fórmula em todos os campos. Não foi aberto um aplicativo de planilhas nesta rodada.
- Preferências usam JSON com tema permitido e substituição atômica no diretório de
  configuração. Oito temas permanecem disponíveis. O local depende do ambiente do
  usuário; o README agora esclarece que não existe proibição de selecionar esse diretório.

## Repositório e privacidade

Nenhuma credencial, arquivo pessoal de conteúdo, caminho absoluto pessoal ou binário
foi encontrado nos arquivos rastreados e na busca dos blobs do histórico local.
Os caches Python presentes são ignorados, não versionados. Não havia ambiente virtual
ou configurações privadas entre os arquivos rastreados, nem remoto configurado.
A análise não alcança repositórios remotos ou históricos que não estejam neste Git local.

O histórico contém um endereço pessoal de e-mail nos metadados de autoria. Isso não
é uma credencial, mas será público com os commits. Antes de enviar, decida se deseja
mantê-lo ou substituir a identidade histórica por um endereço noreply verificado na
sua conta. Alterar apenas `git config user.email` não modifica commits existentes.
Nenhum histórico foi reescrito nesta auditoria.

## GitHub Actions

Workflow revisado: pushes e pull requests, Python 3.11 em Ubuntu, Windows e macOS,
permissão `contents: read`, sintaxe, unittest e instalação, sem publicação automática.
Os inputs e referências v7 foram conferidos nos arquivos oficiais de
[checkout](https://raw.githubusercontent.com/actions/checkout/v7/action.yml) e
[setup-python](https://raw.githubusercontent.com/actions/setup-python/v7/action.yml).
Ambas usam Node 24. Os comandos locais foram exercitados com Python 3.14.7;
Python 3.11 e os backends POSIX não foram executados neste host.

Não existe evidência de execução remota do workflow. Um primeiro envio a um repositório
privado é uma forma de obter os três resultados antes de tornar o código público.

## Pendências antes da divulgação

1. Revisar a exposição do e-mail dos commits e decidir sobre a identidade pública.
2. Executar o CI nos três sistemas e confirmar os motivos de cada teste ignorado.
3. Revisar manualmente Linux/macOS se desejar anunciar suporte gráfico homologado.
4. Adicionar capturas reais conforme `docs/assets/README.md`; sua ausência não bloqueia
   a publicação do código. Não há imagens fictícias ou arquivos PNG vazios.
5. Se ainda não verificado manualmente, abrir um CSV de exemplo em sua planilha habitual.

Nenhum push, merge, release, publicação remota ou controle automatizado de mouse/teclado
foi realizado. Publicar continua dependendo de autorização explícita do autor.
