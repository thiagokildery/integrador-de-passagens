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


class TestSistemaCompleto(unittest.TestCase):

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

    def test_integracao_completa_todas_empresas(self):
   
        passagens = self.integrador.integrar_todos(self.payloads)

  
        self.assertGreater(len(passagens), 0, "Deve retornar pelo menos uma passagem")

        
        for p in passagens:
            self.assertIsInstance(p, Passagem)
            self.assertTrue(len(p.empresa) > 0, "Empresa nao pode ser vazia")
            self.assertTrue(len(p.origem) > 0, "Origem nao pode ser vazia")
            self.assertTrue(len(p.destino) > 0, "Destino nao pode ser vazia")
            self.assertIsInstance(p.horario_saida, datetime)
            self.assertIsInstance(p.horario_chegada, datetime)
            self.assertIsInstance(p.valor, float)
            self.assertGreater(p.valor, 0, "Valor deve ser positivo")

        
        for p in passagens:
            self.assertGreater(p.horario_chegada, p.horario_saida,
                               "Chegada deve ser depois da saida")

    def test_erros_capturados_sem_interromper_sistema(self):

        payloads_com_erros = {}

        
        empresas_registradas = self.integrador.listar_empresas_disponiveis()
        if "empresa_a" in empresas_registradas:
            
            payloads_com_erros["empresa_a"] = [
                {
                    "empresa": "Rapido Norte",
                    "origem": "Fortaleza",
                    "destino": "Recife",
                    "saida": "2026-06-10 08:00",
                    "chegada": "2026-06-10 18:30",
                    "valor": 199.90,
                },
                
                {
                    "empresa": "Quebrada Ltda",
                    "origem": "Sao Paulo",
                    "saida": "2026-06-10 08:00",
                    "chegada": "2026-06-10 18:30",
                    "valor": 50.00,
                },
            ]
        if "empresa_b" in empresas_registradas:
            
            payloads_com_erros["empresa_b"] = [
                {
                    "nome_empresa": "Expresso Turismo",
                    "cidade_origem": "Curitiba",
                    "cidade_destino": "Florianopolis",
                    "horario_saida": "2026-08-01T10:00:00",
                    "horario_chegada": "2026-08-01T14:00:00",
                    "preco_passagem": {"valor": 80.00, "moeda": "USD"},
                },
            ]

       
        payloads_com_erros["empresa_x"] = [{"qualquer": "coisa"}]

       
        passagens = self.integrador.integrar_todos(payloads_com_erros)
        erros = self.integrador.obter_erros()

       
        exportador = ExportadorPassagens(self.pasta_saida)
        exportador.exportar_por_empresa(passagens)
        exportador.exportar_consolidado(passagens)
        caminho_erros = exportador.exportar_erros(erros)

        
        self.assertGreaterEqual(len(passagens), 1, "Deve haver pelo menos uma passagem valida")

       
        self.assertGreaterEqual(len(erros), 1, "Deve haver pelo menos um erro capturado")

        
        for erro in erros:
            self.assertIn("empresa_id", erro)
            self.assertIn("payload", erro)
            self.assertIn("erro", erro)

      
        self.assertTrue(os.path.exists(caminho_erros), "Arquivo de erros deve ser gerado")

        
        with open(caminho_erros, "r", encoding="utf-8") as f:
            erros_json = json.load(f)
        self.assertEqual(len(erros_json), len(erros))

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
                         "Consolidado deve ter o mesmo numero de passagens integradas")


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


if __name__ == "__main__":
    unittest.main()
