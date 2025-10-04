# FloraWatch 🌸 - Monitor de Eventos de Floración Global

## Descripción
FloraWatch es una herramienta visual interactiva que aprovecha las observaciones de la Tierra de NASA para detectar, monitorear y predecir eventos de floración de plantas en todo el mundo. La aplicación utiliza datos satelitales de misiones como MODIS, Landsat, VIIRS, EMIT y PACE para proporcionar información crítica sobre fenología de plantas, patrones estacionales y cambios en la vegetación.

## Características Principales

### 🛰️ Fuentes de Datos
- **MODIS**: Índices de vegetación (NDVI, EVI) cada 16 días
- **Landsat**: Imágenes de alta resolución temporal
- **VIIRS**: Datos diarios de cobertura global
- **EMIT**: Datos hiperespectrales para composición de superficie
- **PACE**: Análisis de ecosistemas y aerosoles

### 🌻 Capacidades de Detección
- Detección automática de eventos de floración
- Análisis de cambios espectrales temporales
- Identificación de patrones estacionales
- Clasificación de tipos de vegetación
- Predicción de eventos futuros

### 📊 Visualización Interactiva
- Mapas globales interactivos con zoom
- Gráficos temporales de tendencias
- Filtros por región, fecha y tipo de cultivo
- Alertas en tiempo real
- Reportes de conservación

### 🎯 Aplicaciones
- **Agricultura**: Monitoreo de cultivos y predicción de cosechas
- **Conservación**: Seguimiento de especies y ecosistemas
- **Investigación**: Estudios fenológicos y climáticos
- **Salud Pública**: Predicción de polen y alérgenos
- **Gestión Ambiental**: Detección de especies invasoras

## Estructura del Proyecto

```
FloraWatch/
├── backend/                 # Servidor Python
│   ├── src/
│   │   ├── data_sources/   # APIs y conectores NASA
│   │   ├── algorithms/     # Detección de floración
│   │   └── utils/          # Utilidades y procesamiento
│   ├── requirements.txt    # Dependencias Python
│   └── app.py             # Aplicación principal
├── frontend/               # Interfaz web
│   ├── static/
│   │   ├── css/           # Estilos
│   │   └── js/            # JavaScript
│   └── templates/         # Plantillas HTML
├── data/                  # Datos y cache
└── docs/                  # Documentación

```

## Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Clave API de NASA (api.nasa.gov)
- Navegador web moderno

### Instalación
```bash
# Clonar el repositorio
git clone https://github.com/username/FloraWatch.git
cd FloraWatch

# Instalar dependencias
pip install -r backend/requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu NASA API key

# Ejecutar la aplicación
python backend/app.py
```

### Configuración de API
1. Registrarse en https://api.nasa.gov/
2. Obtener clave API gratuita
3. Configurar en archivo `.env`

## Uso

### Interfaz Web
1. Abrir http://localhost:5000
2. Seleccionar región de interés en el mapa
3. Configurar filtros temporales
4. Visualizar eventos de floración detectados
5. Exportar datos y reportes

### API REST
```python
# Obtener eventos de floración
GET /api/flowering-events?lat=40.7128&lon=-74.0060&start_date=2024-03-01&end_date=2024-05-31

# Predicción de floración
GET /api/predictions?region=europe&species=cherry_blossom

# Alertas activas
GET /api/alerts?severity=high
```

## Algoritmos de Detección

### Índices Espectrales
- **NDVI** (Normalized Difference Vegetation Index)
- **EVI** (Enhanced Vegetation Index)
- **SAVI** (Soil Adjusted Vegetation Index)
- **NBR** (Normalized Burn Ratio)

### Métodos de Detección
1. **Análisis Temporal**: Detección de cambios en series temporales
2. **Clasificación ML**: Identificación automática de eventos
3. **Análisis Espectral**: Firmas espectrales específicas de floración
4. **Validación Cruzada**: Verificación con múltiples fuentes

## Casos de Uso

### 🌾 Agricultura de Precisión
- Monitoreo de cultivos de floración (almendros, manzanos)
- Optimización de polinización
- Predicción de rendimientos
- Gestión de recursos hídricos

### 🦋 Conservación de Polinizadores
- Mapeo de corredores de polinización
- Sincronización planta-polinizador
- Impacto del cambio climático
- Planificación de hábitats

### 🌸 Turismo y Recreación
- Predicción de floraciones espectaculares
- Rutas de turismo natural
- Calendarios de eventos
- Aplicaciones móviles

### 🔬 Investigación Científica
- Estudios fenológicos globales
- Impactos del cambio climático
- Modelos ecológicos
- Publicaciones científicas

## Tecnologías Utilizadas

### Backend
- **Python 3.8+**: Lenguaje principal
- **Flask**: Framework web
- **NumPy/Pandas**: Procesamiento de datos
- **Scikit-learn**: Machine Learning
- **GDAL/Rasterio**: Procesamiento geoespacial
- **Requests**: APIs HTTP

### Frontend
- **HTML5/CSS3**: Estructura y estilos
- **JavaScript**: Interactividad
- **Leaflet**: Mapas interactivos
- **D3.js**: Visualizaciones avanzadas
- **Chart.js**: Gráficos y métricas

### APIs y Datos
- **NASA API**: Datos satelitales
- **AppEEARS**: Procesamiento geoespacial
- **OpenWeatherMap**: Datos meteorológicos
- **GeoNames**: Información geográfica

## Contribuir

### Desarrollo
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Reportar Bugs
- Usar GitHub Issues
- Incluir pasos para reproducir
- Especificar sistema operativo y versión
- Adjuntar logs si es posible

## Roadmap

### Versión 1.0 (Actual)
- [x] Detección básica de floración
- [x] Visualización interactiva
- [x] APIs NASA integradas
- [x] Interfaz web responsiva

### Versión 2.0 (Próxima)
- [ ] Machine Learning avanzado
- [ ] Aplicación móvil
- [ ] Alertas push
- [ ] Integración redes sociales

### Versión 3.0 (Futuro)
- [ ] IA predictiva
- [ ] Realidad aumentada
- [ ] Colaboración ciudadana
- [ ] API comercial

## Licencia
MIT License - ver archivo [LICENSE](LICENSE) para detalles.

## Contacto
- **Desarrollador**: Tu Nombre
- **Email**: tu.email@example.com
- **Proyecto**: https://github.com/username/FloraWatch
- **Documentación**: https://florawatch.readthedocs.io

## Agradecimientos
- NASA por proporcionar datos de observación de la Tierra
- Comunidad científica por investigación en fenología
- Contribuyentes del proyecto open source
- Organizaciones de conservación ambiental

---

**FloraWatch** - *Detectando el pulso de la vida en nuestro planeta* 🌍🌸