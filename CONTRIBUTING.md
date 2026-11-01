# Como contribuir

O Renamix prioriza segurança de arquivos, simplicidade e uso offline. Contribuições
pequenas e fáceis de revisar são bem-vindas. A interface e a documentação principal
são em português brasileiro.

## Preparar o ambiente

Use Python 3.11+ com Tkinter. Faça um fork ou clone uma cópia do projeto e, na raiz:

```console
python -m venv .venv
```

No Windows:

```console
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m renamix
```

No Linux/macOS:

```console
.venv/bin/python -m pip install -e .
.venv/bin/python -m renamix
```

Não há dependências de execução externas. O backend de instalação é setuptools.
Consulte o README para instalar o suporte Tcl/Tk, se necessário.

## Executar testes

Com seu Python do ambiente virtual, execute:

```console
python -m compileall -q renamix tests
python -m unittest discover -s tests -v
```

Os testes não abrem janelas. Use somente pastas temporárias em testes automatizados.
Mudanças na execução devem preservar o teste real de destino ocupado e o teste de
criação concorrente de destino. Nunca substitua a API exclusiva por uma sequência
`exists()` / `rename()` ou por `replace()`.

## Relatar bugs

Inclua sistema operacional, versão do Python e do Renamix, passos para reproduzir,
regra escolhida, nomes de exemplo e mensagem recebida. Use nomes fictícios e remova
caminhos pessoais de capturas ou relatórios. Informe se a pasta está em volume local,
de rede ou sincronizado. Reproduza com cópias descartáveis; não arrisque seus originais.

## Propor funcionalidades

Descreva a tarefa real e um exemplo de entrada e saída. Explique como a mudança
preserva a prévia, a confirmação e a proteção contra sobrescrita. Para mudanças
grandes, abra uma discussão antes de implementar. O escopo atual não inclui
recursão, contas, nuvem, IA, plugins ou monitoramento automático.

## Enviar pull requests

1. Crie uma branch descritiva a partir da versão atual.
2. Separe a lógica da interface e mantenha o estilo legível da biblioteca padrão.
3. Inclua testes quando alterar regras, validação ou execução.
4. Execute a suíte e atualize a documentação que mudou.
5. Descreva problema, solução, testes executados e limitações no pull request.

Use commits curtos, preferencialmente Conventional Commits, como
`fix: reject occupied destinations`. Para mudanças visuais, anexe uma captura real
e informe o sistema e a escala utilizados. As contribuições são distribuídas sob
a licença MIT do projeto.
