from datetime import datetime


class Passagem:
    def __init__(
        self,
        empresa: str,
        origem: str,
        destino: str,
        horario_saida: datetime,
        horario_chegada: datetime,
        valor: float,
    ):
        self.empresa = empresa
        self.origem = origem
        self.destino = destino
        self.horario_saida = horario_saida
        self.horario_chegada = horario_chegada
        self.valor = valor

    def __repr__(self) -> str:
        return (
            f"Passagem("
            f"empresa='{self.empresa}', "
            f"origem='{self.origem}', "
            f"destino='{self.destino}', "
            f"horario_saida='{self.horario_saida.strftime('%Y-%m-%d %H:%M')}', "
            f"horario_chegada='{self.horario_chegada.strftime('%Y-%m-%d %H:%M')}', "
            f"valor={self.valor:.2f}"
            f")"
        )

    def to_dict(self) -> dict:
        return {
            "empresa": self.empresa,
            "origem": self.origem,
            "destino": self.destino,
            "horario_saida": self.horario_saida.strftime("%Y-%m-%d %H:%M"),
            "horario_chegada": self.horario_chegada.strftime("%Y-%m-%d %H:%M"),
            "valor": round(self.valor, 2),
        }

    def __eq__(self, other) -> bool:
        if not isinstance(other, Passagem):
            return False
        return (
            self.empresa == other.empresa
            and self.origem == other.origem
            and self.destino == other.destino
            and self.horario_saida == other.horario_saida
            and self.horario_chegada == other.horario_chegada
            and abs(self.valor - other.valor) < 0.01
        )
