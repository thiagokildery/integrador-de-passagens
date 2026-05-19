"""
Utilitário para padronização de valores monetários.

Cada empresa parceira pode enviar o valor da passagem em formatos
diferentes: float direto, objeto com moeda, ou em centavos.
Este módulo centraliza a conversão para float em BRL.
"""


def parsear_valor_monetario(valor, moeda_esperada: str = "BRL") -> float:
    """
    Converte diferentes representações de valor monetário para float (BRL).

    Aceita:
        - float direto (ex: 199.90)
        - dict com chaves 'valor' e 'moeda' (ex: {"valor": 149.50, "moeda": "BRL"})
        - int em centavos (ex: 25990 -> 259.90)

    Args:
        valor: Valor monetário em qualquer formato suportado.
        moeda_esperada: Código da moeda esperada quando o valor vem como dict.

    Returns:
        float: Valor em reais (BRL).

    Raises:
        ValueError: Se o valor for de moeda diferente de BRL ou formato inválido.
    """
    # Caso 1: valor já é float ou int direto
    if isinstance(valor, (int, float)):
        return float(valor)

    # Caso 2: valor é um dict com valor e moeda
    if isinstance(valor, dict):
        if "valor" not in valor or "moeda" not in valor:
            raise ValueError(
                f"Dicionário de valor monetário inválido: {valor}. "
                f"Esperado chaves 'valor' e 'moeda'."
            )
        if valor["moeda"] != moeda_esperada:
            raise ValueError(
                f"Moeda não suportada: '{valor['moeda']}'. "
                f"Esperado: '{moeda_esperada}'."
            )
        return float(valor["valor"])

    # Caso 3: string numérica
    if isinstance(valor, str):
        try:
            return float(valor.replace(",", "."))
        except ValueError:
            raise ValueError(f"Valor monetário em string inválido: '{valor}'")

    raise ValueError(
        f"Tipo de valor monetário não suportado: {type(valor).__name__} -> {valor}"
    )


def centavos_para_real(centavos: int) -> float:
    """
    Converte um valor em centavos para reais.

    Args:
        centavos: Valor em centavos (ex: 25990).

    Returns:
        float: Valor em reais (ex: 259.90).
    """
    return centavos / 100.0
