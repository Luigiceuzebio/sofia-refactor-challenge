"""
Este handler gerencia todas as solicitações relacionadas ao Azure Boards.
Ele busca os dados dos work items, utiliza o cache para otimização,
processa as perguntas dos usuários para extrair insights e formata
as respostas de maneira estruturada.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
from core.cache import CacheManager
from config import prompts
from utils import helpers



def _detect_board_project(pergunta_lower: str, user_id: str, user_states: Dict, board_projects: Dict) -> Optional[str]:
    """Detecta o projeto do board com base na pergunta ou no estado do usuário."""
    for keyword, project in board_projects.items():
        if keyword in pergunta_lower:
            return project
    return user_states.get('ultimo_board_por_usuario', {}).get(user_id)


async def _get_boards_data(projeto: str, cache_manager: Any, buscar_epicos: bool, AzureBoardsService: Any, processing_module: Any) -> Optional[pd.DataFrame]:
    """Busca os dados do Azure Boards, utilizando o cache para otimizar."""
    cache_key = f"boards_{projeto}" + ("_epicos" if buscar_epicos else "")
    
    cached_df = cache_manager.get(cache_key)
    if cached_df is not None:
        return cached_df

    try:
        azure_service = AzureBoardsService(projeto)
        work_items = azure_service.buscar_work_items(batch_size=200)
        
        if not work_items:
            return None
        
        df = await processing_module.processar_work_items_df(work_items, projeto=projeto, buscar_epicos=buscar_epicos)
        
        cache_manager.set(cache_key, df, duration_seconds=600)
        return df
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados do Azure Boards para o projeto '{projeto}': {e}")
        return None


def _detect_collaborator(pergunta_lower: str, user_id: str, df: pd.DataFrame, user_states: Dict, collab_refs: List) -> Optional[str]:
    """Detecta se um colaborador é o foco da pergunta."""
    if any(termo in pergunta_lower for termo in collab_refs):
        return user_states.get('ultimo_colaborador_consultado', {}).get(user_id)
    
    tokens_pergunta = set(pergunta_lower.split())
    for responsavel in df['responsavel'].dropna().unique():
        partes_nome = set(responsavel.lower().split())
        if tokens_pergunta & partes_nome: 
        
            if 'ultimo_colaborador_consultado' not in user_states:
                user_states['ultimo_colaborador_consultado'] = {}
            user_states['ultimo_colaborador_consultado'][user_id] = responsavel
            return responsavel
            
    return None

def _process_collaborator_query(pergunta_lower: str, df: pd.DataFrame, nome_colaborador: str, processing_module: Any, constants: Dict) -> str:
    """Processa uma pergunta específica sobre um colaborador."""
    if any(t in pergunta_lower for t in constants.get('PROGRESS_KEYWORDS', [])):
        tarefas = processing_module.extrair_tarefas_por_colaborador_e_estado(df, nome_colaborador, "em andamento")
        return processing_module.formatar_lista_tarefas(tarefas, f"Tarefas em andamento de {nome_colaborador}")
        
    elif any(t in pergunta_lower for t in constants.get('TODO_KEYWORDS', [])):
        tarefas = processing_module.extrair_tarefas_por_colaborador_e_estado(df, nome_colaborador, "a fazer")
        return processing_module.formatar_lista_tarefas(tarefas, f"Tarefas a fazer de {nome_colaborador}")
        
    tarefas = processing_module.extrair_tarefas_por_colaborador(df, nome_colaborador)
    return processing_module.formatar_lista_tarefas(tarefas, f"Todas as tarefas de {nome_colaborador}")


def _process_general_query(pergunta_lower: str, df: pd.DataFrame, nome_amigavel: str, processing_module: Any, constants: Dict) -> str:
    """Processa uma pergunta geral sobre o estado do board."""
    mapa_tipos = constants.get('MAPA_TIPOS_ITENS', {})
    
    for chave, tipo in mapa_tipos.items():
        if f"quantos {chave}" in pergunta_lower or f"quantas {chave}" in pergunta_lower:
            total = len(df[df["tipo"].str.lower() == tipo])
            return f"🔢 Existem **{total}** item(ns) do tipo **{tipo.title()}** no board {nome_amigavel}."

    if any(t in pergunta_lower for t in constants.get('PROGRESS_KEYWORDS', [])):
        tarefas = processing_module.tarefas_em_andamento(df)
        return processing_module.formatar_lista_tarefas(tarefas, f"Tarefas em andamento do board {nome_amigavel}")

    if any(t in pergunta_lower for t in constants.get('TASK_COUNT_KEYWORDS', [])):
        responsavel, quantidade = processing_module.obter_responsavel_com_mais_tarefas(df)
        return f"O colaborador com mais tarefas no total é **{responsavel}**, com **{quantidade}** tarefas."

    return processing_module.formatar_visao_geral(df, f"Visão Geral do Board {nome_amigavel}")


# --- Função Principal do Handler ---

async def handle_boards_analysis(
    user_id: str, 
    message: str, 
    user_states: Dict, 
    cache_manager: Any,
    constants: Dict,
    AzureBoardsService: Any, 
    processing_module: Any   
) -> str:
    """
    Ponto de entrada para analisar e responder perguntas sobre o Azure Boards.
    """
    pergunta_lower = message.lower()

    if any(cmd in pergunta_lower for cmd in constants.get('EXIT_COMMANDS', [])):
        if user_id in user_states.get('modo_analise_boards', {}):
            del user_states['modo_analise_boards'][user_id]
        return constants.get('BOARDS_EXIT_MESSAGE')

    if any(cmd in pergunta_lower for cmd in constants.get('HELP_COMMANDS', [])):
        return constants.get('BOARDS_HELP_MESSAGE')

    projeto = _detect_board_project(pergunta_lower, user_id, user_states, constants.get('BOARD_PROJECTS', {}))
    if not projeto:
        return constants.get('BOARDS_SELECTION_MESSAGE')

    if 'ultimo_board_por_usuario' not in user_states:
        user_states['ultimo_board_por_usuario'] = {}
    user_states['ultimo_board_por_usuario'][user_id] = projeto
    nome_amigavel = "Operações" if projeto == "Sonar" else projeto

    buscar_epicos = any(termo in pergunta_lower for termo in constants.get('CLIENT_SEARCH_KEYWORDS', []))
    df = await _get_boards_data(projeto, cache_manager, buscar_epicos, AzureBoardsService, processing_module)

    if df is None or df.empty:
        return f"Desculpe, não consegui obter os dados do board '{nome_amigavel}' no momento."

    if any(w in pergunta_lower for w in constants.get('CLIENT_KEYWORDS', [])):
        return processing_module.cliente_com_mais_atividades(df, projeto=nome_amigavel)

    nome_colaborador = _detect_collaborator(pergunta_lower, user_id, df, user_states, constants.get('COLLABORATOR_REFERENCES', []))
    if nome_colaborador:
        return _process_collaborator_query(pergunta_lower, df, nome_colaborador, processing_module, constants)

    return _process_general_query(pergunta_lower, df, nome_amigavel, processing_module, constants)
