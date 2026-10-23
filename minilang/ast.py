"""Nós da árvore sintática abstrata (AST) da MiniLang."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class No:
    # linha do fonte, para as mensagens de erro das fases seguintes.
    # Fica fora do repr e da comparação: duas árvores com a mesma forma
    # são iguais, estejam onde estiverem no arquivo.
    linha: int = field(default=0, kw_only=True, repr=False, compare=False)


# --- expressões --------------------------------------------------------

@dataclass
class Num(No):
    valor: int


@dataclass
class Bool(No):
    valor: bool


@dataclass
class Var(No):
    nome: str


@dataclass
class Unario(No):
    op: str
    expr: No


@dataclass
class Binario(No):
    op: str
    esq: No
    dir: No


# --- comandos ----------------------------------------------------------

@dataclass
class Bloco(No):
    comandos: List[No]


@dataclass
class Decl(No):
    nome: str
    tipo: str            # 'int' | 'bool'
    expr: No


@dataclass
class Atrib(No):
    nome: str
    expr: No


@dataclass
class Print(No):
    expr: No


@dataclass
class If(No):
    cond: No
    entao: Bloco
    senao: Optional[Bloco] = None


@dataclass
class While(No):
    cond: No
    corpo: Bloco


@dataclass
class Programa(No):
    comandos: List[No]


# --- impressão indentada (--ast) ---------------------------------------

def _rotulo(no):
    match no:
        case Num(valor=v):
            return f"Num {v}"
        case Bool(valor=v):
            return f"Bool {'true' if v else 'false'}"
        case Var(nome=n):
            return f"Var {n}"
        case Unario(op=op) | Binario(op=op):
            return f"{type(no).__name__} {op}"
        case Decl(nome=n, tipo=t):
            return f"Decl {n}: {t}"
        case Atrib(nome=n):
            return f"Atrib {n}"
    return type(no).__name__


def _filhos(no):
    match no:
        case Programa(comandos=cs) | Bloco(comandos=cs):
            return [("", c) for c in cs]
        case Unario(expr=e) | Decl(expr=e) | Atrib(expr=e) | Print(expr=e):
            return [("", e)]
        case Binario(esq=a, dir=b):
            return [("", a), ("", b)]
        case If(cond=c, entao=s1, senao=s2):
            filhos = [("cond: ", c), ("então: ", s1)]
            if s2 is not None:
                filhos.append(("senão: ", s2))
            return filhos
        case While(cond=c, corpo=s):
            return [("cond: ", c), ("corpo: ", s)]
    return []


def formatar(no):
    """AST indentada, um nó por linha, no estilo do comando `tree`."""
    linhas = [_rotulo(no)]

    def descer(no, prefixo):
        filhos = _filhos(no)
        for k, (papel, filho) in enumerate(filhos):
            ultimo = k == len(filhos) - 1
            linhas.append(prefixo + ("└── " if ultimo else "├── ")
                          + papel + _rotulo(filho))
            descer(filho, prefixo + ("    " if ultimo else "│   "))

    descer(no, "")
    return "\n".join(linhas)
