from converters.base import BasePassagemConverter
from models.passagem import Passagem
from utils.date_utils import parsear_data
from utils.money_utils import parsear_valor_monetario


class EmpresaBConverter(BasePassagemConverter):

    empresa_id = "empresa_b"

    CAMPOS_OBRIGATORIOS = [
        "nome_empresa",
        "cidade_origem",
        "cidade_destino",
        "horario_saida",
        "horario_chegada",
        "preco_passagem",
    ]

    def converter(self, payload: dict) -> Passagem:
        self.validar_payload(payload, self.CAMPOS_OBRIGATORIOS)


        return Passagem(
            empresa=payload["nome_empresa"],
            origem=payload["cidade_origem"],
            destino=payload["cidade_destino"],
            horario_saida=parsear_data(payload["horario_saida"]),
            horario_chegada=parsear_data(payload["horario_chegada"]),
            valor=parsear_valor_monetario(payload["preco_passagem"]),
        )