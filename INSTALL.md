# 🌸 Guía de Instalación - FloraWatch

## 📋 Tabla de Contenidos
- [Prerrequisitos del Sistema](#prerrequisitos-del-sistema)
- [Instalación Automática](#instalación-automática)
- [Instalación Manual](#instalación-manual)
- [Configuración](#configuración)
- [Verificación](#verificación)
- [Solución de Problemas](#solución-de-problemas)

## 🔧 Prerrequisitos del Sistema

### Requisitos Mínimos
- **Python**: 3.8 a 3.11 (recomendado) o 3.12 (con requirements especiales)
- **RAM**: 4GB mínimo, 8GB recomendado
- **Espacio en disco**: 2GB libre
- **Sistema operativo**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### ⚠️ **Nota Importante para Python 3.12**
Si tienes Python 3.12, usa `requirements-python312.txt` en lugar de `requirements.txt` para evitar problemas de compatibilidad con NumPy y otras librerías científicas.

### Herramientas Requeridas

#### Windows
```powershell
# Verificar Python
python --version

# Si no tienes Python, descarga desde: https://python.org
# Asegúrate de marcar "Add Python to PATH"

# Visual Studio Build Tools (para compilar paquetes)
# Descarga desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

#### macOS
```bash
# Verificar Python
python3 --version

# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python y herramientas
brew install python3
```

#### Linux (Ubuntu/Debian)
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y dependencias
sudo apt install python3 python3-pip python3-venv python3-dev
sudo apt install build-essential libproj-dev libgeos-dev
sudo apt install gdal-bin libgdal-dev
```

## 🚀 Instalación Automática (Recomendada)

### 1. Descargar el Proyecto
```bash
# Clonar desde Git
git clone https://github.com/tu-usuario/FloraWatch.git
cd FloraWatch

# O descargar ZIP y extraer
```

### 2. Ejecutar Setup Automático
```bash
# Windows
python setup.py

# macOS/Linux
python3 setup.py
```

El script automáticamente:
- ✅ Verifica la versión de Python
- ✅ Crea el entorno virtual
- ✅ Instala todas las dependencias
- ✅ Configura directorios necesarios
- ✅ Crea archivo de configuración .env

### 3. Activar Entorno y Ejecutar
```bash
# Windows
venv\Scripts\activate
python backend\app.py

# macOS/Linux
source venv/bin/activate
python backend/app.py
```

## 🔨 Instalación Manual

### 1. Crear Entorno Virtual
```bash
# Crear entorno
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 2. Instalar Dependencias

#### Opción A: Para Python 3.12 (Tu caso)
```bash
pip install --upgrade pip
pip install -r requirements-python312.txt
```

#### Opción B: Instalación Básica (Python 3.8-3.11)
```bash
pip install --upgrade pip
pip install -r requirements-production.txt
```

#### Opción C: Instalación Completa (Python 3.8-3.11)
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Opción D: Instalación para Desarrollo
```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```

#### Opción E: Instalación Mínima (Sin GDAL)
```bash
pip install --upgrade pip
pip install -r requirements-basic.txt
```

### 3. Configurar Variables de Entorno
```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar .env con tu editor favorito
# Configura al menos NASA_API_KEY
```

### 4. Crear Directorios
```bash
mkdir -p data/cache/satellite
mkdir -p data/cache/processed
mkdir -p data/cache/predictions
mkdir -p data/cache/events
mkdir -p logs
```

## ⚙️ Configuración

### 1. API Key de NASA (Recomendado)
```bash
# 1. Registrarse en: https://api.nasa.gov/
# 2. Obtener API key gratuita
# 3. Editar .env:
NASA_API_KEY=tu_api_key_aquí
```

### 2. Configuración Básica del .env
```bash
# Configuración mínima requerida
FLASK_ENV=development
SECRET_KEY=cambiar-por-clave-segura
HOST=localhost
PORT=5000
NASA_API_KEY=tu_nasa_api_key
```

### 3. Configuración Opcional

#### Base de Datos PostgreSQL
```bash
# Instalar PostgreSQL
# Windows: https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Linux: sudo apt install postgresql postgresql-contrib

# Configurar en .env:
DATABASE_URL=postgresql://usuario:password@localhost:5432/florawatch
```

#### Cache Redis
```bash
# Instalar Redis
# Windows: https://github.com/microsoftarchive/redis/releases
# macOS: brew install redis
# Linux: sudo apt install redis-server

# Configurar en .env:
REDIS_URL=redis://localhost:6379/0
```

## ✅ Verificación

### 1. Verificar Instalación
```bash
# Activar entorno virtual
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Verificar imports básicos
python -c "import flask, numpy, pandas, requests; print('✅ Imports básicos OK')"

# Verificar estructura de archivos
python -c "import os; print('✅ Estructura OK' if all(os.path.exists(f) for f in ['backend/app.py', 'frontend/templates/index.html']) else '❌ Archivos faltantes')"
```

### 2. Ejecutar Aplicación
```bash
# Desde el directorio raíz del proyecto
python backend/app.py
```

### 3. Probar en Navegador
```
http://localhost:5000
```

Deberías ver:
- 🗺️ Mapa interactivo
- 🎛️ Panel de controles lateral
- 📊 Secciones de análisis y predicciones

## 🐛 Solución de Problemas

### Problemas con Python 3.12 (Tu caso)
```bash
# ¡IMPORTANTE! Python 3.12 requiere versiones específicas
# Usar archivo de requirements especializado:
pip install -r requirements-python312.txt

# Si sigues teniendo problemas con NumPy:
pip install --upgrade pip setuptools wheel
pip install numpy==1.26.2 --force-reinstall
pip install pandas==2.1.4 --force-reinstall

# Alternativa: usar Python 3.11 (más estable)
# Instalar Python 3.11 desde python.org y crear nuevo entorno
```

### Error: "No module named 'gdal'"
```bash
# Opción 1: Usar conda (recomendado)
conda install -c conda-forge gdal

# Opción 2: Usar requirements básicos (sin GDAL)
pip install -r requirements-basic.txt

# Opción 3: Python 3.12 - evitar GDAL por ahora
pip install -r requirements-python312.txt
```

### Error: "Microsoft Visual C++ 14.0 is required"
```bash
# Windows: Instalar Visual Studio Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# O usar wheels precompilados:
pip install --only-binary=all -r requirements-production.txt
```

### Error: "Permission denied"
```bash
# Windows: Ejecutar PowerShell como administrador
# macOS/Linux: Usar sudo solo si es necesario
sudo pip install -r requirements.txt

# Mejor práctica: usar entorno virtual sin sudo
```

### Problemas de Memoria
```bash
# Reducir workers en .env:
MAX_WORKERS=2
CHUNK_SIZE=500

# O usar instalación básica:
pip install -r requirements-basic.txt
```

### Puerto 5000 en Uso
```bash
# Cambiar puerto en .env:
PORT=5001

# O ejecutar directamente:
python backend/app.py --port 5001
```

### Datos Simulados vs Reales
```bash
# Para usar datos simulados (por defecto):
ENABLE_REAL_NASA_API=False
MOCK_EXTERNAL_APIS=True

# Para usar datos reales de NASA:
ENABLE_REAL_NASA_API=True
NASA_API_KEY=tu_api_key_valida
```

## 🚀 Instalación en Producción

### 1. Servidor Linux (Ubuntu)
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install python3 python3-pip python3-venv nginx postgresql redis-server

# Clonar proyecto
git clone https://github.com/tu-usuario/FloraWatch.git
cd FloraWatch

# Instalar dependencias Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-production.txt

# Configurar base de datos
sudo -u postgres createdb florawatch
sudo -u postgres createuser florawatch_user

# Configurar variables de entorno para producción
cp .env.example .env
# Editar .env con configuración de producción

# Ejecutar con Gunicorn
gunicorn --bind 0.0.0.0:5000 backend.app:app
```

### 2. Docker (Opcional)
```dockerfile
# Crear Dockerfile en el directorio raíz
FROM python:3.9-slim

WORKDIR /app
COPY requirements-production.txt .
RUN pip install -r requirements-production.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]
```

```bash
# Construir y ejecutar
docker build -t florawatch .
docker run -p 5000:5000 florawatch
```

## 📞 Soporte

Si encuentras problemas:

1. **Revisa el log**: `logs/florawatch.log`
2. **Verifica la documentación**: `README.md`
3. **Issues en GitHub**: Crea un issue con detalles del error
4. **Stack Overflow**: Busca errores específicos

## 🎉 ¡Listo!

Si llegaste hasta aquí, ¡felicidades! Tu instalación de FloraWatch debería estar funcionando correctamente. 

**Próximos pasos:**
- 🔑 Configura tu NASA API key para datos reales
- 📍 Prueba seleccionando diferentes ubicaciones
- 📊 Explora las funciones de análisis y predicción
- 🔔 Configura alertas para regiones de interés

¡Disfruta monitoreando la floración global! 🌸🌍