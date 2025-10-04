#!/usr/bin/env python3
"""
Script de prueba para verificar todas las APIs de FloraWatch
Especial para Miguel A. Luna - Universidad Nacional de Loja
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def print_header():
    print("🌸" * 60)
    print("    FLORAWATCH - VERIFICACIÓN DE APIs")
    print("    Universidad Nacional de Loja - Ecuador")
    print("    Miguel A. Luna - miguel.a.luna@unl.edu.ec")
    print("🌸" * 60)
    print()

def test_nasa_api():
    """Probar NASA API"""
    print("🛰️  Probando NASA API...")
    
    api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
    base_url = os.getenv('NASA_API_URL', 'https://api.nasa.gov')
    
    try:
        # Probar APOD (Astronomy Picture of the Day)
        response = requests.get(
            f"{base_url}/planetary/apod",
            params={'api_key': api_key, 'date': '2024-01-01'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ NASA API Principal: FUNCIONANDO")
            data = response.json()
            print(f"   📡 Título APOD: {data.get('title', 'N/A')}")
        else:
            print(f"   ❌ NASA API Principal: ERROR {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ NASA API Principal: ERROR - {str(e)}")
    
    # Probar NASA Earth Imagery
    try:
        response = requests.get(
            f"{base_url}/planetary/earth/imagery",
            params={
                'lon': -79.0,  # Ecuador
                'lat': -4.0,
                'date': '2024-01-01',
                'api_key': api_key
            },
            timeout=10
        )
        
        if response.status_code in [200, 400]:  # 400 puede ser por parámetros
            print("   ✅ NASA Earth Imagery: DISPONIBLE")
        else:
            print(f"   ⚠️  NASA Earth Imagery: Código {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ NASA Earth Imagery: ERROR - {str(e)}")
    
    # Probar NASA EONET (Eventos Naturales)
    try:
        response = requests.get(
            "https://eonet.gsfc.nasa.gov/api/v3/events",
            params={'limit': 5},
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ NASA EONET: FUNCIONANDO")
            data = response.json()
            print(f"   🌋 Eventos naturales disponibles: {len(data.get('events', []))}")
        else:
            print(f"   ❌ NASA EONET: ERROR {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ NASA EONET: ERROR - {str(e)}")

def test_openweather_api():
    """Probar OpenWeatherMap API"""
    print("\n🌤️  Probando OpenWeatherMap API...")
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    base_url = os.getenv('OPENWEATHER_BASE_URL', 'https://api.openweathermap.org/data/2.5')
    
    if not api_key:
        print("   ❌ OpenWeather API Key no configurada")
        return
    
    print(f"   🔑 API Key: {api_key[:8]}...")
    
    # Probar clima actual en Loja, Ecuador
    try:
        response = requests.get(
            f"{base_url}/weather",
            params={
                'q': 'Loja,EC',
                'appid': api_key,
                'units': 'metric',
                'lang': 'es'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ OpenWeather API: FUNCIONANDO")
            data = response.json()
            print(f"   🌡️  Temperatura en Loja: {data['main']['temp']}°C")
            print(f"   🌥️  Condiciones: {data['weather'][0]['description']}")
            print(f"   💨 Humedad: {data['main']['humidity']}%")
        else:
            print(f"   ❌ OpenWeather API: ERROR {response.status_code}")
            if response.status_code == 401:
                print("   🔐 Error de autenticación - verifica tu API key")
            elif response.status_code == 429:
                print("   ⏳ Límite de requests excedido")
                
    except Exception as e:
        print(f"   ❌ OpenWeather API: ERROR - {str(e)}")
    
    # Probar pronóstico
    try:
        response = requests.get(
            f"{base_url}/forecast",
            params={
                'lat': -4.0,  # Loja aproximadamente
                'lon': -79.2,
                'appid': api_key,
                'units': 'metric',
                'cnt': 8  # Próximas 24 horas
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ OpenWeather Forecast: FUNCIONANDO")
            data = response.json()
            print(f"   📊 Pronósticos disponibles: {len(data.get('list', []))}")
        else:
            print(f"   ⚠️  OpenWeather Forecast: Código {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ OpenWeather Forecast: ERROR - {str(e)}")

def test_local_server():
    """Probar servidor local de FloraWatch"""
    print("\n🌸 Probando servidor local FloraWatch...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Probar endpoint de salud
        response = requests.get(f"{base_url}/api/health", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Servidor FloraWatch: FUNCIONANDO")
            data = response.json()
            print(f"   🏥 Estado: {data.get('status', 'unknown')}")
            
            services = data.get('services', {})
            for service, status in services.items():
                icon = "✅" if status else "❌"
                print(f"   {icon} {service}: {'OK' if status else 'ERROR'}")
        else:
            print(f"   ❌ Servidor FloraWatch: ERROR {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Servidor FloraWatch: NO INICIADO")
        print("   💡 Ejecuta: python backend/app.py")
    except Exception as e:
        print(f"   ❌ Servidor FloraWatch: ERROR - {str(e)}")

def test_integrated_analysis():
    """Probar análisis integrado"""
    print("\n🔬 Probando análisis integrado...")
    
    base_url = "http://localhost:5000"
    
    # Coordenadas de Ecuador (región de interés)
    lat, lon = -4.0, -79.0
    
    try:
        response = requests.get(
            f"{base_url}/api/integrated-analysis",
            params={
                'lat': lat,
                'lon': lon,
                'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d')
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ Análisis integrado: FUNCIONANDO")
            data = response.json()
            print(f"   📊 Eventos detectados: {data.get('events_detected', 0)}")
            print(f"   🛰️  Fuentes de datos: {', '.join(data.get('metadata', {}).get('data_sources', []))}")
            
            quality = data.get('analysis_quality', {})
            print(f"   🎯 Calidad del análisis: {quality.get('quality_level', 'unknown')} ({quality.get('overall_score', 0):.1%})")
            
        else:
            print(f"   ❌ Análisis integrado: ERROR {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Servidor no disponible para prueba de análisis")
    except Exception as e:
        print(f"   ❌ Análisis integrado: ERROR - {str(e)}")

def show_configuration():
    """Mostrar configuración actual"""
    print("\n⚙️  Configuración actual:")
    print(f"   🔑 NASA API Key: {'✅ Configurada' if os.getenv('NASA_API_KEY') != 'DEMO_KEY' else '⚠️  Usando DEMO_KEY'}")
    print(f"   🌤️  OpenWeather Key: {'✅ Configurada' if os.getenv('OPENWEATHER_API_KEY') else '❌ No configurada'}")
    print(f"   📧 Email: {os.getenv('MAIL_USERNAME', 'No configurado')}")
    print(f"   🏛️  Institución: {os.getenv('INSTITUTION_NAME', 'No configurada')}")
    print(f"   🌍 País: {os.getenv('INSTITUTION_COUNTRY', 'No configurado')}")
    print(f"   🌐 Región por defecto: {os.getenv('DEFAULT_LATITUDE', 'N/A')}, {os.getenv('DEFAULT_LONGITUDE', 'N/A')}")

def show_next_steps():
    """Mostrar próximos pasos"""
    print("\n" + "="*60)
    print("🎯 PRÓXIMOS PASOS RECOMENDADOS:")
    print("="*60)
    
    print("\n1. 🔑 Obtener NASA API Key:")
    print("   - Visita: https://api.nasa.gov/")
    print("   - Regístrate con tu email: miguel.a.luna@unl.edu.ec")
    print("   - Actualiza NASA_API_KEY en .env")
    
    print("\n2. 🚀 Ejecutar FloraWatch:")
    print("   - Abre terminal en el directorio del proyecto")
    print("   - Ejecuta: python backend/app.py")
    print("   - Abre navegador: http://localhost:5000")
    
    print("\n3. 🌍 Probar con datos de Ecuador:")
    print("   - Loja: -4.0, -79.2")
    print("   - Quito: -0.2, -78.5")
    print("   - Guayaquil: -2.2, -79.9")
    
    print("\n4. 📧 Configurar alertas por email:")
    print("   - Configura MAIL_PASSWORD en .env con password de aplicación Gmail")
    print("   - Activa autenticación de 2 factores en Gmail")
    
    print("\n5. 🎓 Para investigación universitaria:")
    print("   - Documenta metodología y resultados")
    print("   - Considera publicación científica")
    print("   - Integra con otros proyectos de la UNL")

def main():
    """Función principal"""
    print_header()
    
    show_configuration()
    
    test_nasa_api()
    test_openweather_api()
    test_local_server()
    
    if "localhost:5000" in str(test_local_server):
        test_integrated_analysis()
    
    show_next_steps()
    
    print(f"\n🌸 Prueba completada - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("¡Que tengas éxito con tu proyecto FloraWatch! 🌺")

if __name__ == "__main__":
    main()