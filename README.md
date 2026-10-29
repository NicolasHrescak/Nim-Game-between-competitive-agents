# TDE2 — Busca Competitiva: Jogo do Nim Misère
**Relatório Técnico e Ficha de Projeto**  
**Indicadores:** ID2.1 (Formalização), ID2.2 (Implementação e Corretude), ID2.3 (Protocolo Experimental e Análise)

---

## 1. O Jogo Escolhido e Verificações

### Nome e Regras em Duas Linhas
O **Jogo do Nim (variante Misère)** consiste em fileiras de palitos onde dois jogadores se alternam retirando qualquer quantidade positiva de palitos de uma única fileira por turno; **quem for forçado a retirar o último palito restante no tabuleiro perde**.

### Verificação das 5 Propriedades Fundamentais
1. **Dois jogadores?** **SIM**. Dois agentes (MAX e MIN) alternam jogadas estritamente.
2. **Soma zero?** **SIM**. O jogo não possui empates; o vencedor recebe utilidade $+1.0$ e o perdedor $-1.0$ (soma $= 0$).
3. **Informação perfeita?** **SIM**. Não há variáveis ocultas; o estado exato de todas as fileiras é completamente observável por ambos os agentes a todo momento.
4. **Determinístico?** **SIM**. Não há nenhum elemento de sorteio, dados ou incerteza estocástica na transição entre estados.
5. **Finito?** **SIM**. Cada jogada legal retira obrigatoriamente pelo menos 1 palito de alguma fileira sem reposição. Se a soma inicial de palitos for $N$, a partida encerra em no máximo $N$ lances.

---

## 2. Formalização do Jogo (ID2.1 — Peso 1,0)

Os seis componentes da busca competitiva foram especificados e justificados formalmente:

### 1. Estado ($s$) e Estado Inicial ($s_0$)
- **Definição:** Um estado $s$ é formalizado como o par ordenado $s = (\vec{P}, j)$, onde:
  - $\vec{P} = (p_1, p_2, \dots, p_k)$ é uma tupla de inteiros não negativos representando a quantidade de palitos em cada fileira.
  - $j \in \{\text{MAX}, \text{MIN}\}$ representa **de quem é a vez**.
- **Justificativa obrigatória:** Sem a inclusão explícita de $j$ no estado, $\text{JOGADOR}(s)$ deixaria de ser função exclusiva do estado, quebrando a propriedade de Markov e a integridade da árvore de busca.
- **Estado Inicial ($s_0$):** Par com a configuração acordada (ex.: $\vec{P} = (3, 4, 5)$) e o jogador inicial definido ($j = \text{MAX}$).

### 2. $\text{JOGADOR}(s)$
- Função que retorna diretamente o componente da vez:
  $$\text{JOGADOR}((\vec{P}, j)) = j$$

### 3. $\text{AÇÕES}(s)$ e $\text{RESULTADO}(s, a)$
- **$\text{AÇÕES}(s)$:** Conjunto de jogadas válidas no estado $s = (\vec{P}, j)$:
  $$\text{AÇÕES}(s) = \{(i, k) \mid 1 \le i \le |\vec{P}|,\; p_i > 0,\; 1 \le k \le p_i\}$$
  Onde $i$ é o índice da fileira escolhida e $k$ é a quantidade de palitos retirados.
- **$\text{RESULTADO}(s, a)$:** Modelo de transição determinístico que subtrai $k$ palitos da fileira $i$ e alterna o turno:
  $$\text{RESULTADO}(((\dots, p_i, \dots), j), (i, k)) = ((\dots, p_i - k, \dots), \text{OPONENTE}(j))$$

### 4. $\text{TESTE-TERMINAL}(s)$
- O jogo atinge seu término quando todas as fileiras forem esvaziadas:
  $$\text{TESTE-TERMINAL}((\vec{P}, j)) \iff \sum_{i} p_i = 0$$

### 5. UTILIDADE(s, MAX)
**Ponto de vista estrito de MAX** retornado como um **único número**.

Na variante Misère, o agente que retira o último palito é declarado perdedor. Ao atingir o estado terminal com o tabuleiro vazio, $j = \text{JOGADOR}(s)$ indica quem jogaria o próximo lance (isto é, o adversário do jogador que acabou de retirar o último palito):

$$
\text{UTILIDADE}(s, \text{MAX}) =
\begin{cases}
+1.0, & \text{se } \text{JOGADOR}(s) = \text{MAX} \quad (\text{MIN retirou o último palito e perdeu}) \\
-1.0, & \text{se } \text{JOGADOR}(s) = \text{MIN} \quad (\text{MAX retirou o último palito e perdeu})
\end{cases}
$$

- Se `JOGADOR(s) == MAX`: MIN jogou por último, esvaziou o tabuleiro e foi forçado a pegar o último palito. Logo, MIN perde e **MAX vence (+1.0)**.
- Se `JOGADOR(s) == MIN`: MAX jogou por último, esvaziou o tabuleiro e foi forçado a pegar o último palito. Logo, **MAX perde (-1.0)**.

### 6. Fator de Ramificação ($b$) e Profundidade ($m$) Estimados
- Para a instância canônica $\vec{P} = (3, 4, 5)$:
  - **Profundidade máxima ($m$):** Ocorrerá se os jogadores retirarem apenas 1 palito por turno:
    $$m = \sum p_i = 3 + 4 + 5 = 12 \text{ lances}$$
  - **Fator de ramificação inicial:** No primeiro lance, há $3 + 4 + 5 = 12$ jogadas possíveis.
  - **Fator de ramificação médio ($b$):** Conforme as pilhas diminuem e fileiras são eliminadas, o número médio de jogadas válidas é aproximadamente $b \approx 5$.
  - **Tamanho do espaço de busca teórico ($b^m$):**
    $$b^m \approx 5^{12} \approx 244.140.625 \text{ nós no pior caso sem poda}$$

---

## 3. Implementação e Prova de Corretude (ID2.2 — Peso 1,0)

### Ordenação de Jogadas (Heurística Barata)
Para maximizar os cortes alfa e beta sem sobrecarga computacional excessiva, as ações candidatas em cada nó são ordenadas lexicograficamente segundo dois critérios prioritários:
1. **Prioridade Nim-sum:** Jogadas que transicionam o tabuleiro para uma posição com soma XOR nula ($\text{Nim-sum} = 0$) são colocadas em primeiro lugar, pois são teoricamente posições seguras que forçam derrotas do adversário.
2. **Critério Secundário de Tamanho:** Em caso de empate, priorizam-se jogadas que removem maior quantidade de palitos, acelerando a chegada aos nós folhas da árvore de busca.

### Função de Avaliação Heurística (Corte de Profundidade)
Para buscas com profundidade limitada, o estado não-terminal é avaliado no intervalo $[-1.0, +1.0]$ pela função $\text{AVALIAÇÃO}(s)$:
- Se existirem duas ou mais fileiras com tamanho $> 1$ (Fase Normal): atribui-se $+0.8$ para o jogador da vez se $\text{Nim-sum} \ne 0$ e $-0.8$ se $\text{Nim-sum} = 0$.
- Se restar exatamente uma fileira com tamanho $> 1$ (Fase de Emboscada): atribui-se $+0.95$ ao jogador da vez, pois ele tem o controle imediato para ditar a vitória forçando número ímpar de palitos unitários.
- Se todas as fileiras forem unitárias: o valor é $+1.0$ se a paridade de unitárias for par e $-1.0$ se for ímpar.
- O valor final é convertido para a perspectiva de MAX multiplicando por $+1$ se $\text{JOGADOR}(s) = \text{MAX}$ ou por $-1$ se for MIN.

### Verificação de Corretude: Minimax vs. Alfa-Beta (Teorema 1 da Aula 7)
A tabela a seguir apresenta os resultados medidos diretamente pela execução do script `main.py`, comprovando que a Poda Alfa-Beta não introduz distorções de valor em profundidade completa:

| Instância Testada | Primeiro Jogador | Valor Minimax | Valor Alfa-Beta | Valores Idênticos? | Nós Minimax | Nós Alfa-Beta | Redução de Custo |
|---|---|---|---|---|---|---|---|
| `(1, 2, 2)` | MAX | **+1.0** | **+1.0** | **SIM ✓** | 149 nós | 49 nós | **67.1%** |
| `(1, 2, 3)` | MAX | **-1.0** | **-1.0** | **SIM ✓** | 446 nós | 108 nós | **75.8%** |
| `(2, 2, 2)` | MIN | **-1.0** | **-1.0** | **SIM ✓** | 549 nós | 89 nós | **83.8%** |

> **Conclusão:** O Teorema 1 é rigorosamente verificado: em todas as instâncias os valores coincidem perfeitamente, com o Alfa-Beta reduzindo até **83.8%** do número de nós visitados.

---

## 4. Protocolo Experimental Reprodutível (ID2.3 — Peso 1,0)

### Definições Obrigatórias do Protocolo
- **Unidade de Custo Padronizada:** **Nós visitados na árvore de busca**. Não se utiliza segundos, milissegundos ou iterações.
- **Controle de Simetria e Não-Repetição:** Para resolver a armadilha de dois agentes determinísticos repetirem eternamente a mesma partida, foi implementado o gerador `gerar_aberturas_reproduziveis()` que:
  1. Utiliza a semente pseudoaleatória `seed = 42`.
  2. Varia sistematicamente a quantidade de palitos das 3 fileiras iniciais.
  3. Alterna rigidamente quem inicia a partida (partidas pares iniciam com MAX, partidas ímpares com MIN).
- **Volume:** 50 partidas completas para cada um dos 3 confrontos obrigatórios (150 partidas no total).

---

## 5. Análise de Resultados (ID2.3 — Peso 1,0)

### Tabela Comparativa de Desempenho

| Confronto | Vitórias MAX | Vitórias MIN | Custo Médio Nós (MAX) | Desvio Padrão | Pior Caso (Máx Nós) |
|---|---|---|---|---|---|
| **Confronto 1:** Alfa-Beta (Completo) vs. **Agente Aleatório** | **96.0%** (48/50) | 4.0% (2/50) | 336.0 | 581.9 | 3664 |
| **Confronto 2:** Alfa-Beta (Completo) vs. **Agente Ótimo (Nim-sum)** | **46.0%** (23/50) | 54.0% (27/50) | 357.0 | 618.0 | 3824 |
| **Confronto 3:** Alfa-Beta (Completo) vs. **Alfa-Beta (Profundidade = 2)** | **46.0%** (23/50) | 54.0% (27/50) | 321.6 | 584.7 | 3705 |

### Discussão dos Resultados
1. **Contra o Agente Aleatório (Baseline Trivial):** O Alfa-Beta em profundidade completa venceu 96.0% das partidas. As duas derrotas (4.0%) ocorreram em configurações iniciais onde a posição era matematicamente perdedora para o jogador inicial e o adversário aleatório acertou por puro acaso a única jogada que preservava a vitória.
2. **Contra o Agente Ótimo:** Como o Nim Misère é um jogo resolvido com informação perfeita e sem sorte, a vitória depende exclusivamente da posição inicial e de quem tem o primeiro lance. Quando a abertura inicial gerada é teoricamente vencedora para quem começa, quem começou vence. O equilíbrio 46% vs 54% reflete com precisão matemática a distribuição aleatória das posições iniciais $P$-positions vs $N$-positions.

---

## 6. Declaração Obrigatória de Limitações e Garantias Ausentes

Em cumprimento estrito aos critérios de avaliação da disciplina (Item 134 da descrição):

1. **Ausência de Garantia contra Posições Perdedoras:**
   O algoritmo Alfa-Beta com profundidade completa encontra a jogada minimax ótima. Entretanto, se a configuração inicial do tabuleiro for uma posição perdedora (isto é, $\text{Nim-sum} = 0$ na fase normal) e o adversário jogar de forma ótima, **o Alfa-Beta não tem garantia alguma de vitória**. Busca heurística e poda alfa-beta não criam vantagens em posições determinísticas comprovadamente perdedoras.
2. **Inviabilidade de Escalabilidade para Tabuleiros Grandes:**
   Para jogos com mais de 4 fileiras e dezenas de palitos (ex.: 5 fileiras de 15 palitos), o número de nós explode exponencialmente ($b^m \gg 10^{15}$). A busca completa torna-se computacionalmente inviável em tempo real, exigindo corte de profundidade que sacrifica a garantia de optimalidade.
3. **Falha na Calibração Heurística Ingênua (O que NÃO funcionou):**
   Durante a calibração inicial, testou-se uma função heurística baseada na simples contagem linear de palitos totais no tabuleiro. **Essa heurística falhou catastroficamente**, pois no Nim Misère a vantagem depende da paridade das potências binárias das pilhas e da regra de inversão nas fileiras unitárias no endgame, e não da quantidade de palitos restante.

---

## 7. Como Reproduzir e Executar

Para executar os testes e reproduzir todas as tabelas e provas de corretude:

```bash
python main.py
```

### Arquivos do Projeto:
- `nim_game.py`: Modelagem formal do jogo, regras, utilidade e heurística de avaliação.
- `minimax.py`: Algoritmo Minimax com contador de nós visitados.
- `alfabeta.py`: Algoritmo Alfa-Beta com poda, ordenação de jogadas e contador de nós.
- `agente_aleatorio.py`: Agente que joga uniformemente ao acaso (linha de base trivial).
- `agente_otimo.py`: Agente analítico ótimo baseado no teorema de Bouton e transição Misère.
- `experimento.py`: Protocolo de testes com aberturas controladas, alternância e métricas.
- `main.py`: Script central de execução e apresentação dos dados.
