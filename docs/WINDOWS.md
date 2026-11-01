# Build portátil para Windows

Este trabalho prepara a distribuição da futura v0.1.1. A versão interna permanece
0.1.0 enquanto o conteúdo da próxima release está em revisão. Antes do build final
de release, alinhe `renamix/__init__.py`, `pyproject.toml` e README à versão aprovada,
execute os testes e reconstrua o binário/checksum. Não altere a tag v0.1.0 existente.

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

## Evidência local desta implementação

- Windows 11, Python 3.14.7 (único interpretador instalado), PyInstaller 6.22.3,
  hooks-contrib 2026.9, Tcl/Tk 9.0. O CI fica em Python 3.11, ainda não executado remotamente.
- Suíte: 67 descobertos, 64 aprovados, 3 ignorados (dois links sem privilégio Windows
  e um FIFO POSIX). Os cinco testes novos validam erros de inicialização, com diálogos
  simulados; não abrem janelas.
- Build onefile/windowed concluído. Uma cópia do EXE iniciou de outra pasta, com PATH
  sem Python; o processo filho expôs a janela principal com título Renamix 0.1.0.
  Isso é uma conferência de processo, não uma inspeção visual.
- Tcl/Tk 9 do Python local armazena scripts em arquivos ZIP embutidos nas próprias
  DLLs. A ausência de pastas `_tcl_data`/`_tk_data` não indica falta desses recursos
  nesse build; os hooks do PyInstaller tratam essa forma de distribuição.
- Um verificador descartável congelado, separado do EXE distribuído, passou com
  janelas Tk ocultas: oito temas, restauração após reabrir, preferências em APPDATA
  temporário, três regras, prévia sem escrita, conflito sem sobrescrita e CSV com
  criação exclusiva. Rodou de pasta separada com PATH sem Python. Esse verificador
  e seus dados ficaram em `build/`, sem integrar o executável ou os arquivos versionados.

Não foi testada uma máquina sem Python instalado. Também não foram homologados
Windows 10, todas as políticas antivírus, a apresentação visual do EXE ou o build
remoto Python 3.11. O executável local não é uma release publicada nem assinada.
