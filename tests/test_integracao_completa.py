import sys
import os
import json
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from converters import ConverterRegistry, descobrir_conversores
from integrador import IntegradorPassagens
from models.passagem import Passagem
from utils.date_utils import parsear_data
from utils.money_utils import parsear_valor_monetario, centavos_para_real


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


class TestIntegracaoCompleta(unittest.TestCase):
    def setUp(self):

        self.registry = ConverterRegistry()
        for conversor_cls in descobrir_conversores():
            self.registry.registrar(conversor_cls())

        self.integrador = IntegradorPassagens(self.registry)

        diretorio_data = os.path.join(os.path.dirname(__file__), "..", "data")
        self.payloads = descobrir_payloads(diretorio_data)

    def test_integracao_completa_todas_empresas(self):
        passagens = self.integrador.integrar_todos(self.payloads)

        self.assertGreater(len(passagens), 0, "Deve retornar pelo menos uma passagem")

        for p in passagens:
            self.assertIsInstance(p, Passagem)
            self.assertTrue(len(p.empresa) > 0, "Empresa não pode ser vazia")
            self.assertTrue(len(p.origem) > 0, "Origem não pode ser vazia")
            self.assertTrue(len(p.destino) > 0, "Destino não pode ser vazio")
            self.assertIsInstance(p.horario_saida, datetime)
            self.assertIsInstance(p.horario_chegada, datetime)
            self.assertIsInstance(p.valor, float)
            self.assertGreater(p.valor, 0, "Valor deve ser positivo")


        for p in passagens:
            self.assertGreater(p.horario_chegada, p.horario_saida,
                               "Chegada deve ser depois da saída")


        if "empresa_a" in self.payloads:
            payload = self.payloads["empresa_a"][0]
            p = self.integrador.integrar("empresa_a", payload)
            self.assertIsNotNone(p)
            self.assertEqual(p.empresa, payload["empresa"])
            self.assertEqual(p.origem, payload["origem"])
            self.assertEqual(p.destino, payload["destino"])
            self.assertEqual(p.horario_saida, parsear_data(payload["saida"]))
            self.assertEqual(p.horario_chegada, parsear_data(payload["chegada"]))
            self.assertAlmostEqual(p.valor, payload["valor"], places=2)

        if "empresa_b" in self.payloads:
            payload = self.payloads["empresa_b"][0]
            p = self.integrador.integrar("empresa_b", payload)
            self.assertIsNotNone(p)
            self.assertEqual(p.empresa, payload["nome_empresa"])
            self.assertEqual(p.origem, payload["cidade_origem"])
            self.assertEqual(p.destino, payload["cidade_destino"])
            self.assertEqual(p.horario_saida, parsear_data(payload["horario_saida"]))
            self.assertEqual(p.horario_chegada, parsear_data(payload["horario_chegada"]))
            self.assertAlmostEqual(p.valor, payload["preco_passagem"]["valor"], places=2)

        if "empresa_c" in self.payloads:
            payload = self.payloads["empresa_c"][0]
            p = self.integrador.integrar("empresa_c", payload)
            self.assertIsNotNone(p)
            self.assertEqual(p.empresa, payload["viacao"])
            self.assertEqual(p.origem, payload["rota"]["inicio"])
            self.assertEqual(p.destino, payload["rota"]["fim"])
            self.assertEqual(p.horario_saida, parsear_data(payload["horarios"]["saida"]))
            self.assertEqual(p.horario_chegada, parsear_data(payload["horarios"]["chegada"]))
            self.assertAlmostEqual(p.valor, centavos_para_real(payload["valor_centavos"]), places=2)

        if "empresa_d" in self.payloads:
            payload = self.payloads["empresa_d"][0]
            p = self.integrador.integrar("empresa_d", payload)
            self.assertIsNotNone(p)
            self.assertEqual(p.empresa, payload["carrier"])
            self.assertEqual(p.origem, payload["from"])
            self.assertEqual(p.destino, payload["to"])
            self.assertEqual(p.horario_saida, parsear_data(payload["departure"]))
            self.assertEqual(p.horario_chegada, parsear_data(payload["arrival"]))
            self.assertAlmostEqual(p.valor, centavos_para_real(payload["fare"]["amount"]), places=2)

        if "empresa_e" in self.payloads:
            payload = self.payloads["empresa_e"][0]
            p = self.integrador.integrar("empresa_e", payload)
            self.assertIsNotNone(p)
            self.assertEqual(p.empresa, payload["nome_comercial"])
            self.assertEqual(p.origem, payload["trajeto"]["partida"])
            self.assertEqual(p.destino, payload["trajeto"]["chegada"])
            self.assertEqual(p.horario_saida, parsear_data(payload["partida"]))
            self.assertEqual(p.horario_chegada, parsear_data(payload["retorno"]))
            self.assertAlmostEqual(p.valor, centavos_para_real(payload["preco_centavos"]), places=2)

        if "empresa_f" in self.payloads:
            payload = self.payloads["empresa_f"][0]
            p = self.integrador.integrar("empresa_f", payload)
            self.assertIsNotNone(p)
            self.assertEqual(p.empresa, payload["companhia"])
            self.assertEqual(p.origem, payload["trajeto_origem"])
            self.assertEqual(p.destino, payload["trajeto_destino"])
            self.assertEqual(p.horario_saida, parsear_data(payload["data_ida"]))
            self.assertEqual(p.horario_chegada, parsear_data(payload["data_volta"]))
            self.assertAlmostEqual(p.valor, payload["pagamento"]["total_reais"], places=2)

        self.assertEqual(len(self.integrador.obter_erros()), 0)


if __name__ == "__main__":
    unittest.main()
