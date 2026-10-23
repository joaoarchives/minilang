import argparse
import sys

from .ast import formatar
from .lexer import Lexer
from .parser import ErroSintatico, Parser


def imprimir_tokens(tokens):
    for t in tokens:
        pos = f"{t.linha}:{t.coluna}"
        print(f"{pos:<6}{t.tipo.name:<13}{t.lexema!r}")


def main():
    # acentos corretos nas mensagens, mesmo com saída redirecionada no Windows
    for fluxo in (sys.stdout, sys.stderr):
        fluxo.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(prog="python -m minilang",
                                 description="Compilador da MiniLang")
    ap.add_argument("arquivo", help="programa .mini")
    ap.add_argument("--tokens", action="store_true",
                    help="imprime a lista de tokens")
    ap.add_argument("--ast", action="store_true",
                    help="imprime a árvore sintática abstrata")
    args = ap.parse_args()

    with open(args.arquivo, encoding="utf-8") as f:
        fonte = f.read()

    lexer = Lexer(fonte)
    tokens = lexer.tokens()
    if lexer.erros:                 # todos os erros de uma vez, em stderr
        for msg in lexer.erros:
            print(msg, file=sys.stderr)
        sys.exit(1)
    if args.tokens:
        imprimir_tokens(tokens)

    try:
        arvore = Parser(tokens).programa()
    except ErroSintatico as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    if args.ast:
        print(formatar(arvore))


if __name__ == "__main__":
    main()
