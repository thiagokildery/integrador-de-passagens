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
    def setUp(self):
        self.registry = ConverterRegistry()
        for conversor_cls in descobrir_conversores():
            self.registry.registrar(conversor_cls())

        self.integrador = IntegradorPassagens(self.registry)

        diretorio_data = os.path.join(os.path.dirname(__file__), "..", "data")
        self.payloads = descobrir_payloads(diretorio_data)

        self.pasta_saida = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.pasta_saida, ignore_errors=True)

    def test_auto_descoberta_e_exportacao_completa(self):
        passagens = self.integrador.integrar_todos(self.payloads)

        
        exportador = ExportadorPassagens(self.pasta_saida)
        arquivos_por_empresa = exportador.exportar_por_empresa(passagens)
        caminho_consolidado = exportador.exportar_consolidado(passagens)

      
        self.assertGreaterEqual(len(arquivos_por_empresa), 1,
                                "Deve gerar pelo menos um arquivo por empresa")

       
        self.assertTrue(os.path.exists(caminho_consolidado),
                        "Arquivo consolidado deve ser gerado")

        with open(caminho_consolidado, "r", encoding="utf-8") as f:
            dados = json.load(f)

        self.assertEqual(len(dados), len(passagens),
                         "Consolidado deve ter o mesmo número de passagens integradas")

        
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

        if "empresa_c" in self.payloads:
            payload_c = self.payloads["empresa_c"][0]
            valor_esperado = centavos_para_real(payload_c["valor_centavos"])
            
            passagem_c = next(
                (d for d in dados if d["empresa"] == payload_c["viacao"]), None
            )
            self.assertIsNotNone(passagem_c, "Empresa C deve estar no consolidado")
            self.assertAlmostEqual(passagem_c["valor"], valor_esperado, places=2,
                                   msg=f"25990 centavos deve virar {valor_esperado} no JSON")

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
