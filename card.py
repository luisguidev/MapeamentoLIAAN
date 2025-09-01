import datetime

class PC_Card:
    def __init__(self, url, nome, gpu):
        self.url = url
        self.nome = nome
        self.gpu = gpu
        self.agendamentos = []  # Agora é uma lista de tuplas (data_inicio, data_fim)
        self.em_manutencao = False

    def agendar_uso(self, data_inicio, data_fim):
        # O agendamento deve ser uma tupla para facilitar a ordenação e salvamento
        self.agendamentos.append((data_inicio, data_fim))
        self.agendamentos.sort() # Mantém os agendamentos em ordem cronológica

    def esta_ocupado(self, agora):
        """Verifica o status atual do PC e o próximo agendamento."""
        agora = datetime.datetime.now()
        uma_hora = datetime.timedelta(hours=1)
        
        proximo_agendamento = None
        for inicio, fim in self.agendamentos:
            # 1. Checa se o PC está ocupado agora
            if inicio <= agora < fim:
                return "ocupado", "Ocupado agora" # Card vermelho

            # 2. Encontra o próximo agendamento válido no futuro
            if inicio > agora and (proximo_agendamento is None or inicio < proximo_agendamento[0]):
                proximo_agendamento = (inicio, fim)
        
        # 3. Define a cor com base no próximo agendamento
        if proximo_agendamento:
            proximo_inicio = proximo_agendamento[0]
            if proximo_inicio - agora <= uma_hora:
                return "quase_ocupado", f"Ocupado em {proximo_inicio.strftime('%H:%M')}" # Card amarelo
            else:
                return "disponivel", f"Próximo em {proximo_inicio.strftime('%d/%m %H:%M')}" # Card verde
        
        return "disponivel", "N/A" # Card verde

    def to_dict(self):
        return {
            "url": self.url,
            "nome": self.nome,
            "gpu": self.gpu,
            "agendamentos": [(d[0].isoformat(), d[1].isoformat()) for d in self.agendamentos],
            "em_manutencao": self.em_manutencao
        }

    @classmethod
    def from_dict(cls, data):
        pc = cls(data["url"], data["nome"], data["gpu"])
        for inicio_str, fim_str in data["agendamentos"]:
            inicio = datetime.datetime.fromisoformat(inicio_str)
            fim = datetime.datetime.fromisoformat(fim_str)
            pc.agendar_uso(inicio, fim)
        pc.em_manutencao = data["em_manutencao"]
        return pc