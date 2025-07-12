"""
Este módulo é o coração do roteamento de intenções da Sofia.
Ele contém a lógica para analisar a mensagem de um usuário e determinar
a sua intenção principal, permitindo que o sistema direcione a solicitação
para o handler correto.
"""

import re
from typing import Dict, Any


from config.constants import (
    BOARDS_SELECTION_MESSAGE, BOARDS_HELP_MESSAGE, BOARDS_EXIT_MESSAGE,
    SHAREPOINT_CONFIG_ERROR, SHAREPOINT_DRIVE_ERROR, NO_FILES_MESSAGE,
    FILE_NOT_FOUND_MESSAGE, ADMIN_COMMAND_NOT_RECOGNIZED, LEARNING_ERROR_MESSAGE,
    LEARNING_QUESTION_PROMPT, LEARNING_ERROR_RETRY, OPENAI_FALLBACK_MESSAGE,
    COURTESY_RESPONSE, IMAGE_ERROR_MESSAGE, FILE_SEARCH_NO_RESULTS,
    GREETING_DEFAULT, GREETING_WELLBEING, ERROR_400_MESSAGE, ERROR_401_MESSAGE,
    ERROR_TECHNICAL_MESSAGE, DIAGNOSTIC_HEADER, DIAGNOSTIC_CONFIG_SECTION,
    DIAGNOSTIC_CONNECTIVITY_SECTION, DIAGNOSTIC_ENDPOINTS_SECTION,
    FILE_LIST_INSTRUCTIONS, SINGLE_FILE_CLICK_INSTRUCTION,
    MULTIPLE_FILES_CLICK_INSTRUCTION, FILE_FOUND_MESSAGE, FILE_CONTENT_ANALYSIS_OFFER,
    
    MAPA_TIPOS_ITENS, BOARDS_COMMANDS, LEARNING_TRIGGERS, LIST_PATTERNS,
    EXIT_COMMANDS, HELP_COMMANDS, ADMIN_COMMANDS, FILE_REQUEST_PATTERNS,
    FILE_KEYWORDS, ACTION_KEYWORDS, CASUAL_WORDS, POSITIVE_WORDS,
    FILE_CONTEXT_WORDS, CASUAL_INDICATORS, FILE_INTENT_INDICATORS,
    GREETING_WORDS, WELLBEING_PHRASES, COLLABORATOR_REFERENCES,
    PROGRESS_KEYWORDS, TODO_KEYWORDS, COMPLETED_KEYWORDS, OVERVIEW_KEYWORDS,
    OVERDUE_KEYWORDS, HIERARCHY_KEYWORDS, CLIENT_KEYWORDS, ACTIVITY_KEYWORDS,
    TASK_COUNT_KEYWORDS, BOARD_PROJECTS, CLIENT_SEARCH_KEYWORDS,
    REGEX_PATTERNS, URL_VALIDATION_PATTERNS, INVALID_URL_PATTERNS,
    
    CACHE_DURATION, CACHE_CLEANUP_INTERVAL, DEFAULT_FILE_LIMIT, MAX_FILE_LIMIT,
    SEARCH_CACHE_DURATION, ENDPOINTS_TIMEOUT, MAX_RELEVANT_WORDS, MIN_WORD_LENGTH,
    URL_FIELDS, GRAPH_ENDPOINTS, LEARNING_STEPS

 )


def _calculate_file_score(
    message: str, 
    file_keywords: list, 
    action_keywords: list, 
    casual_words: list, 
    file_extension_pattern: re.Pattern, 
    file_naming_pattern: re.Pattern
) -> float:
    """
    Calcula uma pontuação de 0.0 a 1.0 para determinar a probabilidade
    de a intenção do usuário ser relacionada a arquivos.

    Args:
        message (str): A mensagem do usuário em minúsculas.
        file_keywords (list): Palavras-chave relacionadas a arquivos (ex: "arquivo", "documento").
        action_keywords (list): Palavras-chave de ação (ex: "buscar", "encontrar").
        casual_words (list): Palavras que diminuem a pontuação (ex: "ideia", "pensando").
        file_extension_pattern (re.Pattern): Regex compilado para extensões de arquivo.
        file_naming_pattern (re.Pattern): Regex compilado para nomes de arquivo.

    Returns:
        float: A pontuação de intenção de arquivo.
    """
    score = 0.0
    
    if file_extension_pattern.search(message):
        score += 0.5
    
    if file_naming_pattern.search(message):
        score += 0.2
        
    score += sum(0.2 for keyword in file_keywords if keyword in message)
    score += sum(0.15 for keyword in action_keywords if keyword in message)
    
    # Reduz a pontuação se palavras casuais forem encontradas
    score -= sum(0.2 for word in casual_words if word in message)
    
    # Garante que a pontuação fique entre 0 e 1
    return max(0.0, min(score, 1.0))


def detect_intent(
    message: str, 
    user_id: str, 
    user_states: Dict[str, Any],
    constants: Dict[str, Any]
) -> str:
    """
    Analisa a mensagem do usuário e o estado da conversa para determinar a intenção.

    Args:
        message (str): A mensagem bruta do usuário.
        user_id (str): A ID do usuário.
        user_states (Dict[str, Any]): O dicionário de estados do usuário 
                                      (ex: modo_analise_boards).
        constants (Dict[str, Any]): Um dicionário contendo todas as listas de
                                    palavras-chave e padrões de regex necessários.

    Returns:
        str: A string que representa a intenção detectada (ex: "boards", "file", "general").
    """
    message_lower = message.lower().strip()

    # 1. Verifica comandos de administrador (maior prioridade)
    if any(cmd in message_lower for cmd in constants.get('ADMIN_COMMANDS', {}).keys()):
        return "admin"

    # 2. Verifica se está no modo de análise de boards ou se um comando foi usado
    if any(cmd in message_lower for cmd in constants.get('BOARDS_COMMANDS', [])) or \
       user_states.get('modo_analise_boards', {}).get(user_id):
        return "boards"
        
    # 3. Verifica se está no modo de aprendizado ou se um gatilho foi usado
    if any(trigger in message_lower for trigger in constants.get('LEARNING_TRIGGERS', [])) or \
       user_id in user_states.get('aprendizado_manual_ativo', {}):
        return "learning"

    # 4. Verifica padrões para listagem de arquivos
    if any(pattern in message_lower for pattern in constants.get('LIST_PATTERNS', [])):
        return "file_list"

    # 5. Verifica saudações simples
    greeting_pattern = constants.get('REGEX_PATTERNS', {}).get('greeting_compiled')
    if greeting_pattern and len(message.split()) <= 6 and greeting_pattern.search(message):
        return "greeting"

    # 6. Calcula a pontuação para intenção de arquivo
    file_score = _calculate_file_score(
        message_lower,
        constants.get('FILE_KEYWORDS', []),
        constants.get('ACTION_KEYWORDS', []),
        constants.get('CASUAL_WORDS', []),
        constants.get('REGEX_PATTERNS', {}).get('file_extension_compiled'),
        constants.get('REGEX_PATTERNS', {}).get('file_naming_compiled')
    )
    if file_score > 0.7:
        return "file"

    # 7. Se nenhuma outra intenção for detectada, retorna "geral"
    return "general"
