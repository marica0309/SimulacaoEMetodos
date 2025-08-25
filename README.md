# **Simulação e Métodos analíticos**

## M2:
Desenvolver um gerador responsável por fornecer os números pseudoaleatórios normalizados entre 0 e 1.

    início:
        definir parâmetros do método da congruência linear:
            a ← multiplicador
            c ← incremento
            M ← módulo
            seed ← valor inicial

        definir variável global:
            último ← seed

        procedimento NextRandom():
            último ← (a * último + c) mod M
            retornar último / M    # número entre 0 e 1

        programa principal:
            criar lista vazia dados
            para i de 1 até N:
                gerar novo número ← NextRandom()
                adicionar novo
    fim

## M4: 
Implementar um simulador de filas orientado a eventos utilizando números pseudoaleatórios gerados pelo método da congruência linear (LCG).

    início:
        inicializar variáveis globais
        count ← limite de números pseudoaleatórios

        criar escalonador de eventos vazio
        agenda primeira chegada

        enquanto (existirem eventos) e (count > 0) faça:
            evento ← remover próximo evento do escalonador
            atualizar estatísticas (tempo acumulado no estado atual)
            avançar relógio para tempo do evento

            se evento for CHEGADA então
                agenda próxima chegada
                se servidor estiver livre então
                    ocupar servidor
                    agenda SAÍDA
                senão se fila tiver espaço então
                    cliente entra na fila
                fim se
            fim se

            se evento for SAÍDA então
                liberar servidor ou atender próximo da fila
                se fila não estiver vazia então
                    agenda próxima SAÍDA
                fim se
            fim se
        fim enquanto

        calcular distribuição de probabilidade:
            para cada estado k:
                prob[k] ← tempo_estado[k] / tempo_total

        imprimir resultados:
            - tempo acumulado em cada estado
            - distribuição de probabilidades
            - número de clientes atendidos
    fim
