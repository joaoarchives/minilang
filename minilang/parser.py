"""Parser recursivo descendente da MiniLang.

Cada regra de docs/gramatica.md vira um método. A alternativa é escolhida
olhando um único token (a gramática é LL(1)).
"""

from . import ast as A
from .tokens import TipoToken as T


class ErroSintatico(Exception):
    pass


COMPARACOES = (T.IGUAL, T.DIFERENTE, T.MENOR, T.MAIOR,
               T.MENOR_IGUAL, T.MAIOR_IGUAL)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # --- utilitários -------------------------------------------------

    def atual(self):
        return self.tokens[self.pos]

    def verificar(self, *tipos):
        return self.atual().tipo in tipos

    def consumir(self):
        tok = self.atual()
        if tok.tipo != T.EOF:           # nunca passa do EOF
            self.pos += 1
        return tok

    def erro(self, msg):
        t = self.atual()
        return ErroSintatico(
            f"{t.linha}:{t.coluna}: erro sintático: {msg}, "
            f"encontrado '{t.lexema or 'EOF'}'")

    def esperar(self, tipo, msg):
        if self.verificar(tipo):
            return self.consumir()
        raise self.erro(msg)

    # --- comandos ----------------------------------------------------

    def programa(self):             # programa → { comando } EOF
        comandos = []
        while not self.verificar(T.EOF):
            comandos.append(self.comando())
        return A.Programa(comandos, linha=1)

    def comando(self):              # escolhe pela FIRST
        if self.verificar(T.VAR):        return self.decl()
        if self.verificar(T.ID):         return self.atrib()
        if self.verificar(T.PRINT):      return self.print_()
        if self.verificar(T.IF):         return self.if_()
        if self.verificar(T.WHILE):      return self.while_()
        if self.verificar(T.ABRE_CHAVE): return self.bloco()
        raise self.erro("comando inesperado")

    def decl(self):                 # "var" ID ":" tipo "=" expr ";"
        ini = self.consumir()
        nome = self.esperar(T.ID, "esperado identificador")
        self.esperar(T.DOIS_PONTOS, "esperado ':'")
        tipo = self.tipo()
        self.esperar(T.ATRIB, "esperado '='")
        expr = self.expr()
        self.esperar(T.PONTO_VIRG, "esperado ';'")
        return A.Decl(nome.lexema, tipo, expr, linha=ini.linha)

    def tipo(self):                 # "int" | "bool"
        if self.verificar(T.INT, T.BOOL):
            return self.consumir().lexema
        raise self.erro("esperado tipo ('int' ou 'bool')")

    def atrib(self):                # ID "=" expr ";"
        nome = self.consumir()
        self.esperar(T.ATRIB, "esperado '='")
        expr = self.expr()
        self.esperar(T.PONTO_VIRG, "esperado ';'")
        return A.Atrib(nome.lexema, expr, linha=nome.linha)

    def print_(self):               # "print" "(" expr ")" ";"
        ini = self.consumir()
        self.esperar(T.ABRE_PAR, "esperado '('")
        expr = self.expr()
        self.esperar(T.FECHA_PAR, "esperado ')'")
        self.esperar(T.PONTO_VIRG, "esperado ';'")
        return A.Print(expr, linha=ini.linha)

    def condicao(self):             # "(" expr ")", comum a if e while
        self.esperar(T.ABRE_PAR, "esperado '('")
        cond = self.expr()
        self.esperar(T.FECHA_PAR, "esperado ')'")
        return cond

    def if_(self):                  # "if" "(" expr ")" bloco [ "else" bloco ]
        ini = self.consumir()
        cond = self.condicao()
        entao = self.bloco()
        senao = None
        if self.verificar(T.ELSE):
            self.consumir()
            senao = self.bloco()
        return A.If(cond, entao, senao, linha=ini.linha)

    def while_(self):               # "while" "(" expr ")" bloco
        ini = self.consumir()
        cond = self.condicao()
        corpo = self.bloco()
        return A.While(cond, corpo, linha=ini.linha)

    def bloco(self):                # "{" { comando } "}"
        ini = self.esperar(T.ABRE_CHAVE, "esperado '{'")
        comandos = []
        while not self.verificar(T.FECHA_CHAVE, T.EOF):
            comandos.append(self.comando())
        self.esperar(T.FECHA_CHAVE, "esperado '}'")
        return A.Bloco(comandos, linha=ini.linha)

    # --- expressões --------------------------------------------------

    def expr(self):                 # soma [ op_comparação soma ]
        esq = self.soma()
        if self.verificar(*COMPARACOES):        # [ ]: não associativo
            op = self.consumir()
            esq = A.Binario(op.lexema, esq, self.soma(), linha=op.linha)
        return esq

    def soma(self):                 # termo { ("+"|"-") termo }
        esq = self.termo()
        while self.verificar(T.MAIS, T.MENOS):
            op = self.consumir()
            esq = A.Binario(op.lexema, esq, self.termo(),
                            linha=op.linha)
        return esq                  # o laço gera associatividade à esquerda

    def termo(self):                # fator { ("*"|"/") fator }
        esq = self.fator()
        while self.verificar(T.VEZES, T.DIV):
            op = self.consumir()
            esq = A.Binario(op.lexema, esq, self.fator(),
                            linha=op.linha)
        return esq

    def fator(self):
        t = self.atual()
        if self.verificar(T.NUM):
            self.consumir()
            return A.Num(int(t.lexema), linha=t.linha)
        if self.verificar(T.TRUE, T.FALSE):
            self.consumir()
            return A.Bool(t.tipo == T.TRUE, linha=t.linha)
        if self.verificar(T.ID):
            self.consumir()
            return A.Var(t.lexema, linha=t.linha)
        if self.verificar(T.ABRE_PAR):          # "(" expr ")"
            self.consumir()
            e = self.expr()
            self.esperar(T.FECHA_PAR, "esperado ')'")
            return e
        if self.verificar(T.MENOS):             # "-" fator
            self.consumir()
            return A.Unario("-", self.fator(), linha=t.linha)
        raise self.erro("expressão esperada")
