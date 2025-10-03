#!/usr/bin/env python3
"""
Script de configuración e instalación para FloraWatch
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    print("🌸" * 50)
    print("    FLORAWATCH - SETUP & INSTALLATION")
    print("🌸" * 50)
    print()

def check_python_version():
    """Verificar que Python sea 3.8 o superior"""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} detectado")

def create_virtual_environment():
    """Crear entorno virtual si no existe"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Entorno virtual ya existe")
        return
    
    print("📦 Creando entorno virtual...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Entorno virtual creado exitosamente")
    except subprocess.CalledProcessError:
        print("❌ Error creando entorno virtual")
        sys.exit(1)

def get_pip_command():
    """Obtener comando pip correcto según el sistema"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "pip.exe")
    else:  # Unix/Linux/macOS
        return os.path.join("venv", "bin", "pip")

def install_dependencies():
    """Instalar dependencias de Python"""
    print("📋 Instalando dependencias...")
    
    pip_cmd = get_pip_command()
    requirements_file = os.path.join("backend", "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print(f"❌ Archivo de requirements no encontrado: {requirements_file}")
        sys.exit(1)
    
    try:
        # Actualizar pip primero
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Instalar dependencias
        subprocess.run([pip_cmd, "install", "-r", requirements_file], check=True)
        print("✅ Dependencias instaladas exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def setup_environment_file():
    """Configurar archivo de variables de entorno"""
    env_example = ".env.example"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("✅ Archivo .env ya existe")
        return
    
    if os.path.exists(env_example):
        shutil.copy(env_example, env_file)
        print("✅ Archivo .env creado desde plantilla")
        print("⚠️  IMPORTANTE: Edita .env y agrega tu NASA API key")
        print("   Obtén tu API key en: https://api.nasa.gov/")
    else:
        print("⚠️  Archivo .env.example no encontrado")

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        "data/cache",
        "logs",
        "data/cache/satellite",
        "data/cache/processed", 
        "data/cache/predictions",
        "data/cache/events"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios de trabajo creados")

def verify_installation():
    """Verificar que la instalación sea correcta"""
    print("\n🔍 Verificando instalación...")
    
    # Verificar estructura de archivos
    required_files = [
        "backend/app.py",
        "backend/requirements.txt",
        "frontend/templates/index.html",
        "frontend/static/css/main.css",
        "frontend/static/js/app.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    # Verificar importaciones Python básicas
    python_cmd = get_pip_command().replace("pip", "python")
    test_imports = [
        "import flask",
        "import numpy",
        "import pandas",
        "import requests"
    ]
    
    for import_statement in test_imports:
        try:
            subprocess.run([python_cmd, "-c", import_statement], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"❌ Error importando: {import_statement}")
            return False
    
    print("✅ Verificación completada exitosamente")
    return True

def print_usage_instructions():
    """Mostrar instrucciones de uso"""
    print("\n" + "="*60)
    print("🎉 ¡INSTALACIÓN COMPLETADA!")
    print("="*60)
    print()
    print("Para ejecutar FloraWatch:")
    print()
    
    if os.name == 'nt':  # Windows
        print("1. Activar entorno virtual:")
        print("   venv\\Scripts\\activate")
        print()
        print("2. Ejecutar aplicación:")
        print("   python backend\\app.py")
    else:  # Unix/Linux/macOS
        print("1. Activar entorno virtual:")
        print("   source venv/bin/activate")
        print()
        print("2. Ejecutar aplicación:")
        print("   python backend/app.py")
    
    print()
    print("3. Abrir en navegador:")
    print("   http://localhost:5000")
    print()
    print("IMPORTANTE:")
    print("- Edita el archivo .env con tu NASA API key")
    print("- La aplicación funciona con datos simulados sin API key")
    print("- Consulta README.md para más información")
    print()

def main():
    """Función principal de setup"""
    print_header()
    
    # Verificar prerrequisitos
    check_python_version()
    
    # Configurar entorno
    create_virtual_environment()
    install_dependencies()
    setup_environment_file()
    create_directories()
    
    # Verificar instalación
    if verify_installation():
        print_usage_instructions()
    else:
        print("❌ La instalación no se completó correctamente")
        print("   Revisa los errores anteriores y vuelve a intentar")
        sys.exit(1)

if __name__ == "__main__":
    main()