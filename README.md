# MiniLang

Compilador da linguagem **MiniLang**, desenvolvido como projeto final da
disciplina de Compiladores 2026.2 (IDP). Ele é construído em etapas, uma por
aula prática, e vai cobrir o pipeline completo de compilação:

```
fonte .mini → léxico → sintático → AST → semântico → TAC → otimizador → VM
              ✅        ✅          ✅     ✅          ⏳     ⏳           ⏳
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
| *(nenhuma)* | roda as fases prontas (léxica, sintática e semântica); sem erros, não imprime nada e sai com `0` |
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

$ python -m minilang exemplos/erro_semantico.mini
linha 5: erro semântico: 'b' é bool, mas recebe int
linha 6: erro semântico: condição deve ser bool, encontrado int
linha 6: erro semântico: 'y' não foi declarada
```

- O **lexer** reporta **todos** os erros de uma vez (recuperação em modo
  pânico).
- O **analisador semântico** também reporta todos, **sem erros em cascata**:
  em `print(z + 1 + 2);` com `z` não declarada, sai um único erro, e não três.
- O **parser** para no primeiro erro. No exemplo, o `;` faltou no fim da linha
  2, mas o parser só percebe a falta ao ver o próximo token (`print`, na linha
  3). GCC e Clang fazem o mesmo.

## Testes

```bash
python -m pytest -q
```

```
115 passed
```

| Arquivo | O que testa |
|---|---|
| `tests/test_lexer.py` | tokens, reservadas × identificadores, maior casamento, posições, comentários e 6 casos de erro léxico |
| `tests/test_parser.py` | precedência, associatividade, `-` unário, comandos, linha nos nós, erros e a impressão do `--ast` |
| `tests/test_simbolos.py` | tabela de símbolos isolada (escopos, sombreamento, redeclaração) e o uso de nomes sobre a AST |
| `tests/test_semantica.py` | tabela de tipos de todos os operadores, regras dos comandos, ausência de cascata e anotação `no.tipo` |
| `tests/test_casos.py` | banco de casos, descrito abaixo |

O banco de casos em `tests/casos/` funciona assim:

| Pasta | Exigência |
|---|---|
| `validos/` (12) | gerar AST e passar pela análise semântica sem erros |
| `invalidos/` (12) | falhar no parser com a mensagem da 1ª linha (`// ERRO: ...`) |
| `semanticos/` (16) | passar no parser e produzir **exatamente** a lista de erros semânticos anotada nas linhas `// ERRO: ...` do início do arquivo |

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
│   ├── ast.py             # nós da AST, Visitor e impressão      ✅
│   ├── parser.py          # parser recursivo descendente         ✅
│   ├── simbolos.py        # tabela de símbolos                   ✅
│   ├── semantica.py       # análise semântica e tipos            ✅
│   ├── ir.py              # geração de TAC              (30/10)
│   ├── vm.py              # máquina virtual             (06/11)
│   └── otimizador.py      # otimizações sobre o TAC     (13/11)
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_simbolos.py
│   ├── test_semantica.py
│   ├── test_casos.py
│   └── casos/
│       ├── validos/       # 12 programas corretos
│       ├── invalidos/     # 12 programas com 1 erro sintático cada
│       └── semanticos/    # 16 programas com erros semânticos anotados
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
| `erro_semantico.mini` | tipo errado, condição `int` e variável não declarada |

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
- **Visitor com despacho pelo nome da classe** (`visitar_Bloco`,
  `visitar_Binario`...). Cada fase que percorre a AST é uma classe própria.
- **Tabela de símbolos como pilha de dicionários.** Cada bloco empilha um
  escopo. Redeclarar no mesmo escopo é erro; sombrear em escopo interno é
  permitido.
- **`var x: int = x + 1;`:** a expressão é analisada **antes** de `x` ser
  declarada, então o `x` da direita é o de um escopo externo, ou erro.
- **Sem erros em cascata.** Cada expressão devolve seu tipo ou `None`, e
  `None` significa que o erro já foi reportado. Uma variável declarada com tipo
  errado entra na tabela mesmo assim, para que os usos seguintes não gerem
  "não foi declarada".
- **AST anotada:** toda expressão válida recebe `no.tipo` (`'int'` ou
  `'bool'`), que a geração de código vai usar.

## Etapas

| Tag | Aula | Etapa | Situação |
|---|---|---|---|
| `v0.0-spec` | 21/08 | Especificação, gramática inicial e módulos | ✅ |
| `v0.1-lexer` | 28/08 e 04/09 | Analisador léxico com recuperação de erros | ✅ |
| `v0.2-checkpoint` | 11/09 a 25/09 | Gramática, parser, AST e checkpoint | ✅ |
| `v0.3-semantica` | 09/10 e 16/10 | Tabela de símbolos e análise semântica | ✅ |
| `v0.4-vm` | 30/10 e 06/11 | Geração de TAC e máquina virtual | ⏳ |
| `v0.5-otimizacao` | 13/11 | Otimizações sobre o TAC | ⏳ |
