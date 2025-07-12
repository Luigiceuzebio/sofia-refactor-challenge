"""
Este módulo contém funções auxiliares e utilitárias puras que podem ser
reutilizadas em diferentes partes da aplicação. Elas não devem manter estado.
"""

import re
import traceback
from datetime import datetime

def formatar_data_com_hora(data_iso: str) -> str:
    """
    Converte uma string de data no formato ISO 8601 para um formato legível.

    Args:
        data_iso (str): A string de data a ser formatada.

    Returns:
        str: A data formatada como 'dd/mm/aaaa às HH:MM'.
    """
    if not data_iso:
        return ""

    try:
        data_iso_clean = data_iso.replace('Z', '')
        
        if '.' in data_iso_clean:
            dt = datetime.fromisoformat(data_iso_clean.split('.')[0])
        else:
            dt = datetime.fromisoformat(data_iso_clean)
            
        return f"📅 {dt.strftime('%d/%m/%Y às %H:%M')}"
    except (ValueError, TypeError):
        return ""


def validar_url(url: str, url_validation_patterns: list, invalid_url_patterns: list) -> bool:
    """
    Verifica se uma URL é válida com base em padrões de regex.

    Args:
        url (str): A URL a ser validada.
        url_validation_patterns (list): Lista de regex para URLs válidas.
        invalid_url_patterns (list): Lista de strings de URLs inválidas.

    Returns:
        bool: True se a URL for válida, False caso contrário.
    """
    if not url or not isinstance(url, str):
        return False
        
    url_lower = url.lower().strip()
    
    if url_lower in invalid_url_patterns:
        return False
        
    for pattern in url_validation_patterns:
        if re.search(pattern, url_lower):
            return True
            
    return False


def obter_url_valida(arquivo: dict, url_fields: list, url_validation_patterns: list, invalid_url_patterns: list) -> str:
    """
    Busca em um dicionário de arquivo por um campo de URL válido.

    Args:
        arquivo (dict): O dicionário representando o arquivo.
        url_fields (list): Uma lista de chaves a serem testadas para a URL.

    Returns:
        str: A primeira URL válida encontrada, ou '#' se nenhuma for encontrada.
    """
    for field in url_fields:
        url = arquivo.get(field)
        if url and validar_url(url, url_validation_patterns, invalid_url_patterns):
            return url
    return "#"

def extrair_quantidade_listagem(message: str, regex_patterns: dict, default_limit: int, max_limit: int) -> int:
    """
    Extrai um número de uma mensagem para determinar a quantidade de itens.

    Args:
        message (str): A mensagem do usuário.
        regex_patterns (dict): Dicionário contendo os padrões de regex.
        default_limit (int): O valor padrão a ser retornado se nenhum número for encontrado.
        max_limit (int): O valor máximo permitido.

    Returns:
        int: A quantidade extraída, limitada entre 1 e max_limit.
    """
    message_lower = message.lower()
    
    for pattern in regex_patterns.get('quantity_patterns', []):
        match = re.search(pattern, message_lower)
        if match:
            try:
                quantidade = int(match.group(1))
                return max(1, min(quantidade, max_limit))
            except (ValueError, IndexError):
                continue
                
    return default_limit


def extract_search_term(message: str, regex_patterns: dict, file_keywords: list, min_word_length: int, max_relevant_words: int) -> str:
    """
    Extrai e limpa um termo de busca de uma mensagem do usuário.

    Args:
        message (str): A mensagem completa do usuário.
        regex_patterns (dict): Dicionário contendo os padrões de regex.
        file_keywords (list): Palavras-chave a serem ignoradas.
        min_word_length (int): Comprimento mínimo de uma palavra relevante.
        max_relevant_words (int): Número máximo de palavras a serem retornadas.

    Returns:
        str: O termo de busca limpo e pronto para ser usado.
    """
    clean_message = re.sub(regex_patterns.get('action_cleaning', ''), '', message, flags=re.IGNORECASE)
    clean_message = re.sub(regex_patterns.get('articles_cleaning', ''), '', clean_message, flags=re.IGNORECASE)
    
    file_extension_pattern = re.compile(regex_patterns.get('file_extension', r'\.\w{2,4}$'), re.IGNORECASE)
    file_match = file_extension_pattern.search(clean_message)
    if file_match:
        words = clean_message.split()
        for word in words:
            if file_extension_pattern.search(word):
                return word.strip('.,?!')

    words = clean_message.strip().split()
    relevant_words = [
        w for w in words if len(w) > min_word_length and w.lower() not in file_keywords
    ]
    
    return ' '.join(relevant_words[:max_relevant_words])

def format_error_response(e: Exception, intent: str, user_id: str) -> str:
    """
    Cria uma mensagem de erro padronizada e amigável para o usuário.

    Args:
        e (Exception): O objeto da exceção capturada.
        intent (str): A intenção que estava sendo processada quando o erro ocorreu.
        user_id (str): A ID do usuário que encontrou o erro.

    Returns:
        str: A mensagem de erro formatada para ser enviada ao usuário.
    """
    erro_id = f"ERR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    mensagem_log = (
        f"❌ [{erro_id}] Erro no handler de intenção '{intent}' para usuário '{user_id}': "
        f"{type(e).__name__}: {e}"
    )
    print(mensagem_log)
    traceback.print_exc()

    return (
        f"⚠️ Algo deu errado ao processar sua solicitação.\n"
        f"Código do erro: `{erro_id}`\n"
        f"Por favor, tente novamente em instantes. Se o problema persistir, "
        f"informe este código ao time técnico."
    )
