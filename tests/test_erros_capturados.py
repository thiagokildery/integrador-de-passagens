"""
Teste 2 — Erros capturados sem interromper o sistema.

Manda payloads inválidos (campo faltando, moeda errada, empresa não registrada)
e verifica se o sistema captura os erros, continua funcionando e exporta
os erros com as mensagens corretas.

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


class TestErrosCapturados(unittest.TestCase):
    """Teste de captura de erros — valida que erros são tratados corretamente."""

    def setUp(self):
        """Arrange: configura o integrador com auto-descoberta."""
        self.registry = ConverterRegistry()
        for conversor_cls in descobrir_conversores():
            self.registry.registrar(conversor_cls())

        self.integrador = IntegradorPassagens(self.registry)
        self.pasta_saida = tempfile.mkdtemp()

    def tearDown(self):
        """Limpa a pasta temporária após o teste."""
        shutil.rmtree(self.pasta_saida, ignore_errors=True)

    def test_erros_capturados_sem_interromper_sistema(self):
        """
        Teste: payloads inválidos devem ser capturados sem interromper o sistema,
        erros são exportados como JSON com mensagens corretas, e passagens
        válidas continuam funcionando com dados corretos.

        Arrange: mistura payload válido com inválidos (campo faltando,
                 moeda errada, empresa não registrada).
        Act: integra tudo e exporta os erros.
        Assert: passagem válida tem dados corretos, cada tipo de erro gera
                a mensagem esperada, arquivo payloads_invalidos.json é gerado
                com o conteúdo correto.
        """
        # Arrange - payloads com erros misturados
        payloads_com_erros = {}
        empresas_registradas = self.integrador.listar_empresas_disponiveis()

        if "empresa_a" in empresas_registradas:
            payloads_com_erros["empresa_a"] = [
                # Payload válido
                {
                    "empresa": "Rapido Norte",
                    "origem": "Fortaleza",
                    "destino": "Recife",
                    "saida": "2026-06-10 08:00",
                    "chegada": "2026-06-10 18:30",
                    "valor": 199.90,
                },
                # Payload inválido — campo faltando
                {
                    "empresa": "Quebrada Ltda",
                    "origem": "Sao Paulo",
                    "saida": "2026-06-10 08:00",
                    "chegada": "2026-06-10 18:30",
                    "valor": 50.00,
                },
            ]

        if "empresa_b" in empresas_registradas:
            # Payload inválido — moeda errada
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

        # Empresa não registrada
        payloads_com_erros["empresa_x"] = [{"qualquer": "coisa"}]

        # Act
        passagens = self.integrador.integrar_todos(payloads_com_erros)
        erros = self.integrador.obter_erros()

        exportador = ExportadorPassagens(self.pasta_saida)
        exportador.exportar_por_empresa(passagens)
        exportador.exportar_consolidado(passagens)
        caminho_erros = exportador.exportar_erros(erros)

        # Assert - pelo menos uma passagem válida
        self.assertGreaterEqual(len(passagens), 1, "Deve haver pelo menos uma passagem válida")

        # Assert - a passagem válida tem os dados corretos
        p = passagens[0]
        self.assertEqual(p.empresa, "Rapido Norte")
        self.assertEqual(p.origem, "Fortaleza")
        self.assertEqual(p.destino, "Recife")
        self.assertEqual(p.horario_saida, datetime(2026, 6, 10, 8, 0))
        self.assertEqual(p.horario_chegada, datetime(2026, 6, 10, 18, 30))
        self.assertAlmostEqual(p.valor, 199.90, places=2)

        # Assert - erros foram capturados
        self.assertGreaterEqual(len(erros), 1, "Deve haver pelo menos um erro capturado")

        # Assert - cada erro tem a estrutura correta
        for erro in erros:
            self.assertIn("empresa_id", erro)
            self.assertIn("payload", erro)
            self.assertIn("erro", erro)

        # Assert - erro de campo faltando tem mensagem clara
        erros_empresa_a = [e for e in erros if e["empresa_id"] == "empresa_a"]
        if erros_empresa_a:
            self.assertTrue(
                any("ausente" in e["erro"].lower() or "obrigat" in e["erro"].lower()
                    for e in erros_empresa_a),
                "Erro de campo faltando deve mencionar 'ausente' ou 'obrigatório'"
            )

        # Assert - erro de moeda errada tem mensagem clara
        erros_empresa_b = [e for e in erros if e["empresa_id"] == "empresa_b"]
        if erros_empresa_b:
            self.assertTrue(
                any("moeda" in e["erro"].lower() or "USD" in e["erro"]
                    for e in erros_empresa_b),
                "Erro de moeda errada deve mencionar 'moeda' ou 'USD'"
            )

        # Assert - erro de empresa não registrada tem mensagem clara
        erros_empresa_x = [e for e in erros if e["empresa_id"] == "empresa_x"]
        if erros_empresa_x:
            self.assertTrue(
                any("registrada" in e["erro"].lower() or "dispon" in e["erro"].lower()
                    for e in erros_empresa_x),
                "Erro de empresa não registrada deve mencionar 'registrada' ou 'disponível'"
            )

        # Assert - arquivo de erros foi gerado
        self.assertTrue(os.path.exists(caminho_erros), "Arquivo de erros deve ser gerado")

        # Assert - conteúdo do arquivo de erros bate com a lista
        with open(caminho_erros, "r", encoding="utf-8") as f:
            erros_json = json.load(f)
        self.assertEqual(len(erros_json), len(erros))

        # Assert - cada erro no JSON tem os mesmos dados da lista
        for i, erro_json in enumerate(erros_json):
            self.assertEqual(erro_json["empresa_id"], erros[i]["empresa_id"])
            self.assertEqual(erro_json["erro"], erros[i]["erro"])


if __name__ == "__main__":
    unittest.main()
