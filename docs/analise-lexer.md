# Análise de um lexer didático

**Projeto analisado:** jlox, o interpretador em Java do livro *Crafting
Interpreters*, de Robert Nystrom
([munificent/craftinginterpreters](https://github.com/munificent/craftinginterpreters))

**Arquivo:** `java/com/craftinginterpreters/lox/Scanner.java`, com cerca de 240
linhas

## 1. Onde está o laço principal do scanner?

Em `scanTokens()`. O laço roda `while (!isAtEnd())`, marca o início do lexema
com `start = current` e chama `scanToken()`, que reconhece **um** token por
chamada. Quando a entrada acaba, o laço adiciona o token `EOF`.

`scanToken()` consome um caractere com `advance()` e decide o que fazer com um
grande `switch (c)`. Os casos de um caractere, como `(`, `;` e `+`, viram token
na hora. Números e identificadores vão para o `default`, que chama `number()` ou
`identifier()`.

## 2. Como diferencia reservada de identificador?

Ele usa uma **tabela de busca**, a mesma estratégia da MiniLang. Um
`Map<String, TokenType> keywords` estático é preenchido no bloco `static`.
`identifier()` lê a palavra inteira (`while (isAlphaNumeric(peek()))`) e só
depois consulta o mapa: se `keywords.get(text)` devolve `null`, o token é
`IDENTIFIER`.

Como a palavra é lida inteira antes da consulta, `orchid` vira identificador, e
não `or` seguido de `chid`. É a regra do maior casamento.

## 3. Como reconhece operadores de 2 caracteres?

Com o auxiliar `match(expected)`: ele olha o próximo caractere e só o consome se
for o esperado. No `switch`, cada operador que pode ter 2 caracteres faz:

```java
case '<': addToken(match('=') ? LESS_EQUAL : LESS); break;
```

O comentário `//` é tratado do mesmo jeito: o `case '/'` usa `match('/')` para
decidir entre comentário e divisão.

## 4. Ao achar caractere inválido: para ou continua?

**Continua.** O `default` chama `Lox.error(line, "Unexpected character.")`, que
imprime a mensagem e liga a flag `hadError`. O caractere já foi consumido pelo
`advance()`, então o laço segue para o próximo lexema. Quem decide parar é a
classe `Lox`: se `hadError` estiver ligada, o programa não é executado e
`runFile` termina com código de saída 65.

O livro observa que o caractere inválido é descartado, mas o scanner continua
para que o usuário veja **todos** os erros de uma vez. É o modo pânico que
adotamos.

Uma string sem fechamento (`"Unterminated string."`) segue a mesma lógica.

## 5. Que posição o token guarda (linha? coluna?)

**Só a linha.** O campo `line` é incrementado quando aparece um `\n`, tanto no
`switch` quanto dentro de `string()` para strings de várias linhas. O `Token`
recebe `(type, lexeme, literal, line)`. Não há coluna, então as mensagens dizem
`[line 3] Error: Unexpected character.`, sem indicar o ponto exato.

## 6. Uma ideia que vamos copiar e por quê

**Separar a detecção do erro da decisão de parar.** O jlox anota o erro e
continua, e só quem chamou o scanner decide se o programa segue. Fizemos o mesmo:
o `Lexer` acumula as mensagens em `self.erros` e o CLI (`__main__.py`) decide
imprimir todas em `stderr` e sair com código 1. Com isso o lexer fica testável
sem capturar a saída: o teste só olha a lista.

O que fizemos **diferente**:

- **Guardamos a coluna**, além da linha. Uma mensagem como `3:14` aponta
  exatamente o caractere, e o jlox não consegue fazer isso.
- **Operadores de 2 caracteres por tabela** (`OPERADORES_DUPLOS`) em vez de
  `match()` caso a caso. A tabela é testada antes da de 1 caractere, o que
  garante o maior casamento sem um `case` para cada operador.
