"""
Este módulo fornece uma classe de gerenciamento de cache em memória simples.
É usado para armazenar temporariamente dados que são caros para buscar,
como resultados de APIs externas (Azure Boards, SharePoint), para melhorar
o desempenho e reduzir o número de chamadas de rede.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

class CacheManager:
    """
    Gerencia um cache em memória com tempo de expiração para os itens.
    """
    def __init__(self, default_duration_seconds: int, cleanup_interval_seconds: int):
        """
        Inicializa o CacheManager.

        Args:
            default_duration_seconds (int): O tempo padrão em segundos que um item
                                            permanece no cache antes de ser considerado expirado.
            cleanup_interval_seconds (int): O intervalo em segundos para executar a
                                            limpeza automática de itens expirados.
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_duration = timedelta(seconds=default_duration_seconds)
        self._cleanup_interval = timedelta(seconds=cleanup_interval_seconds)
        self._last_cache_cleanup = datetime.now()

    def set(self, key: str, value: Any, duration_seconds: Optional[int] = None):
        """
        Adiciona ou atualiza um item no cache.

        Args:
            key (str): A chave única para o item do cache.
            value (Any): O valor a ser armazenado.
            duration_seconds (Optional[int]): Duração específica para este item em segundos.
                                               Se None, usa a duração padrão.
        """
        duration = timedelta(seconds=duration_seconds) if duration_seconds is not None else self._default_duration
        expiration_time = datetime.now() + duration
        
        self._cache[key] = {
            'value': value,
            'expires_at': expiration_time
        }
        print(f"📦 [Cache] Item '{key}' adicionado/atualizado. Expira em: {expiration_time.strftime('%H:%M:%S')}")

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera um item do cache, se ele existir e não estiver expirado.

        Args:
            key (str): A chave do item a ser recuperado.

        Returns:
            Optional[Any]: O valor do item se encontrado e válido, ou None caso contrário.
        """
        item = self._cache.get(key)

        if item and datetime.now() < item['expires_at']:
            print(f"✅ [Cache] Hit para a chave '{key}'.")
            return item['value']
        
        if item:
            print(f"❌ [Cache] Miss para a chave '{key}' (item expirado).")
            # Opcional: remover o item expirado imediatamente ao ser acessado
            del self._cache[key]
        else:
            print(f"🤷 [Cache] Miss para a chave '{key}' (não encontrado).")
            
        return None

    def cleanup(self):
        """
        Remove todos os itens expirados do cache.
        Esta função deve ser chamada periodicamente para evitar o acúmulo de memória.
        """
        now = datetime.now()
        if (now - self._last_cache_cleanup) > self._cleanup_interval:
            print(f"🧹 [Cache] Executando limpeza de itens expirados...")
            expired_keys = [
                key for key, data in self._cache.items()
                if now >= data['expires_at']
            ]
            
            if expired_keys:
                for key in expired_keys:
                    del self._cache[key]
                print(f"🗑️ [Cache] {len(expired_keys)} item(ns) expirado(s) removido(s).")
            else:
                print("✨ [Cache] Nenhum item expirado para remover.")
                
            self._last_cache_cleanup = now

    def clear(self):
        """
        Limpa completamente todos os itens do cache.
        """
        self._cache.clear()
        print("💥 [Cache] Todo o cache foi limpo.")

