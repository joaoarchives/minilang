# Gramática da MiniLang (rascunho)

Versão: `v0.0-spec`. Este rascunho será refinado na aula de 11/09, com a
verificação de ambiguidade, a tabela FIRST e uma derivação feita à mão.

## Notação (EBNF)

| Notação | Significado |
|---|---|
| `{ x }` | `x` repetido zero ou mais vezes |
| `[ x ]` | `x` opcional |
| `a \| b` | alternativa |
| `"x"`, `MAIÚSCULAS` | terminais (tokens do lexer) |
| `minúsculas` | não terminais |

O símbolo inicial é `programa`.

## Regras

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

## Decisões já tomadas

- **Um não terminal por nível de precedência** (`expr` → `soma` → `termo` →
  `fator`). Quanto mais abaixo na gramática, mais forte o operador se liga.
- **Sem recursão à esquerda.** `soma` e `termo` usam repetição `{ }` em vez de
  `soma → soma "+" termo`. A repetição mantém a associatividade à esquerda.
- **Comparação não associativa.** `expr` usa `[ ]` e não `{ }`, então
  `a < b < c` é erro sintático.
- **`if` e `while` exigem bloco.** Isso elimina o *else* pendente sem precisar
  de nenhuma regra extra.
- **Cada alternativa de `comando` começa com um token diferente** (`var`, `ID`,
  `print`, `if`, `while`, `{`). Isso deve permitir um parser LL(1), a ser
  confirmado com a tabela FIRST em 11/09.

## Pendências para 11/09

- [ ] Desenhar as árvores de `1 + 2 * 3` e `1 - 2 - 3` e confirmar que só
      existe uma para cada.
- [ ] Calcular a tabela FIRST das alternativas de `comando` e de `fator`.
- [ ] Documentar uma derivação mais à esquerda de um programa válido.
- [ ] Montar o banco de casos em `tests/casos/validos/` e
      `tests/casos/invalidos/`.
