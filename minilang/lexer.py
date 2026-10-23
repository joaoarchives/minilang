"""Analisador léxico da MiniLang: lexer manual, caractere a caractere."""

from .tokens import (OPERADORES_DUPLOS, OPERADORES_SIMPLES, RESERVADAS,
                     TipoToken as T, Token)


def eh_letra(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"


def eh_digito(c):
    return "0" <= c <= "9"


class Lexer:
    def __init__(self, fonte):
        self.fonte = fonte
        self.pos = 0
        self.linha = 1
        self.coluna = 1
        self.erros = []         # mensagens de erro léxico, na ordem

    # --- utilitários -------------------------------------------------

    def atual(self):
        """Caractere corrente, ou '' no fim do arquivo."""
        return self.fonte[self.pos] if self.pos < len(self.fonte) else ""

    def proximo(self):
        """Caractere seguinte ao corrente, sem consumir."""
        p = self.pos + 1
        return self.fonte[p] if p < len(self.fonte) else ""

    def avancar(self):
        c = self.atual()
        self.pos += 1
        if c == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c

    # --- reconhecimento ----------------------------------------------

    def pular_espacos_e_comentarios(self):
        while True:
            c = self.atual()
            if c in (" ", "\t", "\r", "\n"):
                self.avancar()
            elif c == "/" and self.proximo() == "/":
                while self.atual() not in ("\n", ""):
                    self.avancar()
            else:
                return

    def proximo_token(self):
        self.pular_espacos_e_comentarios()
        lin, col = self.linha, self.coluna
        c = self.atual()

        if c == "":
            return Token(T.EOF, "", lin, col)

        if eh_digito(c):                           # q0 --dígito--> q2
            ini = self.pos
            while eh_digito(self.atual()):
                self.avancar()                     # laço em q2
            return Token(T.NUM, self.fonte[ini:self.pos], lin, col)

        if eh_letra(c):                            # q0 --letra--> q1
            ini = self.pos
            while eh_letra(self.atual()) or eh_digito(self.atual()):
                self.avancar()                     # laço em q1
            lex = self.fonte[ini:self.pos]
            tipo = RESERVADAS.get(lex, T.ID)       # reservada ou ID?
            return Token(tipo, lex, lin, col)

        duplo = c + self.proximo()
        if duplo in OPERADORES_DUPLOS:             # 2 caracteres primeiro
            self.avancar(); self.avancar()
            return Token(OPERADORES_DUPLOS[duplo], duplo, lin, col)

        if c in OPERADORES_SIMPLES:
            self.avancar()
            return Token(OPERADORES_SIMPLES[c], c, lin, col)

        # nenhum padrão casou: recuperação em modo pânico
        self.avancar()                             # descarta o caractere
        self.erros.append(
            f"{lin}:{col}: erro léxico: caractere inválido '{c}'")
        return None                                # tokens() ignora e segue

    def tokens(self):
        lista = []
        while True:
            tok = self.proximo_token()
            if tok is None:
                continue
            lista.append(tok)
            if tok.tipo == T.EOF:
                return lista
