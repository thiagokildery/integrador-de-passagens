import importlib
import os
import pkgutil

from .base import BasePassagemConverter
from .registry import ConverterRegistry


def descobrir_conversores() -> list:
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


