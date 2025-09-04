import heapq
from collections import deque
from gerador import NextRandom


# --- Simulador de Filas em Tandem ---
class Fila:
    def __init__(self, servidores, capacidade):
        self.servidores = servidores
        self.capacidade = capacidade
        self.servidores_ocupados = 0
        self.fila = deque()
        self.clientes_perdidos = 0
        self.clientes_atendidos = 0
        self.tempo_por_estado = [0.0] * (capacidade + 1)
        self.tempo_anterior = 0.0

    def estado_atual(self):
        return self.servidores_ocupados + len(self.fila)

    def atualizar_estatisticas(self, novo_tempo):
        delta = novo_tempo - self.tempo_anterior
        estado = self.estado_atual()
        self.tempo_por_estado[estado] += delta
        self.tempo_anterior = novo_tempo

class SimuladorTandem:
    def __init__(self, chegada_min, chegada_max, atendimento1_min, atendimento1_max,
                 atendimento2_min, atendimento2_max, servidores1, capacidade1,
                 servidores2, capacidade2, limite_randoms=100000):
        self.chegada_min = chegada_min
        self.chegada_max = chegada_max
        self.atendimento1_min = atendimento1_min
        self.atendimento1_max = atendimento1_max
        self.atendimento2_min = atendimento2_min
        self.atendimento2_max = atendimento2_max
        self.limite_randoms = limite_randoms
        self.randoms_usados = 0

        self.fila1 = Fila(servidores1, capacidade1)
        self.fila2 = Fila(servidores2, capacidade2)
        self.eventos = []
        self.relogio = 0.0

    def proximo_random(self):
        if self.randoms_usados >= self.limite_randoms:
            return None
        self.randoms_usados += 1
        return NextRandom()

    def gerar_tempo_chegada(self):
        r = self.proximo_random()
        if r is None:
            return None
        return self.chegada_min + r * (self.chegada_max - self.chegada_min)

    def gerar_tempo_atendimento1(self):
        r = self.proximo_random()
        if r is None:
            return None
        return self.atendimento1_min + r * (self.atendimento1_max - self.atendimento1_min)

    def gerar_tempo_atendimento2(self):
        r = self.proximo_random()
        if r is None:
            return None
        return self.atendimento2_min + r * (self.atendimento2_max - self.atendimento2_min)

    def agendar_evento(self, tempo, tipo, fila):
        heapq.heappush(self.eventos, (tempo, tipo, fila))

    def chegada_fila1(self):
        tempo_chegada = self.gerar_tempo_chegada()
        if tempo_chegada is not None:
            tempo_prox = self.relogio + tempo_chegada
            self.agendar_evento(tempo_prox, "chegada1", None)

        f1 = self.fila1
        if f1.servidores_ocupados < f1.servidores:
            f1.servidores_ocupados += 1
            tempo_atend = self.gerar_tempo_atendimento1()
            if tempo_atend is not None:
                tempo_saida = self.relogio + tempo_atend
                self.agendar_evento(tempo_saida, "saida1", None)
        else:
            if len(f1.fila) < f1.capacidade - f1.servidores:
                f1.fila.append(self.relogio)
            else:
                f1.clientes_perdidos += 1

    def saida_fila1(self):
        f1 = self.fila1
        f1.clientes_atendidos += 1
        self.chegada_fila2()
        if f1.fila:
            f1.fila.popleft()
            tempo_atend = self.gerar_tempo_atendimento1()
            if tempo_atend is not None:
                tempo_saida = self.relogio + tempo_atend
                self.agendar_evento(tempo_saida, "saida1", None)
        else:
            f1.servidores_ocupados -= 1

    def chegada_fila2(self):
        f2 = self.fila2
        if f2.servidores_ocupados < f2.servidores:
            f2.servidores_ocupados += 1
            tempo_atend = self.gerar_tempo_atendimento2()
            if tempo_atend is not None:
                tempo_saida = self.relogio + tempo_atend
                self.agendar_evento(tempo_saida, "saida2", None)
        else:
            if len(f2.fila) < f2.capacidade - f2.servidores:
                f2.fila.append(self.relogio)
            else:
                f2.clientes_perdidos += 1

    def saida_fila2(self):
        f2 = self.fila2
        f2.clientes_atendidos += 1
        if f2.fila:
            f2.fila.popleft()
            tempo_atend = self.gerar_tempo_atendimento2()
            if tempo_atend is not None:
                tempo_saida = self.relogio + tempo_atend
                self.agendar_evento(tempo_saida, "saida2", None)
        else:
            f2.servidores_ocupados -= 1

    def atualizar_estatisticas(self, novo_tempo):
        self.fila1.atualizar_estatisticas(novo_tempo)
        self.fila2.atualizar_estatisticas(novo_tempo)

    def rodar(self):
        self.relogio = 1.5
        self.fila1.tempo_anterior = self.relogio
        self.fila2.tempo_anterior = self.relogio
        self.agendar_evento(self.relogio, "chegada1", None)

        while self.eventos and self.randoms_usados < self.limite_randoms:
            tempo, tipo, fila = heapq.heappop(self.eventos)
            self.atualizar_estatisticas(tempo)
            self.relogio = tempo

            if tipo == "chegada1":
                self.chegada_fila1()
            elif tipo == "saida1":
                self.saida_fila1()
            elif tipo == "saida2":
                self.saida_fila2()

        # Estatísticas finais
        tempo_total = max(sum(self.fila1.tempo_por_estado), sum(self.fila2.tempo_por_estado))
        print("\n--- Simulação de Filas em Tandem ---")
        print(f"Tempo total simulado: {tempo_total:.2f}")
        print("\nFila 1:")
        for i, t in enumerate(self.fila1.tempo_por_estado):
            prob = t / tempo_total if tempo_total > 0 else 0
            print(f"Estado {i}: tempo acumulado = {t:.2f}, probabilidade = {prob:.4f}")
        print(f"Clientes atendidos: {self.fila1.clientes_atendidos}")
        print(f"Clientes perdidos: {self.fila1.clientes_perdidos}")

        print("\nFila 2:")
        for i, t in enumerate(self.fila2.tempo_por_estado):
            prob = t / tempo_total if tempo_total > 0 else 0
            print(f"Estado {i}: tempo acumulado = {t:.2f}, probabilidade = {prob:.4f}")
        print(f"Clientes atendidos: {self.fila2.clientes_atendidos}")
        print(f"Clientes perdidos: {self.fila2.clientes_perdidos}")


def ler_parametros():
    print("Informe os parâmetros da simulação:")
    chegada_min = float(input("Tempo mínimo entre chegadas na Fila 1: "))
    chegada_max = float(input("Tempo máximo entre chegadas na Fila 1: "))
    atendimento1_min = float(input("Tempo mínimo de atendimento na Fila 1: "))
    atendimento1_max = float(input("Tempo máximo de atendimento na Fila 1: "))
    atendimento2_min = float(input("Tempo mínimo de atendimento na Fila 2: "))
    atendimento2_max = float(input("Tempo máximo de atendimento na Fila 2: "))
    servidores1 = int(input("Número de servidores na Fila 1: "))
    capacidade1 = int(input("Capacidade da Fila 1: "))
    servidores2 = int(input("Número de servidores na Fila 2: "))
    capacidade2 = int(input("Capacidade da Fila 2: "))
    return (chegada_min, chegada_max, atendimento1_min, atendimento1_max,
            atendimento2_min, atendimento2_max, servidores1, capacidade1,
            servidores2, capacidade2)


if __name__ == "__main__":
    print("\nSimulador de Filas em Tandem (M/M/s/K)")
    print("Os clientes chegam apenas na Fila 1 e passam para a Fila 2 após atendimento.")
    print("A simulação encerra ao usar 100.000 números aleatórios.")
    print("\nSugestão de parâmetros para teste rápido:")
    print("Tempo entre chegadas: 2 a 5")
    print("Atendimento Fila 1: 3 a 5")
    print("Atendimento Fila 2: 2 a 4")
    print("Servidores Fila 1: 2, Capacidade Fila 1: 5")
    print("Servidores Fila 2: 1, Capacidade Fila 2: 3")

    params = ler_parametros()
    sim = SimuladorTandem(*params, limite_randoms=100000)
    sim.rodar()
