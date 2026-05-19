import json
import logging
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converters import ConverterRegistry, descobrir_conversores
from integrador import IntegradorPassagens
from exportador import ExportadorPassagens


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAIDA_DIR = os.path.join(BASE_DIR, "saida")


def configurar_logging():
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "integracao.log"), mode="w", encoding="utf-8"),
        ],
    )


def criar_integrador() -> IntegradorPassagens:
    registry = ConverterRegistry()
    for conversor_cls in descobrir_conversores():
        registry.registrar(conversor_cls())
    return IntegradorPassagens(registry)


def carregar_json(nome_arquivo: str):
    caminho = os.path.join(DATA_DIR, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def descobrir_payloads() -> dict:
    payloads = {}
    for nome_arquivo in sorted(os.listdir(DATA_DIR)):
        if nome_arquivo.endswith(".json"):
            empresa_id = nome_arquivo.replace(".json", "")
            payloads[empresa_id] = carregar_json(nome_arquivo)
    return payloads


def imprimir_passagem(p, numero: int):
    saida = p.horario_saida.strftime("%d/%m/%Y %H:%M")
    chegada = p.horario_chegada.strftime("%d/%m/%Y %H:%M")
    duracao = p.horario_chegada - p.horario_saida
    horas = int(duracao.total_seconds() // 3600)
    minutos = int((duracao.total_seconds() % 3600) // 60)

    print(f"  +-- Passagem #{numero} --------------------------------------------+")
    print(f"  | Empresa:  {p.empresa}")
    print(f"  | Rota:     {p.origem} -> {p.destino}")
    print(f"  | Saida:    {saida}")
    print(f"  | Chegada:  {chegada}")
    print(f"  | Duracao:  {horas}h{minutos:02d}min")
    print(f"  | Valor:    R$ {p.valor:.2f}")
    print(f"  +----------------------------------------------------------+")


def imprimir_secao(titulo: str):
    print()
    print(f"  >> {titulo}")
    print()


def main():
    configurar_logging()

    print()
    print("  ============================================================")
    print("    INTEGRACAO DE PASSAGENS RODOVIARIAS")
    print("    Plataforma Centralizada de Venda de Passagens")
    print("  ============================================================")

    integrador = criar_integrador()

    imprimir_secao("Empresas Registradas")
    empresas = integrador.listar_empresas_disponiveis()
    for e in empresas:
        print(f"    - {e}")
    print(f"  Total: {len(empresas)} empresa(s)")

    imprimir_secao("Integracao de Passagens")

    payloads = descobrir_payloads()
    passagens = integrador.integrar_todos(payloads)

    if passagens:
        for i, p in enumerate(passagens, 1):
            imprimir_passagem(p, i)
    else:
        print("    Nenhuma passagem valida encontrada.")

    erros = integrador.obter_erros()
    if erros:
        imprimir_secao(f"Payloads Invalidos ({len(erros)})")
        for i, erro in enumerate(erros, 1):
            print(f"  [{i}] {erro['empresa_id']}: {erro['erro']}")

    imprimir_secao("Exportacao de JSONs")

    exportador = ExportadorPassagens(SAIDA_DIR)
    arquivos_por_empresa = exportador.exportar_por_empresa(passagens)
    caminho_consolidado = exportador.exportar_consolidado(passagens)

    for nome, caminho in arquivos_por_empresa.items():
        nome_bonito = nome.replace("_", " ").title()
        print(f"    {nome_bonito}: saida/{os.path.basename(caminho)}")

    print(f"    Consolidado: saida/{os.path.basename(caminho_consolidado)}")

    if erros:
        caminho_erros = exportador.exportar_erros(erros)
        print(f"    Invalidos:   saida/{os.path.basename(caminho_erros)}")

    print()
    print("  ============================================================")
    print("    RESUMO")
    print("  ============================================================")
    print(f"    Passagens integradas:  {len(passagens)}")
    print(f"    Payloads invalidos:    {len(erros)}")
    print(f"    Empresas suportadas:   {len(empresas)}")
    print(f"    Log:                   logs/integracao.log")
    print(f"    Exportados em:         saida/")
    print("  ============================================================")
    print()


if __name__ == "__main__":
    main()
