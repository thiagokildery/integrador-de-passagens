from abc import ABC, abstractmethod
from models.passagem import Passagem


class BasePassagemConverter(ABC):

    empresa_id: str = ""

    @abstractmethod
    def converter(self, payload: dict) -> Passagem:
        pass

    def validar_payload(self, payload: dict, campos_obrigatorios: list) -> None:
        if payload is None:
            raise ValueError("Payload não pode ser None.")

        if not isinstance(payload, dict):
            raise ValueError(
                f"Payload deve ser um dicionário, recebido: {type(payload).__name__}"
            )

        campos_ausentes = [c for c in campos_obrigatorios if c not in payload]
        if campos_ausentes:
            raise ValueError(
                f"Campos obrigatórios ausentes no payload: {campos_ausentes}"
            )
