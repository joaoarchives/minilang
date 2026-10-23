"""Analisador semântico da MiniLang: declarações e escopos."""

from .ast import Visitor
from .simbolos import TabelaSimbolos


class AnalisadorSemantico(Visitor):
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros = []

    def erro(self, no, msg):
        self.erros.append(f"linha {no.linha}: erro semântico: {msg}")

    # --- comandos ----------------------------------------------------

    def visitar_Programa(self, no):
        for c in no.comandos:
            self.visitar(c)
        return self.erros

    def visitar_Bloco(self, no):
        self.tabela.entrar_escopo()
        for c in no.comandos:
            self.visitar(c)
        self.tabela.sair_escopo()

    def visitar_Decl(self, no):
        self.visitar(no.expr)      # antes de declarar!
        if self.tabela.declarar(no.nome, no.tipo, no.linha) is None:
            self.erro(no, f"'{no.nome}' já declarada neste escopo")

    def visitar_Atrib(self, no):
        if self.tabela.buscar(no.nome) is None:
            self.erro(no, f"'{no.nome}' não foi declarada")
        self.visitar(no.expr)

    def visitar_Print(self, no):
        self.visitar(no.expr)

    def visitar_If(self, no):
        self.visitar(no.cond)
        self.visitar(no.entao)
        if no.senao is not None:
            self.visitar(no.senao)

    def visitar_While(self, no):
        self.visitar(no.cond)
        self.visitar(no.corpo)

    # --- expressões --------------------------------------------------

    def visitar_Var(self, no):
        if self.tabela.buscar(no.nome) is None:
            self.erro(no, f"'{no.nome}' não foi declarada")

    def visitar_Binario(self, no):
        self.visitar(no.esq)
        self.visitar(no.dir)

    def visitar_Unario(self, no):
        self.visitar(no.expr)

    def visitar_Num(self, no):
        pass

    def visitar_Bool(self, no):
        pass
