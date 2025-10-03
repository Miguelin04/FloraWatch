"""
Cliente para APIs de NASA - Obtención de datos satelitales
Integra múltiples fuentes: MODIS, Landsat, VIIRS, EMIT, PACE
"""

import requests
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import numpy as np
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class NASADataClient:
    """Cliente para acceder a datos de observación de la Tierra de NASA"""
    
    def __init__(self):
        self.api_key = os.getenv('NASA_API_KEY')
        self.base_url = os.getenv('NASA_API_URL', 'https://api.nasa.gov')
        self.appeears_url = os.getenv('APPEEARS_API_URL', 'https://appeears.earthdatacloud.nasa.gov/api/v1')
        
        if not self.api_key:
            logger.warning("NASA API key no configurada. Usando DEMO_KEY con límites restrictivos.")
            self.api_key = 'DEMO_KEY'
            
        self.session = requests.Session()
        self.session.params.update({'api_key': self.api_key})
        
        # Configurar productos disponibles
        self.products = {
            'modis_ndvi': {
                'product': 'MOD13Q1.061',
                'band': 'NDVI',
                'description': 'MODIS Vegetation Indices 16-Day',
                'resolution': '250m',
                'temporal': '16 days'
            },
            'modis_evi': {
                'product': 'MOD13Q1.061', 
                'band': 'EVI',
                'description': 'MODIS Enhanced Vegetation Index',
                'resolution': '250m',
                'temporal': '16 days'
            },
            'landsat_ndvi': {
                'product': 'LANDSAT_8_C1',
                'band': 'NDVI',
                'description': 'Landsat 8 NDVI',
                'resolution': '30m',
                'temporal': '16 days'
            },
            'viirs_ndvi': {
                'product': 'VNP13A1.001',
                'band': 'NDVI',
                'description': 'VIIRS Vegetation Indices',
                'resolution': '500m', 
                'temporal': '16 days'
            }
        }
    
    def is_available(self) -> bool:
        """Verificar si la API de NASA está disponible"""
        try:
            response = self.session.get(f"{self.base_url}/planetary/apod", 
                                      params={'date': '2024-01-01'}, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_vegetation_data(self, lat: float, lon: float, 
                          start_date: str, end_date: str, 
                          radius: int = 10, product: str = 'modis_ndvi') -> Optional[Dict]:
        """
        Obtener datos de vegetación para una ubicación específica
        
        Args:
            lat: Latitud
            lon: Longitud
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            radius: Radio en km para área de interés
            product: Producto a obtener (modis_ndvi, modis_evi, etc.)
        
        Returns:
            Diccionario con datos de vegetación o None si error
        """
        try:
            logger.info(f"Obteniendo datos {product} for {lat}, {lon} del {start_date} al {end_date}")
            
            # Para demo, simular datos realistas
            # En implementación real, aquí haríamos la llamada a AppEEARS o similar
            mock_data = self._generate_mock_vegetation_data(
                lat, lon, start_date, end_date, product, radius
            )
            
            return mock_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de vegetación: {str(e)}")
            return None
    
    def _generate_mock_vegetation_data(self, lat: float, lon: float, 
                                     start_date: str, end_date: str,
                                     product: str, radius: int) -> Dict:
        """Generar datos simulados realistas para demo"""
        
        # Convertir fechas
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generar serie temporal cada 16 días (ciclo MODIS)
        dates = []
        current_date = start_dt
        while current_date <= end_dt:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=16)
        
        # Simular valores NDVI/EVI realistas basados en:
        # - Estacionalidad (hemisferio norte/sur)
        # - Latitud (tropical vs temperado)
        # - Variabilidad natural
        
        values = []
        for i, date in enumerate(dates):
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            day_of_year = date_obj.timetuple().tm_yday
            
            # Patrón estacional básico
            if lat > 0:  # Hemisferio norte
                seasonal_factor = 0.3 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
            else:  # Hemisferio sur
                seasonal_factor = 0.3 * np.sin(2 * np.pi * (day_of_year - 260) / 365)
            
            # Valor base según latitud
            if abs(lat) < 23.5:  # Tropical
                base_value = 0.7
            elif abs(lat) < 45:  # Subtropical
                base_value = 0.5
            else:  # Templado/polar
                base_value = 0.3
            
            # Agregar ruido realista
            noise = np.random.normal(0, 0.05)
            
            # Simular evento de floración (incremento súbito)
            flowering_boost = 0
            if product in ['modis_ndvi', 'landsat_ndvi']:
                # Simular floración en primaverca (día 90-120 norte, 270-300 sur)
                if lat > 0 and 90 <= day_of_year <= 120:
                    flowering_boost = 0.15 * np.exp(-((day_of_year - 105) / 10) ** 2)
                elif lat < 0 and 270 <= day_of_year <= 300:
                    flowering_boost = 0.15 * np.exp(-((day_of_year - 285) / 10) ** 2)
            
            final_value = max(0, min(1, base_value + seasonal_factor + noise + flowering_boost))
            values.append(round(final_value, 4))
        
        # Calcular estadísticas de calidad
        quality_flags = ['good'] * len(values)
        
        # Algunos valores con calidad reducida por nubes
        cloud_indices = np.random.choice(len(values), size=max(1, len(values)//5), replace=False)
        for idx in cloud_indices:
            quality_flags[idx] = 'cloudy'
            values[idx] *= 0.8  # Reducir valor por interferencia de nubes
        
        return {
            'product_info': self.products.get(product, {}),
            'location': {
                'latitude': lat,
                'longitude': lon,
                'radius_km': radius
            },
            'temporal_range': {
                'start_date': start_date,
                'end_date': end_date,
                'total_observations': len(dates)
            },
            'time_series': {
                'dates': dates,
                'values': values,
                'quality_flags': quality_flags,
                'units': 'NDVI' if 'ndvi' in product else 'EVI',
                'scale_factor': 0.0001,
                'valid_range': [0, 1]
            },
            'statistics': {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'trend': self._calculate_trend(values)
            },
            'metadata': {
                'source': 'NASA MODIS/Landsat (simulated)',
                'processed_at': datetime.utcnow().isoformat(),
                'processing_level': 'L3',
                'coordinate_system': 'WGS84'
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcular tendencia básica de la serie temporal"""
        if len(values) < 3:
            return 'insufficient_data'
        
        # Regresión lineal simple
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.01:
            return 'increasing'
        elif slope < -0.01:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_historical_data(self, region: str, days: int = 365) -> Optional[Dict]:
        """Obtener datos históricos para una región"""
        try:
            # Definir coordenadas representativas por región
            region_coords = {
                'global': (0, 0),
                'north_america': (45, -100),
                'europe': (50, 10),
                'south_america': (-15, -60),
                'asia': (35, 105),
                'africa': (0, 20)
            }
            
            if region not in region_coords:
                region = 'global'
            
            lat, lon = region_coords[region]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            return self.get_vegetation_data(
                lat=lat, lon=lon,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                radius=100  # Área más grande para región
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos: {str(e)}")
            return None
    
    def get_available_products(self) -> Dict:
        """Obtener lista de productos disponibles"""
        return {
            'products': self.products,
            'total_products': len(self.products),
            'data_sources': [
                'MODIS Terra/Aqua',
                'Landsat 8/9', 
                'VIIRS',
                'EMIT',
                'PACE'
            ]
        }
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validar coordenadas geográficas"""
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """Validar rango de fechas"""
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Verificar que las fechas sean lógicas
            return start_dt <= end_dt and start_dt >= datetime(2000, 1, 1)
        except:
            return False
    
    def get_real_data_via_appeears(self, lat: float, lon: float, 
                                  start_date: str, end_date: str) -> Optional[Dict]:
        """
        Método para implementar conexión real con AppEEARS
        Requiere autenticación y manejo de tareas asíncronas
        """
        # TODO: Implementar autenticación AppEEARS
        # TODO: Crear tarea de extracción
        # TODO: Monitorear progreso de tarea
        # TODO: Descargar resultados
        
        logger.info("Implementación de AppEEARS pendiente")
        return None