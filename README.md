# Simulador Generalizado de Rede de Filas

Este simulador suporta qualquer topologia de rede de filas definida em um arquivo de configuração YAML.

## Requisitos

- Python 3.7+
- PyYAML (`pip install PyYAML`)
- Módulo `gerador.py` (gerador de números aleatórios)

## Como usar

1. **Executar o simulador:**
   ```bash
   python simuladorM9.py
   ```

2. **Especificar arquivo de configuração:**
   - O programa solicitará o nome do arquivo de configuração
   - Pressione Enter para usar o arquivo padrão `modelo_rede.yml`
   - Ou digite o nome de outro arquivo YAML

## Formato do arquivo de configuração YAML

```yaml
model:
  name: "Nome do Modelo"
  description: "Descrição do modelo"
  
simulation:
  arrival_time: 2.0      # Tempo da primeira chegada
  max_randoms: 100000    # Máximo de números aleatórios

queues:
  nome_fila:
    servers: 1           # Número de servidores
    capacity: 5          # Capacidade total da fila
    service_time:        # Tempo de atendimento (distribuição uniforme)
      min: 1.0
      max: 2.0

arrivals:
  external:
    - queue: nome_fila   # Fila que recebe chegadas externas
      rate:              # Taxa de chegada (distribuição uniforme)
        min: 2.0
        max: 3.0

routing:
  fila_origem:
    - destination: fila_destino    # Para onde vai o cliente
      probability: 0.8             # Probabilidade dessa rota
    - destination: exit            # Saída do sistema
      probability: 0.2
```

## Exemplo de configuração (modelo_rede.yml)

O arquivo `modelo_rede.yml` implementa o modelo da rede com 3 filas conforme a especificação:

- **Queue1**: G/G/1 (1 servidor, capacidade 1)
- **Queue2**: G/G/2/5 (2 servidores, capacidade 5)  
- **Queue3**: G/G/2/10 (2 servidores, capacidade 10)

Com roteamento probabilístico:
- Queue1 → Queue2 (80%), Queue3 (20%)
- Queue2 → Exit (20%), Queue2 (50%), Queue3 (30%)
- Queue3 → Exit (30%), Queue2 (70%)

## Saída do simulador

O simulador produz um relatório detalhado contendo:

- **Informações gerais**: Nome do modelo, tempo total, números aleatórios usados
- **Para cada fila**:
  - Configuração (servidores e capacidade)
  - Clientes atendidos e perdidos
  - Distribuição de probabilidades por estado
  - Tempo acumulado em cada estado

## Validação

O simulador foi testado com 100.000 números aleatórios, iniciando com filas vazias e primeira chegada no tempo 2.0, conforme especificado.

## Estrutura do código

- `Fila`: Classe que representa uma fila individual
- `SimuladorRedeFilas`: Classe principal que gerencia a rede de filas
- Eventos são gerenciados por uma heap (priority queue)
- Suporte a roteamento probabilístico entre filas
- Coleta automática de estatísticas de estado

## Arquivos

- `simuladorM9.py`: Código principal do simulador
- `modelo_rede.yml`: Arquivo de configuração de exemplo
- `gerador.py`: Gerador de números aleatórios (deve estar presente)

---

## Histórico de Desenvolvimento

### M2:
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
