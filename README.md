# MiniLang

Compilador da linguagem **MiniLang**, desenvolvido como projeto final da
disciplina de Compiladores 2026.2 (IDP). Ele é construído em etapas, uma por
aula prática, e cobre o pipeline completo de compilação:

```
fonte .mini → léxico → sintático → AST → semântico → TAC → otimizador → VM
```

A especificação da linguagem está em
[`docs/especificacao.md`](docs/especificacao.md) e a gramática está em
[`docs/gramatica.md`](docs/gramatica.md).

## Requisitos

- Python 3.10 ou superior
- pytest (para os testes)

## Como executar

Na raiz do repositório:

```bash
python -m minilang exemplos/fatorial.mini
```

Na versão `v0.0-spec`, o programa só lê o arquivo e imprime o conteúdo dele.

## Estrutura

```
minilang/                  # raiz do repositório
├── minilang/              # pacote Python
│   ├── __init__.py
│   ├── __main__.py        # CLI
│   ├── tokens.py          # 28/08
│   ├── lexer.py           # 28/08
│   ├── ast.py             # 18/09
│   ├── parser.py          # 18/09
│   ├── simbolos.py        # 09/10
│   ├── semantica.py       # 16/10
│   ├── ir.py              # 30/10
│   ├── vm.py              # 06/11
│   └── otimizador.py      # 13/11
├── tests/                 # pytest
├── exemplos/              # programas .mini
├── docs/
│   ├── especificacao.md
│   └── gramatica.md
└── README.md
```

## Programas de exemplo

| Arquivo | Conteúdo |
|---|---|
| `fatorial.mini` | `while` e `if/else`; imprime `120` |
| `if_else.mini` | `if/else`, `if` sem `else` e variável `bool` |
| `escopos.mini` | blocos aninhados e sombreamento de variável |
| `erro_lexico.mini` | caractere inválido (erro anotado na 1ª linha) |
| `erro_sintatico.mini` | falta de `;` (erro anotado na 1ª linha) |

## Etapas

| Tag | Etapa | Situação |
|---|---|---|
| `v0.0-spec` | Especificação, gramática inicial e módulos | ✅ |
| `v0.1-lexer` | Analisador léxico com erros léxicos | ⏳ |
| `v0.2-checkpoint` | Parser e AST | ⏳ |
| `v0.3-semantica` | Tabela de símbolos e análise semântica | ⏳ |
| `v0.4-vm` | Geração de TAC e máquina virtual | ⏳ |
| `v0.5-otimizacao` | Otimizações sobre o TAC | ⏳ |
