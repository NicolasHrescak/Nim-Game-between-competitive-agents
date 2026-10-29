"""
Módulo agente_otimo.py
Implementação do Agente Ótimo Teórico para o Nim Misère (solução matemática resolvida via Nim-sum/XOR).
Executa sempre o movimento perfeito sem necessidade de busca em árvore (custo computacional: 0 nós visitados).
"""

from typing import Tuple, Optional
from nim_game import NimMisere


class AgenteOtimoNim:
    """
    Agente Matemático Ótimo para Nim Misère.
    
    Implementa a estratégia formal descrita em Bouton (1901) para a variante Misère:
    - Fase 1 (Jogo Normal): Se >= 2 fileiras possuem tamanho > 1, busca anular a Nim-sum (XOR = 0).
    - Fase 2 (Emboscada Final): Se exatamente 1 fileira possui tamanho > 1, reduz a fileira grande
      para 1 ou 0 palitos, de modo a deixar um número ÍMPAR de fileiras unitárias para o adversário.
    - Fase 3 (Unitárias): Se todas as fileiras forem <= 1, retira 1 palito de qualquer fileira restante.
    
    Custo de busca computacional: 0 nós visitados.
    """

    def __init__(self):
        pass

    def decidir(self, jogo: NimMisere, estado: Tuple[Tuple[int, ...], str]) -> Tuple[Optional[Tuple[int, int]], int]:
        """
        Retorna:
            (melhor_acao, nos_visitados = 0)
        """
        fileiras, _ = estado
        acoes_legais = jogo.acoes(estado)
        if not acoes_legais:
            return None, 0

        # Identifica fileiras com mais de 1 palito e fileiras com exatamente 1 palito
        indices_maiores = [i for i, f in enumerate(fileiras) if f > 1]
        indices_unitarias = [i for i, f in enumerate(fileiras) if f == 1]
        qtd_maiores = len(indices_maiores)
        qtd_unitarias = len(indices_unitarias)

        # ---------------------------------------------------------
        # FASE 2: A EMBOSCADA FINAL (Transição Misère)
        # Condição: Resta EXATAMENTE UMA fileira com mais de 1 palito
        # ---------------------------------------------------------
        if qtd_maiores == 1:
            idx_grande = indices_maiores[0]
            tam_grande = fileiras[idx_grande]

            # Queremos entregar ao adversário um número ÍMPAR de fileiras unitárias
            if qtd_unitarias % 2 == 0:
                # Quantidade de unitárias é PAR (0, 2, 4...) -> Reduz a grande para 1
                # Nova contagem de unitárias ficará qtd_unitarias + 1 (ÍMPAR)
                palitos_a_retirar = tam_grande - 1
                return (idx_grande, palitos_a_retirar), 0
            else:
                # Quantidade de unitárias é ÍMPAR (1, 3, 5...) -> Elimina a grande completamente
                # A contagem de unitárias permanece a mesma (ÍMPAR)
                palitos_a_retirar = tam_grande
                return (idx_grande, palitos_a_retirar), 0

        # ---------------------------------------------------------
        # FASE 3: TODAS AS FILEIRAS SÃO <= 1
        # ---------------------------------------------------------
        if qtd_maiores == 0:
            # Qualquer jogada válida remove 1 palito de uma fileira unitária
            idx_escolhido = indices_unitarias[0]
            return (idx_escolhido, 1), 0

        # ---------------------------------------------------------
        # FASE 1: JOGO NORMAL (2 ou mais fileiras > 1)
        # Regra: Entregar ao adversário uma posição com Nim-sum (XOR) == 0
        # ---------------------------------------------------------
        xor_total = jogo.nim_sum(fileiras)

        if xor_total != 0:
            # Posição vencedora: existe jogada legal para zerar o XOR total
            for i, f in enumerate(fileiras):
                alvo = f ^ xor_total
                if alvo < f:
                    # Encontrou a fileira que deve ser reduzida
                    palitos_a_retirar = f - alvo
                    return (i, palitos_a_retirar), 0

        # Se xor_total == 0, o estado atual é teoricamente perdedor se o oponente não errar.
        # Faz a jogada legal mais conservadora (retira 1 palito da primeira fileira disponível).
        return acoes_legais[0], 0
