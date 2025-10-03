#!/usr/bin/env python3
"""
Script de prueba para verificar que todas las dependencias están instaladas
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Probar que todas las librerías necesarias están disponibles"""
    try:
        print("🔍 Probando importaciones...")
        
        import numpy as np
        print(f"✅ NumPy {np.__version__}")
        
        import pandas as pd
        print(f"✅ Pandas {pd.__version__}")
        
        import sklearn
        print(f"✅ Scikit-learn {sklearn.__version__}")
        
        import scipy
        print(f"✅ SciPy {scipy.__version__}")
        
        import flask
        print(f"✅ Flask {flask.__version__}")
        
        import flask_cors
        print(f"✅ Flask-CORS")
        
        import requests
        print(f"✅ Requests")
        
        print("\n🌸 ¡Todas las dependencias están instaladas correctamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando: {e}")
        return False

def test_flowering_detector():
    """Probar el detector de floración"""
    try:
        from backend.src.algorithms.flowering_detector import FloweringDetector
        print("\n🔍 Probando FloweringDetector...")
        
        detector = FloweringDetector()
        print("✅ FloweringDetector inicializado correctamente")
        
        # Datos de prueba
        test_data = {
            'location': {'latitude': 40.7128, 'longitude': -74.0060},
            'time_series': {
                'dates': ['2024-01-01', '2024-01-15', '2024-02-01', '2024-02-15', '2024-03-01'],
                'values': [0.3, 0.35, 0.4, 0.55, 0.45],
                'quality_flags': ['good', 'good', 'good', 'good', 'good']
            },
            'product_info': {'sensor': 'test'}
        }
        
        events = detector.detect_events(test_data)
        print(f"✅ Detección de eventos funcionando. Eventos encontrados: {len(events)}")
        
        predictions = detector.predict_flowering(test_data, days_ahead=10)
        print(f"✅ Predicciones funcionando. Predicciones generadas: {len(predictions)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando FloweringDetector: {e}")
        return False

def main():
    print("🌿 FloraWatch - Prueba de Sistema")
    print("=" * 50)
    
    imports_ok = test_imports()
    if not imports_ok:
        print("\n❌ Faltan dependencias. Instala con: py -m pip install numpy pandas scikit-learn scipy flask flask-cors requests")
        return False
    
    detector_ok = test_flowering_detector()
    if not detector_ok:
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ¡Sistema FloraWatch listo para funcionar!")
    print("🚀 Para iniciar el servidor web, ejecuta: py run_server.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)