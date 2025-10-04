"""
Cliente para OpenWeatherMap API - Datos meteorológicos complementarios
Integra datos meteorológicos para mejorar las predicciones de floración
"""

import requests
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class OpenWeatherClient:
    """Cliente para acceder a datos meteorológicos de OpenWeatherMap"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = os.getenv('OPENWEATHER_BASE_URL', 'https://api.openweathermap.org/data/2.5')
        
        if not self.api_key:
            logger.warning("OpenWeather API key no configurada.")
            self.api_key = None
            
        self.session = requests.Session()
        
    def is_available(self) -> bool:
        """Verificar si la API de OpenWeatherMap está disponible"""
        if not self.api_key:
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/weather",
                params={
                    'q': 'London',
                    'appid': self.api_key
                },
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Obtener datos meteorológicos actuales para una ubicación
        """
        if not self.api_key:
            logger.warning("API key de OpenWeather no configurada")
            return None
            
        try:
            response = self.session.get(
                f"{self.base_url}/weather",
                params={
                    'lat': lat,
                    'lon': lon,
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'es'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_current_weather(data)
            else:
                logger.error(f"Error API OpenWeather: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo datos meteorológicos: {str(e)}")
            return None
    
    def get_forecast(self, lat: float, lon: float, days: int = 5) -> Optional[Dict]:
        """
        Obtener pronóstico meteorológico para una ubicación
        """
        if not self.api_key:
            return None
            
        try:
            response = self.session.get(
                f"{self.base_url}/forecast",
                params={
                    'lat': lat,
                    'lon': lon,
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'es',
                    'cnt': days * 8  # 8 pronósticos por día (cada 3 horas)
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_forecast(data)
            else:
                logger.error(f"Error API OpenWeather forecast: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo pronóstico: {str(e)}")
            return None
    
    def get_historical_weather(self, lat: float, lon: float, 
                             start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """
        Obtener datos meteorológicos históricos (requiere plan pagado)
        """
        if not self.api_key:
            return None
            
        # Para plan gratuito, simulamos datos históricos
        return self._simulate_historical_weather(lat, lon, start_date, end_date)
    
    def _process_current_weather(self, data: Dict) -> Dict:
        """Procesar datos meteorológicos actuales"""
        return {
            'location': {
                'latitude': data['coord']['lat'],
                'longitude': data['coord']['lon'],
                'city': data['name'],
                'country': data['sys']['country']
            },
            'weather': {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'],
                'icon': data['weather'][0]['icon']
            },
            'wind': {
                'speed': data['wind']['speed'],
                'direction': data['wind'].get('deg', 0)
            },
            'conditions': {
                'visibility': data.get('visibility', 10000),
                'uv_index': data.get('uvi', 0),
                'cloudiness': data['clouds']['all']
            },
            'sun': {
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset'])
            },
            'timestamp': datetime.fromtimestamp(data['dt']),
            'source': 'OpenWeatherMap'
        }
    
    def _process_forecast(self, data: Dict) -> Dict:
        """Procesar datos de pronóstico"""
        forecasts = []
        
        for item in data['list']:
            forecast = {
                'datetime': datetime.fromtimestamp(item['dt']),
                'temperature': {
                    'temp': item['main']['temp'],
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max'],
                    'feels_like': item['main']['feels_like']
                },
                'weather': {
                    'description': item['weather'][0]['description'],
                    'main': item['weather'][0]['main'],
                    'icon': item['weather'][0]['icon']
                },
                'humidity': item['main']['humidity'],
                'pressure': item['main']['pressure'],
                'wind_speed': item['wind']['speed'],
                'cloudiness': item['clouds']['all'],
                'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
            }
            forecasts.append(forecast)
        
        return {
            'location': {
                'latitude': data['city']['coord']['lat'],
                'longitude': data['city']['coord']['lon'],
                'city': data['city']['name'],
                'country': data['city']['country']
            },
            'forecasts': forecasts,
            'total_forecasts': len(forecasts),
            'source': 'OpenWeatherMap'
        }
    
    def _simulate_historical_weather(self, lat: float, lon: float, 
                                   start_date: datetime, end_date: datetime) -> Dict:
        """Simular datos meteorológicos históricos para demo"""
        
        days = (end_date - start_date).days
        historical_data = []
        
        # Generar datos simulados realistas
        for i in range(days):
            date = start_date + timedelta(days=i)
            day_of_year = date.timetuple().tm_yday
            
            # Temperatura basada en latitud y estación
            base_temp = 20 - abs(lat) * 0.5  # Más frío en latitudes altas
            seasonal_temp = 10 * np.sin(2 * np.pi * (day_of_year - 81) / 365)  # Variación estacional
            daily_temp = base_temp + seasonal_temp + np.random.normal(0, 3)
            
            # Humedad y precipitación
            humidity = max(30, min(90, 60 + np.random.normal(0, 15)))
            precipitation = max(0, np.random.exponential(2) if np.random.random() < 0.3 else 0)
            
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'temperature_avg': round(daily_temp, 1),
                'temperature_min': round(daily_temp - 5, 1),
                'temperature_max': round(daily_temp + 5, 1),
                'humidity': round(humidity, 1),
                'precipitation': round(precipitation, 1),
                'wind_speed': round(max(0, np.random.normal(10, 5)), 1),
                'pressure': round(1013 + np.random.normal(0, 10), 1)
            })
        
        return {
            'location': {'latitude': lat, 'longitude': lon},
            'period': {'start': start_date.strftime('%Y-%m-%d'), 'end': end_date.strftime('%Y-%m-%d')},
            'historical_data': historical_data,
            'total_days': len(historical_data),
            'source': 'OpenWeatherMap (simulated)'
        }
    
    def get_weather_for_flowering_analysis(self, lat: float, lon: float) -> Dict:
        """
        Obtener datos meteorológicos específicos para análisis de floración
        """
        current = self.get_current_weather(lat, lon)
        forecast = self.get_forecast(lat, lon, days=7)
        
        if not current:
            return {}
        
        # Calcular índices específicos para floración
        flowering_conditions = self._calculate_flowering_indices(current, forecast)
        
        return {
            'current_weather': current,
            'forecast': forecast,
            'flowering_conditions': flowering_conditions,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_flowering_indices(self, current: Dict, forecast: Dict) -> Dict:
        """Calcular índices meteorológicos relevantes para floración"""
        
        indices = {
            'temperature_favorability': 0,
            'humidity_favorability': 0,
            'precipitation_risk': 0,
            'wind_stress': 0,
            'flowering_probability': 0
        }
        
        if not current:
            return indices
        
        # Análisis de temperatura (óptimo 15-25°C para muchas especies)
        temp = current['weather']['temperature']
        if 15 <= temp <= 25:
            indices['temperature_favorability'] = 1.0
        elif 10 <= temp <= 30:
            indices['temperature_favorability'] = 0.7
        elif 5 <= temp <= 35:
            indices['temperature_favorability'] = 0.4
        else:
            indices['temperature_favorability'] = 0.1
        
        # Análisis de humedad (óptimo 50-70%)
        humidity = current['weather']['humidity']
        if 50 <= humidity <= 70:
            indices['humidity_favorability'] = 1.0
        elif 40 <= humidity <= 80:
            indices['humidity_favorability'] = 0.8
        elif 30 <= humidity <= 90:
            indices['humidity_favorability'] = 0.5
        else:
            indices['humidity_favorability'] = 0.2
        
        # Riesgo por precipitación
        if forecast:
            total_precip = sum(f.get('precipitation', 0) for f in forecast['forecasts'][:8])  # Próximas 24h
            if total_precip > 20:
                indices['precipitation_risk'] = 0.8
            elif total_precip > 10:
                indices['precipitation_risk'] = 0.5
            elif total_precip > 5:
                indices['precipitation_risk'] = 0.2
            else:
                indices['precipitation_risk'] = 0.0
        
        # Estrés por viento (>7 m/s puede dañar flores)
        wind_speed = current['wind']['speed']
        if wind_speed > 10:
            indices['wind_stress'] = 0.9
        elif wind_speed > 7:
            indices['wind_stress'] = 0.6
        elif wind_speed > 5:
            indices['wind_stress'] = 0.3
        else:
            indices['wind_stress'] = 0.0
        
        # Probabilidad general de floración
        indices['flowering_probability'] = (
            indices['temperature_favorability'] * 0.4 +
            indices['humidity_favorability'] * 0.3 +
            (1 - indices['precipitation_risk']) * 0.2 +
            (1 - indices['wind_stress']) * 0.1
        )
        
        return indices