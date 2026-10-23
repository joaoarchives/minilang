import pathlib
import re

import pytest

from minilang.lexer import Lexer
from minilang.parser import ErroSintatico, Parser

CASOS = pathlib.Path(__file__).parent / "casos"


def parse(fonte):
    lexer = Lexer(fonte)
    tokens = lexer.tokens()
    assert lexer.erros == []        # os casos testam o parser, não o lexer
    return Parser(tokens).programa()


@pytest.mark.parametrize("arq",
    sorted((CASOS / "validos").glob("*.mini")), ids=lambda p: p.stem)
def test_validos(arq):
    parse(arq.read_text(encoding="utf-8"))      # não pode lançar exceção


@pytest.mark.parametrize("arq",
    sorted((CASOS / "invalidos").glob("*.mini")), ids=lambda p: p.stem)
def test_invalidos(arq):
    fonte = arq.read_text(encoding="utf-8")
    linha1 = fonte.splitlines()[0]
    assert linha1.startswith("// ERRO: ")
    esperado = linha1.removeprefix("// ERRO: ")
    with pytest.raises(ErroSintatico, match=re.escape(esperado)):
        parse(fonte)
