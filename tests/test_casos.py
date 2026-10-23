import pathlib
import re

import pytest

from minilang.lexer import Lexer
from minilang.parser import ErroSintatico, Parser
from minilang.semantica import AnalisadorSemantico

CASOS = pathlib.Path(__file__).parent / "casos"
EXEMPLOS = pathlib.Path(__file__).parent.parent / "exemplos"


def parse(fonte):
    lexer = Lexer(fonte)
    tokens = lexer.tokens()
    assert lexer.erros == []        # os casos testam o parser, não o lexer
    return Parser(tokens).programa()


def erros_esperados(fonte):
    """Linhas '// ERRO: <mensagem>' do início do arquivo, na ordem."""
    esperados = []
    for linha in fonte.splitlines():
        if not linha.startswith("// ERRO: "):
            break
        esperados.append(linha.removeprefix("// ERRO: "))
    return esperados


def arquivos(pasta):
    return pytest.mark.parametrize(
        "arq", sorted(pasta.glob("*.mini")), ids=lambda p: p.stem)


@arquivos(CASOS / "validos")
def test_validos(arq):
    arvore = parse(arq.read_text(encoding="utf-8"))  # não pode lançar exceção
    assert AnalisadorSemantico().visitar(arvore) == []


@arquivos(CASOS / "invalidos")
def test_invalidos(arq):
    fonte = arq.read_text(encoding="utf-8")
    esperado, = erros_esperados(fonte)      # um único erro por arquivo
    with pytest.raises(ErroSintatico, match=re.escape(esperado)):
        parse(fonte)


@arquivos(CASOS / "semanticos")
def test_semanticos(arq):
    fonte = arq.read_text(encoding="utf-8")
    esperados = erros_esperados(fonte)
    assert esperados, "o caso precisa anotar ao menos um '// ERRO:'"
    assert AnalisadorSemantico().visitar(parse(fonte)) == esperados


@pytest.mark.parametrize("nome", ["fatorial", "if_else", "escopos"])
def test_exemplos_validos(nome):
    arvore = parse((EXEMPLOS / f"{nome}.mini").read_text(encoding="utf-8"))
    assert AnalisadorSemantico().visitar(arvore) == []
