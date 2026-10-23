"""Geração de código de três endereços (TAC) a partir da AST validada.

Formas do TAC:

    x = y                cópia (y é variável, temporário ou constante)
    t = a op b           operação binária: + - * / < > <= >= == !=
    t = -a               operação unária ('neg')
    goto L               salto incondicional
    ifFalse t goto L     salta se t for falso
    L:                   rótulo
    print a              saída

Endereços: uma constante é guardada como valor Python (int ou bool); uma
variável ou um temporário, como str com o nome.
"""

from dataclasses import dataclass
from typing import Optional

from . import ast as A
from .ast import Visitor


def fmt(x):
    """Endereço como texto: true/false, número ou nome."""
    if isinstance(x, bool):             # antes de int: bool é subclasse
        return "true" if x else "false"
    return str(x)


@dataclass
class Instr:
    op: str        # '=', '+', ..., 'neg', 'goto', 'iffalse', 'label', 'print'
    dest: Optional[str] = None
    a1: object = None
    a2: object = None
    linha: int = 0

    def __str__(self):
        if self.op == "label":
            return f"{self.dest}:"
        if self.op == "=":
            corpo = f"{self.dest} = {fmt(self.a1)}"
        elif self.op == "neg":
            corpo = f"{self.dest} = -{fmt(self.a1)}"
        elif self.op == "goto":
            corpo = f"goto {self.dest}"
        elif self.op == "iffalse":
            corpo = f"ifFalse {fmt(self.a1)} goto {self.dest}"
        elif self.op == "print":
            corpo = f"print {fmt(self.a1)}"
        else:                                           # binária
            corpo = f"{self.dest} = {fmt(self.a1)} {self.op} {fmt(self.a2)}"
        return "    " + corpo


def nomes_declarados(no):
    """Todos os nomes de variáveis declarados em qualquer ponto do programa."""
    if isinstance(no, A.Decl):
        yield no.nome
    elif isinstance(no, (A.Programa, A.Bloco)):
        for c in no.comandos:
            yield from nomes_declarados(c)
    elif isinstance(no, A.If):
        yield from nomes_declarados(no.entao)
        if no.senao is not None:
            yield from nomes_declarados(no.senao)
    elif isinstance(no, A.While):
        yield from nomes_declarados(no.corpo)


class GeradorTAC(Visitor):
    def __init__(self):
        self.codigo, self.nt, self.nl = [], 0, 0
        # O TAC tem uma memória plana, sem escopos. Para que uma variável
        # sombreada não sobrescreva a externa, cada nova declaração de um
        # nome já usado ganha um sufixo: x, x.2, x.3 ('.' não existe em
        # identificadores da MiniLang, então não há colisão).
        self.escopos = [{}]             # nome no fonte -> nome no TAC
        self.declaracoes = {}           # nome no fonte -> quantas até agora
        self.reservados = set()         # nomes do fonte: temporários evitam

    def novo_temp(self):
        while True:
            self.nt += 1
            t = f"t{self.nt}"
            if t not in self.reservados:    # ex.: o programa tem 'var t1'
                return t

    def novo_rotulo(self):
        self.nl += 1
        return f"L{self.nl}"

    def emitir(self, op, dest=None, a1=None, a2=None, linha=0):
        self.codigo.append(Instr(op, dest, a1, a2, linha))

    # --- nomes e escopos ---------------------------------------------

    def declarar(self, nome):
        n = self.declaracoes.get(nome, 0) + 1
        self.declaracoes[nome] = n
        nome_tac = nome if n == 1 else f"{nome}.{n}"
        self.escopos[-1][nome] = nome_tac
        return nome_tac

    def resolver(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        raise KeyError(nome)            # impossível após a semântica

    # --- comandos ----------------------------------------------------

    def visitar_Programa(self, no):
        self.reservados = set(nomes_declarados(no))
        for c in no.comandos:
            self.visitar(c)
        return self.codigo

    def visitar_Bloco(self, no):
        self.escopos.append({})
        for c in no.comandos:
            self.visitar(c)
        self.escopos.pop()

    def visitar_Decl(self, no):
        a = self.visitar(no.expr)       # antes de declarar, como na semântica
        self.emitir("=", self.declarar(no.nome), a, linha=no.linha)

    def visitar_Atrib(self, no):
        a = self.visitar(no.expr)
        self.emitir("=", self.resolver(no.nome), a, linha=no.linha)

    def visitar_Print(self, no):
        a = self.visitar(no.expr)
        self.emitir("print", None, a, linha=no.linha)

    def visitar_If(self, no):
        # if sem else usa o mesmo esquema com S2 vazio; o goto L_fim que
        # sobra é removido pelo otimizador
        senao, fim = self.novo_rotulo(), self.novo_rotulo()
        c = self.visitar(no.cond)
        self.emitir("iffalse", senao, c, linha=no.linha)
        self.visitar(no.entao)
        self.emitir("goto", fim)
        self.emitir("label", senao)
        if no.senao is not None:
            self.visitar(no.senao)
        self.emitir("label", fim)

    def visitar_While(self, no):
        ini, fim = self.novo_rotulo(), self.novo_rotulo()
        self.emitir("label", ini)
        c = self.visitar(no.cond)
        self.emitir("iffalse", fim, c, linha=no.linha)
        self.visitar(no.corpo)
        self.emitir("goto", ini)
        self.emitir("label", fim)

    # --- expressões: devolvem o endereço do resultado ------------------

    def visitar_Num(self, no):
        return no.valor

    def visitar_Bool(self, no):
        return no.valor

    def visitar_Var(self, no):
        return self.resolver(no.nome)

    def visitar_Unario(self, no):
        a = self.visitar(no.expr)
        t = self.novo_temp()
        self.emitir("neg", t, a, linha=no.linha)
        return t

    def visitar_Binario(self, no):
        a = self.visitar(no.esq)
        b = self.visitar(no.dir)
        t = self.novo_temp()
        self.emitir(no.op, t, a, b, linha=no.linha)
        return t                        # endereço do resultado
