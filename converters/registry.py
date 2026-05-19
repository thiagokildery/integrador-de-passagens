import logging
from typing import Dict, Type

from converters.base import BasePassagemConverter
from models.passagem import Passagem


logger = logging.getLogger(__name__)


class ConverterRegistry:

    def __init__(self):
        self._converters: Dict[str, BasePassagemConverter] = {}

    def registrar(self, converter: BasePassagemConverter) -> None:
        if not isinstance(converter, BasePassagemConverter):
            raise TypeError(
                f"O conversor deve herdar de BasePassagemConverter, "
                f"recebido: {type(converter).__name__}"
            )

        if not converter.empresa_id:
            raise ValueError(
                f"O conversor {type(converter).__name__} deve ter um 'empresa_id' definido."
            )

        self._converters[converter.empresa_id] = converter
        logger.info(f"Conversor registrado: {converter.empresa_id} -> {type(converter).__name__}")

    def obter(self, empresa_id: str) -> BasePassagemConverter:
        if empresa_id not in self._converters:
            raise KeyError(
                f"Nenhum conversor registrado para a empresa '{empresa_id}'. "
                f"Empresas disponíveis: {list(self._converters.keys())}"
            )
        return self._converters[empresa_id]

    def listar_empresas(self) -> list:
        return list(self._converters.keys())

    def converter_payload(self, empresa_id: str, payload: dict) -> Passagem:
        converter = self.obter(empresa_id)
        return converter.converter(payload)
