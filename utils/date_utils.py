"""
Utilitário para padronização de datas.

Cada empresa parceira envia datas em formatos diferentes.
Este módulo centraliza a lógica de parsing e padronização,
sempre retornando objetos datetime no formato ISO 8601.
"""

from datetime import datetime


# Formatos de data suportados pelo sistema
FORMATOS_DATA = {
    "iso_com_espaco": "%Y-%m-%d %H:%M",           
    "iso_com_segundos": "%Y-%m-%d %H:%M:%S",      
    "iso_completo": "%Y-%m-%dT%H:%M:%S",          
    "br_barra": "%d/%m/%Y %H:%M",                
    "br_barra_segundos": "%d/%m/%Y %H:%M:%S",     
    "br_traco": "%d-%m-%Y %H:%M",                 
    "br_traco_segundos": "%d-%m-%Y %H:%M:%S",    
    "br_ponto": "%d.%m.%Y %H:%M",                 
    "br_ponto_segundos": "%d.%m.%Y %H:%M:%S",
}


def parsear_data(data_str: str, formato: str = None) -> datetime:
    """
    Converte uma string de data em um objeto datetime.

    Se um formato específico for fornecido, tenta usá-lo diretamente.
    Caso contrário, tenta todos os formatos conhecidos automaticamente.

    Args:
        data_str: String representando uma data/hora.
        formato: Formato strftime opcional para parsing direto.

    Returns:
        datetime: Objeto datetime padronizado.

    Raises:
        ValueError: Se a string não puder ser parseada com nenhum formato conhecido.
    """
    if not data_str or not isinstance(data_str, str):
        raise ValueError(f"Data inválida: esperado string não vazia, recebido '{data_str}'")

    data_str = data_str.strip()

    # Tenta com o formato especificado primeiro
    if formato:
        try:
            return datetime.strptime(data_str, formato)
        except ValueError:
            pass

    # Tenta todos os formatos conhecidos
    for fmt in FORMATOS_DATA.values():
        try:
            return datetime.strptime(data_str, fmt)
        except ValueError:
            continue

    raise ValueError(
        f"Não foi possível parsear a data '{data_str}'. "
        f"Formatos suportados: {list(FORMATOS_DATA.values())}"
    )


def formatar_data_iso(dt: datetime) -> str:
    """
    Formata um datetime no padrão ISO 8601.

    Args:
        dt: Objeto datetime a ser formatado.

    Returns:
        str: Data formatada em ISO 8601 (ex: '2026-06-10T08:00:00').
    """
    return dt.isoformat()
