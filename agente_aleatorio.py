"""
Módulo agente_aleatorio.py
Implementação da Linha de Base (Baseline Trivial): Agente Aleatório.
Escolhe uniformemente entre todas as ações legais com controle de semente.
"""

import random
from typing import Tuple, Optional
from nim_game import NimMisere


class AgenteAleatorio:
    """
    Agente que seleciona ações uniformemente ao acaso.
    Custo de busca computacional: 0 nós visitados.
    """

    def __init__(self, semente: Optional[int] = None):
        self.rng = random.Random(semente)

    def redefinir_semente(self, semente: int):
        """Atualiza a semente pseudoaleatória."""
        self.rng.seed(semente)

    def decidir(self, jogo: NimMisere, estado: Tuple[Tuple[int, ...], str]) -> Tuple[Optional[Tuple[int, int]], int]:
        """
        Retorna:
            (acao_escolhida, nos_visitados = 0)
        """
        acoes = jogo.acoes(estado)
        if not acoes:
            return None, 0
        escolha = self.rng.choice(acoes)
        return escolha, 0
