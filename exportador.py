import json
import os
import logging
from typing import List

from models.passagem import Passagem


logger = logging.getLogger(__name__)


class ExportadorPassagens:
    def __init__(self, pasta_saida: str):
        self._pasta_saida = pasta_saida
        os.makedirs(pasta_saida, exist_ok=True)

    def exportar_por_empresa(self, passagens: List[Passagem]) -> dict:
        passagens_por_empresa = {}
        for p in passagens:
            nome_arquivo = p.empresa.lower().replace(" ", "_").replace("ã", "a").replace("ç", "c").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            if nome_arquivo not in passagens_por_empresa:
                passagens_por_empresa[nome_arquivo] = []
            passagens_por_empresa[nome_arquivo].append(p.to_dict())

        arquivos_gerados = {}

        for nome_empresa, lista in passagens_por_empresa.items():
            caminho = os.path.join(self._pasta_saida, f"{nome_empresa}_saida.json")
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(lista, f, ensure_ascii=False, indent=4)
            arquivos_gerados[nome_empresa] = caminho
            logger.info(f"Exportado: {caminho} ({len(lista)} passagem(ns))")

        return arquivos_gerados

    def exportar_consolidado(self, passagens: List[Passagem]) -> str:
        dados = [p.to_dict() for p in passagens]
        caminho = os.path.join(self._pasta_saida, "todas_passagens.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        logger.info(f"Exportado consolidado: {caminho} ({len(dados)} passagem(ns))")
        return caminho

    def exportar_erros(self, erros: list) -> str:
        if not erros:
            return ""

        caminho = os.path.join(self._pasta_saida, "payloads_invalidos.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(erros, f, ensure_ascii=False, indent=4)
        logger.info(f"Exportado erros: {caminho} ({len(erros)} erro(s))")
        return caminho
