"""Tabela de símbolos com escopos aninhados (pilha de dicionários)."""

from dataclasses import dataclass


@dataclass
class Simbolo:
    nome: str
    tipo: str            # 'int' | 'bool'
    categoria: str       # 'variavel'
    linha: int           # linha da declaração
    nivel: int           # 0 = global; cada bloco soma 1


class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]          # [global, bloco1, ...]

    def entrar_escopo(self):
        self.escopos.append({})

    def sair_escopo(self):
        self.escopos.pop()

    def declarar(self, nome, tipo, linha):
        """Declara no escopo atual; devolve None se for redeclaração."""
        atual = self.escopos[-1]
        if nome in atual:
            return None
        s = Simbolo(nome, tipo, "variavel", linha, len(self.escopos) - 1)
        atual[nome] = s
        return s

    def buscar(self, nome):
        """Procura do escopo mais interno para o global."""
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None
