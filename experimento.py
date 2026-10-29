"""
Módulo experimento.py
Protocolo Experimental Reprodutível (ID2.3).
Executa baterias de partidas entre agentes, coletando métricas rigorosas:
- Taxa de vitórias (%)
- Unidade de custo: Nós visitados (Média, Desvio Padrão, Pior Caso / Máximo)
- Variação controlada de aberturas e alternância de primeiro jogador para evitar repetição determinística.
"""

import math
import random
from typing import Tuple, List, Dict, Any
from nim_game import NimMisere, MAX_PLAYER, MIN_PLAYER
from alfabeta import AlfaBeta
from agente_aleatorio import AgenteAleatorio
from agente_otimo import AgenteOtimoNim


def calcular_estatisticas(valores: List[float]) -> Dict[str, float]:
    """Calcula média, desvio padrão amostral, mínimo e pior caso (máximo)."""
    if not valores:
        return {"media": 0.0, "desvio": 0.0, "min": 0.0, "max": 0.0}
    n = len(valores)
    media = sum(valores) / n
    if n > 1:
        variancia = sum((x - media) ** 2 for x in valores) / (n - 1)
        desvio = math.sqrt(variancia)
    else:
        desvio = 0.0
    return {
        "media": media,
        "desvio": desvio,
        "min": min(valores),
        "max": max(valores)
    }


def jogar_partida(
    configuracao: Tuple[int, ...],
    primeiro_jogador: str,
    agente_max: Any,
    agente_min: Any,
    tipo_max: str,
    tipo_min: str
) -> Dict[str, Any]:
    """
    Executa uma partida única entre agente_max (MAX) e agente_min (MIN).
    Rastreia nós visitados para cada jogador.
    """
    jogo = NimMisere(configuracao_inicial=configuracao, primeiro_jogador=primeiro_jogador)
    estado = jogo.estado_inicial()
    
    nos_max_partida = 0
    nos_min_partida = 0
    num_lances = 0

    while not jogo.teste_terminal(estado):
        jogador_vez = jogo.jogador(estado)
        num_lances += 1

        if jogador_vez == MAX_PLAYER:
            if tipo_max == 'alfabeta':
                acao, _, nos = agente_max.decidir(estado)
            elif tipo_max in ('aleatorio', 'otimo'):
                acao, nos = agente_max.decidir(jogo, estado)
            else:
                raise ValueError(f"Tipo de agente MAX desconhecido: {tipo_max}")
            nos_max_partida += nos
        else:
            if tipo_min == 'alfabeta':
                acao, _, nos = agente_min.decidir(estado)
            elif tipo_min in ('aleatorio', 'otimo'):
                acao, nos = agente_min.decidir(jogo, estado)
            else:
                raise ValueError(f"Tipo de agente MIN desconhecido: {tipo_min}")
            nos_min_partida += nos

        if acao is None:
            break
        estado = jogo.resultado(estado, acao)

    utilidade_final = jogo.utilidade(estado)
    vencedor = MAX_PLAYER if utilidade_final > 0 else MIN_PLAYER

    return {
        "vencedor": vencedor,
        "lances": num_lances,
        "nos_max": nos_max_partida,
        "nos_min": nos_min_partida,
        "configuracao_inicial": configuracao,
        "primeiro_jogador": primeiro_jogador
    }


def gerar_aberturas_reproduziveis(num_partidas: int, semente: int = 42) -> List[Tuple[Tuple[int, ...], str]]:
    """
    Gera uma lista balanceada de aberturas com semente fixa para reprodutibilidade.
    Evita a armadilha de dois agentes determinísticos jogarem sempre a mesma partida.
    Varia a configuração inicial de pilhas e alterna o primeiro jogador.
    """
    rng = random.Random(semente)
    aberturas = []
    
    for i in range(num_partidas):
        # Gera 3 pilhas com tamanhos entre 1 e 5 (garantindo pelo menos 2 palitos no total)
        p1 = rng.randint(1, 4)
        p2 = rng.randint(2, 5)
        p3 = rng.randint(1, 4)
        # Alterna quem começa para simetria estrita
        primeiro = MAX_PLAYER if (i % 2 == 0) else MIN_PLAYER
        aberturas.append(((p1, p2, p3), primeiro))
        
    return aberturas


def executar_bateria(
    nome_confronto: str,
    agente_max: Any,
    agente_min: Any,
    tipo_max: str,
    tipo_min: str,
    aberturas: List[Tuple[Tuple[int, ...], str]]
) -> Dict[str, Any]:
    """
    Executa uma bateria completa de partidas para um confronto específico.
    """
    resultados = []
    vitórias_max = 0
    vitórias_min = 0
    lista_nos_max = []
    lista_nos_min = []

    for config, primeiro in aberturas:
        partida = jogar_partida(config, primeiro, agente_max, agente_min, tipo_max, tipo_min)
        resultados.append(partida)

        if partida["vencedor"] == MAX_PLAYER:
            vitórias_max += 1
        else:
            vitórias_min += 1

        lista_nos_max.append(partida["nos_max"])
        lista_nos_min.append(partida["nos_min"])

    total = len(aberturas)
    return {
        "confronto": nome_confronto,
        "total_partidas": total,
        "vitorias_max": vitórias_max,
        "pct_max": (vitórias_max / total) * 100,
        "vitorias_min": vitórias_min,
        "pct_min": (vitórias_min / total) * 100,
        "stats_nos_max": calcular_estatisticas(lista_nos_max),
        "stats_nos_min": calcular_estatisticas(lista_nos_min),
        "partidas": resultados
    }
