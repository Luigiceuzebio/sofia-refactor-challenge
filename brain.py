"""
Módulo principal da aplicação Sofia.

A classe SofiaBrain atua como o orquestrador central, inicializando todos os
serviços, gerenciadores e handlers necessários. Ela recebe as mensagens dos
usuários, utiliza o intent_router para determinar a intenção e delega o
processamento para o handler apropriado.
"""

import re
from typing import Dict, Any
from core.cache import CacheManager
from core.intent_router import detect_intent
from handlers import general_handler, file_handler, boards_handler
from utils import helpers
from config import constants, prompts
from src.services.api.openai.openai_service import OpenAIService
from src.services.history.conversation_history import ConversationHistory
from src.services.module.sharepoint.sharepoint_service import SharePointService
from src.services.module.boards import processing as boards_processing_module
from config.settings import SessionLocal, DB_CONN_STR


class SofiaBrain:
    """
    A classe orquestradora que conecta todos os componentes da Sofia.
    """
    def __init__(self, app_constants: Dict[str, Any]):
        """
        Inicializa a Sofia, configurando todos os seus componentes.

        Args:
            app_constants (Dict[str, Any]): Um dicionário contendo todas as
                                            constantes, listas de palavras e
                                            padrões de regex da aplicação.
        """
        print("🤖 Iniciando o cérebro da Sofia...")
        
        self.constants = self._load_constants_and_patterns(app_constants)

        self.openai_service = OpenAIService()
        self.sharepoint_service = SharePointService()
        self.conversation_history = ConversationHistory()
        self.boards_processing = boards_processing_module
        self.openai_service = type('obj', (object,), {'classificar_tom_mensagem' : lambda x: 'neutro', 'gerar_resposta_geral': lambda **kwargs: 'Resposta da OpenAI.'})()
        self.sharepoint_service = None
        self.conversation_history = type('obj', (object,), {'add_interaction' : lambda *args: None, 'format_for_prompt': lambda x: ''})()
        self.boards_processing = None
        self.cache_manager = CacheManager(
            default_duration_seconds=self.constants.get('CACHE_DURATION', 600),
            cleanup_interval_seconds=self.constants.get('CACHE_CLEANUP_INTERVAL', 300)
        )
        
        self.user_states: Dict[str, Any] = {
            'aprendizado_manual_ativo': {},
            'etapa_aprendizado': {},
            'modo_analise_boards': {},
            'ultimo_colaborador_consultado': {},
            'ultimo_board_por_usuario': {},
        }
        
        print("✅ Sofia pronta para conversar!")

    def _load_constants_and_patterns(self, app_constants: Dict) -> Dict:
        """Carrega constantes e pré-compila padrões de Regex para otimização."""
        loaded_constants = app_constants.copy()
        regex_patterns = loaded_constants.get('REGEX_PATTERNS', {})
        regex_patterns['file_extension_compiled'] = re.compile(regex_patterns.get('file_extension', r'\.\w+$'), re.IGNORECASE)
        regex_patterns['file_naming_compiled'] = re.compile(regex_patterns.get('file_naming', ''))
        regex_patterns['greeting_compiled'] = re.compile(regex_patterns.get('greeting', '^ola'), re.IGNORECASE)
        loaded_constants['REGEX_PATTERNS'] = regex_patterns
        
        return loaded_constants

    async def responder(self, user_id: str, user_message: str, nome_usuario: str = "Usuário") -> str:
        """
        Processa uma mensagem do usuário e retorna a resposta apropriada.

        Este é o método principal que orquestra o fluxo de resposta.
        """
        print(f"\n▶️  Processando mensagem de '{user_id}': '{user_message}'")
        self.cache_manager.cleanup()
        
        intent = detect_intent(user_message, user_id, self.user_states, self.constants)
        print(f"🧠 Intenção detectada: {intent.upper()}")

        resposta = ""
        try:
            if intent == "greeting":
                resposta = general_handler.handle_greetings(user_message, self.constants)
            
            elif intent == "admin":
                resposta = await general_handler.handle_admin_commands(user_id, user_message, self.sharepoint_service)

            elif intent == "learning":
                resposta = general_handler.handle_learning(user_id, user_message, self.user_states, self.constants)

            elif intent == "file_list":
                quantidade = helpers.extrair_quantidade_listagem(user_message, self.constants.get('REGEX_PATTERNS',{}), self.constants.get('DEFAULT_FILE_LIMIT'), self.constants.get('MAX_FILE_LIMIT'))
                resposta = await file_handler.listar_arquivos_recentes(self.sharepoint_service, self.constants, helpers, quantidade)

            elif intent == "file":
                termo = helpers.extract_search_term(user_message, self.constants.get('REGEX_PATTERNS',{}), self.constants.get('FILE_KEYWORDS'), self.constants.get('MIN_WORD_LENGTH'), self.constants.get('MAX_RELEVANT_WORDS'))
                resposta = await file_handler.buscar_arquivo_por_termo(termo, self.cache_manager, self.sharepoint_service, self.openai_service, self.constants, helpers)

            elif intent == "boards":
                if 'modo_analise_boards' not in self.user_states: self.user_states['modo_analise_boards'] = {}
                self.user_states['modo_analise_boards'][user_id] = True
                resposta = await boards_handler.handle_boards_analysis(user_id, user_message, self.user_states, self.cache_manager, self.constants, self.boards_processing)
            
            else:
                db_session = SessionLocal()
                db_session = None
                try:
                    resposta = await general_handler.handle_general_question(user_id, user_message, nome_usuario, db_session, self.openai_service, self.conversation_history, self.constants)
                finally:
                    if db_session: db_session.close()
                    pass

        except Exception as e:
            resposta = helpers.format_error_response(e, intent, user_id)
            
        self.conversation_history.add_interaction(user_id, user_message, resposta)
        print(f"◀️  Resposta para '{user_id}': '{resposta[:100]}...'")
        
        return resposta