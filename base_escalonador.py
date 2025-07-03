import random
import time
from collections import deque
from abc import ABC, abstractmethod
import math

#Atual

# Para implementar um novo método de escalonamento, vocês devem criar uma nova classe que herda de Escalonador e implementar o método escalonar de acordo com sua estratégia.
# Este código fornece a base para que vocês experimentem e implementem suas próprias ideias de escalonamento, mantendo a estrutura flexível e fácil de estender.

class TarefaCAV:
    def __init__(self, nome, duracao, tempo_chegada, possivelmente_catastrofico, prioridade=1):
        self.nome = nome            # Nome da tarefa (ex. Detecção de Obstáculo)
        self.duracao = duracao      # Tempo necessário para completar a tarefa (em segundos)
        self.prioridade = prioridade # Prioridade da tarefa (quanto menor o número, maior a prioridade)
        self.tempo_restante = duracao # Tempo restante para completar a tarefa
        self.tempo_inicio = None       # Hora em que a tarefa começa
        self.tempo_final = None        # Hora em que a tarefa termina
        self.tempo_chegada = tempo_chegada  # Tempo em que a tarefa chega
        self.tempo_em_espera = 0    # Tempo total de espera na fila
        self.tempo_de_resposta = None # Tempo desde a chegada até a primeira execução
        self.tempo_inicio_execucao_atual = None   # Hora em que a tarefa começa a execução no tempo atual
        self.tempo_final_execucao_atual = None    # Hora em que a tarefa termina a execução no tempo atual
        self.possivelmente_catastrofico = possivelmente_catastrofico # Define se a não-realização da tarefa é possivelmente catastrófica

    def __str__(self):
        return f"Tarefa {self.nome} (Prioridade {self.prioridade}): {self.duracao} segundos"

    def executar(self, quantum):
        """Executa a tarefa por um tempo de 'quantum' ou até terminar"""
        tempo_exec = min(self.tempo_restante, quantum)
        self.tempo_restante -= tempo_exec
        return tempo_exec

# Cada processo tem um nome, um tempo total de execução (tempo_execucao),
# e um tempo restante (tempo_restante), que é decrementado conforme o processo vai sendo executado.
# O método executar(quantum) executa o processo por uma quantidade limitada de tempo (quantum) ou até ele terminar.


# Classe abstrata de Escalonador
class EscalonadorCAV(ABC):
    def __init__(self):
        self.tarefas: list[TarefaCAV] = []
        self.menor_tarefa = None
        self.sobrecarga_total = 0  # Sobrecarga total acumulada
        self.tempo_atual = 0

    def adicionar_tarefa(self, tarefa: TarefaCAV):
        """Adiciona uma tarefa (ação do CAV) à lista de tarefas"""
        self.tarefas.append(tarefa)
        if (self.menor_tarefa is None):
            self.menor_tarefa = tarefa
        else:
            if (tarefa.duracao < self.menor_tarefa.duracao):
                self.menor_tarefa = tarefa

    @abstractmethod
    def escalonar(self):
        """Método que será implementado pelos alunos para o algoritmo de escalonamento"""
        pass

    def registrar_sobrecarga(self, tempo):
        """Adiciona tempo de sobrecarga ao total"""
        self.sobrecarga_total += tempo

    def exibir_sobrecarga(self):
        """Exibe a sobrecarga total acumulada"""
        print(f"Sobrecarga total acumulada: {self.sobrecarga_total} segundos.\n")

# A classe base Escalonador define a estrutura para os escalonadores, incluindo um método escalonar
# que vocês deverão implementar em suas versões específicas de escalonamento (como FIFO e Round Robin).


class EscalonadorFIFO(EscalonadorCAV):
    def escalonar(self):
        """Escalonamento FIFO para veículos autônomos"""
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        
        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada  # Inicializa o relógio da simulação
            for tarefa in self.tarefas:
                tarefa.tempo_inicio = max(self.tempo_atual, tarefa.tempo_chegada)
                tarefa.tempo_inicio_execucao_atual = tarefa.tempo_inicio
                
                self.tempo_atual = tarefa.tempo_inicio
                print(
                    f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos. (chegada: {tarefa.tempo_chegada}s)")
                time.sleep(tarefa.duracao / 10)  # Simula a execução da tarefa 10x mais rápido
                self.tempo_atual += tarefa.duracao
                
                tarefa.tempo_final_execucao_atual = self.tempo_atual
                tarefa.tempo_final = self.tempo_atual
                tarefa.tempo_em_espera = tarefa.tempo_inicio - tarefa.tempo_chegada
                tarefa.tempo_de_resposta = tarefa.tempo_em_espera
                # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                #self.registrar_sobrecarga(0.5)  # 0.5 segundos de sobrecarga por tarefa (simulando troca de contexto)
                print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\n")

        self.exibir_sobrecarga()

# O escalonador FIFO executa os processos na ordem em que foram adicionados, sem interrupção, até que todos os processos terminem.


class EscalonadorRoundRobin(EscalonadorCAV):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def escalonar(self):
        """Escalonamento Round Robin com tarefas de CAVs"""
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        fila = deque(self.tarefas)
        
        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada
            
            while fila:
                tarefas_que_chegaram = [tarefa for tarefa in fila if tarefa.tempo_chegada <= self.tempo_atual]
                if (len(tarefas_que_chegaram) == 0):
                    self.tempo_atual = math.ceil(self.tempo_atual + 1)
                    continue
                
                tarefa = tarefas_que_chegaram[0]
                fila.remove(tarefa)
                if tarefa.tempo_restante > 0:
                    tarefa.tempo_inicio_execucao_atual = max(self.tempo_atual, tarefa.tempo_chegada)
                    
                    tarefa.tempo_inicio = tarefa.tempo_inicio_execucao_atual if tarefa.tempo_inicio is None else tarefa.tempo_inicio
                    tempo_exec = min(tarefa.tempo_restante, self.quantum)
                    
                    tarefa.tempo_em_espera += tarefa.tempo_inicio_execucao_atual - tarefa.tempo_final_execucao_atual
                    
                    print(
                        f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos por {tempo_exec} segundos. (chegada: {tarefa.tempo_chegada}s)")
                    
                    time.sleep(tempo_exec / 10)  # Simula a execução da tarefa 10x mais rapida
                    
                    
                    
                    self.tempo_atual = tarefa.tempo_inicio_execucao_atual + tempo_exec
                    tarefa.tempo_final_execucao_atual = self.tempo_atual
                    tarefa.tempo_restante -= tempo_exec
                    
                    tarefa.tempo_de_resposta = tarefa.tempo_inicio - tarefa.tempo_chegada
                    
                    
                    
                    if tarefa.tempo_restante > 0:
                        # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                        self.registrar_sobrecarga(0.3)  # 0.3 segundos de sobrecarga por tarefa
                        self.tempo_atual += 0.3
                        
                        if (fila):
                            for i in range(len(fila)):
                                if (fila[i].tempo_chegada > self.tempo_atual):
                                    fila.insert(i, tarefa)
                                    break
                                if (i == len(fila) - 1):
                                    fila.append(tarefa)
                        else:
                            fila.append(tarefa)
                        
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} ainda pendente.\n")
                    else: 
                        tarefa.tempo_final = self.tempo_atual
                        print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\n")

        self.exibir_sobrecarga()

# O escalonador Round Robin permite que cada processo seja executado por um tempo limitado (quantum).
# Quando o processo termina ou o quantum é atingido, o próximo processo da fila é executado.
# Se o processo não terminar no quantum, ele é colocado de volta na fila.


class EscalonadorPrioridade(EscalonadorCAV):
    def escalonar(self):
        """Escalonamento por Prioridade (menor número = maior prioridade)"""
        print("Escalonamento por Prioridade:")
        # Ordena as tarefas pela prioridade
        self.tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)
        fila = deque(self.tarefas)

        if (len(self.tarefas) > 0):
            self.tempo_atual = self.tarefas[0].tempo_chegada
            while (fila):
                tarefas_que_chegaram = [tarefa for tarefa in fila if tarefa.tempo_chegada <= self.tempo_atual]
                if (len(tarefas_que_chegaram) == 0):
                    self.tempo_atual += 1
                    continue
                tarefas_que_chegaram.sort(key=lambda tarefa: tarefa.prioridade)
                
                tarefa = tarefas_que_chegaram[0]
                fila.remove(tarefa)
                
                # Executando a tarefa
                tarefa.tempo_inicio = self.tempo_atual
                tarefa.tempo_inicio_execucao_atual = tarefa.tempo_inicio
                
                print(f"[{self.tempo_atual}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos com prioridade {tarefa.prioridade}. (chegada: {tarefa.tempo_chegada}s)")
                time.sleep(tarefa.duracao / 10)
                
                self.tempo_atual += tarefa.duracao
                tarefa.tempo_final = self.tempo_atual
                tarefa.tempo_de_resposta = tarefa.tempo_inicio - tarefa.tempo_chegada
                tarefa.tempo_em_espera = tarefa.tempo_de_resposta
                tarefa.tempo_final_execucao_atual = self.tempo_atual

                # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                # self.registrar_sobrecarga(0.4)  # 0.4 segundos de sobrecarga por tarefa
                print(f"[{self.tempo_atual}s] Tarefa {tarefa.nome} finalizada.\n")

        self.exibir_sobrecarga()

class CAV:
    def __init__(self, id):
        self.id = id  # Identificador único para cada CAV
        self.tarefas = []  # Lista de tarefas atribuídas a esse CAV

    def adicionar_tarefa(self, tarefa):
        self.tarefas.append(tarefa)

    def executar_tarefas(self, escalonador):
        print(f"CAV {self.id} começando a execução de tarefas...\n")
        escalonador.escalonar()
        print(f"CAV {self.id} terminou todas as suas tarefas.\n")


# Função para criar algumas tarefas fictícias
def criar_tarefas():
    tarefas = [
        TarefaCAV("Detecção de Obstáculo", random.randint(5, 10), prioridade=1, tempo_chegada=5, possivelmente_catastrofico=True),
        TarefaCAV("Planejamento de Rota", random.randint(3, 6), prioridade=2, tempo_chegada=1, possivelmente_catastrofico=False),
        TarefaCAV("Manutenção de Velocidade", random.randint(2, 5), prioridade=3, tempo_chegada=30, possivelmente_catastrofico=False),
        TarefaCAV("Comunicando com Infraestrutura", random.randint(4, 7), prioridade=1, tempo_chegada=20, possivelmente_catastrofico=False),
        TarefaCAV("Aumento de Velocidade", random.randint(2, 5), prioridade=3, tempo_chegada=1, possivelmente_catastrofico=False),
        TarefaCAV("Aumentar volume do rádio", random.randint(1, 2), prioridade=5, tempo_chegada=2, possivelmente_catastrofico=False),
        TarefaCAV("Comunicação de SOS", random.randint(10, 15), prioridade=1, tempo_chegada=22, possivelmente_catastrofico=True),
        TarefaCAV("Reconhecimento de Sinais de Trânsito", random.randint(3, 6), prioridade=2, tempo_chegada=8, possivelmente_catastrofico=False),
        TarefaCAV("Monitoramento de Ponto Cego", random.randint(4, 8), prioridade=2, tempo_chegada=12, possivelmente_catastrofico=True),
        TarefaCAV("Análise de Condições Climáticas", random.randint(2, 5), prioridade=3, tempo_chegada=15, possivelmente_catastrofico=False),
        TarefaCAV("Atualização de Mapas", random.randint(5, 9), prioridade=4, tempo_chegada=50, possivelmente_catastrofico=False),
        # TarefaCAV("Detecção de Faixa de Rodagem", random.randint(3, 6), prioridade=2, tempo_chegada=9, possivelmente_catastrofico=False),
        # TarefaCAV("Verificação de Sistemas Internos", random.randint(2, 4), prioridade=4, tempo_chegada=25, possivelmente_catastrofico=False),
        # TarefaCAV("Ajuste de Suspensão", random.randint(2, 3), prioridade=5, tempo_chegada=35, possivelmente_catastrofico=False),
        TarefaCAV("Resfriamento de Bateria", random.randint(3, 6), prioridade=3, tempo_chegada=20, possivelmente_catastrofico=False),
        # TarefaCAV("Manobra de Ultrapassagem", random.randint(6, 10), prioridade=1, tempo_chegada=11, possivelmente_catastrofico=True),
        # TarefaCAV("Redução de Velocidade", random.randint(2, 4), prioridade=2, tempo_chegada=3, possivelmente_catastrofico=False),
        TarefaCAV("Recarregamento por Indução", random.randint(5, 7), prioridade=4, tempo_chegada=90, possivelmente_catastrofico=False),
        # TarefaCAV("Monitoramento de Passageiros", random.randint(1, 2), prioridade=5, tempo_chegada=6, possivelmente_catastrofico=False),
        # TarefaCAV("Envio de Diagnóstico Remoto", random.randint(3, 6), prioridade=4, tempo_chegada=27, possivelmente_catastrofico=False),
    ]
    return tarefas


# Exemplo de uso
if __name__ == "__main__":
    # Criar algumas tarefas fictícias
    tarefas = criar_tarefas()

    # Criar um CAV
    cav = CAV(id=1)
    for t in tarefas:
        cav.adicionar_tarefa(t)

    # Criar um escalonador FIFO
    print("Simulando CAV com FIFO:\n")
    escalonador_fifo = EscalonadorFIFO()
    for t in tarefas:
        escalonador_fifo.adicionar_tarefa(t)

    simulador_fifo = CAV(id=1)
    simulador_fifo.executar_tarefas(escalonador_fifo)

    # Criar um escalonador Round Robin com quantum de 3 segundos
    print("\nSimulando CAV com Round Robin:\n")
    escalonador_rr = EscalonadorRoundRobin(quantum=3)
    for t in tarefas:
        escalonador_rr.adicionar_tarefa(t)

    simulador_rr = CAV(id=1)
    simulador_rr.executar_tarefas(escalonador_rr)

    # Criar um escalonador por Prioridade
    print("\nSimulando CAV com Escalonamento por Prioridade:\n")
    escalonador_prio = EscalonadorPrioridade()
    for t in tarefas:
        escalonador_prio.adicionar_tarefa(t)

    simulador_prio = CAV(id=1)
    simulador_prio.executar_tarefas(escalonador_prio)
