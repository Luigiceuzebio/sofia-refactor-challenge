"""
Este módulo centraliza todos os textos, mensagens e prompts usados pela assistente Sofia.
Isso facilita a manutenção, tradução e consistência da comunicação.
"""

from datetime import datetime
from functools import lru_cache
from typing import Any
from sqlalchemy.orm import Session

from database.fragments import (
    gerar_fragmento_empresa,
    gerar_fragmento_setores,
    gerar_fragmento_funcionarios,
    gerar_fragmento_gerentes,
    gerar_fragmento_persona,
    gerar_fragmento_conhecimentos,
    gerar_fragmento_cerimonias,
    gerar_fragmento_projetos,
    gerar_fragmento_participacoes
)


# Mensagens Gerais e de Interação 
GREETING_DEFAULT = "Olá! Eu sou a Sofia. Como posso te ajudar hoje? 😊"
GREETING_WELLBEING = "Olá! Tudo ótimo por aqui. E com você? Espero que esteja tudo bem! No que posso ser útil?"
COURTESY_RESPONSE = "De nada! Se precisar de mais alguma coisa, é só chamar. 😉"
OPENAI_FALLBACK_MESSAGE = "Peço desculpas, mas não consegui processar sua pergunta no momento. Poderia tentar reformulá-la?"
IMAGE_ERROR_MESSAGE = "Desculpe, ocorreu um erro ao tentar analisar a imagem. Por favor, verifique o arquivo e tente novamente."

# Mensagens do Módulo Boards
BOARDS_SELECTION_MESSAGE = "Claro! Qual board você gostaria de analisar? As opções são **Sonar** ou **Sonar Labs**."
BOARDS_HELP_MESSAGE = """
Aqui estão alguns exemplos do que você pode me perguntar sobre os boards:

- "qual a visão geral do board sonar?"
- "quais as tarefas em andamento do sonar labs?"
- "liste as tarefas do fulano no board sonar"
- "quem é o cliente com mais atividades no sonar?"
- "quantas bugs temos no board sonar labs?"

Lembre-se de especificar o board na primeira pergunta. Depois, posso manter o contexto para as próximas. Para sair, diga "sair do modo boards".
"""
BOARDS_EXIT_MESSAGE = "Tudo bem! Saindo do modo de análise de boards. Se precisar de algo mais, estou à disposição."

# Mensagens do Módulo de Arquivos (SharePoint) 
SHAREPOINT_CONFIG_ERROR = "⚠️ **Erro de Configuração:** Não foi possível autenticar no SharePoint. Verifique as credenciais no arquivo de configuração."
SHAREPOINT_DRIVE_ERROR = "⚠️ **Erro de Acesso:** Autenticado com sucesso, mas não foi possível encontrar o Drive de destino no SharePoint. Verifique o nome do Drive configurado."
NO_FILES_MESSAGE = "Não encontrei nenhum arquivo recente no SharePoint."
FILE_NOT_FOUND_MESSAGE = "Não consegui encontrar um arquivo com esse nome. Que tal tentar listar os arquivos recentes para ver se ele aparece?"
FILE_SEARCH_NO_RESULTS = "Busquei por '**{}**', mas não encontrei nenhum arquivo correspondente. 😔"
FILE_FOUND_MESSAGE = "Encontrei o seguinte arquivo para você:\n\n"
FILE_CONTENT_ANALYSIS_OFFER = "Gostaria que eu lesse o conteúdo deste arquivo para você? Posso fazer um resumo ou responder perguntas sobre ele."

# Instruções para o Usuário 
FILE_LIST_INSTRUCTIONS = "Você pode clicar em qualquer arquivo para abri-lo. Se quiser que eu analise o conteúdo de algum deles, é só pedir!"
SINGLE_FILE_CLICK_INSTRUCTION = "Você pode clicar no nome do arquivo para abri-lo."
MULTIPLE_FILES_CLICK_INSTRUCTION = "Você pode clicar em qualquer um dos nomes para abrir o arquivo correspondente."

# Mensagens do Módulo de Aprendizado 
LEARNING_ERROR_MESSAGE = "Não entendi. Se você quer me ensinar algo, comece sua frase com 'quero te ensinar' ou 'aprenda'."
LEARNING_QUESTION_PROMPT = "Entendido. Qual é a resposta para essa pergunta?"
LEARNING_ERROR_RETRY = "Algo deu errado no processo de aprendizado. Por favor, tente novamente."

# Mensagens de Comandos Administrativos e Diagnóstico
ADMIN_COMMAND_NOT_RECOGNIZED = "Comando administrativo não reconhecido."
DIAGNOSTIC_HEADER = "--- 🩺 **Relatório de Diagnóstico da Sofia** ---"
DIAGNOSTIC_CONFIG_SECTION = "\n**1. Verificação de Configuração:**"
DIAGNOSTIC_CONNECTIVITY_SECTION = "\n**2. Teste de Conectividade com SharePoint:**"
DIAGNOSTIC_ENDPOINTS_SECTION = "\n**3. Verificação de Endpoints do Microsoft Graph:**"

# Mensagens de Erro
ERROR_400_MESSAGE = "Ocorreu um erro na sua solicitação (Erro 400 - Bad Request). Verifique se os parâmetros estão corretos."
ERROR_401_MESSAGE = "Acesso não autorizado (Erro 401 - Unauthorized). Minhas credenciais para este serviço podem ter expirado. Avise o time técnico!"
ERROR_TECHNICAL_MESSAGE = "Ocorreu um erro técnico inesperado. A equipe de desenvolvimento já foi notificada. Por favor, tente novamente mais tarde."


# Geração do Prompt de Sistema para a OpenAI

@lru_cache(maxsize=32)
def gerar_system_prompt(db: Any = None, historico_conversa: str = "", tom: str = "neutro") -> str:
    """
    Monta o prompt de sistema dinamicamente. No futuro, usará o banco de dados
    para definir a persona, contexto e o tom da resposta da IA.
    """
    fragmentos = []

    if db:
        fragmentos = [
            gerar_fragmento_persona(db),
            gerar_fragmento_empresa(db),
            gerar_fragmento_setores(db),
            gerar_fragmento_funcionarios(db),
            gerar_fragmento_gerentes(db),
            gerar_fragmento_projetos(db),
            gerar_fragmento_participacoes(db),
            gerar_fragmento_conhecimentos(db),
            gerar_fragmento_cerimonias(db),
        ]
    else:
        
        fragmentos.append("Você é Sofia, uma assistente de IA da Sonar. Você é prestativa, eficiente e se comunica de forma clara e amigável.")

    data_hoje = datetime.now().strftime("%d de %B de %Y")
    fragmentos.append(
        f"A data de hoje é {data_hoje}. Use essa informação para responder perguntas como 'qual é o dia de hoje?'."
    )

    if tom == "animado":
        fragmentos.append(
            "Adote um tom leve, simpático, entusiasmado e espontâneo. Use emoticons para deixar a interação mais agradável. 😊"
        )
    elif tom == "sério":
        fragmentos.append(
            "Adote um tom mais formal, direto e profissional, mantendo cordialidade e clareza."
        )

    if historico_conversa:
        fragmentos.append("\n--- Histórico da Conversa Recente ---\n" + historico_conversa)

    return "\n\n".join(p for p in fragmentos if p and p.strip())