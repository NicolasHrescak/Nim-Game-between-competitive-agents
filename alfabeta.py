"""
Módulo alfabeta.py
Implementação do algoritmo Alfa-Beta com poda e ordenação de jogadas.
Mantém rastreamento exato do número de nós visitados (UNIDADE DE CUSTO).
Em profundidade completa, garante devolução de valor idêntico ao Minimax (Teorema 1).
"""

from typing import Tuple, Optional, List
from nim_game import NimMisere, MAX_PLAYER, MIN_PLAYER


class AlfaBeta:
    """
    Agente com Poda Alfa-Beta e Ordenação Heurística de Ações.
    """

    def __init__(self, jogo: NimMisere, limite_profundidade: Optional[int] = None, ordenar_jogadas: bool = True):
        self.jogo = jogo
        self.limite_profundidade = limite_profundidade
        self.ordenar_jogadas = ordenar_jogadas
        self.nos_visitados = 0

    def ordenar_acoes(self, estado: Tuple[Tuple[int, ...], str], acoes: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Ordenação de jogadas (Heurística barata):
        Prioriza ações mais promissoras para antecipar podas alfa-beta.
        Critérios:
        1. Jogadas que deixam o tabuleiro com Nim-sum = 0 (posições perdedoras para o adversário).
        2. Jogadas que removem mais palitos (aproximam do fim do jogo mais rapidamente).
        """
        if not self.ordenar_jogadas:
            return acoes

        def chave_prioridade(acao: Tuple[int, int]) -> Tuple[int, int]:
            s_prox = self.jogo.resultado(estado, acao)
            fileiras_prox, _ = s_prox
            xor = self.jogo.nim_sum(fileiras_prox)
            # xor == 0 é prioridade máxima (1 se xor==0, senão 0)
            prioridade_xor = 1 if xor == 0 else 0
            qtd_retirada = acao[1]
            return (prioridade_xor, qtd_retirada)

        # Ordena em ordem decrescente de prioridade
        return sorted(acoes, key=chave_prioridade, reverse=True)

    def decidir(self, estado: Tuple[Tuple[int, ...], str]) -> Tuple[Optional[Tuple[int, int]], float, int]:
        """
        Executa a decisão Alfa-Beta.
        Retorna:
            (melhor_acao, melhor_valor, nos_visitados_neste_lance)
        """
        self.nos_visitados = 0
        jogador = self.jogo.jogador(estado)

        if self.jogo.teste_terminal(estado):
            return None, self.jogo.utilidade(estado), 0

        acoes = self.ordenar_acoes(estado, self.jogo.acoes(estado))
        melhor_acao = acoes[0]
        alpha = float('-inf')
        beta = float('inf')

        if jogador == MAX_PLAYER:
            melhor_valor = float('-inf')
            for a in acoes:
                prox_estado = self.jogo.resultado(estado, a)
                v = self._min_value(prox_estado, 1, alpha, beta)
                if v > melhor_valor:
                    melhor_valor = v
                    melhor_acao = a
                alpha = max(alpha, melhor_valor)
        else:
            melhor_valor = float('inf')
            for a in acoes:
                prox_estado = self.jogo.resultado(estado, a)
                v = self._max_value(prox_estado, 1, alpha, beta)
                if v < melhor_valor:
                    melhor_valor = v
                    melhor_acao = a
                beta = min(beta, melhor_valor)

        return melhor_acao, melhor_valor, self.nos_visitados

    def _max_value(self, s: Tuple[Tuple[int, ...], str], profundidade: int, alpha: float, beta: float) -> float:
        self.nos_visitados += 1

        if self.jogo.teste_terminal(s):
            return self.jogo.utilidade(s)

        if self.limite_profundidade is not None and profundidade >= self.limite_profundidade:
            return self.jogo.avaliacao(s)

        v = float('-inf')
        acoes = self.ordenar_acoes(s, self.jogo.acoes(s))
        for a in acoes:
            prox_estado = self.jogo.resultado(s, a)
            v = max(v, self._min_value(prox_estado, profundidade + 1, alpha, beta))
            if v >= beta:
                return v  # Poda beta
            alpha = max(alpha, v)
        return v

    def _min_value(self, s: Tuple[Tuple[int, ...], str], profundidade: int, alpha: float, beta: float) -> float:
        self.nos_visitados += 1

        if self.jogo.teste_terminal(s):
            return self.jogo.utilidade(s)

        if self.limite_profundidade is not None and profundidade >= self.limite_profundidade:
            return self.jogo.avaliacao(s)

        v = float('inf')
        acoes = self.ordenar_acoes(s, self.jogo.acoes(s))
        for a in acoes:
            prox_estado = self.jogo.resultado(s, a)
            v = min(v, self._max_value(prox_estado, profundidade + 1, alpha, beta))
            if v <= alpha:
                return v  # Poda alfa
            beta = min(beta, v)
        return v
