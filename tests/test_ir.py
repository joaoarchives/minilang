import pathlib

import pytest

from minilang.ir import GeradorTAC, Instr
from minilang.lexer import Lexer
from minilang.parser import Parser
from minilang.semantica import AnalisadorSemantico

EXEMPLOS = pathlib.Path(__file__).parent.parent / "exemplos"
CASOS = pathlib.Path(__file__).parent / "casos"


def parse(fonte):
    return Parser(Lexer(fonte).tokens()).programa()


def gerar(fonte):
    arv = parse(fonte)
    assert AnalisadorSemantico().visitar(arv) == []
    return GeradorTAC().visitar(arv)


def tac(fonte):
    return [str(i) for i in gerar(fonte)]


# --- expressões --------------------------------------------------------

def test_expressao():
    assert tac("var x: int = 1 + 2 * 3;") == [
        "    t1 = 2 * 3",
        "    t2 = 1 + t1",
        "    x = t2"]


def test_constante_e_variavel_sem_temporario():
    assert tac("var n: int = 5; var m: int = n; var b: bool = true;") == [
        "    n = 5",
        "    m = n",
        "    b = true"]


def test_associatividade_esquerda():
    assert tac("var x: int = 10 - 3 - 2;") == [
        "    t1 = 10 - 3",
        "    t2 = t1 - 2",
        "    x = t2"]


def test_unario():
    assert tac("var a: int = 1; var b: int = -a; var c: int = - -2;") == [
        "    a = 1",
        "    t1 = -a",
        "    b = t1",
        "    t2 = -2",
        "    t3 = -t2",
        "    c = t3"]


def test_comparacoes_de_int_e_bool():
    assert tac("var b: bool = (1 < 2) == true;") == [
        "    t1 = 1 < 2",
        "    t2 = t1 == true",
        "    b = t2"]


def test_print():
    assert tac("var x: int = 4; print(x * 2); print(false);") == [
        "    x = 4",
        "    t1 = x * 2",
        "    print t1",
        "    print false"]


# --- controle de fluxo -------------------------------------------------

def test_while_tem_rotulos_e_saltos():
    cod = tac("var i: int = 0; while (i < 3) { i = i + 1; }")
    assert "L1:" in cod and "    goto L1" in cod
    assert "    ifFalse t1 goto L2" in cod


def test_while_completo():
    assert tac("var i: int = 0; while (i < 3) { i = i + 1; }") == [
        "    i = 0",
        "L1:",
        "    t1 = i < 3",
        "    ifFalse t1 goto L2",
        "    t2 = i + 1",
        "    i = t2",
        "    goto L1",
        "L2:"]


def test_if_else():
    assert tac("var x: int = 3; "
               "if (x > 5) { print(1); } else { print(0); }") == [
        "    x = 3",
        "    t1 = x > 5",
        "    ifFalse t1 goto L1",
        "    print 1",
        "    goto L2",
        "L1:",
        "    print 0",
        "L2:"]


def test_if_sem_else():
    assert tac("var x: int = 3; if (x > 5) { print(1); }") == [
        "    x = 3",
        "    t1 = x > 5",
        "    ifFalse t1 goto L1",
        "    print 1",
        "    goto L2",          # sobra para o otimizador remover
        "L1:",
        "L2:"]


def test_condicao_variavel_bool_sem_temporario():
    assert tac("var ok: bool = true; while (ok) { ok = false; }") == [
        "    ok = true",
        "L1:",
        "    ifFalse ok goto L2",
        "    ok = false",
        "    goto L1",
        "L2:"]


def test_fatorial_igual_ao_slide():
    fonte = (EXEMPLOS / "fatorial.mini").read_text(encoding="utf-8")
    assert tac(fonte) == [
        "    n = 5",
        "    f = 1",
        "L1:",
        "    t1 = n > 0",
        "    ifFalse t1 goto L2",
        "    t2 = f * n",
        "    f = t2",
        "    t3 = n - 1",
        "    n = t3",
        "    goto L1",
        "L2:",
        "    t4 = f > 100",
        "    ifFalse t4 goto L3",
        "    print f",
        "    goto L4",
        "L3:",
        "    print 0",
        "L4:"]


# --- temporários, rótulos e nomes ---------------------------------------

@pytest.mark.parametrize("arq",
    sorted((CASOS / "validos").glob("*.mini")), ids=lambda p: p.stem)
def test_temporarios_e_rotulos_nunca_se_repetem(arq):
    cod = gerar(arq.read_text(encoding="utf-8"))
    destinos_temp = [i.dest for i in cod
                     if i.op not in ("=", "label", "goto", "iffalse", "print")]
    rotulos = [i.dest for i in cod if i.op == "label"]
    assert len(destinos_temp) == len(set(destinos_temp))
    assert len(rotulos) == len(set(rotulos))
    # todo salto aponta para um rótulo que existe
    alvos = {i.dest for i in cod if i.op in ("goto", "iffalse")}
    assert alvos <= set(rotulos)


def test_whiles_aninhados_tem_rotulos_diferentes():
    cod = tac("var i: int = 0; while (i < 2) { var j: int = 0; "
              "while (j < 2) { j = j + 1; } i = i + 1; }")
    assert [c for c in cod if c.endswith(":")] == ["L1:", "L3:", "L4:", "L2:"]


def test_sombreamento_ganha_nome_proprio():
    cod = tac("var x: int = 1; { var x: bool = true; print(x); } print(x);")
    assert cod == [
        "    x = 1",
        "    x.2 = true",
        "    print x.2",
        "    print x"]


def test_inicializacao_usa_o_nome_externo():
    assert tac("var x: int = 1; { var x: int = x + 1; print(x); }") == [
        "    x = 1",
        "    t1 = x + 1",
        "    x.2 = t1",
        "    print x.2"]


def test_temporario_nao_colide_com_variavel_do_programa():
    cod = tac("var t1: int = 2 * 3; var t2: int = t1 + 1;")
    assert cod == [
        "    t3 = 2 * 3",
        "    t1 = t3",
        "    t4 = t1 + 1",
        "    t2 = t4"]


# --- Instr ---------------------------------------------------------------

def test_instr_guarda_a_linha_do_fonte():
    cod = gerar("var z: int = 0;\nprint(\n  1 / z);")
    div = next(i for i in cod if i.op == "/")
    assert div.linha == 3


def test_formato_das_instrucoes():
    assert str(Instr("label", "L7")) == "L7:"
    assert str(Instr("=", "x", True)) == "    x = true"
    assert str(Instr("neg", "t1", "a")) == "    t1 = -a"
    assert str(Instr("goto", "L1")) == "    goto L1"
    assert str(Instr("iffalse", "L2", "t1")) == "    ifFalse t1 goto L2"
    assert str(Instr("print", None, 0)) == "    print 0"
    assert str(Instr("<=", "t3", "a", 10)) == "    t3 = a <= 10"
