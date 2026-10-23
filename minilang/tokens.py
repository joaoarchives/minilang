"""Tipos de token e palavras reservadas da MiniLang."""

from dataclasses import dataclass
from enum import Enum, auto


class TipoToken(Enum):
    # literais e nomes
    NUM = auto(); ID = auto()
    # palavras reservadas
    VAR = auto(); INT = auto(); BOOL = auto()
    TRUE = auto(); FALSE = auto(); IF = auto()
    ELSE = auto(); WHILE = auto(); PRINT = auto()
    # operadores
    MAIS = auto(); MENOS = auto(); VEZES = auto()
    DIV = auto(); ATRIB = auto(); IGUAL = auto()
    DIFERENTE = auto(); MENOR = auto(); MAIOR = auto()
    MENOR_IGUAL = auto(); MAIOR_IGUAL = auto()
    # delimitadores
    ABRE_PAR = auto(); FECHA_PAR = auto()
    ABRE_CHAVE = auto(); FECHA_CHAVE = auto()
    DOIS_PONTOS = auto(); PONTO_VIRG = auto()
    EOF = auto()


@dataclass
class Token:
    tipo: TipoToken
    lexema: str
    linha: int
    coluna: int


RESERVADAS = {
    "var": TipoToken.VAR,
    "int": TipoToken.INT,
    "bool": TipoToken.BOOL,
    "true": TipoToken.TRUE,
    "false": TipoToken.FALSE,
    "if": TipoToken.IF,
    "else": TipoToken.ELSE,
    "while": TipoToken.WHILE,
    "print": TipoToken.PRINT,
}

# operadores de 2 caracteres: testados antes dos de 1 (maior casamento)
OPERADORES_DUPLOS = {
    "==": TipoToken.IGUAL,
    "!=": TipoToken.DIFERENTE,
    "<=": TipoToken.MENOR_IGUAL,
    ">=": TipoToken.MAIOR_IGUAL,
}

OPERADORES_SIMPLES = {
    "+": TipoToken.MAIS,
    "-": TipoToken.MENOS,
    "*": TipoToken.VEZES,
    "/": TipoToken.DIV,
    "=": TipoToken.ATRIB,
    "<": TipoToken.MENOR,
    ">": TipoToken.MAIOR,
    "(": TipoToken.ABRE_PAR,
    ")": TipoToken.FECHA_PAR,
    "{": TipoToken.ABRE_CHAVE,
    "}": TipoToken.FECHA_CHAVE,
    ":": TipoToken.DOIS_PONTOS,
    ";": TipoToken.PONTO_VIRG,
}
