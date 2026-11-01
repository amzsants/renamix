# Build portátil para Windows

Este trabalho prepara a distribuição da **v0.1.1**, ainda não publicada. A versão
interna, o título da janela e os metadados Python usam 0.1.1. A branch
`codex/windows-portable` aguarda revisão antes de integrar `main`.
Não altere a tag nem a release v0.1.0 existente.

## Construir localmente

Use Windows x64 com Python 3.11 e Tcl/Tk. Na raiz do checkout:

```powershell
py -3.11 -m venv .venv-build
.venv-build\Scripts\python -m pip install -r requirements-build.txt
.venv-build\Scripts\python -m unittest discover -s tests -v
.venv-build\Scripts\python scripts\build_windows.py
```

O script resolve todos os caminhos a partir de seu próprio arquivo, portanto também
pode ser chamado por caminho absoluto de outro diretório. O launcher importa o pacote
por nome absoluto; não usa a pasta atual para localizar o código na execução congelada.

Saídas: `dist/Renamix.exe`, `dist/Renamix.exe.sha256`, `dist/LICENSE`. Somente o EXE é
necessário para executar; distribua também o checksum e a licença. `build/`, `dist/`
e `.venv-build/` são ignorados pelo Git. Não versione os binários, caches ou o spec
gerado, que contém caminhos locais do ambiente de build.

PyInstaller e suas dependências são exclusivos de build, com versões fixadas em
`requirements-build.txt`. A instalação das ferramentas pode usar rede; a aplicação
não usa rede. O processo usa onefile, windowed e `--noupx`, sem coletar a árvore do
repositório como dados. Build reproduzível significa repetir o processo com os mesmos
inputs; não se promete igualdade bit a bit entre sistemas/versões diferentes.
O ambiente de build precisa conseguir inicializar Tcl/Tk; importar `tkinter` sozinho
não comprova isso. Confira com `python -c "import tkinter; tkinter.Tcl()"` usando
o mesmo interpretador do build. Nesta preparação, o isolamento do terminal bloqueou
o acesso aos scripts Tcl; o build foi repetido fora desse isolamento, sem modificar
o Python ou os arquivos do aplicativo.

Erros capturados na inicialização são enviados ao stderr quando disponível. Sem console,
há um diálogo Tk, com fallback para uma mensagem nativa do Windows se o próprio Tk
falhar. O processo retorna código de falha. Não há logs persistentes ou telemetria.

## Workflow manual

Arquivo: `.github/workflows/build-windows.yml`. Após revisão e envio autorizados, o
workflow deve estar na branch padrão para aparecer na interface do GitHub Actions.
Abra **Actions → Build Windows portable → Run workflow**, escolha a referência aprovada
e inicie manualmente. O job usa Windows, Python 3.11 x64, executa testes e sintaxe,
gera o EXE, verifica tamanho e SHA-256 e envia o artefato **Renamix-Windows-x64**,
retido por 14 dias. Requer apenas `contents: read`; não cria release ou tag.

O checksum é do arquivo EXE, não do ZIP que o GitHub cria para o artefato. Não há
resultado remoto declarado nesta implementação. Builds locais e do CI podem ter
checksums diferentes; sempre use o checksum do mesmo artefato.

## Validação manual antes de distribuir

1. Extraia o artefato em outra pasta, confira o hash e abra o EXE com usuário comum.
2. Confira abertura sem terminal, duas abas, tabela, botões, diálogos e tamanho mínimo.
3. Em pasta descartável, crie três arquivos com conteúdo conhecido. Confira a prévia
   e teste prefixo, sufixo e substituição separadamente, incluindo `.tar.gz` e acentos.
4. Crie um destino ocupado, confira a recusa e confirme que os dois conteúdos permanecem.
   Confira também cancelar a confirmação e um lote parcialmente inválido.
5. Exporte CSV para um nome novo; tente repetir o destino e confira a recusa.
6. Percorra os oito temas, escolha um, feche e reabra. A configuração deve ficar em
   `%APPDATA%\Renamix\settings.json`, sem arquivos de preferência ao lado do EXE.
7. Repita em Windows 10 e 11 x64 sem Python, idealmente em VM limpa. Não desinstale
   seu Python nem desative antivírus/SmartScreen para fazer esse teste.

## Evidência local da preparação v0.1.1

- Windows 11 x64, Python 3.11.18 isolado em `build/` (distribuição
  python-build-standalone obtida por uv, sem registro no Windows), PyInstaller
  6.22.3, hooks-contrib 2026.9 e Tcl/Tk 8.6. O CI usa Python 3.11 de setup-python;
  o workflow de build ainda não teve execução remota verificada nesta preparação.
- Suíte: 67 descobertos, 64 aprovados, 3 ignorados (dois links sem privilégio Windows
  e um FIFO POSIX). Os cinco testes novos validam erros de inicialização, com diálogos
  simulados; não abrem janelas. A mesma suíte também passou em Python 3.14.7.
- Build onefile/windowed concluído. Uma cópia do EXE iniciou de outra pasta, com PATH
  sem Python; o processo filho expôs a janela principal com título Renamix 0.1.1.
  Isso é uma conferência de processo, não uma inspeção visual.
- O nome de saída anterior em `dist/` permaneceu bloqueado pelo Windows durante
  as tentativas locais. O build foi concluído com o mesmo spec gerado pelo script,
  usando `python -m PyInstaller --noconfirm --distpath build/plain011 --workpath
  build/pyinstaller build/Renamix.spec`. A cópia final está em
  `dist/v0.1.1/Renamix.exe`, com checksum e licença nessa mesma pasta. O workflow
  continua usando `dist/Renamix.exe` em um checkout limpo. Nenhuma proteção foi desativada.
- EXE local: 11.487.227 bytes; SHA-256
  `12ed11d6786da4a48e1031c86960a0f95e0db7377d848056b98adcd42684ff6e`.
  A inspeção confirmou a versão embutida 0.1.1, Python 3.11, recursos Tcl/Tk,
  arquitetura x64, subsistema GUI, manifesto `asInvoker`, checksum e licença.
- Wheel `renamix-0.1.1-py3-none-any.whl` construído sem dependências de execução;
  sintaxe verificada em Python 3.11 e 3.14. Regras, executor, interface e temas
  não receberam alterações nesta preparação.
- Na etapa anterior (0.1.0, Python 3.14), um verificador descartável congelado,
  separado do EXE distribuído, passou com
  janelas Tk ocultas: oito temas, restauração após reabrir, preferências em APPDATA
  temporário, três regras, prévia sem escrita, conflito sem sobrescrita e CSV com
  criação exclusiva. Rodou de pasta separada com PATH sem Python. Esse verificador
  e seus dados ficaram em `build/`, sem integrar o executável ou os arquivos versionados.

O autor confirmou manualmente abertura, interface, renomeação com arquivos de teste,
CSV e troca/persistência de temas no executável anterior. O novo build 0.1.1 deve
receber uma conferência manual final com o checklist acima.

Na finalização da documentação, três capturas reais com título 0.1.1 foram revisadas
e integradas ao README: prévia com três propostas prontas, Dark Beach e Vampire.
Somente o caminho pessoal foi ocultado com autorização do autor. As capturas não
substituem o checklist funcional do novo executável. A suíte foi executada novamente
em Python 3.11.18: 67 testes, 64 aprovados, três ignorados e nenhuma falha.

Não foi testada uma máquina sem Python instalado. Também não foram homologados
Windows 10, todas as políticas antivírus ou o build remoto Python 3.11.
O executável local não é uma release publicada nem assinada.
