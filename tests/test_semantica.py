import pytest

from minilang.lexer import Lexer
from minilang.parser import Parser
from minilang.semantica import REGRAS, AnalisadorSemantico


def analisar(fonte):
    arvore = Parser(Lexer(fonte).tokens()).programa()
    erros = AnalisadorSemantico().visitar(arvore)
    return arvore, erros


def sem(fonte):
    return analisar(fonte)[1]


# --- tabela de tipos dos operadores ------------------------------------

@pytest.mark.parametrize("op", ["+", "-", "*", "/"])
def test_aritmeticos(op):
    assert REGRAS[(op, "int", "int")] == "int"
    assert sem(f"var r: int = 6 {op} 2;") == []
    assert sem(f"var r: int = true {op} 2;") == [
        f"linha 1: erro semântico: operador '{op}' inválido para bool e int"]


@pytest.mark.parametrize("op", ["<", ">", "<=", ">="])
def test_relacionais(op):
    assert sem(f"var r: bool = 1 {op} 2;") == []
    assert sem(f"var r: bool = false {op} true;") == [
        f"linha 1: erro semântico: operador '{op}' inválido para bool e bool"]


@pytest.mark.parametrize("op", ["==", "!="])
def test_igualdade(op):
    assert sem(f"var r: bool = 1 {op} 2;") == []
    assert sem(f"var r: bool = true {op} false;") == []
    assert sem(f"var r: bool = 1 {op} true;") == [
        f"linha 1: erro semântico: operador '{op}' inválido para int e bool"]


def test_unario():
    assert sem("var r: int = -5;") == []
    assert sem("var r: int = -false;") == [
        "linha 1: erro semântico: operador '-' inválido para bool"]


# --- comandos ----------------------------------------------------------

def test_declaracao_com_tipo_errado():
    assert sem("var b: bool = 1 + 2;") == [
        "linha 1: erro semântico: 'b' é bool, mas recebe int"]


def test_atribuicao_com_tipo_errado():
    assert sem("var x: int = 0; x = true;") == [
        "linha 1: erro semântico: 'x' é int, mas recebe bool"]


def test_condicoes():
    assert sem("if (1 < 2) { } while (false) { }") == []
    assert sem("if (1) { }") == [
        "linha 1: erro semântico: condição deve ser bool, encontrado int"]
    assert sem("while (0) { }") == [
        "linha 1: erro semântico: condição deve ser bool, encontrado int"]


def test_print_aceita_int_e_bool():
    assert sem("print(1); print(true); print(1 < 2);") == []


def test_sem_conversao_implicita():
    assert sem("var b: bool = 0;") == [
        "linha 1: erro semântico: 'b' é bool, mas recebe int"]


# --- erros em cascata ----------------------------------------------------

def test_sem_cascata_em_expressao():
    assert sem("print(z + 1 + 2);") == [
        "linha 1: erro semântico: 'z' não foi declarada"]


def test_sem_cascata_na_declaracao():
    # a expressão já falhou: não reclama também do tipo de 'b'
    assert sem("var b: bool = true + 1;") == [
        "linha 1: erro semântico: operador '+' inválido para bool e int"]


def test_sem_cascata_na_condicao():
    assert sem("if (z) { }") == [
        "linha 1: erro semântico: 'z' não foi declarada"]


def test_variavel_com_erro_ainda_e_declarada():
    # 'b' entra na tabela mesmo com o tipo errado: o uso seguinte não
    # gera um segundo erro de "não foi declarada"
    assert sem("var b: bool = 1;\nprint(b);") == [
        "linha 1: erro semântico: 'b' é bool, mas recebe int"]


def test_todos_os_erros_de_uma_vez():
    erros = sem("var x: int = 1;\nvar b: bool = x + 1;\nif (x) { y = 2; }")
    assert erros == [
        "linha 2: erro semântico: 'b' é bool, mas recebe int",
        "linha 3: erro semântico: condição deve ser bool, encontrado int",
        "linha 3: erro semântico: 'y' não foi declarada"]


# --- anotação da AST -----------------------------------------------------

def test_expressoes_anotadas_com_tipo():
    arvore, erros = analisar("var x: int = 1; var b: bool = x + 2 < 3;")
    assert erros == []
    cmp = arvore.comandos[1].expr
    assert cmp.tipo == "bool"
    assert cmp.esq.tipo == "int"            # x + 2
    assert cmp.esq.esq.tipo == "int"        # x
    assert cmp.dir.tipo == "int"            # 3


def test_var_anotada_com_tipo_do_escopo_certo():
    arvore, _ = analisar("var x: int = 1; { var x: bool = true; print(x); }")
    prt = arvore.comandos[1].comandos[1]
    assert prt.expr.tipo == "bool"
