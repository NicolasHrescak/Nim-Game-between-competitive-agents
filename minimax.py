"""
Módulo minimax.py
Implementação do algoritmo Minimax canônico (busca completa ou com corte de profundidade).
Mantém rastreamento exato do número de nós visitados (UNIDADE DE CUSTO).
"""

from typing import Tuple, Optional
from nim_game import NimMisere, MAX_PLAYER, MIN_PLAYER


class Minimax:
    """
    Agente Minimax para busca competitiva.
    """

    def __init__(self, jogo: NimMisere, limite_profundidade: Optional[int] = None):
        self.jogo = jogo
        self.limite_profundidade = limite_profundidade
        self.nos_visitados = 0

    def decidir(self, estado: Tuple[Tuple[int, ...], str]) -> Tuple[Optional[Tuple[int, int]], float, int]:
        """
        Calcula a melhor ação para o estado atual a partir de Minimax.
        Retorna:
            (melhor_acao, melhor_valor, nos_visitados_neste_lance)
        """
        self.nos_visitados = 0
        jogador = self.jogo.jogador(estado)

        if self.jogo.teste_terminal(estado):
            return None, self.jogo.utilidade(estado), 0

        acoes = self.jogo.acoes(estado)
        melhor_acao = acoes[0]

        if jogador == MAX_PLAYER:
            melhor_valor = float('-inf')
            for a in acoes:
                prox_estado = self.jogo.resultado(estado, a)
                v = self._min_value(prox_estado, 1)
                if v > melhor_valor:
                    melhor_valor = v
                    melhor_acao = a
        else:
            melhor_valor = float('inf')
            for a in acoes:
                prox_estado = self.jogo.resultado(estado, a)
                v = self._max_value(prox_estado, 1)
                if v < melhor_valor:
                    melhor_valor = v
                    melhor_acao = a

        return melhor_acao, melhor_valor, self.nos_visitados

    def _max_value(self, s: Tuple[Tuple[int, ...], str], profundidade: int) -> float:
        self.nos_visitados += 1

        if self.jogo.teste_terminal(s):
            return self.jogo.utilidade(s)

        if self.limite_profundidade is not None and profundidade >= self.limite_profundidade:
            return self.jogo.avaliacao(s)

        v = float('-inf')
        for a in self.jogo.acoes(s):
            prox_estado = self.jogo.resultado(s, a)
            v = max(v, self._min_value(prox_estado, profundidade + 1))
        return v

    def _min_value(self, s: Tuple[Tuple[int, ...], str], profundidade: int) -> float:
        self.nos_visitados += 1

        if self.jogo.teste_terminal(s):
            return self.jogo.utilidade(s)

        if self.limite_profundidade is not None and profundidade >= self.limite_profundidade:
            return self.jogo.avaliacao(s)

        v = float('inf')
        for a in self.jogo.acoes(s):
            prox_estado = self.jogo.resultado(s, a)
            v = min(v, self._max_value(prox_estado, profundidade + 1))
        return v
