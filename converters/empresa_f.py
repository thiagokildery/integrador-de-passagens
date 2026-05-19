from converters.base import BasePassagemConverter
from models.passagem import Passagem
from utils.date_utils import parsear_data
from utils.money_utils import parsear_valor_monetario


class EmpresaFConverter(BasePassagemConverter):

    empresa_id = "empresa_f"

    CAMPOS_OBRIGATORIOS = [
        "companhia",
        "trajeto_origem",
        "trajeto_destino",
        "data_ida",
        "data_volta",
        "pagamento",
    ]

    def converter(self, payload: dict) -> Passagem:
        self.validar_payload(payload, self.CAMPOS_OBRIGATORIOS)


        return Passagem(
            empresa=payload["companhia"],
            origem=payload["trajeto_origem"],
            destino=payload["trajeto_destino"],
            horario_saida=parsear_data(payload["data_ida"]),
            horario_chegada=parsear_data(payload["data_volta"]),
            valor=parsear_valor_monetario(payload["pagamento"]["total_reais"]),
        )