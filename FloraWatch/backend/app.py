"""
FloraWatch - Aplicación principal Flask
Herramienta de monitoreo de eventos de floración usando datos de NASA
"""

from flask import Flask, render_template, jsonify, request
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
import json

# Importar módulos locales
from src.data_sources.nasa_api import NASADataClient
from src.algorithms.flowering_detector import FloweringDetector
from src.utils.data_processor import DataProcessor
from src.utils.cache_manager import CacheManager

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask app
app = Flask(__name__, 
           template_folder='../frontend/templates',
           static_folder='../frontend/static')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Inicializar componentes
nasa_client = NASADataClient()
flowering_detector = FloweringDetector()
data_processor = DataProcessor()
cache_manager = CacheManager()

@app.route('/')
def index():
    """Página principal de la aplicación"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Endpoint de verificación de salud del servicio"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'services': {
            'nasa_api': nasa_client.is_available(),
            'cache': cache_manager.is_available(),
            'detector': True
        }
    })

@app.route('/api/flowering-events')
def get_flowering_events():
    """
    Obtener eventos de floración para una región y período específico
    Parámetros:
    - lat: latitud (requerido)
    - lon: longitud (requerido) 
    - start_date: fecha inicio (YYYY-MM-DD)
    - end_date: fecha fin (YYYY-MM-DD)
    - radius: radio en km (default: 10)
    """
    try:
        # Validar parámetros requeridos
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if lat is None or lon is None:
            return jsonify({'error': 'Latitud y longitud son requeridos'}), 400
            
        # Parámetros opcionales
        start_date = request.args.get('start_date', 
                                     (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', 
                                   datetime.now().strftime('%Y-%m-%d'))
        radius = request.args.get('radius', 10, type=int)
        
        logger.info(f"Solicitando eventos de floración para {lat}, {lon} del {start_date} al {end_date}")
        
        # Verificar cache primero
        cache_key = f"flowering_{lat}_{lon}_{start_date}_{end_date}_{radius}"
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            logger.info("Devolviendo resultado desde cache")
            return jsonify(cached_result)
        
        # Obtener datos satelitales
        satellite_data = nasa_client.get_vegetation_data(
            lat=lat, lon=lon, 
            start_date=start_date, 
            end_date=end_date,
            radius=radius
        )
        
        if not satellite_data:
            return jsonify({'error': 'No se pudieron obtener datos satelitales'}), 404
            
        # Procesar datos para detección de floración
        processed_data = data_processor.process_time_series(satellite_data)
        
        # Detectar eventos de floración
        flowering_events = flowering_detector.detect_events(processed_data)
        
        # Preparar respuesta
        result = {
            'location': {'lat': lat, 'lon': lon},
            'period': {'start': start_date, 'end': end_date},
            'events_detected': len(flowering_events),
            'events': flowering_events,
            'metadata': {
                'data_source': 'NASA MODIS/Landsat',
                'algorithm': 'Spectral Index Analysis',
                'processed_at': datetime.utcnow().isoformat()
            }
        }
        
        # Guardar en cache
        cache_manager.set(cache_key, result, expiry_hours=24)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error obteniendo eventos de floración: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/predictions')
def get_flowering_predictions():
    """Obtener predicciones de floración futura"""
    try:
        region = request.args.get('region', 'global')
        species = request.args.get('species', 'general')
        days_ahead = request.args.get('days_ahead', 30, type=int)
        
        logger.info(f"Generando predicciones para {region}, especie: {species}")
        
        # Obtener datos históricos
        historical_data = nasa_client.get_historical_data(region, days=365)
        
        # Generar predicciones
        predictions = flowering_detector.predict_flowering(
            historical_data, 
            days_ahead=days_ahead,
            species=species
        )
        
        return jsonify({
            'region': region,
            'species': species,
            'prediction_period': days_ahead,
            'predictions': predictions,
            'confidence': 'medium',  # TODO: implementar cálculo de confianza
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generando predicciones: {str(e)}")
        return jsonify({'error': 'Error generando predicciones'}), 500

@app.route('/api/regions')
def get_available_regions():
    """Obtener regiones disponibles para monitoreo"""
    regions = [
        {
            'id': 'global',
            'name': 'Global',
            'bbox': [-180, -90, 180, 90],
            'description': 'Cobertura mundial'
        },
        {
            'id': 'north_america',
            'name': 'América del Norte',
            'bbox': [-168, 7, -52, 83],
            'description': 'Estados Unidos, Canadá, México'
        },
        {
            'id': 'europe',
            'name': 'Europa',
            'bbox': [-31, 27, 69, 81],
            'description': 'Continente europeo'
        },
        {
            'id': 'south_america',
            'name': 'América del Sur',
            'bbox': [-109, -56, -28, 16],
            'description': 'Continente sudamericano'
        },
        {
            'id': 'asia',
            'name': 'Asia',
            'bbox': [19, -12, 180, 82],
            'description': 'Continente asiático'
        },
        {
            'id': 'africa',
            'name': 'África',
            'bbox': [-25, -47, 63, 38],
            'description': 'Continente africano'
        }
    ]
    
    return jsonify({'regions': regions})

@app.route('/api/species')
def get_plant_species():
    """Obtener especies de plantas monitoreables"""
    species = [
        {
            'id': 'cherry_blossom',
            'name': 'Cerezo (Sakura)',
            'scientific_name': 'Prunus serrulata',
            'flowering_season': 'spring',
            'regions': ['asia', 'north_america', 'europe']
        },
        {
            'id': 'almond',
            'name': 'Almendro',
            'scientific_name': 'Prunus dulcis',
            'flowering_season': 'late_winter',
            'regions': ['europe', 'north_america']
        },
        {
            'id': 'apple',
            'name': 'Manzano',
            'scientific_name': 'Malus domestica',
            'flowering_season': 'spring',
            'regions': ['global']
        },
        {
            'id': 'lavender',
            'name': 'Lavanda',
            'scientific_name': 'Lavandula angustifolia',
            'flowering_season': 'summer',
            'regions': ['europe', 'north_america']
        },
        {
            'id': 'sunflower',
            'name': 'Girasol',
            'scientific_name': 'Helianthus annuus',
            'flowering_season': 'summer',
            'regions': ['global']
        }
    ]
    
    return jsonify({'species': species})

@app.route('/api/alerts')
def get_active_alerts():
    """Obtener alertas activas de eventos de floración"""
    severity = request.args.get('severity', 'all')
    
    # TODO: implementar sistema de alertas en tiempo real
    alerts = [
        {
            'id': 'alert_001',
            'type': 'flowering_event',
            'severity': 'high',
            'title': 'Floración masiva detectada en California',
            'description': 'Floración inusualmente intensa de amapolas en el valle central',
            'location': {'lat': 36.7378, 'lon': -119.7871},
            'timestamp': datetime.utcnow().isoformat(),
            'species': 'amapola',
            'confidence': 0.92
        },
        {
            'id': 'alert_002',
            'type': 'early_flowering',
            'severity': 'medium',
            'title': 'Floración temprana en Europa',
            'description': 'Cerezos floreciendo 2 semanas antes de lo normal',
            'location': {'lat': 50.1109, 'lon': 8.6821},
            'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            'species': 'cherry_blossom',
            'confidence': 0.85
        }
    ]
    
    if severity != 'all':
        alerts = [alert for alert in alerts if alert['severity'] == severity]
    
    return jsonify({'alerts': alerts, 'count': len(alerts)})

@app.route('/api/statistics')
def get_global_statistics():
    """Obtener estadísticas globales del sistema"""
    # TODO: implementar estadísticas reales desde la base de datos
    stats = {
        'total_events_detected': 15847,
        'regions_monitored': 156,
        'species_tracked': 24,
        'active_alerts': 3,
        'last_update': datetime.utcnow().isoformat(),
        'data_sources': {
            'modis': {'status': 'active', 'last_update': '2024-10-01T12:00:00Z'},
            'landsat': {'status': 'active', 'last_update': '2024-10-01T10:30:00Z'},
            'viirs': {'status': 'active', 'last_update': '2024-10-01T14:15:00Z'}
        }
    }
    
    return jsonify(stats)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {str(error)}")
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Crear directorios necesarios
    os.makedirs('data/cache', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Configurar y ejecutar la aplicación
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando FloraWatch en {host}:{port}")
    logger.info(f"Modo debug: {debug}")
    
    app.run(host=host, port=port, debug=debug)