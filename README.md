# MiniLang

Compilador da linguagem **MiniLang**, desenvolvido como projeto final da
disciplina de Compiladores 2026.2 (IDP). Ele é construído em etapas, uma por
aula prática, e vai cobrir o pipeline completo de compilação:

```
fonte .mini → léxico → sintático → AST → semântico → TAC → otimizador → VM
              ✅        ✅          ✅     ⏳          ⏳     ⏳           ⏳
```

## A linguagem

```
// fatorial de 5
var n: int = 5;
var f: int = 1;
while (n > 0) {
  f = f * n;
  n = n - 1;
}
if (f > 100) {
  print(f);
} else {
  print(0);
}
```

A linguagem tem tipos `int` e `bool`, declarações sempre inicializadas,
atribuição, `print`, `if/else` e `while` com chaves obrigatórias, operadores
aritméticos e de comparação, comentários `//` e um escopo por bloco.

- Especificação completa: [`docs/especificacao.md`](docs/especificacao.md)
- Gramática em EBNF, com FIRST e derivação: [`docs/gramatica.md`](docs/gramatica.md)

## Instalação

Requisitos: **Python 3.10 ou superior** e **pytest**. O compilador não tem
outras dependências.

```bash
git clone https://github.com/joaoarchives/minilang.git
cd minilang
python -m pip install pytest
```

## Como executar

Na raiz do repositório:

```bash
python -m minilang <arquivo.mini> [--tokens] [--ast]
```

| Opção | O que faz |
|---|---|
| *(nenhuma)* | roda as fases prontas (léxica e sintática); sem erros, não imprime nada e sai com `0` |
| `--tokens` | imprime os tokens no formato `linha:coluna  TIPO  'lexema'` |
| `--ast` | imprime a árvore sintática abstrata indentada, um nó por linha |

### Tokens

```
$ python -m minilang exemplos/fatorial.mini --tokens
2:1   VAR          'var'
2:5   ID           'n'
2:6   DOIS_PONTOS  ':'
2:8   INT          'int'
2:12  ATRIB        '='
2:14  NUM          '5'
2:15  PONTO_VIRG   ';'
...
13:1  EOF          ''
```

### AST

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
│       ├── Atrib f
│       │   └── Binario *
│       │       ├── Var f
│       │       └── Var n
│       └── Atrib n
│           └── Binario -
│               ├── Var n
│               └── Num 1
└── If
    ├── cond: Binario >
    │   ├── Var f
    │   └── Num 100
    ├── então: Bloco
    │   └── Print
    │       └── Var f
    └── senão: Bloco
        └── Print
            └── Num 0
```

### Erros

As mensagens de erro vão para `stderr` e o processo termina com código de saída
`1`. Uma fase só roda se a anterior não tiver erros.

```
$ python -m minilang exemplos/erro_lexico.mini
3:7: erro léxico: caractere inválido '@'
5:18: erro léxico: caractere inválido '$'

$ python -m minilang exemplos/erro_sintatico.mini
3:1: erro sintático: esperado ';', encontrado 'print'
```

- O **lexer** reporta **todos** os erros de uma vez (recuperação em modo
  pânico).
- O **parser** para no primeiro erro. No exemplo, o `;` faltou no fim da linha
  2, mas o parser só percebe a falta ao ver o próximo token (`print`, na linha
  3). GCC e Clang fazem o mesmo.

## Testes

```bash
python -m pytest -q
```

```
59 passed
```

| Arquivo | O que testa |
|---|---|
| `tests/test_lexer.py` | tokens, reservadas × identificadores, maior casamento, posições, comentários e 6 casos de erro léxico |
| `tests/test_parser.py` | precedência, associatividade, `-` unário, comandos, linha nos nós, erros e a impressão do `--ast` |
| `tests/test_casos.py` | banco de casos: todo arquivo em `tests/casos/validos/` precisa gerar AST; todo arquivo em `tests/casos/invalidos/` precisa falhar com a mensagem da 1ª linha (`// ERRO: ...`) |

Para incluir um caso novo no banco, basta criar um arquivo `.mini` na pasta
certa, sem mexer no código dos testes.

## Estrutura

```
minilang/                  # raiz do repositório
├── minilang/              # pacote Python
│   ├── __init__.py
│   ├── __main__.py        # CLI
│   ├── tokens.py          # tipos de token e reservadas          ✅
│   ├── lexer.py           # analisador léxico                    ✅
│   ├── ast.py             # nós da AST e impressão indentada     ✅
│   ├── parser.py          # parser recursivo descendente         ✅
│   ├── simbolos.py        # tabela de símbolos          (09/10)
│   ├── semantica.py       # analisador semântico        (16/10)
│   ├── ir.py              # geração de TAC              (30/10)
│   ├── vm.py              # máquina virtual             (06/11)
│   └── otimizador.py      # otimizações sobre o TAC     (13/11)
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_casos.py
│   └── casos/
│       ├── validos/       # 10 programas que devem gerar AST
│       └── invalidos/     # 12 programas com 1 erro sintático cada
├── exemplos/              # programas .mini para a demonstração
├── docs/
│   ├── especificacao.md   # a linguagem
│   ├── gramatica.md       # EBNF, árvores, FIRST, derivação
│   ├── analise-lexer.md   # ficha de análise do scanner do jlox
│   └── checkpoint.md      # autoavaliação e roteiro da demonstração
├── pyproject.toml         # configuração do pytest
└── README.md
```

## Programas de exemplo

| Arquivo | Conteúdo |
|---|---|
| `fatorial.mini` | `while` e `if/else`; imprime `120` |
| `if_else.mini` | `if/else`, `if` sem `else` e variável `bool` |
| `escopos.mini` | blocos aninhados e sombreamento de variável |
| `erro_lexico.mini` | dois caracteres inválidos, reportados de uma vez |
| `erro_sintatico.mini` | falta de `;` |

## Decisões de projeto

- **Lexer manual**, caractere a caractere, com linha e coluna em cada token. A
  recuperação de erros foi inspirada no scanner do jlox
  ([`docs/analise-lexer.md`](docs/analise-lexer.md)).
- **Primeira versão do lexer (desafio de 28/08).** No commit "lexer inicial",
  rodar `x @ y` interrompia a análise no primeiro caractere inválido. Desde
  `v0.1-lexer`, o lexer registra o erro, descarta o caractere e continua.
- **Identificadores só em ASCII.** `ação` não é identificador válido: `ç` e `ã`
  geram erro léxico, conforme `[a-zA-Z_][a-zA-Z0-9_]*`.
- **`!` sozinho é inválido.** Só `!=` existe no núcleo da linguagem.
- **`12ab`** vira `NUM 12` seguido de `ID ab` (maior casamento). Quem rejeita
  esse trecho é o parser.
- **Gramática LL(1):** um não terminal por nível de precedência, repetição
  `{ }` no lugar de recursão à esquerda, comparação não associativa e chaves
  obrigatórias (sem *else* pendente).
- **AST:** todo nó guarda a linha, para as mensagens das fases seguintes. A
  linha não entra na comparação de nós, então os testes comparam árvores
  inteiras.

## Etapas

| Tag | Aula | Etapa | Situação |
|---|---|---|---|
| `v0.0-spec` | 21/08 | Especificação, gramática inicial e módulos | ✅ |
| `v0.1-lexer` | 28/08 e 04/09 | Analisador léxico com recuperação de erros | ✅ |
| `v0.2-checkpoint` | 11/09 a 25/09 | Gramática, parser, AST e checkpoint | ✅ |
| `v0.3-semantica` | 09/10 e 16/10 | Tabela de símbolos e análise semântica | ⏳ |
| `v0.4-vm` | 30/10 e 06/11 | Geração de TAC e máquina virtual | ⏳ |
| `v0.5-otimizacao` | 13/11 | Otimizações sobre o TAC | ⏳ |
