import heapq
import numpy as np
from gerador import NextRandom  # importa o LCG do outro arquivo

class SimuladorFila:
    def __init__(self, taxa_chegada, taxa_atendimento, capacidade=10):
        self.taxa_chegada = taxa_chegada
        self.taxa_atendimento = taxa_atendimento
        self.relogio = 0.0
        self.servidor_ocupado = False
        self.fila = []
        self.eventos = [] 
        self.num_atendidos = 0
        self.capacidade = capacidade

        # Estatísticas por estado (0, 1, 2, ..., capacidade)
        self.tempo_por_estado = [0.0] * (capacidade + 2)
        self.tempo_anterior = 0.0

    def estado_atual(self):
        """Retorna o número de clientes no sistema (fila + servidor)"""
        return len(self.fila) + (1 if self.servidor_ocupado else 0)

    def atualizar_estatisticas(self, novo_tempo):
        """Acumula o tempo no estado atual até o próximo evento."""
        delta = novo_tempo - self.tempo_anterior
        estado = self.estado_atual()
        self.tempo_por_estado[estado] += delta
        self.tempo_anterior = novo_tempo

    def agendar_evento(self, tempo, tipo):
        heapq.heappush(self.eventos, (tempo, tipo))

    def gerar_tempo_exponencial(self, taxa):
        global count
        count -= 1
        u = NextRandom()
        return - (1.0 / taxa) * np.log(1 - u)

    def chegada(self):
        # agenda próxima chegada
        tempo_prox = self.relogio + self.gerar_tempo_exponencial(self.taxa_chegada)
        self.agendar_evento(tempo_prox, "chegada")

        # agenda saída ou entra na fila
        if not self.servidor_ocupado:
            self.servidor_ocupado = True
            tempo_saida = self.relogio + self.gerar_tempo_exponencial(self.taxa_atendimento)
            self.agendar_evento(tempo_saida, "saida")
        else:
            if len(self.fila) < self.capacidade:
                self.fila.append(self.relogio)  # cliente entra na fila

    def saida(self):
        self.num_atendidos += 1
        if self.fila:
            self.fila.pop(0)
            tempo_saida = self.relogio + self.gerar_tempo_exponencial(self.taxa_atendimento)
            self.agendar_evento(tempo_saida, "saida")
        else:
            self.servidor_ocupado = False

    def rodar(self, limite_randoms):
        global count
        count = limite_randoms

        # agenda primeira chegada
        primeira_chegada = self.gerar_tempo_exponencial(self.taxa_chegada)
        self.agendar_evento(primeira_chegada, "chegada")

        while self.eventos and count > 0:
            tempo, tipo = heapq.heappop(self.eventos)
            self.atualizar_estatisticas(tempo)
            self.relogio = tempo

            if tipo == "chegada":
                self.chegada()
            elif tipo == "saida":
                self.saida()

        # Estatísticas finais
        tempo_total = sum(self.tempo_por_estado)
        print("Distribuição de probabilidade dos estados da fila:")
        for i, t in enumerate(self.tempo_por_estado):
            prob = t / tempo_total if tempo_total > 0 else 0
            print(f"Estado {i}: tempo acumulado = {t:.2f}, probabilidade = {prob:.4f}")

        print(f"\nTempo total simulado: {tempo_total:.2f}")
        print(f"Clientes atendidos: {self.num_atendidos}")

if __name__ == "__main__":
    sim = SimuladorFila(taxa_chegada=1/5, taxa_atendimento=1/4, capacidade=10)
    sim.rodar(limite_randoms=100000)
