"""
Este handler é responsável por todas as interações relacionadas a arquivos.
Ele se comunica com o SharePointService para buscar e listar documentos,
utiliza o CacheManager para otimizar as buscas e formata as respostas
de forma clara para o usuário.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from core.cache import CacheManager
from config import prompts
from utils import helpers

def _formatar_resultados_busca(termo_busca: str, arquivos: List[Dict], constants: Dict, helpers: Any) -> str:
    """Formata a lista de arquivos encontrados em uma string de resposta."""
    if not arquivos:
        return constants.get('FILE_SEARCH_NO_RESULTS', "Nenhum arquivo encontrado para '{}'").format(termo_busca)

    total_arquivos = len(arquivos)
    header = f"📂 Encontrei **{total_arquivos}** arquivo(s) para '**{termo_busca}**':\n\n"
    
    resultados_formatados = []
    for i, arquivo in enumerate(arquivos, 1):
        nome = arquivo.get('name', 'Sem nome')
        url = helpers.obter_url_valida(arquivo, constants.get('URL_FIELDS'), constants.get('URL_VALIDATION_PATTERNS'), constants.get('INVALID_URL_PATTERNS'))
        data_modificacao = helpers.formatar_data_com_hora(arquivo.get("lastModifiedDateTime"))
        
        resultados_formatados.append(f"{i}. **[{nome}]({url})** 📄 {data_modificacao}")

    instrucao = constants.get('MULTIPLE_FILES_CLICK_INSTRUCTION') if total_arquivos > 1 else constants.get('SINGLE_FILE_CLICK_INSTRUCTION')
    
    return header + "\n".join(resultados_formatados) + f"\n\n{instrucao}"


async def _search_with_ai_interpretation(termo_busca: str, openai_service: Any, sharepoint_service: Any) -> Optional[List[Dict]]:
    """Tenta refinar o termo de busca usando IA antes de pesquisar."""
    try:
        termo_limpo = await openai_service.interpretar_termo_busca(termo_busca)
        if termo_limpo.lower() != termo_busca.lower():
            return sharepoint_service.search_files(termo_limpo)
    except Exception as e:
        print(f"⚠️ Erro na interpretação por IA do termo de busca: {e}")
    return None


def _search_with_variations(termo_busca: str, sharepoint_service: Any) -> Optional[List[Dict]]:
    """Busca por variações comuns do termo de busca."""
    variations = [
        termo_busca.replace(' ', '_'),
        termo_busca.replace(' ', '-'),
        termo_busca.title()
    ]
    for variation in variations:
        try:
            arquivos = sharepoint_service.search_files(variation)
            if arquivos:
                return arquivos
        except Exception:
            continue
    return None

async def listar_arquivos_recentes(sharepoint_service: Any, constants: Dict, helpers: Any, quantidade: int) -> str:
    """
    Busca os arquivos mais recentes no SharePoint e formata a resposta.

    Args:
        sharepoint_service: A instância do serviço do SharePoint.
        constants: Dicionário com constantes de prompts e configurações.
        helpers: Módulo com funções utilitárias.
        quantidade: O número de arquivos a serem listados.

    Returns:
        Uma string com a lista de arquivos formatada ou uma mensagem de erro.
    """
    try:
        arquivos = sharepoint_service.list_recent_files(limit=quantidade)
        if not arquivos:
            return constants.get('NO_FILES_MESSAGE')

        header = f"📂 Aqui estão os **{len(arquivos)}** arquivos mais recentes que encontrei:\n\n"
        
        resultados_formatados = []
        for i, arquivo in enumerate(arquivos, 1):
            nome = arquivo.get('name', 'Sem nome')
            url = helpers.obter_url_valida(arquivo, constants.get('URL_FIELDS'), constants.get('URL_VALIDATION_PATTERNS'), constants.get('INVALID_URL_PATTERNS'))
            data_modificacao = helpers.formatar_data_com_hora(arquivo.get("lastModifiedDateTime"))
            resultados_formatados.append(f"{i}. **[{nome}]({url})** 📄 {data_modificacao}")

        return header + "\n".join(resultados_formatados) + f"\n\n{constants.get('FILE_LIST_INSTRUCTIONS')}"

    except Exception as e:
        print(f"❌ Erro ao listar arquivos no file_handler: {e}")
        return constants.get('ERROR_TECHNICAL_MESSAGE')


async def buscar_arquivo_por_termo(
    termo_busca: str, 
    cache_manager: Any,
    sharepoint_service: Any, 
    openai_service: Any,
    constants: Dict,
    helpers: Any
) -> str:
    """
    Orquestra a busca por um arquivo usando múltiplas estratégias em cascata.

    Args:
        termo_busca: O termo que o usuário deseja buscar.
        cache_manager: A instância do gerenciador de cache.
        sharepoint_service: A instância do serviço do SharePoint.
        openai_service: A instância do serviço da OpenAI.
        constants: Dicionário com constantes.
        helpers: Módulo com funções utilitárias.

    Returns:
        Uma string com os resultados da busca formatados.
    """
    if not termo_busca.strip():
        return constants.get('FILE_NOT_FOUND_MESSAGE')

    cache_key = f"search_{termo_busca.lower().replace(' ', '_')}"
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        return cached_result

    arquivos_encontrados = None
    
    try:
        arquivos_encontrados = sharepoint_service.search_files(termo_busca)
    except Exception:
        pass

    if not arquivos_encontrados:
        arquivos_encontrados = await _search_with_ai_interpretation(termo_busca, openai_service, sharepoint_service)

    if not arquivos_encontrados:
        arquivos_encontrados = _search_with_variations(termo_busca, sharepoint_service)

    resultado_final = _formatar_resultados_busca(termo_busca, arquivos_encontrados or [], constants, helpers)
    
    cache_manager.set(cache_key, resultado_final, duration_seconds=300)
    
    return resultado_final
