#!/usr/bin/env python3
"""
Servidor de desarrollo para FloraWatch
Ejecuta la aplicación Flask con configuración de desarrollo
"""

import sys
import os
from pathlib import Path

# Agregar el directorio backend al path de Python
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

try:
    from app import app
    
    if __name__ == '__main__':
        print("🌿 Iniciando FloraWatch Server...")
        print("🔍 Monitoreo Global de Floración - NASA Space Apps Challenge")
        print("=" * 60)
        print("🌐 Servidor ejecutándose en: http://localhost:5000")
        print("📱 Interface web disponible en el navegador")
        print("🔄 API REST disponible en /api/")
        print("=" * 60)
        print("⭐ Para detener el servidor: Ctrl+C")
        print()
        
        # Ejecutar servidor Flask en modo desarrollo
        app.run(
            host='0.0.0.0',  # Permitir conexiones externas
            port=5000,       # Puerto estándar
            debug=True,      # Modo desarrollo con recarga automática
            threaded=True    # Soporte para múltiples solicitudes
        )
        
except ImportError as e:
    print(f"❌ Error importando la aplicación Flask: {e}")
    print("🔧 Verifica que todos los archivos estén en su lugar:")
    print("   - backend/app.py")
    print("   - backend/src/algorithms/flowering_detector.py")
    print("   - backend/src/utils/data_processor.py")
    print("   - backend/src/utils/cache_manager.py")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error iniciando el servidor: {e}")
    sys.exit(1)