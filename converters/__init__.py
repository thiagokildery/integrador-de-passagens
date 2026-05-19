"""
Pacote de conversores de payload.

Descobre e registra automaticamente todos os conversores que herdam
de BasePassagemConverter neste pacote. Para adicionar uma nova empresa,
basta criar um arquivo empresa_x.py com uma classe que herda de
BasePassagemConverter — nenhuma outra alteracao e necessaria.
"""

import importlib
import os
import pkgutil

from .base import BasePassagemConverter
from .registry import ConverterRegistry


def descobrir_conversores() -> list:
    """
    Descobre automaticamente todas as subclasses de BasePassagemConverter
    neste pacote.

    Percorre todos os modulos da pasta converters/ e encontra classes
    que herdam de BasePassagemConverter, ignorando a propria classe base.

    Returns:
        list: Lista de classes de conversores encontradas.
    """
    conversores = []
    pacote_dir = os.path.dirname(__file__)

    for _, nome_modulo, _ in pkgutil.iter_modules([pacote_dir]):
        if nome_modulo in ("base", "registry"):
            continue

        modulo = importlib.import_module(f".{nome_modulo}", package=__name__)

        for nome_atributo in dir(modulo):
            atributo = getattr(modulo, nome_atributo)
            if (
                isinstance(atributo, type)
                and issubclass(atributo, BasePassagemConverter)
                and atributo is not BasePassagemConverter
            ):
                conversores.append(atributo)

    return conversores


