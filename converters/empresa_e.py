from converters.base import BasePassagemConverter
from models.passagem import Passagem
from utils.date_utils import parsear_data
from utils.money_utils import centavos_para_real


class EmpresaEConverter(BasePassagemConverter):

    empresa_id = "empresa_e"

    CAMPOS_OBRIGATORIOS = [
        "nome_comercial",
        "trajeto",
        "partida",
        "retorno",
        "preco_centavos",
    ]

    def converter(self, payload: dict) -> Passagem:
        self.validar_payload(payload, self.CAMPOS_OBRIGATORIOS)


        return Passagem(
            empresa=payload["nome_comercial"],
            origem=payload["trajeto"]["partida"],
            destino=payload["trajeto"]["chegada"],
            horario_saida=parsear_data(payload["partida"]),
            horario_chegada=parsear_data(payload["retorno"]),
            valor=centavos_para_real(payload["preco_centavos"]),
        )