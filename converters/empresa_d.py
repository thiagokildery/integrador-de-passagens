from converters.base import BasePassagemConverter
from models.passagem import Passagem
from utils.date_utils import parsear_data
from utils.money_utils import centavos_para_real


class EmpresaDConverter(BasePassagemConverter):

    empresa_id = "empresa_d"

    CAMPOS_OBRIGATORIOS = [
        "carrier",
        "from",
        "to",
        "departure",
        "arrival",
        "fare",
    ]

    def converter(self, payload: dict) -> Passagem:
        self.validar_payload(payload, self.CAMPOS_OBRIGATORIOS)


        return Passagem(
            empresa=payload["carrier"],
            origem=payload["from"],
            destino=payload["to"],
            horario_saida=parsear_data(payload["departure"]),
            horario_chegada=parsear_data(payload["arrival"]),
            valor=centavos_para_real(payload["fare"]["amount"]),
        )