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
        Implementación real de conexión con AppEEARS API
        """
        try:
            # Usar NASA API para obtener datos MODIS
            return self._get_modis_data_via_nasa_api(lat, lon, start_date, end_date)
        except Exception as e:
            logger.error(f"Error con AppEEARS API: {str(e)}")
            return None
    
    def _get_modis_data_via_nasa_api(self, lat: float, lon: float, 
                                   start_date: str, end_date: str) -> Optional[Dict]:
        """
        Obtener datos MODIS reales usando NASA API
        """
        try:
            # Endpoint para datos MODIS
            endpoint = f"{self.base_url}/planetary/earth/assets"
            
            params = {
                'lon': lon,
                'lat': lat,
                'date': start_date,
                'dim': 0.1,  # Tamaño del área en grados
                'api_key': self.api_key
            }
            
            response = self.session.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                assets_data = response.json()
                return self._process_nasa_earth_assets(assets_data, lat, lon, start_date, end_date)
            else:
                logger.warning(f"NASA API respondió con código: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo datos MODIS reales: {str(e)}")
            return None
    
    def _process_nasa_earth_assets(self, assets_data: Dict, lat: float, lon: float,
                                 start_date: str, end_date: str) -> Dict:
        """
        Procesar datos de NASA Earth Assets
        """
        # Implementación básica - en producción sería más compleja
        return {
            'location': {'latitude': lat, 'longitude': lon},
            'period': {'start': start_date, 'end': end_date},
            'assets': assets_data,
            'data_source': 'NASA Earth Assets API',
            'processing_note': 'Datos reales de NASA - implementación básica'
        }
    
    def get_nasa_imagery(self, lat: float, lon: float, date: str) -> Optional[Dict]:
        """
        Obtener imágenes satelitales de NASA Earthdata con manejo de timeouts
        """
        nasa_timeout = int(os.getenv('NASA_API_TIMEOUT', 30))
        retry_attempts = int(os.getenv('RETRY_ATTEMPTS', 3))
        
        for attempt in range(retry_attempts):
            try:
                endpoint = f"{self.base_url}/planetary/earth/imagery"
                
                params = {
                    'lon': lon,
                    'lat': lat,
                    'date': date,
                    'dim': 0.1,
                    'api_key': self.api_key
                }
                
                response = self.session.get(endpoint, params=params, timeout=nasa_timeout)
                
                if response.status_code == 200:
                    return {
                        'image_url': response.url,
                        'location': {'latitude': lat, 'longitude': lon},
                        'date': date,
                        'source': 'NASA Landsat/Sentinel',
                        'attempt': attempt + 1
                    }
                elif response.status_code == 404:
                    logger.info(f"No hay imagen NASA disponible para {date} en {lat}, {lon}")
                    return None
                else:
                    logger.warning(f"NASA Imagery respondió con código: {response.status_code}")
                    if attempt == retry_attempts - 1:
                        return None
                        
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout en NASA Imagery (intento {attempt + 1}/{retry_attempts})")
                if attempt == retry_attempts - 1:
                    return None
            except Exception as e:
                logger.error(f"Error obteniendo imagen NASA (intento {attempt + 1}): {str(e)}")
                if attempt == retry_attempts - 1:
                    return None
        
        return None
    
    def get_integrated_earth_data(self, lat: float, lon: float,
                                start_date: str, end_date: str) -> Dict:
        """
        Obtener datos integrados de múltiples fuentes NASA
        """
        integrated_data = {
            'location': {'latitude': lat, 'longitude': lon},
            'period': {'start': start_date, 'end': end_date},
            'data_sources': [],
            'vegetation_data': None,
            'imagery_data': None,
            'additional_data': {}
        }
        
        # 1. Datos de vegetación (MODIS/Landsat)
        if os.getenv('ENABLE_REAL_NASA_API', 'False').lower() == 'true':
            vegetation_data = self.get_real_data_via_appeears(lat, lon, start_date, end_date)
            if vegetation_data:
                integrated_data['vegetation_data'] = vegetation_data
                integrated_data['data_sources'].append('NASA Earth Assets')
        
        # Si no hay datos reales, usar simulados
        if not integrated_data['vegetation_data']:
            integrated_data['vegetation_data'] = self.get_vegetation_data(
                lat, lon, start_date, end_date
            )
            integrated_data['data_sources'].append('Simulated MODIS')
        
        # 2. Imágenes satelitales
        if os.getenv('ENABLE_REAL_NASA_API', 'False').lower() == 'true':
            imagery = self.get_nasa_imagery(lat, lon, start_date)
            if imagery:
                integrated_data['imagery_data'] = imagery
                integrated_data['data_sources'].append('NASA Imagery')
        
        # 3. Datos adicionales de NASA APIs
        try:
            # API de eventos naturales
            natural_events = self._get_nasa_natural_events(lat, lon)
            if natural_events:
                integrated_data['additional_data']['natural_events'] = natural_events
                integrated_data['data_sources'].append('NASA EONET')
        except:
            pass
        
        return integrated_data
    
    def _get_nasa_natural_events(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Obtener eventos naturales de NASA EONET
        """
        try:
            # NASA Earth Observatory Natural Event Tracker
            eonet_url = "https://eonet.gsfc.nasa.gov/api/v3/events"
            
            params = {
                'status': 'open',
                'limit': 10
            }
            
            response = requests.get(eonet_url, params=params, timeout=15)
            
            if response.status_code == 200:
                events_data = response.json()
                
                # Filtrar eventos cercanos a la ubicación
                nearby_events = []
                for event in events_data.get('events', []):
                    for geometry in event.get('geometry', []):
                        if geometry['type'] == 'Point':
                            event_lon, event_lat = geometry['coordinates']
                            # Calcular distancia aproximada
                            distance = ((lat - event_lat)**2 + (lon - event_lon)**2)**0.5
                            if distance < 5.0:  # Dentro de ~5 grados
                                nearby_events.append({
                                    'id': event['id'],
                                    'title': event['title'],
                                    'category': event['categories'][0]['title'] if event['categories'] else 'Unknown',
                                    'date': event['geometry'][0]['date'] if event['geometry'] else None,
                                    'coordinates': [event_lat, event_lon],
                                    'distance_degrees': round(distance, 2)
                                })
                
                return {
                    'nearby_events': nearby_events,
                    'total_events': len(nearby_events),
                    'source': 'NASA EONET'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"No se pudieron obtener eventos naturales NASA: {str(e)}")
            return None
    
    def get_api_status(self) -> Dict:
        """
        Verificar estado de todas las APIs de NASA
        """
        status = {
            'nasa_main_api': False,
            'nasa_earth_imagery': False,
            'nasa_eonet': False,
            'appeears_api': False,
            'api_key_valid': self.api_key != 'DEMO_KEY',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Probar API principal de NASA
        try:
            response = self.session.get(f"{self.base_url}/planetary/apod", 
                                      params={'date': '2024-01-01'}, timeout=10)
            status['nasa_main_api'] = response.status_code == 200
        except:
            pass
        
        # Probar NASA Earth Imagery
        try:
            response = requests.get(f"{self.base_url}/planetary/earth/imagery", 
                                  params={'lon': 0, 'lat': 0, 'date': '2024-01-01', 'api_key': self.api_key}, 
                                  timeout=10)
            status['nasa_earth_imagery'] = response.status_code in [200, 400]  # 400 puede ser por parámetros
        except:
            pass
        
        # Probar NASA EONET
        try:
            response = requests.get("https://eonet.gsfc.nasa.gov/api/v3/events", 
                                  params={'limit': 1}, timeout=10)
            status['nasa_eonet'] = response.status_code == 200
        except:
            pass
        
        # Probar AppEEARS (básico)
        try:
            response = requests.get(f"{self.appeears_url}/product", timeout=10)
            status['appeears_api'] = response.status_code == 200
        except:
            pass
        
        return status