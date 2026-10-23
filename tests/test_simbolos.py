from minilang.lexer import Lexer
from minilang.parser import Parser
from minilang.semantica import AnalisadorSemantico
from minilang.simbolos import TabelaSimbolos


def sem(fonte):
    arvore = Parser(Lexer(fonte).tokens()).programa()
    return AnalisadorSemantico().visitar(arvore)


# --- tabela isolada, sem AST --------------------------------------------

def test_escopos():
    ts = TabelaSimbolos()
    ts.declarar("x", "int", 1)
    ts.entrar_escopo()
    ts.declarar("x", "bool", 2)          # sombreia
    assert ts.buscar("x").tipo == "bool"
    ts.sair_escopo()
    assert ts.buscar("x").tipo == "int"
    assert ts.declarar("x", "int", 3) is None


def test_atributos_do_simbolo():
    ts = TabelaSimbolos()
    ts.entrar_escopo()
    s = ts.declarar("y", "int", 3)
    assert (s.nome, s.tipo, s.categoria, s.linha, s.nivel) == (
        "y", "int", "variavel", 3, 1)


def test_busca_atravessa_escopos():
    ts = TabelaSimbolos()
    ts.declarar("g", "int", 1)
    ts.entrar_escopo()
    ts.entrar_escopo()
    assert ts.buscar("g").nivel == 0


def test_saida_de_escopo_remove_nomes():
    ts = TabelaSimbolos()
    ts.entrar_escopo()
    ts.declarar("t", "int", 1)
    ts.sair_escopo()
    assert ts.buscar("t") is None


def test_nao_declarada():
    assert TabelaSimbolos().buscar("nada") is None


# --- analisador sobre a AST -----------------------------------------------

def test_programa_valido_sem_erros():
    assert sem("var x: int = 1; { var y: int = x; print(y); }") == []


def test_fora_do_escopo():
    erros = sem("{ var y: int = 1; } print(y);")
    assert erros == [
        "linha 1: erro semântico: 'y' não foi declarada"]


def test_redeclaracao_no_mesmo_escopo():
    assert sem("var a: int = 1;\nvar a: int = 2;") == [
        "linha 2: erro semântico: 'a' já declarada neste escopo"]


def test_sombreamento_e_permitido():
    assert sem("var x: int = 1; { var x: bool = true; }") == []


def test_atribuicao_a_nao_declarada():
    assert sem("x = 1;") == [
        "linha 1: erro semântico: 'x' não foi declarada"]


def test_expressao_visitada_antes_de_declarar():
    assert sem("var x: int = x;") == [
        "linha 1: erro semântico: 'x' não foi declarada"]
    # com um x externo, o da direita é o externo: sem erro
    assert sem("var x: int = 1; { var x: int = x; }") == []


def test_bloco_de_if_e_while_abre_escopo():
    erros = sem("if (true) { var a: int = 1; }\n"
                "while (false) { var b: int = 2; }\n"
                "print(a); print(b);")
    assert erros == [
        "linha 3: erro semântico: 'a' não foi declarada",
        "linha 3: erro semântico: 'b' não foi declarada"]
