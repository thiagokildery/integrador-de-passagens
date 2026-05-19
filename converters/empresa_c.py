from converters.base import BasePassagemConverter
from models.passagem import Passagem
from utils.date_utils import parsear_data
from utils.money_utils import centavos_para_real


class EmpresaCConverter(BasePassagemConverter):

    empresa_id = "empresa_c"

    CAMPOS_OBRIGATORIOS = [
        "viacao",
        "rota",
        "horarios",
        "valor_centavos",
    ]

    def converter(self, payload: dict) -> Passagem:
        self.validar_payload(payload, self.CAMPOS_OBRIGATORIOS)


        return Passagem(
            empresa=payload["viacao"],
            origem=payload["rota"]["inicio"],
            destino=payload["rota"]["fim"],
            horario_saida=parsear_data(payload["horarios"]["saida"]),
            horario_chegada=parsear_data(payload["horarios"]["chegada"]),
            valor=centavos_para_real(payload["valor_centavos"]),
        )