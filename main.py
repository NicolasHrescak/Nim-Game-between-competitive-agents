"""
Módulo main.py
Ponto de entrada do projeto de Busca Competitiva — Jogo do Nim Misère.
Executa:
1. Verificação das 5 propriedades do jogo e formalização dos 6 componentes (ID2.1).
2. Verificação de Corretude (Teorema 1): Igualdade de valor Minimax vs. Alfa-Beta (ID2.2).
3. Protocolo Experimental com 3 baterias de 50 partidas (ID2.3).
4. Tabela consolidada de métricas (Nós visitados e taxa de vitórias).
5. Declaração obrigatória de limitações e garantias ausentes.
"""

import sys

# Garante compatibilidade UTF-8 no Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from nim_game import NimMisere, MAX_PLAYER, MIN_PLAYER
from minimax import Minimax
from alfabeta import AlfaBeta
from agente_aleatorio import AgenteAleatorio
from agente_otimo import AgenteOtimoNim
from experimento import gerar_aberturas_reproduziveis, executar_bateria


def secao_1_formalizacao():
    print("=" * 80)
    print("SECAO 1 - FORMALIZACAO DO JOGO (ID2.1)")
    print("=" * 80)
    print("Jogo Escolhido: Nim na variante Misere ('quem retira o ultimo palito perde').")
    print("\nVerificacao das 5 propriedades:")
    print("  1. Dois jogadores?        SIM (MAX e MIN se alternam estritamente).")
    print("  2. Soma zero?             SIM (Utilidade: +1.0 para vitoria, -1.0 para derrota).")
    print("  3. Informacao perfeita?   SIM (Todas as fileiras e palitos sao visiveis a todo instante).")
    print("  4. Deterministico?        SIM (Transicoes de estado sao exatas, sem dados ou sorteio).")
    print("  5. Finito?                SIM (Cada jogada remove >= 1 palito; termina em <= sum(fileiras) lances).")

    print("\nOs 6 Componentes Formais (ID2.1):")
    print("  1. Estado s = (fileiras, jogador_da_vez). Exemplo: ((3, 4, 5), 'MAX').")
    print("     s0 = Configuracao inicial acordada com primeiro jogador definido.")
    print("  2. JOGADOR(s): Funcao estrita do estado que retorna s[1] (MAX ou MIN).")
    print("  3. ACOES(s) e RESULTADO(s, a):")
    print("     Acoes: tuplas (i, k) com 1 <= k <= fileiras[i].")
    print("     Resultado: decrementa fileira i em k e alterna o jogador da vez.")
    print("  4. TESTE-TERMINAL(s): Retorna True se sum(fileiras) == 0.")
    print("  5. UTILIDADE(s, MAX): Um unico numero sob a otica de MAX:")
    print("     Se jogador(s) == MIN -> MAX acabou de esvaziar o tabuleiro -> MAX perdeu (-1.0).")
    print("     Se jogador(s) == MAX -> MIN acabou de esvaziar o tabuleiro -> MAX venceu (+1.0).")
    print("  6. b e m estimados:")
    print("     Para a instancia classica [3, 4, 5]:")
    print("     - Profundidade tipica maxima m = 3 + 4 + 5 = 12 lances.")
    print("     - Fator de ramificacao b: no estado inicial sao 3 + 4 + 5 = 12 acoes.")
    print("       Conforme as pilhas diminuem, a media de acoes validas e b approx 5.")
    print("     - Espaco b^m approx 5^12 approx 2.44 x 10^8 nos no pior caso teorico sem poda.")
    print("=" * 80 + "\n")


def secao_2_verificacao_corretude():
    print("=" * 80)
    print("SECAO 2 - VERIFICACAO DE CORRETUDE ANTES DE SAIR DA AULA (ID2.2)")
    print("Teorema 1 da Aula 7: Alfa-Beta DEVE devolver exatamente o mesmo valor que Minimax.")
    print("=" * 80)

    instancias_teste = [
        ((1, 2, 2), MAX_PLAYER),
        ((1, 2, 3), MAX_PLAYER),
        ((2, 2, 2), MIN_PLAYER)
    ]

    todos_corretos = True

    for config, primeiro in instancias_teste:
        jogo = NimMisere(configuracao_inicial=config, primeiro_jogador=primeiro)
        estado = jogo.estado_inicial()

        mm = Minimax(jogo, limite_profundidade=None)
        acao_mm, val_mm, nos_mm = mm.decidir(estado)

        ab = AlfaBeta(jogo, limite_profundidade=None, ordenar_jogadas=True)
        acao_ab, val_ab, nos_ab = ab.decidir(estado)

        iguais = (val_mm == val_ab)
        if not iguais:
            todos_corretos = False

        economia = ((nos_mm - nos_ab) / nos_mm) * 100 if nos_mm > 0 else 0

        print(f"Instancia: {config} | Primeiro a jogar: {primeiro}")
        print(f"  * Minimax  -> Acao: {acao_mm} | Valor Teorico: {val_mm:+.1f} | Nos visitados: {nos_mm}")
        print(f"  * AlfaBeta -> Acao: {acao_ab} | Valor Teorico: {val_ab:+.1f} | Nos visitados: {nos_ab}")
        print(f"  * Valores identicos? {'SIM [OK]' if iguais else 'NAO [ERRO]'}")
        print(f"  * Economia de nos pela poda alfa-beta: {economia:.1f}%\n")

    if todos_corretos:
        print("[OK] PROVA DE CORRETUDE HOMOLOGADA: Alfa-Beta preserva integralmente o valor de Minimax!")
    else:
        print("[ERRO] FALHA CRITICA: Valores divergiram entre Minimax e Alfa-Beta!")
        sys.exit(1)
    print("=" * 80 + "\n")


def secao_3_experimentos():
    print("=" * 80)
    print("SECAO 3 - PROTOCOLO EXPERIMENTAL REPRODUTIVEL (ID2.3)")
    print("Parametros do protocolo:")
    print("  * Unidade de custo: NOS VISITADOS (declarada e padronizada).")
    print("  * Partidas por confronto: 50 partidas.")
    print("  * Semente do gerador de aberturas: 42 (reprodutibilidade estrita).")
    print("  * Aberturas variadas e alternancia de primeiro jogador para evitar repeticao deterministica.")
    print("  * Calibracao simetrica: busca exata em profundidade completa vs baselines padronizadas.")
    print("=" * 80)

    num_partidas = 50
    semente = 42
    aberturas = gerar_aberturas_reproduziveis(num_partidas, semente=semente)

    jogo_base = NimMisere()

    # Agentes
    ab_completo = AlfaBeta(jogo_base, limite_profundidade=None, ordenar_jogadas=True)
    ab_menor = AlfaBeta(jogo_base, limite_profundidade=2, ordenar_jogadas=True)
    aleatorio = AgenteAleatorio(semente=semente)
    otimo = AgenteOtimoNim()

    confrontos = [
        (
            "Confronto 1: Alfa-Beta (Completo) vs Agente Aleatorio",
            ab_completo, aleatorio, 'alfabeta', 'aleatorio'
        ),
        (
            "Confronto 2: Alfa-Beta (Completo) vs Agente Otimo (Nim-sum)",
            ab_completo, otimo, 'alfabeta', 'otimo'
        ),
        (
            "Confronto 3: Alfa-Beta (Completo) vs Alfa-Beta (Profundidade=2)",
            ab_completo, ab_menor, 'alfabeta', 'alfabeta'
        )
    ]

    resultados_finais = []

    for nome, ag_max, ag_min, t_max, t_min in confrontos:
        print(f"\nExecutando {nome} ({num_partidas} partidas)...")
        res = executar_bateria(nome, ag_max, ag_min, t_max, t_min, aberturas)
        resultados_finais.append(res)
        print(f"  Vitorias MAX ({t_max}): {res['vitorias_max']} ({res['pct_max']:.1f}%) | "
              f"Vitorias MIN ({t_min}): {res['vitorias_min']} ({res['pct_min']:.1f}%)")
        print(f"  Custo MAX (nos) -> Media: {res['stats_nos_max']['media']:.1f} | "
              f"Desvio: {res['stats_nos_max']['desvio']:.1f} | "
              f"Pior Caso: {res['stats_nos_max']['max']:.0f}")

    print("\n" + "=" * 80)
    print("SECAO 4 - TABELA CONSOLIDADA DE RESULTADOS (ID2.3)")
    print("=" * 80)
    cabecalho = f"{'Confronto':<48} | {'Vit. MAX':<10} | {'Vit. MIN':<10} | {'Media Nos (MAX)':<16} | {'Desvio':<10} | {'Pior Caso':<10}"
    print(cabecalho)
    print("-" * len(cabecalho))

    for r in resultados_finais:
        nome_curto = r['confronto'][:46]
        vit_max_str = f"{r['pct_max']:.1f}%"
        vit_min_str = f"{r['pct_min']:.1f}%"
        media_nos = f"{r['stats_nos_max']['media']:.1f}"
        desvio_nos = f"{r['stats_nos_max']['desvio']:.1f}"
        max_nos = f"{r['stats_nos_max']['max']:.0f}"
        print(f"{nome_curto:<48} | {vit_max_str:<10} | {vit_min_str:<10} | {media_nos:<16} | {desvio_nos:<10} | {max_nos:<10}")

    print("=" * 80 + "\n")

    print("=" * 80)
    print("SECAO 5 - DECLARACAO DE LIMITACOES E GARANTIAS AUSENTES (ID2.3)")
    print("=" * 80)
    print("Em conformidade estrita com os criterios de avaliacao (Item 134 da descricao):")
    print("1. Limitacao Teorica contra Agente Otimo:")
    print("   O Alfa-Beta em profundidade completa joga com perfeicao matematica. Contudo,")
    print("   o Nim e um jogo estritamente determinado. Se a posicao inicial for perdedora")
    print("   (isto e, Nim-sum == 0 na fase normal) e o Agente Otimo comecar ou nao errar,")
    print("   o Alfa-Beta NAO PODE vencer. A busca competitiva nao e capaz de forcar vitoria")
    print("   a partir de posicoes teoricamente perdedoras contra um adversario otimo.")
    print("2. Escalabilidade do Espaco de Estados:")
    print("   Para configuracoes com mais de 4 fileiras e >20 palitos, o fator de ramificacao")
    print("   faz com que o Minimax e Alfa-Beta completo estourem a memoria e o tempo viavel.")
    print("   Nessas configuracoes, o corte de profundidade se torna obrigatorio, perdendo a")
    print("   garantia de optimalidade global e dependendo criticamente da funcao heuristica.")
    print("3. O que NAO funcionou na calibracao heuristica preliminar:")
    print("   Tentar avaliar posicoes no Nim Misere considerando apenas a contagem total de")
    print("   palitos restantes gera lances catastroficos, pois o que dita a vitoria e a paridade")
    print("   binaria (XOR) e o numero de fileiras unitarias no endgame, nao a quantidade bruta.")
    print("=" * 80)


if __name__ == "__main__":
    secao_1_formalizacao()
    secao_2_verificacao_corretude()
    secao_3_experimentos()
