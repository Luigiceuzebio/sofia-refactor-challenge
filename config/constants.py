import re

# Palavras-chave e Comandos
ADMIN_COMMANDS = {"diagnosticar sharepoint": "", "testar busca": ""}
BOARDS_COMMANDS = ["analisar board", "modo boards", "azure boards"]
LEARNING_TRIGGERS = ["quero te ensinar", "aprenda", "anote"]
LIST_PATTERNS = ["liste os arquivos", "arquivos recentes"]
EXIT_COMMANDS = ["sair", "exit", "sair do modo boards"]
HELP_COMMANDS = ["ajuda", "help", "comandos"]
CLIENT_KEYWORDS = ["cliente", "clientes"]
ACTIVITY_KEYWORDS = ["atividades", "atividade", "tarefas"]
COLLABORATOR_REFERENCES = ["dele", "dela", "suas tarefas"]
PROGRESS_KEYWORDS = ["em andamento", "fazendo", "progresso"]
TODO_KEYWORDS = ["a fazer", "to do", "pendente"]
TASK_COUNT_KEYWORDS = ["mais tarefas", "quem tem mais"]

# Mapeamentos
BOARD_PROJECTS = {"sonar": "Sonar", "sonar labs": "Sonar Labs"}
MAPA_TIPOS_ITENS = {"bug": "bug", "bugs": "bug", "tarefa": "task", "tarefas": "task"}

# Parâmetros de Configuração
CACHE_DURATION = 600  
CACHE_CLEANUP_INTERVAL = 300 
DEFAULT_FILE_LIMIT = 10
MAX_FILE_LIMIT = 50
MIN_WORD_LENGTH = 2
MAX_RELEVANT_WORDS = 5

# Padrões de Regex (aqui como strings)
REGEX_PATTERNS = {
    'file_extension': r'\.(docx|pdf|xlsx|pptx|txt|md)$',
    'file_naming': r'[\w\s_-]+\.(docx|pdf|xlsx|pptx|txt|md)',
    'greeting': r'\b(olá|oi|bom dia|boa tarde|boa noite|tudo bem)\b',
    'action_cleaning': r'^(me mostre|mostre|busque por|buscar|encontre|encontrar|procure por|procurar)\s*',
    'articles_cleaning': r'\b(o|a|os|as|um|uma|uns|umas|de|do|da|dos|das)\b',
    'quantity_patterns': [r'(\d+)\s+arquivos', r'top\s+(\d+)']
}

# Listas para o file_handler e intent_router
FILE_KEYWORDS = ["arquivo", "documento", "planilha", "apresentação", "relatório"]
ACTION_KEYWORDS = ["buscar", "encontrar", "procure", "ache", "liste"]
CASUAL_WORDS = ["ideia", "pensando", "talvez", "acho que"]
WELLBEING_PHRASES = ["tudo bem", "como vai", "tudo certo"]
URL_FIELDS = ["webUrl", "web_url", "@microsoft.graph.downloadUrl"]
URL_VALIDATION_PATTERNS = [r'^https?://']
INVALID_URL_PATTERNS = ["#", ""]