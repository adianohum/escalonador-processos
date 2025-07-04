import random
import time
from collections import deque
from abc import ABC, abstractmethod

#Atual

# Para implementar um novo método de escalonamento, vocês devem criar uma nova classe que herda de Escalonador e implementar o método escalonar de acordo com sua estratégia.
# Este código fornece a base para que vocês experimentem e implementem suas próprias ideias de escalonamento, mantendo a estrutura flexível e fácil de estender.

class TarefaCAV:
    def __init__(self, nome, duracao, tempo_chegada=0,prioridade=1, deadline = 2**32 -1):
        self.nome = nome            # Nome da tarefa (ex. Detecção de Obstáculo)
        self.duracao = duracao      # Tempo necessário para completar a tarefa (em segundos)
        self.prioridade = prioridade # Prioridade da tarefa (quanto menor o número, maior a prioridade)
        self.deadline = deadline     #Valor da deadline, caso não seja passado nenhum valor assume o maior valor possível para um sistema de 32 bits (daedline quase infinita)
        self.tempo_chegada = tempo_chegada
        self.tempo_restante = duracao # Tempo restante para completar a tarefa
        self.tempo_inicio = 0       # Hora em que a tarefa começa
        self.tempo_final = 0        # Hora em que a tarefa termina

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
    def __init__(self, valor_sobrecarga=None):  #Podemos atribuir agora o valor da sobrecarga
        self.tarefas = []
        self.sobrecarga_total = 0  # Sobrecarga total acumulada

        if valor_sobrecarga == None:                    #Se o valor de sobrecarga não for passado, gera um aleatório
            valor_sobrecarga = decimal_aleatorio()
        
        self.valor_sobrecarga = valor_sobrecarga

    def adicionar_tarefa(self, tarefa):
        """Adiciona uma tarefa (ação do CAV) à lista de tarefas"""
        self.tarefas.append(tarefa)

    @abstractmethod
    def escalonar(self):
        """Método que será implementado pelos alunos para o algoritmo de escalonamento"""
        pass

    def registrar_sobrecarga(self, tempo):
        """Adiciona tempo de sobrecarga ao total"""
        self.sobrecarga_total += tempo

    def exibir_sobrecarga(self):
        """Exibe a sobrecarga total acumulada"""
        print(f"valor da sobrecarga: {self.valor_sobrecarga}")  #Mostra o valor atribuído a cada ocorrência de sobrecarga
        print(f"Sobrecarga total acumulada: {self.sobrecarga_total:.2f} segundos.\n") #Mostra a sobrecarga total

# A classe base Escalonador define a estrutura para os escalonadores, incluindo um método escalonar
# que vocês deverão implementar em suas versões específicas de escalonamento (como FIFO e Round Robin).


class EscalonadorFIFO(EscalonadorCAV):
    def __init__(self, valor_sobrecarga=None):
        super().__init__(valor_sobrecarga)

    def escalonar(self):
        """Escalonamento FIFO para veículos autônomos"""
        tempo_inicial = 0
        for tarefa in self.tarefas:
            tarefa.tempo_inicio = tempo_inicial
            tempo_inicial += tarefa.duracao
            tarefa.tempo_final = tempo_inicial
            print(f"Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos.")
            time.sleep(tarefa.duracao)  # Simula a execução da tarefa

            print(f"Tarefa {tarefa.nome} finalizada.\n")

        self.exibir_sobrecarga()

# O escalonador FIFO executa os processos na ordem em que foram adicionados, sem interrupção, até que todos os processos terminem.


class EscalonadorRoundRobin(EscalonadorCAV):
    def __init__(self, quantum, valor_sobrecarga=None):
        super().__init__(valor_sobrecarga)
        self.quantum = quantum

    def escalonar(self):
        """Escalonamento Round Robin com tarefas de CAVs"""
        fila = deque(self.tarefas)
        tempo_inicial = 0
        while fila:
            tarefa = fila.popleft()
            if tarefa.tempo_restante > 0:
                tarefa.tempo_inicio = tempo_inicial
                tempo_exec = min(tarefa.tempo_restante, self.quantum)
                tarefa.tempo_restante -= tempo_exec
                tempo_inicial += tempo_exec
                print(f"Executando tarefa {tarefa.nome} por {tempo_exec} segundos.")
                time.sleep(tempo_exec)  # Simula a execução da tarefa

                # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
                self.registrar_sobrecarga(self.valor_sobrecarga)  # 0.3 segundos de sobrecarga por tarefa
                if tarefa.tempo_restante > 0:
                    fila.append(tarefa)  # Coloca a tarefa de volta na fila se não terminar
                tarefa.tempo_final = tempo_inicial
                print(f"Tarefa {tarefa.nome} finalizada ou ainda pendente.\n")

        self.exibir_sobrecarga()

# O escalonador Round Robin permite que cada processo seja executado por um tempo limitado (quantum).
# Quando o processo termina ou o quantum é atingido, o próximo processo da fila é executado.
# Se o processo não terminar no quantum, ele é colocado de volta na fila.


class EscalonadorPrioridade(EscalonadorCAV):
    def __init__(self, valor_sobrecarga=None):
        super().__init__(valor_sobrecarga)

    def escalonar(self):
        """Escalonamento por Prioridade (menor número = maior prioridade)"""
        print("Escalonamento por Prioridade:")
        # Ordena as tarefas pela prioridade
        self.tarefas.sort(key=lambda tarefa: tarefa.prioridade)
        tempo_inicial = 0
        for tarefa in self.tarefas:
            tarefa.tempo_inicio = tempo_inicial
            tempo_inicial += tarefa.duracao
            tarefa.tempo_final = tempo_inicial
            print(f"Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos com prioridade {tarefa.prioridade}.")
            time.sleep(tarefa.duracao)

            # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
            self.registrar_sobrecarga(self.valor_sobrecarga)  # 0.4 segundos de sobrecarga por tarefa
            print(f"Tarefa {tarefa.nome} finalizada.\n")

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
        TarefaCAV("Detecção de Obstáculo", random.randint(5, 10), prioridade=1),
        TarefaCAV("Planejamento de Rota", random.randint(3, 6), prioridade=2),
        TarefaCAV("Manutenção de Velocidade", random.randint(2, 5), prioridade=3),
        TarefaCAV("Comunicando com Infraestrutura", random.randint(4, 7), prioridade=1)
    ]
    tarefas.sort(key=lambda tarefa: tarefa.tempo_chegada)  #ordena de acordo com o tempo de chegada
    return tarefas

#Função para gerar um número aleatório entre 0 e 10 com uma casa decimal (pode aumentar se quiser um escopo maior de tempo de sobrecarga)
def decimal_aleatorio():
    return random.randint(1, 10)/10

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
