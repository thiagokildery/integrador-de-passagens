import logging
from typing import List, Optional

from models.passagem import Passagem
from converters.registry import ConverterRegistry


logger = logging.getLogger(__name__)


class IntegradorPassagens:
    def __init__(self, registry: ConverterRegistry):
        self._registry = registry
        self._erros = []

    def integrar(self, empresa_id: str, payload: dict) -> Optional[Passagem]:
        try:
            passagem = self._registry.converter_payload(empresa_id, payload)
            logger.info(
                f"Passagem integrada com sucesso: {passagem.empresa} "
                f"({passagem.origem} -> {passagem.destino})"
            )
            return passagem
        except KeyError as e:
            erro_msg = f"Empresa não registrada: {e}"
            logger.error(erro_msg)
            self._erros.append({"empresa_id": empresa_id, "payload": payload, "erro": erro_msg})
            return None
        except ValueError as e:
            erro_msg = str(e)
            logger.error(f"Payload inválido da empresa '{empresa_id}': {erro_msg}")
            self._erros.append({"empresa_id": empresa_id, "payload": payload, "erro": erro_msg})
            return None
        except Exception as e:
            erro_msg = str(e)
            logger.error(f"Erro inesperado ao integrar payload da empresa '{empresa_id}': {erro_msg}")
            self._erros.append({"empresa_id": empresa_id, "payload": payload, "erro": erro_msg})
            return None

    def integrar_todos(self, payloads: dict) -> List[Passagem]:
        passagens = []

        for empresa_id, lista_payloads in payloads.items():
            if not isinstance(lista_payloads, list):
                logger.warning(
                    f"Payloads da empresa '{empresa_id}' não são uma lista. Ignorando."
                )
                continue

            for i, payload in enumerate(lista_payloads):
                passagem = self.integrar(empresa_id, payload)
                if passagem:
                    passagens.append(passagem)
                else:
                    logger.warning(
                        f"Payload #{i + 1} da empresa '{empresa_id}' ignorado por erro."
                    )

        return passagens

    def listar_empresas_disponiveis(self) -> list:
        return self._registry.listar_empresas()

    def obter_erros(self) -> list:
        return self._erros

    def limpar_erros(self) -> None:
        self._erros = []
