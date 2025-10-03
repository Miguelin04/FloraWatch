# Guía de Inicio Rápido - FloraWatch 🌸

## Instalación Automática

### Opción 1: Usando el script de setup (Recomendado)

```bash
# En Windows PowerShell:
python setup.py

# En Linux/macOS:
python3 setup.py
```

### Opción 2: Instalación manual

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r backend/requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu NASA API key

# 5. Crear directorios
mkdir -p data/cache logs
```

## Ejecución

```bash
# Activar entorno virtual si no está activo
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Ejecutar aplicación
python backend/app.py
```

Abrir en navegador: http://localhost:5000

## Configuración de NASA API

1. Registrarse en https://api.nasa.gov/
2. Obtener API key gratuita
3. Editar archivo `.env`:
   ```
   NASA_API_KEY=tu_api_key_aqui
   ```

## Uso Básico

1. **Seleccionar ubicación**: Hacer clic en el mapa o usar coordenadas
2. **Configurar fechas**: Seleccionar período de análisis
3. **Elegir especie**: Opcional, para análisis específico
4. **Analizar**: Hacer clic en "Analizar Floración"
5. **Explorar resultados**: Ver mapa, gráficos y predicciones

## Funcionalidades Principales

- 🗺️ **Mapa Global**: Visualización interactiva de eventos
- 📊 **Análisis Temporal**: Gráficos de series de tiempo NDVI
- 🔮 **Predicciones**: Eventos futuros basados en ML
- 🔔 **Alertas**: Notificaciones de eventos significativos
- 🌸 **Detección**: Algoritmos avanzados de floración

## Datos Satelitales Soportados

- **MODIS**: Índices de vegetación cada 16 días
- **Landsat**: Imágenes de alta resolución
- **VIIRS**: Datos diarios globales
- **EMIT**: Datos hiperespectrales
- **PACE**: Análisis de ecosistemas

## Solución de Problemas

### Error de dependencias
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Puerto ocupado
Cambiar puerto en `.env`:
```
PORT=5001
```

### Sin datos
- Verificar conexión a internet
- Obtener NASA API key válida
- La app funciona con datos simulados sin API key

## Estructura del Proyecto

```
FloraWatch/
├── backend/           # Servidor Python Flask
├── frontend/          # Interfaz web HTML/CSS/JS
├── data/             # Cache y datos procesados
├── docs/             # Documentación
├── setup.py          # Script de instalación
└── README.md         # Documentación completa
```

## Enlaces Útiles

- **NASA API**: https://api.nasa.gov/
- **Documentación**: Ver README.md completo
- **Soporte**: Crear issue en GitHub
- **Contribuir**: Ver sección de desarrollo en README

¡Disfruta explorando los eventos de floración global! 🌍🌸