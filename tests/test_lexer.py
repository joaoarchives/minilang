from minilang.lexer import Lexer
from minilang.tokens import TipoToken as T


def tipos(fonte):
    return [t.tipo for t in Lexer(fonte).tokens()]


def test_declaracao():
    assert tipos("var x: int = 10;") == [
        T.VAR, T.ID, T.DOIS_PONTOS, T.INT,
        T.ATRIB, T.NUM, T.PONTO_VIRG, T.EOF]


def test_todas_as_reservadas():
    fonte = "var int bool true false if else while print"
    assert tipos(fonte)[:-1] == [
        T.VAR, T.INT, T.BOOL, T.TRUE, T.FALSE,
        T.IF, T.ELSE, T.WHILE, T.PRINT]


def test_reservada_vs_identificador():
    assert tipos("while whilex")[:-1] == [T.WHILE, T.ID]


def test_identificadores():
    toks = Lexer("x _tmp contador2 Var").tokens()[:-1]
    assert [t.tipo for t in toks] == [T.ID] * 4
    assert [t.lexema for t in toks] == ["x", "_tmp", "contador2", "Var"]


def test_numero():
    t = Lexer("12345").tokens()[0]
    assert (t.tipo, t.lexema) == (T.NUM, "12345")


def test_operadores_de_um_caractere():
    assert tipos("+ - * / = < >")[:-1] == [
        T.MAIS, T.MENOS, T.VEZES, T.DIV, T.ATRIB, T.MENOR, T.MAIOR]


def test_operadores_de_dois_caracteres():
    assert tipos("<= >= == !=")[:-1] == [
        T.MENOR_IGUAL, T.MAIOR_IGUAL, T.IGUAL, T.DIFERENTE]


def test_maior_casamento_sem_espacos():
    assert tipos("a<=b==c")[:-1] == [
        T.ID, T.MENOR_IGUAL, T.ID, T.IGUAL, T.ID]


def test_delimitadores():
    assert tipos("( ) { } : ;")[:-1] == [
        T.ABRE_PAR, T.FECHA_PAR, T.ABRE_CHAVE, T.FECHA_CHAVE,
        T.DOIS_PONTOS, T.PONTO_VIRG]


def test_comentario_e_espacos_descartados():
    assert tipos("// só comentário\n\t x // outro\n") == [T.ID, T.EOF]


def test_divisao_nao_e_comentario():
    assert tipos("a / b")[:-1] == [T.ID, T.DIV, T.ID]


def test_posicao():
    t = Lexer("var\n  x").tokens()[1]
    assert (t.linha, t.coluna) == (2, 3)


def test_posicao_apos_comentario():
    t = Lexer("// linha 1\n// linha 2\n   y").tokens()[0]
    assert (t.linha, t.coluna) == (3, 4)


def test_entrada_vazia_gera_so_eof():
    toks = Lexer("").tokens()
    assert [t.tipo for t in toks] == [T.EOF]
    assert (toks[0].linha, toks[0].coluna) == (1, 1)
