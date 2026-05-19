"""
Teste 3 — Auto-descoberta e exportação completa.

Carrega conversores e payloads automaticamente, integra tudo,
exporta os JSONs e verifica se os arquivos exportados têm
os valores corretos — não só os campos, mas os dados convertidos.

Estrutura AAA (Arrange, Act, Assert):
    - Arrange: prepara o cenário do teste
    - Act: executa a ação que se quer testar
    - Assert: verifica se o resultado é o esperado
"""

import sys
import os
import json
import tempfile
import shutil
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from converters import ConverterRegistry, descobrir_conversores
from integrador import IntegradorPassagens
from exportador import ExportadorPassagens
from models.passagem import Passagem
from utils.date_utils import parsear_data
from utils.money_utils import centavos_para_real


def descobrir_payloads(diretorio):
    """
    Descobre automaticamente todos os arquivos .json no diretório,
    igual ao app.py faz. Retorna um dict {empresa_id: [payloads]}.
    """
    payloads = {}
    if not os.path.isdir(diretorio):
        return payloads
    for nome_arquivo in sorted(os.listdir(diretorio)):
        if nome_arquivo.endswith(".json") and nome_arquivo != "invalidos.json":
            empresa_id = nome_arquivo.replace(".json", "")
            caminho = os.path.join(diretorio, nome_arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                payloads[empresa_id] = json.load(f)
    return payloads


class TestAutoDescobertaExportacao(unittest.TestCase):
    """Teste de auto-descoberta e exportação — valida que os JSONs exportados estão corretos."""

    def setUp(self):
        """Arrange: configura o integrador e descobre payloads automaticamente."""
        self.registry = ConverterRegistry()
        for conversor_cls in descobrir_conversores():
            self.registry.registrar(conversor_cls())

        self.integrador = IntegradorPassagens(self.registry)

        diretorio_data = os.path.join(os.path.dirname(__file__), "..", "data")
        self.payloads = descobrir_payloads(diretorio_data)

        self.pasta_saida = tempfile.mkdtemp()

    def tearDown(self):
        """Limpa a pasta temporária após o teste."""
        shutil.rmtree(self.pasta_saida, ignore_errors=True)

    def test_auto_descoberta_e_exportacao_completa(self):
        """
        Teste: auto-descoberta de conversores e payloads, mais exportação completa,
        devem funcionar juntos, gerando arquivos JSON com dados convertidos corretamente.

        Arrange: integra payloads descobertos automaticamente da pasta data/.
        Act: exporta por empresa e consolidado.
        Assert: arquivos JSON são gerados, cada passagem tem os 6 campos
                padronizados, e os valores exportados batem com a conversão
                esperada (datas no formato ISO, valores em reais).
        """
        # Act - integra
        passagens = self.integrador.integrar_todos(self.payloads)

        # Act - exporta
        exportador = ExportadorPassagens(self.pasta_saida)
        arquivos_por_empresa = exportador.exportar_por_empresa(passagens)
        caminho_consolidado = exportador.exportar_consolidado(passagens)

        # Assert - pelo menos um arquivo por empresa
        self.assertGreaterEqual(len(arquivos_por_empresa), 1,
                                "Deve gerar pelo menos um arquivo por empresa")

        # Assert - arquivo consolidado existe
        self.assertTrue(os.path.exists(caminho_consolidado),
                        "Arquivo consolidado deve ser gerado")

        # Assert - conteúdo do consolidado
        with open(caminho_consolidado, "r", encoding="utf-8") as f:
            dados = json.load(f)

        self.assertEqual(len(dados), len(passagens),
                         "Consolidado deve ter o mesmo número de passagens integradas")

        # Assert - cada passagem tem exatamente os 6 campos padronizados
        campos_esperados = {"empresa", "origem", "destino", "horario_saida",
                            "horario_chegada", "valor"}
        for p in dados:
            self.assertEqual(set(p.keys()), campos_esperados,
                             f"Cada passagem deve ter exatamente os campos: {campos_esperados}")
            self.assertIsInstance(p["empresa"], str)
            self.assertIsInstance(p["origem"], str)
            self.assertIsInstance(p["destino"], str)
            self.assertIsInstance(p["valor"], (int, float))
            self.assertGreater(p["valor"], 0, "Valor deve ser positivo no JSON")

        # Assert - os dados exportados batem com os objetos Passagem
        for i, passagem in enumerate(passagens):
            dado = dados[i]
            self.assertEqual(dado["empresa"], passagem.empresa,
                             "Empresa no JSON deve bater com a Passagem")
            self.assertEqual(dado["origem"], passagem.origem,
                             "Origem no JSON deve bater com a Passagem")
            self.assertEqual(dado["destino"], passagem.destino,
                             "Destino no JSON deve bater com a Passagem")
            self.assertEqual(dado["horario_saida"],
                             passagem.horario_saida.strftime("%Y-%m-%d %H:%M"),
                             "Data de saída no JSON deve bater com a Passagem formatada")
            self.assertEqual(dado["horario_chegada"],
                             passagem.horario_chegada.strftime("%Y-%m-%d %H:%M"),
                             "Data de chegada no JSON deve bater com a Passagem formatada")
            self.assertAlmostEqual(dado["valor"], passagem.valor, places=2,
                                   msg="Valor no JSON deve bater com a Passagem")

        # Assert - valida conversão de centavos para reais no JSON exportado
        # Se empresa_c existe, 25990 centavos deve virar 259.90
        if "empresa_c" in self.payloads:
            payload_c = self.payloads["empresa_c"][0]
            valor_esperado = centavos_para_real(payload_c["valor_centavos"])
            # Encontra a passagem da empresa_c no consolidado
            passagem_c = next(
                (d for d in dados if d["empresa"] == payload_c["viacao"]), None
            )
            self.assertIsNotNone(passagem_c, "Empresa C deve estar no consolidado")
            self.assertAlmostEqual(passagem_c["valor"], valor_esperado, places=2,
                                   msg=f"25990 centavos deve virar {valor_esperado} no JSON")

        # Assert - valida formatação de data BR no JSON exportado
        # Se empresa_c existe, "10/06/2026 21:00" deve virar "2026-06-10 21:00"
        if "empresa_c" in self.payloads:
            payload_c = self.payloads["empresa_c"][0]
            data_esperada = parsear_data(payload_c["horarios"]["saida"])
            passagem_c = next(
                (d for d in dados if d["empresa"] == payload_c["viacao"]), None
            )
            self.assertIsNotNone(passagem_c)
            self.assertEqual(passagem_c["horario_saida"],
                             data_esperada.strftime("%Y-%m-%d %H:%M"),
                             "Data BR com barra deve ser exportada no formato ISO")

        # Assert - cada arquivo por empresa tem dados corretos
        for nome_empresa, caminho_arquivo in arquivos_por_empresa.items():
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados_empresa = json.load(f)
            self.assertGreater(len(dados_empresa), 0,
                               f"Arquivo de {nome_empresa} deve ter pelo menos uma passagem")
            for d in dados_empresa:
                self.assertEqual(set(d.keys()), campos_esperados,
                                 f"Passagem de {nome_empresa} deve ter os campos padronizados")


if __name__ == "__main__":
    unittest.main()
