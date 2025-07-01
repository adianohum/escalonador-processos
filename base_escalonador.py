import random
import time
from collections import deque
from abc import ABC, abstractmethod
import copy

#Atual

# Para implementar um novo método de escalonamento, vocês devem criar uma nova classe que herda de Escalonador e implementar o método escalonar de acordo com sua estratégia.
# Este código fornece a base para que vocês experimentem e implementem suas próprias ideias de escalonamento, mantendo a estrutura flexível e fácil de estender.

class TarefaCAV:
    def __init__(self, nome, duracao, prioridade=1, tempo_chegada=0, deadline=None):
        self.nome = nome            # Nome da tarefa (ex. Detecção de Obstáculo)
        self.duracao = duracao      # Tempo necessário para completar a tarefa (em segundos)
        self.prioridade = prioridade # Prioridade da tarefa (quanto menor o número, maior a prioridade)
        self.tempo_chegada = tempo_chegada # Tempo em que a tarefa chega
        self.deadline = deadline # Deadline da tarefa
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
    def __init__(self):
        self.tarefas = []
        self.sobrecarga_total = 0  # Sobrecarga total acumulada

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
        print(f"Sobrecarga total acumulada: {self.sobrecarga_total:.2f} segundos.\n")

# A classe base Escalonador define a estrutura para os escalonadores, incluindo um método escalonar
# que vocês deverão implementar em suas versões específicas de escalonamento (como FIFO e Round Robin).


class EscalonadorFIFO(EscalonadorCAV):
    def escalonar(self):
        fila_tarefas = list(self.tarefas) # Assumindo que as tarefas são ordenadas por tempo de chegada
        fila_prontos = []
        tempo = 0

        while fila_tarefas or fila_prontos:
            while fila_tarefas and fila_tarefas[0].tempo_chegada <= tempo: # Move para a fila de prontas as tarefas que já chegaram
                fila_prontos.append(fila_tarefas.pop(0))

            if not fila_prontos:
                tempo = fila_tarefas[0].tempo_chegada # Se nada está pronto, avança o tempo até a próxima chegada
                continue

            tarefa = fila_prontos.pop(0)
            print(f"[{tempo}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos. (chegada: {tarefa.tempo_chegada}s)")
            tarefa.tempo_inicio = tempo
            time.sleep(tarefa.duracao) # Simula a execução da tarefa
            tempo += tarefa.duracao
            tarefa.tempo_final = tempo
            print(f"[{tempo}s] Finalizou a tarefa: {tarefa.nome}.\n")
            # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
            #self.registrar_sobrecarga(0.5)  # 0.5 segundos de sobrecarga por tarefa (simulando troca de contexto)

        self.exibir_sobrecarga()

# O escalonador FIFO executa os processos na ordem em que foram adicionados, sem interrupção, até que todos os processos terminem.


class EscalonadorRoundRobin(EscalonadorCAV):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def escalonar(self):
        fila_tarefas = list(self.tarefas)
        fila_prontos = deque()
        tempo = 0

        while fila_tarefas or fila_prontos:
            while fila_tarefas and fila_tarefas[0].tempo_chegada <= tempo: # Adiciona à fila de prontos as tarefas que chegaram até agora
                fila_prontos.append(fila_tarefas.pop(0))

            if not fila_prontos:
                tempo = fila_tarefas[0].tempo_chegada # Avança o tempo até a próxima tarefa chegar
                continue

            tarefa = fila_prontos.popleft()

            if tarefa.tempo_inicio == 0 and tempo == 0: # Registra o tempo de início se ainda não começou
                tarefa.tempo_inicio = tempo

            tempo_exec = min(tarefa.tempo_restante, self.quantum)
            print(f"[{tempo}s] Executando {tarefa.nome} por {tempo_exec} segundos. (chegada: {tarefa.tempo_chegada}s)")

            time.sleep(tempo_exec) # Simula a execução da tarefa
            tempo += tempo_exec
            tarefa.tempo_restante -= tempo_exec
            print(f"[{tempo}s] => restante: {tarefa.tempo_restante}s\n")

            # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
            self.registrar_sobrecarga(0.3)  # 0.3 segundos de sobrecarga por tarefa

            while fila_tarefas and fila_tarefas[0].tempo_chegada <= tempo: # Adiciona novas tarefas que chegaram durante esse quantum
                fila_prontos.append(fila_tarefas.pop(0))

            if tarefa.tempo_restante > 0:
                fila_prontos.append(tarefa)  # Coloca a tarefa de volta na fila se não terminar
            else:
                tarefa.tempo_final = tempo
                print(f"[{tempo}s] Finalizou tarefa {tarefa.nome}.\n")

        self.exibir_sobrecarga()


# O escalonador Round Robin permite que cada processo seja executado por um tempo limitado (quantum).
# Quando o processo termina ou o quantum é atingido, o próximo processo da fila é executado.
# Se o processo não terminar no quantum, ele é colocado de volta na fila.


class EscalonadorPrioridade(EscalonadorCAV):
    def escalonar(self):
        fila_tarefas = list(self.tarefas)
        fila_prontos = []
        tempo = 0

        while fila_tarefas or fila_prontos:
            while fila_tarefas and fila_tarefas[0].tempo_chegada <= tempo: # Move as tarefas que já chegaram para fila de prontos
                fila_prontos.append(fila_tarefas.pop(0))

            if not fila_prontos:
                tempo = fila_tarefas[0].tempo_chegada # Nenhuma tarefa pronta, avança para a próxima chegada
                continue

            fila_prontos.sort(key=lambda t: t.prioridade) # Ordena as tarefas prontas pela prioridade (menor número = maior prioridade)

            tarefa = fila_prontos.pop(0)
            print(f"[{tempo}s] Executando tarefa {tarefa.nome} de {tarefa.duracao} segundos com prioridade {tarefa.prioridade}. (chegada: {tarefa.tempo_chegada}s)")
            tarefa.tempo_inicio = tempo
            time.sleep(tarefa.duracao)
            tempo += tarefa.duracao
            tarefa.tempo_final = tempo

            # Registrando a sobrecarga, como exemplo, podemos adicionar um tempo fixo de sobrecarga
            self.registrar_sobrecarga(0.4)   # 0.4 segundos de sobrecarga por tarefa
            print(f"[{tempo}s] Finalizou a tarefa: {tarefa.nome}.\n")

        self.exibir_sobrecarga()


class EscalonadorEDF(EscalonadorCAV):
    def __init__(self, quantum):
        super().__init__()
        self.quantum = quantum

    def escalonar(self):
        fila_tarefas = sorted(self.tarefas, key=lambda t: t.tempo_chegada)
        fila_prontos = []
        tempo = 0
        tarefa_atual = None

        while fila_tarefas or fila_prontos or tarefa_atual:
            while fila_tarefas and fila_tarefas[0].tempo_chegada <= tempo: # Adiciona tarefas cujo tempo de chegada já passou
                fila_prontos.append(fila_tarefas.pop(0))

            if not tarefa_atual: # Se não há tarefa em execução, seleciona a de menor deadline
                if not fila_prontos:
                    if fila_tarefas:
                        tempo = fila_tarefas[0].tempo_chegada
                    else:
                        break
                    continue

                fila_prontos.sort(key=lambda t: t.deadline)
                tarefa_atual = fila_prontos.pop(0)
                if tarefa_atual.tempo_inicio is None:
                    tarefa_atual.tempo_inicio = tempo

            tempo_exec = min(self.quantum, tarefa_atual.tempo_restante) # Calcula quanto tempo irá executar nesta fatia (quantum ou resto)
            print(
                f"[{tempo}s] Executando {tarefa_atual.nome} por {tempo_exec}s "
                f"(chegada: {tarefa_atual.tempo_chegada}s, deadline: {tarefa_atual.deadline}s)"
            )

            time.sleep(tempo_exec) # Simula execução
            tempo += tempo_exec
            tarefa_atual.tempo_restante -= tempo_exec

            print(f"[{tempo}s] => restante: {tarefa_atual.tempo_restante}s\n") # Exibe restante após a fatia

            while fila_tarefas and fila_tarefas[0].tempo_chegada <= tempo: # Adiciona novas chegadas durante este quantum
                fila_prontos.append(fila_tarefas.pop(0))

            if fila_prontos:  # Verifica se precisa preemptar por prazo mais urgente
                fila_prontos.sort(key=lambda t: t.deadline)
                if tarefa_atual.deadline > fila_prontos[0].deadline:
                    fila_prontos.append(tarefa_atual)
                    tarefa_atual = fila_prontos.pop(0)
                    if tarefa_atual.tempo_inicio is None:
                        tarefa_atual.tempo_inicio = tempo

            if tarefa_atual and tarefa_atual.tempo_restante == 0: # Se a tarefa atual terminou, finaliza e checa deadline
                tarefa_atual.tempo_final = tempo
                print(f"[{tempo}s] Finalizou a tarefa: {tarefa_atual.nome}.")
                if tarefa_atual.tempo_final > tarefa_atual.deadline:
                    print(
                        f"Tarefa {tarefa_atual.nome} perdeu o deadline "
                        f"(deadline: {tarefa_atual.deadline}s, terminou: {tarefa_atual.tempo_final}s)\n"
                    )
                else:
                    print(
                        f"Tarefa {tarefa_atual.nome} cumpriu o deadline "
                        f"(deadline: {tarefa_atual.deadline}s, terminou: {tarefa_atual.tempo_final}s)\n"
                    )
                self.registrar_sobrecarga(0.4)
                tarefa_atual = None

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
        TarefaCAV("Detecção de Obstáculo", random.randint(5, 10), prioridade=1, tempo_chegada=0, deadline=15),
        TarefaCAV("Planejamento de Rota", random.randint(3, 6), prioridade=2, tempo_chegada=2, deadline=10),
        TarefaCAV("Manutenção de Velocidade", random.randint(2, 5), prioridade=3, tempo_chegada=5, deadline=12),
        TarefaCAV("Comunicando com Infraestrutura", random.randint(4, 7), prioridade=1, tempo_chegada=10, deadline=18)
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
    tarefas_fifo = copy.deepcopy(tarefas)
    for t in tarefas_fifo:
        escalonador_fifo.adicionar_tarefa(t)

    cav.executar_tarefas(escalonador_fifo)

    # Criar um escalonador Round Robin com quantum de 3 segundos
    print("\nSimulando CAV com Round Robin:\n")
    escalonador_rr = EscalonadorRoundRobin(quantum=3)
    tarefas_rr = copy.deepcopy(tarefas)
    for t in tarefas_rr:
        escalonador_rr.adicionar_tarefa(t)

    cav.executar_tarefas(escalonador_rr)

    # Criar um escalonador por Prioridade
    print("\nSimulando CAV com Escalonamento por Prioridade:\n")
    escalonador_prio = EscalonadorPrioridade()
    tarefas_prio = copy.deepcopy(tarefas)
    for t in tarefas_prio:
        escalonador_prio.adicionar_tarefa(t)

    cav.executar_tarefas(escalonador_prio)

    # Criar um escalonador por Deadline
    print("\nSimulando CAV com Escalonamento EDF:\n")
    escalonador_edf = EscalonadorEDF(quantum=3)
    tarefas_edf = copy.deepcopy(tarefas)
    for t in tarefas_edf:
        escalonador_edf.adicionar_tarefa(t)

    cav.executar_tarefas(escalonador_edf)
