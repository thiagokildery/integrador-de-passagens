from converters.base import BasePassagemConverter
from models.passagem import Passagem
from utils.date_utils import parsear_data
from utils.money_utils import parsear_valor_monetario


class EmpresaAConverter(BasePassagemConverter):

    empresa_id = "empresa_a"

    CAMPOS_OBRIGATORIOS = [
        "empresa",
        "origem",
        "destino",
        "saida",
        "chegada",
        "valor",
    ]

    def converter(self, payload: dict) -> Passagem:
        self.validar_payload(payload, self.CAMPOS_OBRIGATORIOS)


        return Passagem(
            empresa=payload["empresa"],
            origem=payload["origem"],
            destino=payload["destino"],
            horario_saida=parsear_data(payload["saida"]),
            horario_chegada=parsear_data(payload["chegada"]),
            valor=parsear_valor_monetario(payload["valor"]),
        )