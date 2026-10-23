# Especificação da MiniLang

Versão: `v0.0-spec` (congelada em 21/08/2026)

A MiniLang é uma linguagem imperativa mínima, criada para o projeto da
disciplina de Compiladores 2026.2. Ela é pequena de propósito: cada recurso a
mais custa trabalho em todas as fases do compilador. Extensões só entram depois
que o pipeline estiver completo.

## 1. Visão geral

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

Um programa é uma sequência de comandos executados de cima para baixo. Não há
funções, e a única saída é o comando `print`.

Arquivos-fonte usam a extensão `.mini` e a codificação UTF-8.

## 2. Elementos léxicos

| Categoria | Lexemas | Observação |
|---|---|---|
| Palavras reservadas | `var` `int` `bool` `true` `false` `if` `else` `while` `print` | Não podem ser usadas como identificadores |
| Identificadores | `[a-zA-Z_][a-zA-Z0-9_]*` | Diferenciam maiúsculas de minúsculas |
| Números inteiros | `[0-9]+` | Apenas decimais, sem sinal. `-5` é o operador unário aplicado a `5` |
| Operadores aritméticos | `+` `-` `*` `/` | |
| Operadores de comparação | `==` `!=` `<` `>` `<=` `>=` | |
| Atribuição | `=` | |
| Delimitadores | `(` `)` `{` `}` `:` `;` | |
| Comentário | `//` até o fim da linha | Descartado pelo lexer |
| Espaços | espaço, tabulação, `\r`, `\n` | Descartados pelo lexer |

Regras de reconhecimento:

- **Maior casamento (maximal munch):** o lexer sempre consome o lexema mais
  longo possível. Assim, `whilex` é um identificador e `<=` é um único token.
- **Reservadas por tabela:** a palavra é lida inteira como identificador e só
  então comparada à tabela de reservadas.
- **Erro léxico:** qualquer caractere fora do alfabeto acima (por exemplo `@`,
  `$`, `#`, `&`, `"`) gera erro léxico, reportado como `linha:coluna`.

## 3. Tipos

| Tipo | Valores | Literais |
|---|---|---|
| `int` | inteiros | `0`, `42`, `1000` |
| `bool` | verdadeiro ou falso | `true`, `false` |

A MiniLang é **fortemente tipada**. Não existe conversão implícita entre `int` e
`bool`: `0` não é falso e `true` não vale 1.

## 4. Comandos

| Comando | Forma | Semântica |
|---|---|---|
| Declaração | `var nome: tipo = expr;` | Cria a variável no escopo atual. A inicialização é obrigatória |
| Atribuição | `nome = expr;` | Altera o valor de uma variável já declarada |
| Saída | `print(expr);` | Imprime o valor seguido de quebra de linha. `bool` sai como `true` ou `false` |
| Condicional | `if (c) { … } else { … }` | O `else` é opcional. As chaves são obrigatórias |
| Repetição | `while (c) { … }` | Repete o bloco enquanto `c` for `true`. As chaves são obrigatórias |
| Bloco | `{ … }` | Agrupa comandos e abre um novo escopo |

Como `if` e `while` sempre exigem `{ }`, não existe ambiguidade de *else*
pendente.

## 5. Operadores e precedência

Operadores em ordem **crescente** de precedência (do que liga mais fraco ao que
liga mais forte):

| Nível | Operadores | Associatividade | Tipos dos operandos | Resultado |
|---|---|---|---|---|
| 1 | `==` `!=` | não associativo | `int, int` ou `bool, bool` | `bool` |
| 1 | `<` `>` `<=` `>=` | não associativo | `int, int` | `bool` |
| 2 | `+` `-` | esquerda | `int, int` | `int` |
| 3 | `*` `/` | esquerda | `int, int` | `int` |
| 4 | `-` (unário) | direita (prefixo) | `int` | `int` |

- Os parênteses `( )` alteram a ordem de avaliação.
- Comparações **não são associativas**: `a < b < c` é erro sintático.
- `10 - 3 - 2` é avaliado como `(10 - 3) - 2 = 5`.
- `/` é divisão inteira truncada para zero, como em C: `-7 / 2 = -3`.
- Divisão por zero é erro em **tempo de execução**, reportado com a linha.

## 6. Escopo

- O programa inteiro é o escopo global (nível 0).
- Cada bloco `{ }`, inclusive o de `if`, `else` e `while`, abre um novo escopo.
- Uma variável é visível do ponto da sua declaração até o fim do bloco em que
  foi declarada, incluindo os blocos internos.
- **Redeclarar** um nome no mesmo escopo é erro.
- **Sombreamento é permitido:** declarar o mesmo nome em um escopo interno
  esconde a variável externa até o fim desse bloco.
- Na declaração `var x: int = expr;`, a expressão é avaliada **antes** de `x`
  existir. Logo, em `var x: int = x + 1;` o `x` da direita se refere a um `x`
  de escopo externo, ou é erro se não houver nenhum.

## 7. Regras semânticas

1. Toda variável é declarada antes do uso.
2. Não há redeclaração no mesmo escopo.
3. Em `var x: T = e;` e em `x = e;`, o tipo de `e` é igual ao tipo de `x`.
4. A condição de `if` e de `while` é do tipo `bool`.
5. Cada operador recebe os tipos da tabela da seção 5.

## 8. Mensagens de erro

O compilador reporta **todos** os erros encontrados em uma fase, e não só o
primeiro. Se houver erro, nenhuma fase seguinte é executada e o processo termina
com código de saída `1`.

| Fase | Formato |
|---|---|
| Léxica | `3:14: erro léxico: caractere inválido '@'` |
| Sintática | `2:1: erro sintático: esperado ';', encontrado 'print'` |
| Semântica | `linha 3: erro semântico: 'y' não foi declarada` |
| Execução | `linha 5: divisão por zero` |

## 9. Extensão opcional (fora do núcleo)

Proposta de operadores lógicos, para depois que o pipeline estiver completo:

| Operador | Tipos | Resultado | Precedência |
|---|---|---|---|
| `\|\|` | `bool, bool` | `bool` | abaixo da comparação (a mais fraca) |
| `&&` | `bool, bool` | `bool` | entre `\|\|` e a comparação |
| `!` | `bool` | `bool` | mesmo nível do `-` unário |

Assim, `!a || b && c` é lido como `(!a) || (b && c)`. Os dois operadores
binários seriam associativos à esquerda e avaliados em curto-circuito.
