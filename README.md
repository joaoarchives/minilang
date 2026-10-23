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

| Opção | O que faz |
|---|---|
| *(nenhuma)* | roda as fases prontas (léxica e sintática); sem erros, não imprime nada e sai com `0` |
| `--tokens` | imprime os tokens no formato `linha:coluna  TIPO  'lexema'` |
| `--ast` | imprime a árvore sintática abstrata indentada, um nó por linha |

```
$ python -m minilang exemplos/fatorial.mini --tokens
2:1   VAR          'var'
2:5   ID           'n'
2:6   DOIS_PONTOS  ':'
...
```

```
$ python -m minilang exemplos/fatorial.mini --ast
Programa
├── Decl n: int
│   └── Num 5
├── Decl f: int
│   └── Num 1
├── While
│   ├── cond: Binario >
│   │   ├── Var n
│   │   └── Num 0
│   └── corpo: Bloco
...
```

Se houver erros léxicos, **todos** são impressos em `stderr` e o processo
termina com código de saída `1`. Um erro sintático também termina com código
`1`, e o parser só roda se não houver erro léxico:

```
$ python -m minilang exemplos/erro_lexico.mini
3:7: erro léxico: caractere inválido '@'
5:18: erro léxico: caractere inválido '$'

$ python -m minilang exemplos/erro_sintatico.mini
3:1: erro sintático: esperado ';', encontrado 'print'
```

O erro aponta a linha 3 porque o `;` faltou no fim da linha 2, mas o parser
só percebe a falta ao ver o próximo token (`print`). GCC e Clang fazem o mesmo.

## Testes

```bash
pip install pytest
python -m pytest -q
```

## Decisões e observações

- **Erros léxicos (desafio de 28/08).** Na primeira versão do lexer (commit
  "lexer inicial"), rodar `x @ y` interrompia a análise com uma exceção no
  primeiro caractere inválido. Desde `v0.1-lexer`, o lexer usa recuperação em
  modo pânico: registra a mensagem, descarta o caractere e continua, e assim o
  programador vê todos os erros de uma vez.
- **Identificadores só em ASCII.** `ação` não é um identificador válido: `ç` e
  `ã` geram erro léxico, conforme `[a-zA-Z_][a-zA-Z0-9_]*`.
- **`!` sozinho é inválido.** Só `!=` existe no núcleo da linguagem.
- **`12ab`** vira `NUM 12` seguido de `ID ab` (maior casamento). Quem recusa
  esse trecho é o parser, porque dois tokens não podem aparecer em sequência ali.
- A análise do scanner do jlox, que inspirou a recuperação de erros, está em
  [`docs/analise-lexer.md`](docs/analise-lexer.md).

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
│   └── casos/             # programas válidos e inválidos para o parser
├── exemplos/              # programas .mini
├── docs/
│   ├── especificacao.md
│   ├── gramatica.md
│   └── analise-lexer.md
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
| `v0.1-lexer` | Analisador léxico com erros léxicos | ✅ |
| `v0.2-checkpoint` | Parser e AST | 🔧 parser pronto; falta o checkpoint |
| `v0.3-semantica` | Tabela de símbolos e análise semântica | ⏳ |
| `v0.4-vm` | Geração de TAC e máquina virtual | ⏳ |
| `v0.5-otimizacao` | Otimizações sobre o TAC | ⏳ |
