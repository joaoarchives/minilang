import pytest

from minilang import ast as A
from minilang.ast import formatar
from minilang.lexer import Lexer
from minilang.parser import ErroSintatico, Parser


def parse(fonte):
    return Parser(Lexer(fonte).tokens()).programa()


def expr(fonte):
    """Expressão do primeiro comando (uma atribuição)."""
    return parse(f"x = {fonte};").comandos[0].expr


# --- expressões --------------------------------------------------------

def test_precedencia():
    e = parse("x = 1 + 2 * 3;").comandos[0].expr
    assert e.op == "+" and e.dir.op == "*"


def test_associatividade_esquerda():
    e = parse("x = 10 - 3 - 2;").comandos[0].expr
    assert e.op == "-" and e.esq.op == "-"


def test_associatividade_esquerda_multiplicativa():
    e = expr("100 / 10 / 5")
    assert e == A.Binario("/", A.Binario("/", A.Num(100), A.Num(10)),
                          A.Num(5))


def test_parenteses_mudam_a_precedencia():
    e = expr("(1 + 2) * 3")
    assert e.op == "*" and e.esq.op == "+"


def test_menos_unario_liga_mais_forte():
    assert expr("-1 * 2") == A.Binario(
        "*", A.Unario("-", A.Num(1)), A.Num(2))


def test_menos_unario_encadeado():
    assert expr("- -5") == A.Unario("-", A.Unario("-", A.Num(5)))


def test_comparacao_abaixo_da_soma():
    e = expr("a + 1 < b * 2")
    assert e.op == "<" and e.esq.op == "+" and e.dir.op == "*"


def test_literais():
    assert expr("true") == A.Bool(True)
    assert expr("false") == A.Bool(False)
    assert expr("42") == A.Num(42)
    assert expr("y") == A.Var("y")


# --- comandos ----------------------------------------------------------

def test_ast_completa():
    assert parse("var x: int = 1; x = x + 2 * 3;") == A.Programa([
        A.Decl("x", "int", A.Num(1)),
        A.Atrib("x", A.Binario("+", A.Var("x"),
                               A.Binario("*", A.Num(2), A.Num(3))))])


def test_if_com_e_sem_else():
    p = parse("if (a) { print(1); } else { print(2); } if (b) { }")
    com_else, sem_else = p.comandos
    assert com_else.senao == A.Bloco([A.Print(A.Num(2))])
    assert sem_else == A.If(A.Var("b"), A.Bloco([]), None)


def test_while_e_bloco_aninhado():
    p = parse("while (i < 3) { { i = i + 1; } }")
    w = p.comandos[0]
    assert isinstance(w, A.While) and w.cond.op == "<"
    assert isinstance(w.corpo.comandos[0], A.Bloco)


def test_programa_vazio():
    assert parse("// nada aqui\n") == A.Programa([])


def test_linha_nos_nos():
    p = parse("var x: int = 1;\n\nprint(\n  x + 1);")
    decl, prt = p.comandos
    assert decl.linha == 1
    assert prt.linha == 3
    assert prt.expr.linha == 4          # linha do operador '+'


# --- erros -------------------------------------------------------------

def test_falta_ponto_virgula():
    with pytest.raises(ErroSintatico, match="esperado ';'"):
        parse("var x: int = 1")


def test_erro_aponta_o_token_seguinte():
    with pytest.raises(ErroSintatico) as e:
        parse("var x: int = 1\nprint(x);")
    assert str(e.value) == (
        "2:1: erro sintático: esperado ';', encontrado 'print'")


def test_comparacao_nao_associativa():
    with pytest.raises(ErroSintatico, match="encontrado '<'"):
        parse("x = a < b < c;")


# --- impressão indentada (--ast) ---------------------------------------

def test_formatar():
    p = parse("var x: int = 1; x = x + 2 * 3;")
    assert formatar(p) == "\n".join([
        "Programa",
        "├── Decl x: int",
        "│   └── Num 1",
        "└── Atrib x",
        "    └── Binario +",
        "        ├── Var x",
        "        └── Binario *",
        "            ├── Num 2",
        "            └── Num 3",
    ])
