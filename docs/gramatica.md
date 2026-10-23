# Gramática da MiniLang

Versão final, de 11/09. Esta é a gramática que o parser recursivo descendente
(`minilang/parser.py`) implementa.

## Notação (EBNF)

| Notação | Significado |
|---|---|
| `{ x }` | `x` repetido zero ou mais vezes |
| `[ x ]` | `x` opcional |
| `a \| b` | alternativa |
| `"x"`, `MAIÚSCULAS` | terminais (tokens do lexer) |
| `minúsculas` | não terminais |

A gramática é **G = (V, T, P, S)**, em que:

- **V** são os não terminais: `programa`, `comando`, `decl`, `tipo`, `atrib`,
  `print`, `if`, `while`, `bloco`, `expr`, `soma`, `termo` e `fator`;
- **T** são os terminais, ou seja, os tokens produzidos pelo lexer;
- **P** são as produções abaixo;
- **S** é o símbolo inicial, `programa`.

## Produções

```
programa   → { comando } EOF

comando    → decl | atrib | print | if | while | bloco

decl       → "var" ID ":" tipo "=" expr ";"
tipo       → "int" | "bool"
atrib      → ID "=" expr ";"
print      → "print" "(" expr ")" ";"
if         → "if" "(" expr ")" bloco [ "else" bloco ]
while      → "while" "(" expr ")" bloco
bloco      → "{" { comando } "}"

expr       → soma [ ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) soma ]
soma       → termo { ( "+" | "-" ) termo }
termo      → fator { ( "*" | "/" ) fator }
fator      → NUM | "true" | "false" | ID
           | "(" expr ")"
           | "-" fator
```

## Como a ambiguidade foi eliminada

### O problema

Uma gramática ingênua como `E → E + E | E * E | id` é **ambígua**: a cadeia
`id + id * id` tem duas árvores de derivação, uma que agrupa `(id + id) * id` e
outra que agrupa `id + (id * id)`.

### A solução: um não terminal por nível de precedência

Cada nível de precedência virou um não terminal: `expr` (comparação), `soma`
(`+` e `-`), `termo` (`*` e `/`) e `fator` (`-` unário, literais e parênteses).
Quanto mais abaixo na gramática, mais forte o operador se liga.

### Árvore de `1 + 2 * 3`

Só existe uma árvore. O `*` fica **dentro** de um `termo`, então é agrupado
antes do `+`:

```
expr
└── soma
    ├── termo
    │   └── fator ── NUM 1
    ├── "+"
    └── termo
        ├── fator ── NUM 2
        ├── "*"
        └── fator ── NUM 3

agrupa: 1 + (2 * 3)  =  7
```

Uma árvore em que `1 + 2` fica sob o `*` exigiria que `soma` aparecesse dentro
de um `termo`. A única forma de isso acontecer é por `fator → "(" expr ")"`, ou
seja, com parênteses explícitos.

### Árvore de `1 - 2 - 3`

Também existe uma só árvore. A repetição `{ ( "+" | "-" ) termo }` deixa os
três `termo` no mesmo nível, e o parser monta a AST da esquerda para a direita
(**associatividade à esquerda**):

```
expr
└── soma
    ├── termo ── fator ── NUM 1
    ├── "-"
    ├── termo ── fator ── NUM 2
    ├── "-"
    └── termo ── fator ── NUM 3

agrupa: (1 - 2) - 3  =  -4      (e não 1 - (2 - 3) = 2)
```

### Recursão à esquerda

A forma clássica `soma → soma "+" termo | termo` faria um parser descendente
chamar `soma()` dentro de `soma()` sem consumir nenhum token, em laço infinito.
Por isso ela foi reescrita com a regra:

```
A → A α | β     ⇒     A → β { α }
soma → soma "+" termo | termo     ⇒     soma → termo { "+" termo }
```

### Outras decisões

- **Comparação não associativa.** `expr` usa `[ ]` e não `{ }`, então
  `a < b < c` é erro sintático.
- **Sem *else* pendente.** `if` e `while` exigem bloco `{ }`, então todo `else`
  pertence sem ambiguidade ao `if` cujo bloco acabou de fechar.

## Condição LL(1): conjuntos FIRST

### Alternativas de `comando`

| Alternativa | FIRST |
|---|---|
| `decl` | `var` |
| `atrib` | `ID` |
| `print` | `print` |
| `if` | `if` |
| `while` | `while` |
| `bloco` | `{` |

### Alternativas de `fator`

| Alternativa | FIRST |
|---|---|
| `NUM` | `NUM` |
| `"true"` | `true` |
| `"false"` | `false` |
| `ID` | `ID` |
| `"(" expr ")"` | `(` |
| `"-" fator` | `-` |

Logo, `FIRST(expr) = FIRST(soma) = FIRST(termo) = FIRST(fator) =
{ NUM, true, false, ID, (, - }`.

Os conjuntos são **disjuntos** dentro de cada tabela. Isso significa que o
parser escolhe a alternativa olhando um único token, sem voltar atrás.

### Partes opcionais e repetições

Em `{ x }` e `[ x ]`, o parser precisa decidir entre entrar em `x` e seguir em
frente. Isso também é feito com um token, porque `FIRST(x)` não se mistura com
o que pode vir depois:

| Construção | Entra se o token for | O que pode vir depois (FOLLOW) |
|---|---|---|
| `{ comando }` em `programa` | FIRST(comando) | `EOF` |
| `{ comando }` em `bloco` | FIRST(comando) | `}` |
| `[ "else" bloco ]` | `else` | FIRST(comando), `}`, `EOF` |
| `[ op_comparação soma ]` | `== != < > <= >=` | `)`, `;` |
| `{ ( "+" \| "-" ) termo }` | `+ -` | comparações, `)`, `;` |
| `{ ( "*" \| "/" ) fator }` | `* /` | `+ -`, comparações, `)`, `;` |

**Atenção:** `atrib` começa com `ID`. Se um dia a linguagem tiver chamada de
função `f(x);`, que também começa com `ID`, os FIRST deixam de ser disjuntos e
o parser precisará olhar 2 tokens.

## Derivação mais à esquerda de um caso válido

Programa: `var x: int = 1 + 2 * 3;`

Tokens: `var ID : int = NUM + NUM * NUM ; EOF`

A cada passo, o não terminal **mais à esquerda** é reescrito. As repetições
`{ }` e as opções `[ ]` são expandidas o número de vezes necessário.

| # | Forma sentencial | Regra aplicada |
|---|---|---|
| 1 | `programa` | símbolo inicial |
| 2 | `comando EOF` | `programa → { comando } EOF` (1 repetição) |
| 3 | `decl EOF` | `comando → decl` |
| 4 | `var ID : tipo = expr ; EOF` | `decl → "var" ID ":" tipo "=" expr ";"` |
| 5 | `var ID : int = expr ; EOF` | `tipo → "int"` |
| 6 | `var ID : int = soma ; EOF` | `expr → soma [ … ]` (opção vazia) |
| 7 | `var ID : int = termo + termo ; EOF` | `soma → termo { "+" termo }` (1 repetição) |
| 8 | `var ID : int = fator + termo ; EOF` | `termo → fator { … }` (0 repetições) |
| 9 | `var ID : int = NUM + termo ; EOF` | `fator → NUM` |
| 10 | `var ID : int = NUM + fator * fator ; EOF` | `termo → fator { "*" fator }` (1 repetição) |
| 11 | `var ID : int = NUM + NUM * fator ; EOF` | `fator → NUM` |
| 12 | `var ID : int = NUM + NUM * NUM ; EOF` | `fator → NUM` |

A forma final só tem terminais e é igual à sequência de tokens, então o programa
pertence à linguagem. Repare que `2 * 3` nasceu dentro do segundo `termo`
(passo 10), o que confirma a precedência do `*` sobre o `+`.

## Banco de casos

Os casos de teste ficam em `tests/casos/`:

- `validos/`: programas que o parser deve aceitar e transformar em AST;
- `invalidos/`: cada arquivo tem **um único** erro sintático. A primeira linha é
  um comentário `// ERRO: <mensagem esperada>`, que o teste automático
  (`tests/test_casos.py`) lê e compara com a mensagem do parser.
