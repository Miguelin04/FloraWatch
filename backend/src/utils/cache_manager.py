"""
Gestor de cache para optimizar rendimiento
"""

import os
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestor de cache para datos satelitales y resultados procesados"""
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.getenv('CACHE_DIR', './data/cache')
        self.default_expiry_hours = int(os.getenv('CACHE_EXPIRY_HOURS', 24))
        
        # Crear directorio de cache si no existe
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Subdirectorios para diferentes tipos de datos
        self.subdirs = {
            'satellite_data': os.path.join(self.cache_dir, 'satellite'),
            'processed_data': os.path.join(self.cache_dir, 'processed'),
            'predictions': os.path.join(self.cache_dir, 'predictions'),
            'events': os.path.join(self.cache_dir, 'events')
        }
        
        for subdir in self.subdirs.values():
            os.makedirs(subdir, exist_ok=True)
    
    def is_available(self) -> bool:
        """Verificar si el sistema de cache está disponible"""
        try:
            test_file = os.path.join(self.cache_dir, '.test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except:
            return False
    
    def get(self, key: str, data_type: str = 'general') -> Optional[Any]:
        """
        Obtener datos del cache
        
        Args:
            key: Clave única del cache
            data_type: Tipo de datos (satellite_data, processed_data, etc.)
        
        Returns:
            Datos del cache o None si no existe/expiró
        """
        try:
            cache_file = self._get_cache_file_path(key, data_type)
            
            if not os.path.exists(cache_file):
                return None
            
            # Verificar si el archivo ha expirado
            if self._is_expired(cache_file):
                self._remove_cache_file(cache_file)
                return None
            
            # Leer datos del cache
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            logger.debug(f"Cache hit para clave: {key}")
            return cache_data['data']
            
        except Exception as e:
            logger.warning(f"Error leyendo cache para {key}: {str(e)}")
            return None
    
    def set(self, key: str, data: Any, data_type: str = 'general', 
            expiry_hours: int = None) -> bool:
        """
        Guardar datos en cache
        
        Args:
            key: Clave única del cache
            data: Datos a guardar
            data_type: Tipo de datos
            expiry_hours: Horas hasta expiración (None usa default)
        
        Returns:
            True si se guardó exitosamente
        """
        try:
            cache_file = self._get_cache_file_path(key, data_type)
            expiry_hours = expiry_hours or self.default_expiry_hours
            
            cache_data = {
                'data': data,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat(),
                'key': key,
                'data_type': data_type
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.debug(f"Datos guardados en cache: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando en cache {key}: {str(e)}")
            return False
    
    def delete(self, key: str, data_type: str = 'general') -> bool:
        """Eliminar entrada del cache"""
        try:
            cache_file = self._get_cache_file_path(key, data_type)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                logger.debug(f"Cache eliminado: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando cache {key}: {str(e)}")
            return False
    
    def clear(self, data_type: str = None) -> int:
        """
        Limpiar cache
        
        Args:
            data_type: Tipo específico a limpiar (None limpia todo)
        
        Returns:
            Número de archivos eliminados
        """
        removed_count = 0
        
        try:
            if data_type and data_type in self.subdirs:
                # Limpiar tipo específico
                target_dir = self.subdirs[data_type]
                for filename in os.listdir(target_dir):
                    file_path = os.path.join(target_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        removed_count += 1
            else:
                # Limpiar todo el cache
                for subdir in self.subdirs.values():
                    if os.path.exists(subdir):
                        for filename in os.listdir(subdir):
                            file_path = os.path.join(subdir, filename)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                removed_count += 1
            
            logger.info(f"Cache limpiado: {removed_count} archivos eliminados")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error limpiando cache: {str(e)}")
            return removed_count
    
    def cleanup_expired(self) -> int:
        """Limpiar archivos de cache expirados"""
        removed_count = 0
        
        try:
            for subdir in self.subdirs.values():
                if os.path.exists(subdir):
                    for filename in os.listdir(subdir):
                        file_path = os.path.join(subdir, filename)
                        if os.path.isfile(file_path) and self._is_expired(file_path):
                            os.remove(file_path)
                            removed_count += 1
            
            logger.info(f"Limpieza de cache: {removed_count} archivos expirados eliminados")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error en limpieza de cache: {str(e)}")
            return removed_count
    
    def get_cache_stats(self) -> dict:
        """Obtener estadísticas del cache"""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_type': {},
            'oldest_file': None,
            'newest_file': None
        }
        
        try:
            oldest_time = None
            newest_time = None
            
            for data_type, subdir in self.subdirs.items():
                if os.path.exists(subdir):
                    type_files = 0
                    type_size = 0
                    
                    for filename in os.listdir(subdir):
                        file_path = os.path.join(subdir, filename)
                        if os.path.isfile(file_path):
                            type_files += 1
                            type_size += os.path.getsize(file_path)
                            
                            # Rastrear fechas
                            file_time = os.path.getmtime(file_path)
                            if oldest_time is None or file_time < oldest_time:
                                oldest_time = file_time
                                stats['oldest_file'] = datetime.fromtimestamp(file_time).isoformat()
                            
                            if newest_time is None or file_time > newest_time:
                                newest_time = file_time
                                stats['newest_file'] = datetime.fromtimestamp(file_time).isoformat()
                    
                    stats['by_type'][data_type] = {
                        'files': type_files,
                        'size_mb': round(type_size / (1024 * 1024), 2)
                    }
                    
                    stats['total_files'] += type_files
                    stats['total_size_mb'] += type_size / (1024 * 1024)
            
            stats['total_size_mb'] = round(stats['total_size_mb'], 2)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de cache: {str(e)}")
        
        return stats
    
    def _get_cache_file_path(self, key: str, data_type: str) -> str:
        """Generar path del archivo de cache"""
        # Hash de la clave para nombre de archivo seguro
        key_hash = hashlib.md5(key.encode()).hexdigest()
        
        # Determinar subdirectorio
        if data_type in self.subdirs:
            subdir = self.subdirs[data_type]
        else:
            subdir = self.cache_dir
        
        return os.path.join(subdir, f"{key_hash}.cache")
    
    def _is_expired(self, file_path: str) -> bool:
        """Verificar si un archivo de cache ha expirado"""
        try:
            # Leer metadata del archivo
            with open(file_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            expires_at = datetime.fromisoformat(cache_data['expires_at'])
            return datetime.utcnow() > expires_at
            
        except:
            # Si no se puede leer, considerar expirado
            return True
    
    def _remove_cache_file(self, file_path: str):
        """Remover archivo de cache"""
        try:
            os.remove(file_path)
        except:
            pass
    
    def exists(self, key: str, data_type: str = 'general') -> bool:
        """Verificar si existe una clave en cache (sin cargar datos)"""
        cache_file = self._get_cache_file_path(key, data_type)
        if not os.path.exists(cache_file):
            return False
        
        return not self._is_expired(cache_file)
    
    def update_expiry(self, key: str, data_type: str = 'general', 
                     new_expiry_hours: int = None) -> bool:
        """Actualizar tiempo de expiración de una entrada"""
        try:
            cache_file = self._get_cache_file_path(key, data_type)
            
            if not os.path.exists(cache_file):
                return False
            
            # Leer datos existentes
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Actualizar expiración
            new_expiry_hours = new_expiry_hours or self.default_expiry_hours
            cache_data['expires_at'] = (
                datetime.utcnow() + timedelta(hours=new_expiry_hours)
            ).isoformat()
            
            # Reescribir archivo
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando expiración para {key}: {str(e)}")
            return False