"""
Este módulo lida com as intenções gerais que não se encaixam nos handlers
específicos de 'files' ou 'boards'. Inclui saudações, comandos administrativos,
o fluxo de aprendizado manual e o fallback para o serviço da OpenAI para
perguntas gerais.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from config import prompts

def handle_greetings(message: str, constants: Dict[str, Any]) -> str:
    """
    Processa e responde a saudações.

    Args:
        message (str): A mensagem do usuário.
        constants (Dict[str, Any]): Dicionário com constantes, incluindo GREETING_WORDS.

    Returns:
        str: Uma resposta de saudação apropriada.
    """
    message_lower = message.lower()
    
    # Utiliza as constantes do arquivo de prompts
    if any(phrase in message_lower for phrase in constants.get('WELLBEING_PHRASES', [])):
        return constants.get('GREETING_WELLBEING', "Olá! Tudo bem?")
        
    return constants.get('GREETING_DEFAULT', "Olá! Como posso ajudar?")


async def handle_admin_commands(user_id: str, message: str, sharepoint_service: Any) -> str:
    """
    Processa comandos administrativos, como diagnósticos.

    Args:
        user_id (str): A ID do usuário.
        message (str): A mensagem do usuário.
        sharepoint_service (Any): A instância do serviço do SharePoint.

    Returns:
        str: O resultado do comando administrativo.
    """
    message_lower = message.lower()
    
    .
    if message_lower == "diagnosticar sharepoint":
         return await diagnosticar_sharepoint_completo(sharepoint_service)
        
    return "Comando administrativo não reconhecido."


def handle_learning(user_id: str, message: str, user_states: Dict[str, Any], constants: Dict[str, Any]) -> str:
    """
    Gerencia o fluxo de aprendizado manual em múltiplos passos.

    Args:
        user_id (str): A ID do usuário.
        message (str): A mensagem do usuário.
        user_states (Dict[str, Any]): O dicionário de estados para rastrear o progresso.
        constants (Dict[str, Any]): Dicionário com constantes (LEARNING_STEPS, etc).

    Returns:
        str: A resposta apropriada para a etapa atual do aprendizado.
    """
    aprendizado_ativo = user_states.get('aprendizado_manual_ativo', {})
    etapa_aprendizado = user_states.get('etapa_aprendizado', {})
    learning_steps = constants.get('LEARNING_STEPS', {})

    # Inicia o fluxo de aprendizado
    if not aprendizado_ativo.get(user_id):
        aprendizado_ativo[user_id] = {"pergunta": message}
        etapa_aprendizado[user_id] = learning_steps.get('resposta', 2)
        return constants.get('LEARNING_QUESTION_PROMPT', "Qual é a resposta?")

    # Processa a resposta
    etapa_atual = etapa_aprendizado.get(user_id)
    if etapa_atual == learning_steps.get('resposta', 2):
        pergunta = aprendizado_ativo[user_id]["pergunta"]
        resposta_usuario = message
        
        mensagem_salva = f"Aprendido! Quando me perguntarem sobre '{pergunta}', responderei com '{resposta_usuario}'."
        
        del aprendizado_ativo[user_id]
        del etapa_aprendizado[user_id]
        
        return mensagem_salva
        
    return constants.get('LEARNING_ERROR_RETRY', "Algo deu errado. Vamos tentar de novo.")


async def handle_general_question(
    user_id: str, 
    message: str, 
    nome_usuario: str,
    db_session: Any, 
    openai_service: Any, 
    conversation_history: Any,
    constants: Dict[str, Any]
) -> str:
    """
    Lida com perguntas gerais, usando o conhecimento manual e, como fallback, a OpenAI.
    """
    # 1. Verifica se é uma pergunta já aprendida manualmente
    resposta_manual = responder_com_aprendizados_manuais(message)
    if resposta_manual:
         return resposta_manual

    # 2. Se não, processa com a OpenAI
    try:
        tom = await openai_service.classificar_tom_mensagem(message)
        
        historico = conversation_history.format_for_prompt(user_id)
  
        system_prompt = prompts.gerar_system_prompt(db_session, historico, tom)

        resposta_openai = await openai_service.gerar_resposta_geral(
            user_message=message,
            system_prompt=system_prompt,
            historico_formatado=historico,
            tom=tom
        )
        
        return resposta_openai or constants.get('OPENAI_FALLBACK_MESSAGE')

    except Exception as e:
        print(f"❌ Erro ao chamar a OpenAI no general_handler: {e}")
        return constants.get('OPENAI_FALLBACK_MESSAGE')
