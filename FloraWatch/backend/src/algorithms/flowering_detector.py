"""
Algoritmos de detección de eventos de floración
Utiliza análisis de series temporales e índices espectrales
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from scipy import signal
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

class FloweringDetector:
    """Detector de eventos de floración usando datos satelitales"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.detection_algorithms = {
            'threshold': self._detect_by_threshold,
            'change_detection': self._detect_by_change,
            'seasonal_anomaly': self._detect_seasonal_anomaly,
            'machine_learning': self._detect_by_ml
        }
        
        # Parámetros de detección configurables
        self.config = {
            'ndvi_flowering_threshold': 0.15,  # Incremento mínimo en NDVI
            'evi_flowering_threshold': 0.12,   # Incremento mínimo en EVI
            'min_duration_days': 5,            # Duración mínima del evento
            'max_duration_days': 45,           # Duración máxima del evento
            'smoothing_window': 3,             # Ventana de suavizado
            'seasonal_baseline_days': 365,     # Días para calcular baseline estacional
            'anomaly_threshold_sigma': 2.0     # Umbral de anomalía en sigmas
        }
    
    def detect_events(self, satellite_data: Dict, 
                     algorithm: str = 'change_detection') -> List[Dict]:
        """
        Detectar eventos de floración en datos satelitales
        
        Args:
            satellite_data: Datos de series temporales
            algorithm: Algoritmo a usar ('threshold', 'change_detection', etc.)
        
        Returns:
            Lista de eventos detectados
        """
        try:
            if not self._validate_data(satellite_data):
                logger.error("Datos de entrada inválidos")
                return []
            
            # Extraer serie temporal
            time_series = satellite_data['time_series']
            dates = [datetime.strptime(d, '%Y-%m-%d') for d in time_series['dates']]
            values = np.array(time_series['values'])
            quality_flags = time_series.get('quality_flags', ['good'] * len(values))
            
            # Filtrar datos de buena calidad
            good_indices = [i for i, flag in enumerate(quality_flags) if flag == 'good']
            if len(good_indices) < 3:
                logger.warning("Datos insuficientes de buena calidad")
                return []
            
            clean_dates = [dates[i] for i in good_indices]
            clean_values = values[good_indices]
            
            # Aplicar suavizado
            smoothed_values = self._smooth_time_series(clean_values)
            
            # Detectar eventos usando algoritmo especificado
            if algorithm not in self.detection_algorithms:
                logger.warning(f"Algoritmo {algorithm} no disponible, usando change_detection")
                algorithm = 'change_detection'
            
            events = self.detection_algorithms[algorithm](clean_dates, smoothed_values)
            
            # Enriquecer eventos con metadatos
            enriched_events = []
            for event in events:
                enriched_event = self._enrich_event(event, satellite_data)
                enriched_events.append(enriched_event)
            
            logger.info(f"Detectados {len(enriched_events)} eventos de floración")
            return enriched_events
            
        except Exception as e:
            logger.error(f"Error detectando eventos: {str(e)}")
            return []
    
    def _validate_data(self, data: Dict) -> bool:
        """Validar estructura de datos de entrada"""
        required_keys = ['time_series', 'location']
        if not all(key in data for key in required_keys):
            return False
        
        ts = data['time_series']
        required_ts_keys = ['dates', 'values']
        if not all(key in ts for key in required_ts_keys):
            return False
        
        if len(ts['dates']) != len(ts['values']):
            return False
        
        return True
    
    def _smooth_time_series(self, values: np.ndarray) -> np.ndarray:
        """Aplicar suavizado a la serie temporal"""
        window_size = self.config['smoothing_window']
        if len(values) < window_size:
            return values
        
        # Usar filtro de media móvil
        return pd.Series(values).rolling(
            window=window_size, 
            center=True, 
            min_periods=1
        ).mean().values
    
    def _detect_by_threshold(self, dates: List[datetime], 
                           values: np.ndarray) -> List[Dict]:
        """Detección por umbral absoluto de incremento"""
        events = []
        threshold = self.config['ndvi_flowering_threshold']
        
        # Calcular baseline como media móvil de largo plazo
        baseline_window = min(len(values) // 3, 10)
        if baseline_window < 2:
            baseline = np.mean(values)
        else:
            baseline = pd.Series(values).rolling(
                window=baseline_window, 
                center=True, 
                min_periods=1
            ).mean().values
        
        # Detectar puntos que superan el umbral
        exceedances = values - baseline > threshold
        
        # Agrupar exceedances consecutivos en eventos
        events = self._group_consecutive_exceedances(dates, values, exceedances)
        
        return events
    
    def _detect_by_change(self, dates: List[datetime], 
                         values: np.ndarray) -> List[Dict]:
        """Detección por cambio relativo significativo"""
        events = []
        
        if len(values) < 5:
            return events
        
        # Calcular diferencias suavizadas
        diff = np.diff(values)
        diff_smooth = self._smooth_time_series(diff)
        
        # Detectar incrementos significativos
        threshold = np.std(diff_smooth) * 1.5
        significant_increases = diff_smooth > threshold
        
        # Encontrar inicio de eventos (incrementos significativos)
        event_starts = []
        for i, is_increase in enumerate(significant_increases):
            if is_increase and (i == 0 or not significant_increases[i-1]):
                event_starts.append(i)
        
        # Para cada inicio, encontrar el pico y fin del evento
        for start_idx in event_starts:
            event = self._track_flowering_event(dates, values, start_idx)
            if event:
                events.append(event)
        
        return events
    
    def _detect_seasonal_anomaly(self, dates: List[datetime], 
                                values: np.ndarray) -> List[Dict]:
        """Detección basada en anomalías estacionales"""
        events = []
        
        if len(values) < 10:
            return events
        
        # Crear DataFrame para análisis
        df = pd.DataFrame({
            'date': dates,
            'value': values,
            'day_of_year': [d.timetuple().tm_yday for d in dates]
        })
        
        # Calcular media y desviación estándar por día del año
        seasonal_stats = df.groupby('day_of_year')['value'].agg(['mean', 'std'])
        
        # Calcular anomalías
        anomalies = []
        for _, row in df.iterrows():
            day = row['day_of_year']
            if day in seasonal_stats.index:
                mean_val = seasonal_stats.loc[day, 'mean']
                std_val = seasonal_stats.loc[day, 'std']
                if std_val > 0:
                    anomaly = (row['value'] - mean_val) / std_val
                else:
                    anomaly = 0
            else:
                anomaly = 0
            anomalies.append(anomaly)
        
        # Detectar anomalías positivas significativas
        threshold = self.config['anomaly_threshold_sigma']
        significant_anomalies = np.array(anomalies) > threshold
        
        events = self._group_consecutive_exceedances(dates, values, significant_anomalies)
        
        return events
    
    def _detect_by_ml(self, dates: List[datetime], 
                     values: np.ndarray) -> List[Dict]:
        """Detección usando clustering/clasificación"""
        events = []
        
        if len(values) < 10:
            return events
        
        # Crear características para cada punto temporal
        features = []
        for i in range(len(values)):
            # Valor actual
            current_val = values[i]
            
            # Valores en ventana temporal
            window_start = max(0, i - 2)
            window_end = min(len(values), i + 3)
            window_vals = values[window_start:window_end]
            
            # Características estadísticas
            feature_vector = [
                current_val,
                np.mean(window_vals),
                np.std(window_vals),
                np.max(window_vals) - np.min(window_vals),
                dates[i].timetuple().tm_yday / 365.0,  # Día del año normalizado
            ]
            
            features.append(feature_vector)
        
        features = np.array(features)
        
        # Aplicar clustering para identificar patrones anómalos
        try:
            features_scaled = self.scaler.fit_transform(features)
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_scaled)
            
            # Identificar cluster que podría representar floración
            # (valores altos, variabilidad moderada)
            cluster_means = []
            for cluster_id in range(3):
                cluster_mask = clusters == cluster_id
                if np.any(cluster_mask):
                    cluster_mean_ndvi = np.mean(values[cluster_mask])
                    cluster_means.append((cluster_id, cluster_mean_ndvi))
            
            # Seleccionar cluster con valores más altos
            if cluster_means:
                flowering_cluster = max(cluster_means, key=lambda x: x[1])[0]
                flowering_points = clusters == flowering_cluster
                
                events = self._group_consecutive_exceedances(dates, values, flowering_points)
        
        except Exception as e:
            logger.warning(f"Error en detección ML: {str(e)}")
            # Fallback a detección por cambios
            events = self._detect_by_change(dates, values)
        
        return events
    
    def _group_consecutive_exceedances(self, dates: List[datetime], 
                                     values: np.ndarray, 
                                     exceedances: np.ndarray) -> List[Dict]:
        """Agrupar exceedances consecutivos en eventos"""
        events = []
        
        # Encontrar grupos consecutivos
        groups = []
        current_group = []
        
        for i, exceeds in enumerate(exceedances):
            if exceeds:
                current_group.append(i)
            else:
                if current_group:
                    groups.append(current_group)
                    current_group = []
        
        # No olvidar el último grupo
        if current_group:
            groups.append(current_group)
        
        # Convertir grupos en eventos
        for group in groups:
            if len(group) >= 2:  # Evento mínimo de 2 puntos
                start_idx = group[0]
                end_idx = group[-1]
                peak_idx = group[np.argmax(values[group])]
                
                duration = (dates[end_idx] - dates[start_idx]).days
                
                # Filtrar por duración
                min_dur = self.config['min_duration_days']
                max_dur = self.config['max_duration_days']
                
                if min_dur <= duration <= max_dur:
                    event = {
                        'start_date': dates[start_idx].strftime('%Y-%m-%d'),
                        'end_date': dates[end_idx].strftime('%Y-%m-%d'),
                        'peak_date': dates[peak_idx].strftime('%Y-%m-%d'),
                        'duration_days': duration,
                        'peak_value': float(values[peak_idx]),
                        'intensity': float(values[peak_idx] - np.mean(values)),
                        'confidence': self._calculate_confidence(group, values)
                    }
                    events.append(event)
        
        return events
    
    def _track_flowering_event(self, dates: List[datetime], 
                              values: np.ndarray, start_idx: int) -> Optional[Dict]:
        """Rastrear un evento de floración desde su inicio"""
        if start_idx >= len(values) - 1:
            return None
        
        # Buscar el pico del evento
        peak_idx = start_idx
        peak_value = values[start_idx]
        
        # Buscar hacia adelante hasta encontrar el máximo
        for i in range(start_idx + 1, min(len(values), start_idx + 10)):
            if values[i] > peak_value:
                peak_value = values[i]
                peak_idx = i
            elif values[i] < peak_value * 0.8:  # Declive significativo
                break
        
        # Buscar el final del evento (cuando baja significativamente)
        end_idx = peak_idx
        for i in range(peak_idx + 1, min(len(values), peak_idx + 15)):
            if values[i] < peak_value * 0.7:
                end_idx = i
                break
            end_idx = i
        
        duration = (dates[end_idx] - dates[start_idx]).days
        
        # Validar duración
        min_dur = self.config['min_duration_days']
        max_dur = self.config['max_duration_days']
        
        if min_dur <= duration <= max_dur:
            return {
                'start_date': dates[start_idx].strftime('%Y-%m-%d'),
                'end_date': dates[end_idx].strftime('%Y-%m-%d'),
                'peak_date': dates[peak_idx].strftime('%Y-%m-%d'),
                'duration_days': duration,
                'peak_value': float(peak_value),
                'intensity': float(peak_value - np.mean(values)),
                'confidence': self._calculate_confidence(list(range(start_idx, end_idx + 1)), values)
            }
        
        return None
    
    def _calculate_confidence(self, event_indices: List[int], 
                            values: np.ndarray) -> float:
        """Calcular confianza del evento detectado"""
        if not event_indices:
            return 0.0
        
        event_values = values[event_indices]
        all_values = values
        
        # Factores de confianza
        factors = {
            'intensity': min(1.0, (np.max(event_values) - np.mean(all_values)) / np.std(all_values)),
            'duration': min(1.0, len(event_indices) / 5.0),  # Normalizar por duración esperada
            'consistency': 1.0 - (np.std(event_values) / np.mean(event_values)) if np.mean(event_values) > 0 else 0,
            'contrast': min(1.0, np.mean(event_values) / np.mean(all_values) - 1.0)
        }
        
        # Peso promedio de factores
        weights = {'intensity': 0.4, 'duration': 0.2, 'consistency': 0.2, 'contrast': 0.2}
        
        confidence = sum(factors[key] * weights[key] for key in factors.keys())
        return max(0.0, min(1.0, confidence))
    
    def _enrich_event(self, event: Dict, satellite_data: Dict) -> Dict:
        """Enriquecer evento con información adicional"""
        enriched = event.copy()
        
        # Agregar información de ubicación
        enriched['location'] = satellite_data['location']
        
        # Agregar información del producto satelital
        enriched['data_source'] = satellite_data.get('product_info', {})
        
        # Clasificar tipo de evento
        enriched['event_type'] = self._classify_event_type(event)
        
        # Agregar nivel de certeza en texto
        confidence = event['confidence']
        if confidence > 0.8:
            enriched['confidence_level'] = 'high'
        elif confidence > 0.6:
            enriched['confidence_level'] = 'medium'
        else:
            enriched['confidence_level'] = 'low'
        
        # Agregar descripción
        enriched['description'] = self._generate_event_description(enriched)
        
        return enriched
    
    def _classify_event_type(self, event: Dict) -> str:
        """Clasificar tipo de evento de floración"""
        duration = event['duration_days']
        intensity = event['intensity']
        
        if duration < 10:
            return 'brief_flowering' if intensity > 0.1 else 'vegetation_pulse'
        elif duration < 25:
            return 'typical_flowering'
        else:
            return 'extended_flowering'
    
    def _generate_event_description(self, event: Dict) -> str:
        """Generar descripción textual del evento"""
        location = event['location']
        event_type = event['event_type']
        confidence = event['confidence_level']
        
        type_descriptions = {
            'brief_flowering': 'Evento de floración breve e intenso',
            'typical_flowering': 'Evento de floración típico',
            'extended_flowering': 'Evento de floración prolongado',
            'vegetation_pulse': 'Pulso de crecimiento vegetal'
        }
        
        base_desc = type_descriptions.get(event_type, 'Evento de vegetación')
        
        return f"{base_desc} detectado en {location['latitude']:.2f}°, {location['longitude']:.2f}° " \
               f"del {event['start_date']} al {event['end_date']} (confianza: {confidence})"
    
    def predict_flowering(self, historical_data: Dict, 
                         days_ahead: int = 30, species: str = 'general') -> List[Dict]:
        """Predecir eventos de floración futuros"""
        try:
            if not historical_data or 'time_series' not in historical_data:
                return []
            
            ts = historical_data['time_series']
            dates = [datetime.strptime(d, '%Y-%m-%d') for d in ts['dates']]
            values = np.array(ts['values'])
            
            # Análisis de patrones estacionales históricos
            seasonal_pattern = self._extract_seasonal_pattern(dates, values)
            
            # Generar fechas futuras
            last_date = max(dates)
            future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
            
            # Predecir valores futuros basados en patrón estacional
            predictions = []
            for future_date in future_dates:
                day_of_year = future_date.timetuple().tm_yday
                predicted_value = seasonal_pattern.get(day_of_year, np.mean(values))
                
                # Agregar variabilidad realista
                noise = np.random.normal(0, np.std(values) * 0.1)
                predicted_value += noise
                
                predictions.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_ndvi': float(predicted_value),
                    'confidence': 0.7,  # Confianza moderada para predicciones
                    'flowering_probability': self._calculate_flowering_probability(predicted_value, seasonal_pattern, day_of_year)
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generando predicciones: {str(e)}")
            return []
    
    def _extract_seasonal_pattern(self, dates: List[datetime], 
                                 values: np.ndarray) -> Dict:
        """Extraer patrón estacional promedio"""
        seasonal_data = {}
        
        for date, value in zip(dates, values):
            day_of_year = date.timetuple().tm_yday
            if day_of_year not in seasonal_data:
                seasonal_data[day_of_year] = []
            seasonal_data[day_of_year].append(value)
        
        # Calcular promedio por día del año
        seasonal_pattern = {}
        for day, day_values in seasonal_data.items():
            seasonal_pattern[day] = np.mean(day_values)
        
        return seasonal_pattern
    
    def _calculate_flowering_probability(self, predicted_value: float, 
                                       seasonal_pattern: Dict, 
                                       day_of_year: int) -> float:
        """Calcular probabilidad de floración"""
        # Obtener valor típico para esa época del año
        typical_value = seasonal_pattern.get(day_of_year, 0.5)
        
        # Probabilidad basada en cuánto supera el valor típico
        if predicted_value > typical_value * 1.15:
            return min(1.0, (predicted_value - typical_value) / typical_value)
        else:
            return 0.0