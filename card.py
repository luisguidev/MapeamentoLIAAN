import datetime

class PC_Card:
    def __init__(self, url, nome, gpu):
        self.url = url
        self.nome = nome
        self.gpu = gpu
        self.data_ocupado = None
        self.em_manutencao = False

    def agendar_uso(self, data_inicio, data_fim):
        self.data_ocupado = [data_inicio, data_fim]

    def esta_ocupado(self):
        if self.data_ocupado and len(self.data_ocupado) == 2:
            data_inicio, data_fim = self.data_ocupado
            agora = datetime.datetime.now()
            uma_hora = datetime.timedelta(hours=1)

            if agora > data_fim:
                self.data_ocupado = None
                return "disponivel"
            elif data_inicio <= agora < data_fim:
                return "ocupado"
            elif data_inicio - agora <= uma_hora:
                return "quase_ocupado"
        return "disponivel"

    def to_dict(self):
        return {
            "url": self.url,
            "nome": self.nome,
            "gpu": self.gpu,
            "data_ocupado": [d.isoformat() for d in self.data_ocupado] if self.data_ocupado else None,
            "em_manutencao": self.em_manutencao
        }

    @classmethod
    def from_dict(cls, data):
        data_ocupado_dt = [datetime.datetime.fromisoformat(d) for d in data["data_ocupado"]] if data["data_ocupado"] else None
        pc = cls(data["url"], data["nome"], data["gpu"])
        pc.data_ocupado = data_ocupado_dt
        pc.em_manutencao = data["em_manutencao"]
        return pc