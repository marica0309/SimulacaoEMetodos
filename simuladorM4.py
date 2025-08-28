import heapq
import numpy as np
from collections import deque

class SimuladorFilaGG:
    def __init__(self, servidores=1, capacidade=5, limite_randoms=100000):
        self.servidores = servidores
        self.capacidade = capacidade
        self.limite_randoms = limite_randoms
        self.randoms_usados = 0

        self.relogio = 0.0
        self.servidores_ocupados = 0
        self.fila = deque()
        self.eventos = []

        self.tempo_por_estado = [0.0] * (capacidade + 1)
        self.tempo_anterior = 0.0
        self.clientes_atendidos = 0
        self.clientes_perdidos = 0

    def estado_atual(self):
        return self.servidores_ocupados + len(self.fila)

    def atualizar_estatisticas(self, novo_tempo):
        delta = novo_tempo - self.tempo_anterior
        estado = self.estado_atual()
        self.tempo_por_estado[estado] += delta
        self.tempo_anterior = novo_tempo

    # Eventos
    def agendar_evento(self, tempo, tipo):
        heapq.heappush(self.eventos, (tempo, tipo))

    def gerar_tempo_chegada(self):
        if self.randoms_usados >= self.limite_randoms:
            return None
        self.randoms_usados += 1
        return np.random.uniform(2, 5)  # chegada uniforme entre 2 e 5

    def gerar_tempo_atendimento(self):
        if self.randoms_usados >= self.limite_randoms:
            return None
        self.randoms_usados += 1
        return np.random.uniform(3, 5)  # serviço uniforme entre 3 e 5

    def chegada(self):
        tempo_prox = self.relogio + self.gerar_tempo_chegada()
        if tempo_prox is not None:
            self.agendar_evento(tempo_prox, "chegada")

        if self.servidores_ocupados < self.servidores:
            self.servidores_ocupados += 1
            tempo_saida = self.relogio + self.gerar_tempo_atendimento()
            if tempo_saida is not None:
                self.agendar_evento(tempo_saida, "saida")
        else:
            if len(self.fila) < self.capacidade - self.servidores:
                self.fila.append(self.relogio)
            else:
                self.clientes_perdidos += 1

    def saida(self):
        self.clientes_atendidos += 1
        if self.fila:
            self.fila.popleft()
            tempo_saida = self.relogio + self.gerar_tempo_atendimento()
            if tempo_saida is not None:
                self.agendar_evento(tempo_saida, "saida")
        else:
            self.servidores_ocupados -= 1

    def rodar(self):
        self.relogio = 2.0
        self.agendar_evento(2.0, "chegada")

        while self.eventos and self.randoms_usados < self.limite_randoms:
            tempo, tipo = heapq.heappop(self.eventos)
            self.atualizar_estatisticas(tempo)
            self.relogio = tempo

            if tipo == "chegada":
                self.chegada()
            elif tipo == "saida":
                self.saida()

        tempo_total = sum(self.tempo_por_estado)
        print(f"\nSimulação: G/G/{self.servidores}/{self.capacidade}")
        print("Distribuição de probabilidade dos estados da fila:")
        for i, t in enumerate(self.tempo_por_estado):
            prob = t / tempo_total if tempo_total > 0 else 0
            print(f"Estado {i}: tempo acumulado = {t:.2f}, probabilidade = {prob:.4f}")

        print(f"\nTempo total simulado: {tempo_total:.2f}")
        print(f"Clientes atendidos: {self.clientes_atendidos}")
        print(f"Clientes perdidos: {self.clientes_perdidos}")


if __name__ == "__main__":
    # G/G/1/5
    sim1 = SimuladorFilaGG(servidores=1, capacidade=5, limite_randoms=100000)
    sim1.rodar()

    # G/G/2/5
    sim2 = SimuladorFilaGG(servidores=2, capacidade=5, limite_randoms=100000)
    sim2.rodar()
