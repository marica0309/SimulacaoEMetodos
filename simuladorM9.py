import heapq
import yaml
import random
from collections import deque
from gerador import NextRandom


# --- Simulador Generalizado de Rede de Filas ---
class Fila:
    def __init__(self, nome, servidores, capacidade, tempo_servico_min, tempo_servico_max):
        self.nome = nome
        self.servidores = servidores
        self.capacidade = capacidade
        self.tempo_servico_min = tempo_servico_min
        self.tempo_servico_max = tempo_servico_max
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

    def pode_aceitar_cliente(self):
        return self.estado_atual() < self.capacidade

    def tem_servidor_livre(self):
        return self.servidores_ocupados < self.servidores

class SimuladorRedeFilas:
    def __init__(self, arquivo_config):
        self.config = self.carregar_configuracao(arquivo_config)
        self.filas = {}
        self.roteamento = {}
        self.chegadas_externas = []
        self.eventos = []
        self.relogio = 0.0
        self.randoms_usados = 0
        self.limite_randoms = self.config['simulation']['max_randoms']
        self.tempo_primeira_chegada = self.config['simulation']['arrival_time']
        
        self.inicializar_filas()
        self.inicializar_roteamento()
        self.inicializar_chegadas_externas()

    def carregar_configuracao(self, arquivo):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Erro: Arquivo {arquivo} não encontrado!")
            return None
        except yaml.YAMLError as e:
            print(f"Erro ao ler arquivo YAML: {e}")
            return None

    def inicializar_filas(self):
        for nome, config in self.config['queues'].items():
            fila = Fila(
                nome=nome,
                servidores=config['servers'],
                capacidade=config['capacity'],
                tempo_servico_min=config['service_time']['min'],
                tempo_servico_max=config['service_time']['max']
            )
            self.filas[nome] = fila

    def inicializar_roteamento(self):
        if 'routing' in self.config:
            self.roteamento = self.config['routing']

    def inicializar_chegadas_externas(self):
        if 'arrivals' in self.config and 'external' in self.config['arrivals']:
            self.chegadas_externas = self.config['arrivals']['external']

    def proximo_random(self):
        if self.randoms_usados >= self.limite_randoms:
            return None
        self.randoms_usados += 1
        return NextRandom()

    def gerar_tempo_uniforme(self, min_val, max_val):
        r = self.proximo_random()
        if r is None:
            return None
        return min_val + r * (max_val - min_val)

    def gerar_tempo_servico(self, fila):
        return self.gerar_tempo_uniforme(fila.tempo_servico_min, fila.tempo_servico_max)

    def agendar_evento(self, tempo, tipo, dados):
        heapq.heappush(self.eventos, (tempo, tipo, dados))

    def selecionar_destino(self, origem):
        """Seleciona o próximo destino baseado nas probabilidades de roteamento"""
        if origem not in self.roteamento:
            return None
            
        rotas = self.roteamento[origem]
        r = self.proximo_random()
        if r is None:
            return None
            
        prob_acumulada = 0.0
        for rota in rotas:
            prob_acumulada += rota['probability']
            if r <= prob_acumulada:
                return rota['destination']
        
        # Se chegou aqui, retorna o último destino
        return rotas[-1]['destination'] if rotas else None

    def processar_chegada_externa(self, nome_fila):
        """Processa chegada de cliente externo na fila especificada"""
        fila = self.filas[nome_fila]
        
        # Agenda próxima chegada externa se ainda há randoms disponíveis
        for chegada in self.chegadas_externas:
            if chegada['queue'] == nome_fila:
                tempo_entre_chegadas = self.gerar_tempo_uniforme(
                    chegada['rate']['min'], 
                    chegada['rate']['max']
                )
                if tempo_entre_chegadas is not None:
                    proximo_tempo = self.relogio + tempo_entre_chegadas
                    self.agendar_evento(proximo_tempo, "chegada_externa", nome_fila)
                break
        
        # Processa o cliente que chegou
        self.processar_chegada_cliente(fila)

    def processar_chegada_cliente(self, fila):
        """Processa chegada de um cliente em uma fila"""
        if not fila.pode_aceitar_cliente():
            fila.clientes_perdidos += 1
            return
            
        if fila.tem_servidor_livre():
            # Cliente vai direto para o servidor
            fila.servidores_ocupados += 1
            tempo_servico = self.gerar_tempo_servico(fila)
            if tempo_servico is not None:
                tempo_saida = self.relogio + tempo_servico
                self.agendar_evento(tempo_saida, "saida", fila.nome)
        else:
            # Cliente vai para a fila de espera
            fila.fila.append(self.relogio)

    def processar_saida_cliente(self, nome_fila):
        """Processa saída de um cliente de uma fila"""
        fila = self.filas[nome_fila]
        fila.clientes_atendidos += 1
        
        # Determina próximo destino do cliente
        destino = self.selecionar_destino(nome_fila)
        
        if destino and destino != "exit" and destino in self.filas:
            # Cliente vai para outra fila
            self.processar_chegada_cliente(self.filas[destino])
        
        # Processa próximo cliente na fila (se houver)
        if fila.fila:
            fila.fila.popleft()
            tempo_servico = self.gerar_tempo_servico(fila)
            if tempo_servico is not None:
                tempo_saida = self.relogio + tempo_servico
                self.agendar_evento(tempo_saida, "saida", nome_fila)
        else:
            fila.servidores_ocupados -= 1

    def atualizar_estatisticas(self, novo_tempo):
        for fila in self.filas.values():
            fila.atualizar_estatisticas(novo_tempo)

    def rodar(self):
        """Executa a simulação da rede de filas"""
        if not self.config:
            print("Erro: Configuração não carregada!")
            return
            
        # Inicializa o relógio e as estatísticas
        self.relogio = 0.0
        for fila in self.filas.values():
            fila.tempo_anterior = self.relogio
        
        # Agenda primeira chegada externa
        for chegada in self.chegadas_externas:
            self.agendar_evento(self.tempo_primeira_chegada, "chegada_externa", chegada['queue'])
        
        print(f"Iniciando simulação com {self.limite_randoms} números aleatórios...")
        print(f"Primeira chegada no tempo: {self.tempo_primeira_chegada}")
        
        # Loop principal da simulação
        while self.eventos and self.randoms_usados < self.limite_randoms:
            tempo, tipo, dados = heapq.heappop(self.eventos)
            self.atualizar_estatisticas(tempo)
            self.relogio = tempo
            
            if tipo == "chegada_externa":
                self.processar_chegada_externa(dados)
            elif tipo == "saida":
                self.processar_saida_cliente(dados)
        
        # Atualiza estatísticas finais
        self.atualizar_estatisticas(self.relogio)
        self.imprimir_relatorio()

    def imprimir_relatorio(self):
        """Imprime o relatório final da simulação"""
        print("\n" + "="*60)
        print(f"RELATÓRIO FINAL DA SIMULAÇÃO")
        print("="*60)
        print(f"Modelo: {self.config['model']['name']}")
        print(f"Tempo global da simulação: {self.relogio:.2f}")
        print(f"Números aleatórios utilizados: {self.randoms_usados}")
        
        for nome, fila in self.filas.items():
            tempo_total = sum(fila.tempo_por_estado)
            print(f"\n--- FILA {nome.upper()} ---")
            print(f"Configuração: {fila.servidores} servidor(es), capacidade {fila.capacidade}")
            print(f"Clientes atendidos: {fila.clientes_atendidos}")
            print(f"Clientes perdidos: {fila.clientes_perdidos}")
            print(f"Tempo total na fila: {tempo_total:.2f}")
            
            print("\nDistribuição de Probabilidades por Estado:")
            for i, tempo_estado in enumerate(fila.tempo_por_estado):
                if tempo_estado > 0 or i <= fila.servidores:  # Mostra estados relevantes
                    prob = tempo_estado / self.relogio if self.relogio > 0 else 0
                    print(f"  Estado {i}: tempo = {tempo_estado:.2f}, probabilidade = {prob:.6f}")
        
        print("\n" + "="*60)


def main():
    """Função principal do simulador"""
    print("\n" + "="*60)
    print("SIMULADOR GENERALIZADO DE REDE DE FILAS")
    print("="*60)
    print("Este simulador suporta qualquer topologia de rede de filas")
    print("definida em um arquivo de configuração YAML.")
    print("\nArquivos de exemplo disponíveis:")
    print("- modelo_rede.yml (modelo da imagem fornecida)")
    
    # Solicita o arquivo de configuração
    arquivo_config = input("\nDigite o nome do arquivo de configuração (ou pressione Enter para usar 'modelo_rede.yml'): ").strip()
    
    if not arquivo_config:
        arquivo_config = "modelo_rede.yml"
    
    # Verifica se o arquivo existe
    import os
    if not os.path.exists(arquivo_config):
        print(f"Erro: Arquivo '{arquivo_config}' não encontrado!")
        print("Certifique-se de que o arquivo existe no diretório atual.")
        return
    
    # Cria e executa o simulador
    try:
        simulador = SimuladorRedeFilas(arquivo_config)
        simulador.rodar()
    except Exception as e:
        print(f"Erro durante a simulação: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
