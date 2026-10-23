"""Analisador semântico da MiniLang: escopos e verificação de tipos.

Regras (docs/especificacao.md, seção 7):
1. Toda variável é declarada antes do uso.
2. Não há redeclaração no mesmo escopo.
3. Em `var x: T = e;` e `x = e;`, o tipo de e é igual ao de x.
4. A condição de if e while é bool.
5. Cada operador recebe os tipos da tabela REGRAS.

Cada visitar_* de expressão devolve 'int', 'bool' ou None. None quer dizer
que um erro já foi reportado ali dentro, e quem recebe None não reporta de
novo (evita erros em cascata).
"""

from .ast import Visitor
from .simbolos import TabelaSimbolos

REGRAS = {}                     # (op, esq, dir) -> resultado
for op in "+-*/":
    REGRAS[(op, "int", "int")] = "int"
for op in ("<", ">", "<=", ">="):
    REGRAS[(op, "int", "int")] = "bool"
for op in ("==", "!="):
    REGRAS[(op, "int", "int")] = "bool"
    REGRAS[(op, "bool", "bool")] = "bool"

REGRAS_UNARIAS = {("-", "int"): "int"}


class AnalisadorSemantico(Visitor):
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros = []

    def erro(self, no, msg):
        self.erros.append(f"linha {no.linha}: erro semântico: {msg}")

    def checar_condicao(self, cond):
        t = self.visitar(cond)
        if t and t != "bool":
            self.erro(cond, f"condição deve ser bool, encontrado {t}")

    def checar_atribuicao(self, no, tipo_var, tipo_expr):
        if tipo_expr and tipo_expr != tipo_var:
            self.erro(no, f"'{no.nome}' é {tipo_var}, mas recebe {tipo_expr}")

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
        te = self.visitar(no.expr)          # antes de declarar!
        if self.tabela.declarar(no.nome, no.tipo, no.linha) is None:
            self.erro(no, f"'{no.nome}' já declarada neste escopo")
        self.checar_atribuicao(no, no.tipo, te)

    def visitar_Atrib(self, no):
        s = self.tabela.buscar(no.nome)
        if s is None:
            self.erro(no, f"'{no.nome}' não foi declarada")
        te = self.visitar(no.expr)
        if s is not None:
            self.checar_atribuicao(no, s.tipo, te)

    def visitar_Print(self, no):
        self.visitar(no.expr)               # int e bool podem ser impressos

    def visitar_If(self, no):
        self.checar_condicao(no.cond)
        self.visitar(no.entao)
        if no.senao is not None:
            self.visitar(no.senao)

    def visitar_While(self, no):
        self.checar_condicao(no.cond)
        self.visitar(no.corpo)

    # --- expressões: devolvem o tipo e anotam no.tipo ------------------

    def visitar_Num(self, no):
        no.tipo = "int"
        return no.tipo

    def visitar_Bool(self, no):
        no.tipo = "bool"
        return no.tipo

    def visitar_Var(self, no):
        s = self.tabela.buscar(no.nome)
        if s is None:
            self.erro(no, f"'{no.nome}' não foi declarada")
            return None
        no.tipo = s.tipo
        return no.tipo

    def visitar_Unario(self, no):
        t = self.visitar(no.expr)
        if t is None:
            return None                     # evita erro em cascata
        res = REGRAS_UNARIAS.get((no.op, t))
        if res is None:
            self.erro(no, f"operador '{no.op}' inválido para {t}")
        no.tipo = res
        return res

    def visitar_Binario(self, no):
        te, td = self.visitar(no.esq), self.visitar(no.dir)
        if te is None or td is None:
            return None                     # evita erro em cascata
        res = REGRAS.get((no.op, te, td))
        if res is None:
            self.erro(no, f"operador '{no.op}' inválido "
                          f"para {te} e {td}")
        no.tipo = res                       # anota a AST
        return res
