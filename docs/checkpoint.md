# Checkpoint de 25/09: lexer, parser e AST

Tag: `v0.2-checkpoint`

## Autoavaliação dos 8 critérios

| # | Critério | Evidência | Situação |
|---|---|---|---|
| 1 | Lexer completo | `--tokens` reconhece as 9 palavras reservadas, identificadores, números, os 10 operadores e os 6 delimitadores da especificação. Testes `test_todas_as_reservadas`, `test_operadores_de_um_caractere`, `test_operadores_de_dois_caracteres` e `test_delimitadores` | ☑ ok |
| 2 | Erros léxicos | Mensagens `linha:coluna: erro léxico: caractere inválido 'c'`. O lexer descarta o caractere e continua, e o CLI lista todos os erros em `stderr` e sai com `1`. São 6 testes de erro em `tests/test_lexer.py` | ☑ ok |
| 3 | Parser completo | Os 10 programas de `tests/casos/validos/` e os 3 válidos de `exemplos/` geram AST (`test_validos`) | ☑ ok |
| 4 | Erros sintáticos | Os 12 programas de `tests/casos/invalidos/` falham com a mensagem **e a posição** anotadas na 1ª linha (`test_invalidos`) | ☑ ok |
| 5 | Precedência e associatividade | `test_precedencia` (`1+2*3`), `test_associatividade_esquerda` (`10-3-2`), além de testes para `/`, `-` unário, parênteses e comparação não associativa | ☑ ok |
| 6 | Testes automatizados | `pytest -q` dá **59 passed**, e também passa em um clone limpo do GitHub | ☑ ok |
| 7 | Repositório | Um commit por etapa e as tags `v0.0-spec`, `v0.1-lexer` e `v0.2-checkpoint` publicadas. Porém todos os commits são de um único autor e foram feitos em 23/10, depois das datas das aulas | ☐ parcial |
| 8 | Documentação | README com instalação, execução, testes e saídas de exemplo; `especificacao.md`, `gramatica.md` e `analise-lexer.md` atualizados | ☑ ok |

**Sobre o critério 7:** o histórico mostra a ordem certa das etapas, mas não um
ritmo de entregas ao longo do semestre. Se o trabalho for em grupo, cada
membro precisa ter commits próprios a partir daqui. Daqui em diante, o ideal é
fazer commits no dia de cada aula (TAC em 30/10, VM em 06/11, otimização em
13/11).

## Problemas comuns (slide 5) conferidos

| Sintoma do slide | Situação na nossa implementação |
|---|---|
| Parser entra em laço infinito | Todo caminho consome um token ou lança `ErroSintatico`. Entradas como `x = ;`, `}`, `if (` e `while (x) {` terminam com erro |
| `10 - 3 - 2` resulta em `10-(3-2)` | `soma` e `termo` usam `while`. Coberto por `test_associatividade_esquerda` |
| `RecursionError` em `soma` | Não há recursão à esquerda. Uma soma com 3000 termos é analisada sem erro |
| `whilex` vira `WHILE` + `x` | A palavra é lida inteira antes de consultar `RESERVADAS` (`test_reservada_vs_identificador`) |
| `<=` vira `<` e `=` | Os operadores de 2 caracteres são testados primeiro (`test_operadores_de_dois_caracteres`) |
| Coluna errada após quebra de linha | `avancar()` faz `linha += 1` e `coluna = 1` no `\n` (`test_posicao`) |
| `x = 1; }` é aceito sem erro | `programa()` repete até o `EOF`. A saída é `1:8: erro sintático: comando inesperado, encontrado '}'` (caso `chave_sobrando`) |

Uma limitação conhecida, que é natural em um parser recursivo descendente: uma
expressão com milhares de parênteses ou de `-` unários aninhados estoura o
limite de recursão do Python. Isso não acontece em programas reais.

## Roteiro da demonstração (3 min)

Rodar na raiz do repositório:

```
$ git log --oneline | head -5
61992e8 parser e AST
77a2b2a Gramática final e banco de casos de teste
ffdb458 Erros léxicos com recuperação e análise do lexer do jlox
b3af56d lexer inicial
b1b4ce8 Especificação inicial da MiniLang

$ python -m pytest -q
59 passed

$ python -m minilang exemplos/fatorial.mini --tokens
2:1   VAR          'var'
2:5   ID           'n'
2:6   DOIS_PONTOS  ':'
2:8   INT          'int'
2:12  ATRIB        '='
2:14  NUM          '5'
2:15  PONTO_VIRG   ';'
...                                 (56 tokens, terminando em 13:1 EOF)

$ python -m minilang exemplos/fatorial.mini --ast
Programa
├── Decl n: int
│   └── Num 5
...

$ python -m minilang exemplos/erro_lexico.mini
3:7: erro léxico: caractere inválido '@'
5:18: erro léxico: caractere inválido '$'

$ python -m minilang exemplos/erro_sintatico.mini
3:1: erro sintático: esperado ';', encontrado 'print'
```

**O que falar em cada passo:**

1. **`git log`**: um commit por etapa, na ordem das aulas.
2. **`pytest`**: testes do lexer, do parser e o banco de 22 casos (10 válidos e
   12 inválidos com a mensagem esperada).
3. **`--tokens`**: cada token tem tipo, lexema, linha e coluna. Comentários e
   espaços não geram token.
4. **`--ast`**: a precedência está na forma da árvore. No `If`, os papéis
   `cond`, `então` e `senão` aparecem rotulados.
5. **Erro léxico**: dois erros no mesmo arquivo, reportados de uma vez (modo
   pânico). Código de saída 1.
6. **Erro sintático**: aponta a linha 3 porque o `;` faltou no fim da linha 2
   e o parser só percebe ao ver o `print`, como fazem GCC e Clang.
