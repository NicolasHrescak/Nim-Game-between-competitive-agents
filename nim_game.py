"""
Módulo nim_game.py
Implementação formal das regras do Jogo do Nim na variante Misère ("quem tira o último perde").
Seguindo rigorosamente o indicador ID2.1 e ID2.2 de Busca Competitiva.
"""

from typing import Tuple, List

# Constantes para os jogadores
MAX_PLAYER = 'MAX'
MIN_PLAYER = 'MIN'


def outro_jogador(jogador: str) -> str:
    """Retorna o oponente do jogador fornecido."""
    return MIN_PLAYER if jogador == MAX_PLAYER else MAX_PLAYER


class NimMisere:
    """
    Representação formal do Jogo do Nim Misère.
    
    Formalização dos seis componentes (ID2.1):
    1. Estado (s): Tupla (fileiras, jogador_da_vez).
       Exemplo: ((3, 4, 5), 'MAX')
       s₀: Configuração inicial das fileiras + indicação do primeiro a jogar.
    2. JOGADOR(s): Retorna de quem é a vez (MAX ou MIN).
    3. AÇÕES(s): Lista de tuplas (indice_fileira, palitos_a_retirar).
       Legal: 1 <= palitos <= fileira[indice_fileira].
    4. RESULTADO(s, a): Novo estado com os palitos subtraídos e a vez alternada.
    5. TESTE-TERMINAL(s): Verdadeiro se a soma de palitos de todas as fileiras for 0.
    6. UTILIDADE(s, MAX): Um único número do ponto de vista de MAX.
       Na variante Misère, quem é forçado a tirar o último palito PERDE.
       Logo, se o tabuleiro esvaziou:
       - Se jogador(s) == MIN: MAX acabou de jogar e esvaziou o tabuleiro (pegou o último).
         Portanto MAX perdeu -> Utilidade = -1.
       - Se jogador(s) == MAX: MIN acabou de jogar e esvaziou o tabuleiro (pegou o último).
         Portanto MIN perdeu e MAX venceu -> Utilidade = +1.
    """

    def __init__(self, configuracao_inicial: Tuple[int, ...] = (3, 4, 5), primeiro_jogador: str = MAX_PLAYER):
        self.configuracao_inicial = tuple(configuracao_inicial)
        self.primeiro_jogador = primeiro_jogador

    def estado_inicial(self) -> Tuple[Tuple[int, ...], str]:
        """Retorna o estado inicial s₀."""
        return (self.configuracao_inicial, self.primeiro_jogador)

    def jogador(self, s: Tuple[Tuple[int, ...], str]) -> str:
        """Função JOGADOR(s): retorna de quem é a vez no estado s."""
        return s[1]

    def acoes(self, s: Tuple[Tuple[int, ...], str]) -> List[Tuple[int, int]]:
        """
        Função AÇÕES(s): retorna a lista de jogadas legais no estado s.
        Cada ação é uma tupla (indice_fileira, palitos_a_retirar).
        """
        fileiras, _ = s
        jogadas = []
        for i, count in enumerate(fileiras):
            if count > 0:
                for k in range(1, count + 1):
                    jogadas.append((i, k))
        return jogadas

    def resultado(self, s: Tuple[Tuple[int, ...], str], a: Tuple[int, int]) -> Tuple[Tuple[int, ...], str]:
        """
        Função RESULTADO(s, a): retorna o novo estado resultante da ação a.
        """
        fileiras, player = s
        idx_fileira, qtd_retirar = a
        if fileiras[idx_fileira] < qtd_retirar or qtd_retirar <= 0:
            raise ValueError(f"Ação ilegal {a} para fileiras {fileiras}")

        novas_fileiras = list(fileiras)
        novas_fileiras[idx_fileira] -= qtd_retirar
        prox_player = outro_jogador(player)
        return (tuple(novas_fileiras), prox_player)

    def teste_terminal(self, s: Tuple[Tuple[int, ...], str]) -> bool:
        """
        Função TESTE-TERMINAL(s):
        O jogo termina quando o tabuleiro fica completamente vazio.
        """
        return sum(s[0]) == 0

    def utilidade(self, s: Tuple[Tuple[int, ...], str]) -> float:
        """
        Função UTILIDADE(s, MAX):
        Retorna um único número sempre sob a ótica de MAX.
        Na regra Misère, o jogador forçado a retirar o último palito perde.
        Quando o jogo atinge o estado terminal, s[1] é o jogador que teria o próximo turno.
        - Se s[1] == MIN, quem jogou por último foi MAX, logo MAX perdeu: -1.0.
        - Se s[1] == MAX, quem jogou por último foi MIN, logo MAX venceu: +1.0.
        """
        if not self.teste_terminal(s):
            raise ValueError("Cálculo de utilidade chamado em estado não terminal!")
        
        _, prox_jogador = s
        if prox_jogador == MIN_PLAYER:
            # MAX retirou o último palito -> MAX perde
            return -1.0
        else:
            # MIN retirou o último palito -> MIN perde, MAX vence
            return 1.0

    def nim_sum(self, fileiras: Tuple[int, ...]) -> int:
        """Calcula o XOR sum de todas as fileiras."""
        xor_total = 0
        for f in fileiras:
            xor_total ^= f
        return xor_total

    def avaliacao(self, s: Tuple[Tuple[int, ...], str]) -> float:
        """
        Função de Avaliação Heurística (para busca com corte de profundidade).
        Retorna um valor estimado no intervalo [-1.0, +1.0] do ponto de vista de MAX.
        
        Características e justificativas:
        1. Análise da Posição Teórica (Misère):
           - Se existirem 2+ fileiras com tamanho > 1:
             Uma posição com nim_sum != 0 é VENCEDORA para o jogador da vez (+0.8).
             Uma posição com nim_sum == 0 é PERDEDORA para o jogador da vez (-0.8).
           - Se restar exatamente 1 fileira com tamanho > 1 (Fase de Emboscada):
             O jogador da vez tem controle absoluto e garante a vitória (+0.95).
           - Se todas as fileiras forem <= 1:
             Contagem de 1s:
             Se for ÍMPAR: o jogador da vez perde (-1.0).
             Se for PAR: o jogador da vez ganha (+1.0).
        
        Perspectiva:
        O valor da posição é computado sob a ótica do jogador da vez (jogador(s))
        e depois convertido para a perspectiva de MAX (+1 se MAX, -1 se MIN).
        """
        if self.teste_terminal(s):
            return self.utilidade(s)

        fileiras, jogador_vez = s
        maiores_que_um = [f for f in fileiras if f > 1]
        iguais_a_um = [f for f in fileiras if f == 1]
        qtd_maiores = len(maiores_que_um)
        qtd_unitarias = len(iguais_a_um)

        if qtd_maiores >= 2:
            # Fase Normal: Nim-sum != 0 é vantajoso para quem tem a vez
            xor = self.nim_sum(fileiras)
            val_jogador_vez = 0.8 if xor != 0 else -0.8
        elif qtd_maiores == 1:
            # Fase de Emboscada: quem tem a vez pode forçar a vitória em 1 jogada
            val_jogador_vez = 0.95
        else:
            # Todas <= 1: jogo puramente de contagem de unitárias
            if qtd_unitarias % 2 == 1:
                val_jogador_vez = -1.0  # O jogador atual terá que retirar o último se jogarem 1 a 1
            else:
                val_jogador_vez = 1.0

        # Converte para a ótica de MAX
        return val_jogador_vez if jogador_vez == MAX_PLAYER else -val_jogador_vez
