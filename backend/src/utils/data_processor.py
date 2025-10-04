"""
Procesador de datos satelitales y utilidades de análisis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """Procesador de datos para análisis de vegetación"""
    
    def __init__(self):
        self.filters = {
            'cloud_mask': self._apply_cloud_mask,
            'outlier_removal': self._remove_outliers,
            'temporal_smoothing': self._apply_temporal_smoothing,
            'spatial_aggregation': self._aggregate_spatially
        }
    
    def process_time_series(self, raw_data: Dict, 
                          filters: List[str] = None) -> Dict:
        """
        Procesar serie temporal de datos satelitales
        
        Args:
            raw_data: Datos crudos de la API de NASA
            filters: Lista de filtros a aplicar
        
        Returns:
            Datos procesados y limpios
        """
        try:
            if filters is None:
                filters = ['cloud_mask', 'outlier_removal', 'temporal_smoothing']
            
            processed_data = raw_data.copy()
            
            # Aplicar filtros en secuencia
            for filter_name in filters:
                if filter_name in self.filters:
                    processed_data = self.filters[filter_name](processed_data)
                    logger.debug(f"Aplicado filtro: {filter_name}")
                else:
                    logger.warning(f"Filtro desconocido: {filter_name}")
            
            # Calcular índices adicionales
            processed_data = self._calculate_vegetation_indices(processed_data)
            
            # Agregar estadísticas de calidad
            processed_data = self._add_quality_metrics(processed_data)
            
            logger.info("Procesamiento de datos completado")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error procesando datos: {str(e)}")
            return raw_data
    
    def _apply_cloud_mask(self, data: Dict) -> Dict:
        """Aplicar máscara de nubes y pixels de mala calidad"""
        if 'time_series' not in data:
            return data
        
        ts = data['time_series']
        quality_flags = ts.get('quality_flags', ['good'] * len(ts['values']))
        values = np.array(ts['values'])
        
        # Identificar pixels de buena calidad
        good_quality = np.array([flag == 'good' for flag in quality_flags])
        
        # Para pixels de mala calidad, interpolar usando vecinos
        if np.any(~good_quality):
            interpolated_values = self._interpolate_missing_values(values, good_quality)
            ts['values'] = interpolated_values.tolist()
            
            # Actualizar flags de calidad
            new_flags = ['interpolated' if not good else 'good' 
                        for good in good_quality]
            ts['quality_flags'] = new_flags
        
        return data
    
    def _interpolate_missing_values(self, values: np.ndarray, 
                                   mask: np.ndarray) -> np.ndarray:
        """Interpolar valores faltantes o de mala calidad"""
        result = values.copy()
        
        # Encontrar índices de valores válidos
        valid_indices = np.where(mask)[0]
        invalid_indices = np.where(~mask)[0]
        
        if len(valid_indices) < 2:
            # No hay suficientes puntos válidos, usar media
            result[invalid_indices] = np.nanmean(values[mask])
        else:
            # Interpolación lineal
            for invalid_idx in invalid_indices:
                # Encontrar vecinos válidos más cercanos
                left_neighbor = None
                right_neighbor = None
                
                for valid_idx in valid_indices:
                    if valid_idx < invalid_idx:
                        left_neighbor = valid_idx
                    elif valid_idx > invalid_idx and right_neighbor is None:
                        right_neighbor = valid_idx
                        break
                
                # Interpolar
                if left_neighbor is not None and right_neighbor is not None:
                    # Interpolación lineal entre vecinos
                    weight = (invalid_idx - left_neighbor) / (right_neighbor - left_neighbor)
                    result[invalid_idx] = (values[left_neighbor] * (1 - weight) + 
                                         values[right_neighbor] * weight)
                elif left_neighbor is not None:
                    # Usar valor del vecino izquierdo
                    result[invalid_idx] = values[left_neighbor]
                elif right_neighbor is not None:
                    # Usar valor del vecino derecho
                    result[invalid_idx] = values[right_neighbor]
                else:
                    # Usar media de todos los valores válidos
                    result[invalid_idx] = np.mean(values[mask])
        
        return result
    
    def _remove_outliers(self, data: Dict) -> Dict:
        """Remover outliers estadísticos"""
        if 'time_series' not in data:
            return data
        
        ts = data['time_series']
        values = np.array(ts['values'])
        
        # Método IQR para detección de outliers
        q25 = np.percentile(values, 25)
        q75 = np.percentile(values, 75)
        iqr = q75 - q25
        
        # Límites para outliers
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        
        # Identificar outliers
        is_outlier = (values < lower_bound) | (values > upper_bound)
        
        if np.any(is_outlier):
            # Reemplazar outliers con valores interpolados
            clean_mask = ~is_outlier
            clean_values = self._interpolate_missing_values(values, clean_mask)
            ts['values'] = clean_values.tolist()
            
            # Actualizar flags de calidad
            quality_flags = ts.get('quality_flags', ['good'] * len(values))
            for i, is_out in enumerate(is_outlier):
                if is_out:
                    quality_flags[i] = 'outlier_corrected'
            ts['quality_flags'] = quality_flags
            
            logger.debug(f"Corregidos {np.sum(is_outlier)} outliers")
        
        return data
    
    def _apply_temporal_smoothing(self, data: Dict) -> Dict:
        """Aplicar suavizado temporal para reducir ruido"""
        if 'time_series' not in data:
            return data
        
        ts = data['time_series']
        values = np.array(ts['values'])
        
        # Aplicar filtro de media móvil
        window_size = min(5, len(values) // 2)
        if window_size >= 3:
            smoothed = pd.Series(values).rolling(
                window=window_size, 
                center=True, 
                min_periods=1
            ).mean().values
            
            ts['values_smoothed'] = smoothed.tolist()
            ts['smoothing_applied'] = {
                'method': 'moving_average',
                'window_size': window_size
            }
        
        return data
    
    def _aggregate_spatially(self, data: Dict) -> Dict:
        """Agregar datos espacialmente (para futuras mejoras)"""
        # Placeholder para agregación espacial
        # En implementación completa, manejaría múltiples pixels
        return data
    
    def _calculate_vegetation_indices(self, data: Dict) -> Dict:
        """Calcular índices de vegetación adicionales"""
        if 'time_series' not in data:
            return data
        
        ts = data['time_series']
        values = np.array(ts['values'])
        
        # Si tenemos NDVI, calcular índices derivados
        if 'NDVI' in ts.get('units', ''):
            # EVI simulado (normalmente requiere bandas adicionales)
            evi_approx = self._approximate_evi_from_ndvi(values)
            ts['evi_approximated'] = evi_approx.tolist()
            
            # SAVI (Soil Adjusted Vegetation Index) aproximado
            L = 0.5  # Factor de ajuste de suelo
            savi_approx = values * (1 + L) / (values + L)
            ts['savi_approximated'] = savi_approx.tolist()
            
            # Índice de verdor relativo
            greenness_index = (values - np.min(values)) / (np.max(values) - np.min(values))
            ts['greenness_index'] = greenness_index.tolist()
        
        return data
    
    def _approximate_evi_from_ndvi(self, ndvi: np.ndarray) -> np.ndarray:
        """Aproximar EVI desde NDVI (simplificado)"""
        # Relación empírica aproximada NDVI -> EVI
        # En realidad EVI requiere bandas roja, NIR y azul
        evi = 2.5 * ndvi / (1 + 6 * ndvi - 7.5 * ndvi + 1)
        return np.clip(evi, -1, 1)
    
    def _add_quality_metrics(self, data: Dict) -> Dict:
        """Agregar métricas de calidad del procesamiento"""
        if 'time_series' not in data:
            return data
        
        ts = data['time_series']
        values = np.array(ts['values'])
        quality_flags = ts.get('quality_flags', [])
        
        # Calcular métricas de calidad
        quality_metrics = {
            'total_observations': len(values),
            'good_quality_count': sum(1 for flag in quality_flags if flag == 'good'),
            'interpolated_count': sum(1 for flag in quality_flags if 'interpolated' in flag),
            'outlier_corrected_count': sum(1 for flag in quality_flags if 'outlier' in flag),
            'data_completeness': sum(1 for flag in quality_flags if flag == 'good') / len(quality_flags) if quality_flags else 1.0,
            'temporal_consistency': self._calculate_temporal_consistency(values),
            'signal_to_noise_ratio': self._calculate_snr(values)
        }
        
        data['quality_metrics'] = quality_metrics
        return data
    
    def _calculate_temporal_consistency(self, values: np.ndarray) -> float:
        """Calcular consistencia temporal de la serie"""
        if len(values) < 3:
            return 1.0
        
        # Calcular variabilidad de las diferencias consecutivas
        diffs = np.diff(values)
        consistency = 1.0 - (np.std(diffs) / np.mean(np.abs(diffs))) if np.mean(np.abs(diffs)) > 0 else 1.0
        return max(0.0, min(1.0, consistency))
    
    def _calculate_snr(self, values: np.ndarray) -> float:
        """Calcular relación señal-ruido aproximada"""
        if len(values) < 3:
            return 1.0
        
        # Señal: tendencia general (media móvil)
        if len(values) >= 5:
            signal = pd.Series(values).rolling(window=5, center=True, min_periods=1).mean()
            noise = np.std(values - signal)
            signal_power = np.std(signal)
            
            if noise > 0:
                snr = signal_power / noise
            else:
                snr = float('inf')
        else:
            snr = np.mean(values) / np.std(values) if np.std(values) > 0 else 1.0
        
        return min(100.0, max(0.1, snr))  # Limitar rango
    
    def calculate_phenology_metrics(self, data: Dict) -> Dict:
        """Calcular métricas fenológicas"""
        if 'time_series' not in data:
            return {}
        
        ts = data['time_series']
        dates = [datetime.strptime(d, '%Y-%m-%d') for d in ts['dates']]
        values = np.array(ts['values'])
        
        metrics = {}
        
        # Start of Season (SOS) - cuando los valores comienzan a aumentar
        sos_idx = self._find_season_start(values)
        if sos_idx is not None:
            metrics['start_of_season'] = dates[sos_idx].strftime('%Y-%m-%d')
        
        # Peak of Season (POS) - valor máximo
        pos_idx = np.argmax(values)
        metrics['peak_of_season'] = dates[pos_idx].strftime('%Y-%m-%d')
        metrics['peak_value'] = float(values[pos_idx])
        
        # End of Season (EOS) - cuando los valores comienzan a declinar
        eos_idx = self._find_season_end(values, pos_idx)
        if eos_idx is not None:
            metrics['end_of_season'] = dates[eos_idx].strftime('%Y-%m-%d')
        
        # Length of Season
        if sos_idx is not None and eos_idx is not None:
            metrics['season_length_days'] = (dates[eos_idx] - dates[sos_idx]).days
        
        # Integrated NDVI (área bajo la curva)
        metrics['integrated_ndvi'] = float(np.trapz(values))
        
        # Amplitud estacional
        metrics['seasonal_amplitude'] = float(np.max(values) - np.min(values))
        
        return metrics
    
    def _find_season_start(self, values: np.ndarray) -> Optional[int]:
        """Encontrar inicio de temporada de crecimiento"""
        if len(values) < 5:
            return None
        
        # Buscar el punto donde la serie comienza a aumentar consistentemente
        min_val = np.min(values)
        threshold = min_val + 0.2 * (np.max(values) - min_val)
        
        for i in range(len(values) - 2):
            if values[i] < threshold and values[i+1] >= threshold:
                return i + 1
        
        return None
    
    def _find_season_end(self, values: np.ndarray, peak_idx: int) -> Optional[int]:
        """Encontrar final de temporada de crecimiento"""
        if peak_idx >= len(values) - 1:
            return None
        
        peak_val = values[peak_idx]
        threshold = peak_val * 0.5  # 50% del pico
        
        for i in range(peak_idx + 1, len(values)):
            if values[i] <= threshold:
                return i
        
        return len(values) - 1
    
    def export_processed_data(self, data: Dict, format_type: str = 'json') -> Any:
        """Exportar datos procesados en diferentes formatos"""
        if format_type == 'json':
            return data
        elif format_type == 'csv':
            return self._convert_to_csv(data)
        elif format_type == 'dataframe':
            return self._convert_to_dataframe(data)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")
    
    def _convert_to_csv(self, data: Dict) -> str:
        """Convertir datos a formato CSV"""
        if 'time_series' not in data:
            return ""
        
        ts = data['time_series']
        df = pd.DataFrame({
            'date': ts['dates'],
            'value': ts['values'],
            'quality_flag': ts.get('quality_flags', ['good'] * len(ts['values']))
        })
        
        # Agregar columnas adicionales si existen
        for key in ['values_smoothed', 'evi_approximated', 'savi_approximated']:
            if key in ts:
                df[key] = ts[key]
        
        return df.to_csv(index=False)
    
    def _convert_to_dataframe(self, data: Dict) -> pd.DataFrame:
        """Convertir datos a DataFrame de pandas"""
        if 'time_series' not in data:
            return pd.DataFrame()
        
        ts = data['time_series']
        df = pd.DataFrame({
            'date': pd.to_datetime(ts['dates']),
            'value': ts['values'],
            'quality_flag': ts.get('quality_flags', ['good'] * len(ts['values']))
        })
        
        # Agregar columnas adicionales
        for key in ['values_smoothed', 'evi_approximated', 'savi_approximated']:
            if key in ts:
                df[key] = ts[key]
        
        return df