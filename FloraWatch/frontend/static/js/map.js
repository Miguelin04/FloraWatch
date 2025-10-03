/**
 * FloraWatch - Gestor de Mapas
 * Maneja la visualización interactiva de mapas con eventos de floración
 */

class MapManager {
    constructor() {
        this.map = null;
        this.markers = [];
        this.floweringLayers = {};
        this.baseLayers = {};
        this.overlayLayers = {};
        this.currentLocation = null;
        
        this.init();
    }
    
    init() {
        this.initializeMap();
        this.setupBaseLayers();
        this.setupOverlayLayers();
        this.setupEventListeners();
        
        console.log('🗺️ Gestor de mapas inicializado');
    }
    
    initializeMap() {
        // Inicializar mapa centrado en una ubicación por defecto
        this.map = L.map('map', {
            center: [40.0, -3.0], // Madrid, España
            zoom: 6,
            zoomControl: false
        });
        
        // Agregar control de zoom personalizado
        L.control.zoom({
            position: 'topright'
        }).addTo(this.map);
        
        // Agregar control de escala
        L.control.scale({
            position: 'bottomleft'
        }).addTo(this.map);
        
        // Event listeners del mapa
        this.map.on('click', (e) => {
            this.handleMapClick(e);
        });
        
        this.map.on('zoomend', () => {
            this.updateMarkersVisibility();
        });
    }
    
    setupBaseLayers() {
        // Definir capas base
        this.baseLayers = {
            satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: '&copy; Esri, Maxar, Earthstar Geographics',
                maxZoom: 18
            }),
            terrain: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenTopoMap contributors',
                maxZoom: 17
            }),
            street: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 18
            })
        };
        
        // Agregar capa por defecto
        this.baseLayers.satellite.addTo(this.map);
        
        // Configurar selector de capas base
        this.setupLayerSelector();
    }
    
    setupOverlayLayers() {
        // Capas de superposición para datos satelitales
        this.overlayLayers = {
            ndvi: L.layerGroup(),
            evi: L.layerGroup(),
            temperature: L.layerGroup()
        };
        
        // Configurar selector de capas de superposición
        this.setupOverlaySelector();
    }
    
    setupLayerSelector() {
        const baseLayerSelect = document.getElementById('base-layer');
        if (baseLayerSelect) {
            baseLayerSelect.addEventListener('change', (e) => {
                const selectedLayer = e.target.value;
                this.switchBaseLayer(selectedLayer);
            });
        }
    }
    
    setupOverlaySelector() {
        const overlaySelect = document.getElementById('overlay-layer');
        if (overlaySelect) {
            overlaySelect.addEventListener('change', (e) => {
                const selectedOverlay = e.target.value;
                this.switchOverlayLayer(selectedOverlay);
            });
        }
    }
    
    setupEventListeners() {
        // Redimensionar mapa cuando cambie el tamaño de ventana
        window.addEventListener('resize', () => {
            this.resize();
        });
    }
    
    switchBaseLayer(layerName) {
        // Remover capa actual
        Object.values(this.baseLayers).forEach(layer => {
            this.map.removeLayer(layer);
        });
        
        // Agregar nueva capa
        if (this.baseLayers[layerName]) {
            this.baseLayers[layerName].addTo(this.map);
        }
    }
    
    switchOverlayLayer(layerName) {
        // Remover todas las capas de superposición
        Object.values(this.overlayLayers).forEach(layer => {
            this.map.removeLayer(layer);
        });
        
        // Agregar capa seleccionada
        if (layerName !== 'none' && this.overlayLayers[layerName]) {
            this.overlayLayers[layerName].addTo(this.map);
            this.loadOverlayData(layerName);
        }
    }
    
    async loadOverlayData(layerType) {
        try {
            // En una implementación real, aquí cargaríamos datos de NASA
            console.log(`Cargando datos de superposición: ${layerType}`);
            
            // Simular carga de datos NDVI/EVI/Temperatura
            const bounds = this.map.getBounds();
            const data = await this.simulateOverlayData(layerType, bounds);
            this.displayOverlayData(layerType, data);
            
        } catch (error) {
            console.error(`Error cargando datos de ${layerType}:`, error);
        }
    }
    
    async simulateOverlayData(layerType, bounds) {
        // Simular demora de carga
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const data = [];
        const gridSize = 0.5; // Grados
        
        for (let lat = bounds.getSouth(); lat <= bounds.getNorth(); lat += gridSize) {
            for (let lng = bounds.getWest(); lng <= bounds.getEast(); lng += gridSize) {
                let value;
                
                switch (layerType) {
                    case 'ndvi':
                        value = Math.random() * 0.8 + 0.1; // 0.1 a 0.9
                        break;
                    case 'evi':
                        value = Math.random() * 0.6 + 0.1; // 0.1 a 0.7
                        break;
                    case 'temperature':
                        value = Math.random() * 40 + 5; // 5°C a 45°C
                        break;
                    default:
                        value = Math.random();
                }
                
                data.push({
                    lat: lat,
                    lng: lng,
                    value: value
                });
            }
        }
        
        return data;
    }
    
    displayOverlayData(layerType, data) {
        const layer = this.overlayLayers[layerType];
        
        data.forEach(point => {
            const color = this.getColorForValue(layerType, point.value);
            const opacity = 0.6;
            
            const rectangle = L.rectangle(
                [[point.lat, point.lng], [point.lat + 0.5, point.lng + 0.5]], {
                    color: color,
                    fillColor: color,
                    fillOpacity: opacity,
                    weight: 1
                }
            );
            
            // Tooltip con información
            rectangle.bindTooltip(
                `${layerType.toUpperCase()}: ${point.value.toFixed(3)}`,
                { permanent: false, direction: 'top' }
            );
            
            layer.addLayer(rectangle);
        });
    }
    
    getColorForValue(layerType, value) {
        let color;
        
        switch (layerType) {
            case 'ndvi':
            case 'evi':
                // Escala de verde para índices de vegetación
                const greenIntensity = Math.floor(value * 255);
                color = `rgb(${255 - greenIntensity}, ${greenIntensity}, 0)`;
                break;
            case 'temperature':
                // Escala de azul a rojo para temperatura
                const tempNormalized = (value - 5) / 40; // Normalizar 5-45°C a 0-1
                const red = Math.floor(tempNormalized * 255);
                const blue = Math.floor((1 - tempNormalized) * 255);
                color = `rgb(${red}, 0, ${blue})`;
                break;
            default:
                color = '#666666';
        }
        
        return color;
    }
    
    handleMapClick(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        console.log(`Clic en mapa: ${lat.toFixed(4)}, ${lng.toFixed(4)}`);
        
        // Actualizar ubicación en la aplicación principal
        if (window.app) {
            window.app.setLocation(lat, lng);
        }
        
        // Agregar marcador temporal
        this.addTemporaryMarker(lat, lng);
    }
    
    addTemporaryMarker(lat, lng) {
        // Remover marcador temporal anterior
        if (this.tempMarker) {
            this.map.removeLayer(this.tempMarker);
        }
        
        // Crear nuevo marcador temporal
        this.tempMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                html: '<i class="fas fa-crosshairs"></i>',
                iconSize: [20, 20],
                className: 'temp-marker'
            })
        }).addTo(this.map);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            if (this.tempMarker) {
                this.map.removeLayer(this.tempMarker);
                this.tempMarker = null;
            }
        }, 3000);
    }
    
    setLocation(lat, lng) {
        this.currentLocation = { lat, lng };
        
        // Centrar mapa en la nueva ubicación
        this.map.setView([lat, lng], Math.max(this.map.getZoom(), 10));
        
        // Agregar marcador de ubicación actual si no existe
        if (this.locationMarker) {
            this.map.removeLayer(this.locationMarker);
        }
        
        this.locationMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                html: '<i class="fas fa-map-marker-alt"></i>',
                iconSize: [25, 25],
                className: 'location-marker'
            })
        }).addTo(this.map);
        
        this.locationMarker.bindPopup(
            `<strong>Ubicación Seleccionada</strong><br>
             ${lat.toFixed(4)}°, ${lng.toFixed(4)}°`
        );
    }
    
    showFloweringEvents(events) {
        // Limpiar eventos anteriores
        this.clearFloweringEvents();
        
        if (!events || events.length === 0) {
            console.log('No hay eventos de floración para mostrar');
            return;
        }
        
        console.log(`Mostrando ${events.length} eventos de floración en el mapa`);
        
        events.forEach((event, index) => {
            this.addFloweringEventMarker(event, index);
        });
        
        // Ajustar vista del mapa para incluir todos los eventos
        if (this.currentLocation) {
            const group = new L.featureGroup(this.markers);
            if (this.markers.length > 0) {
                this.map.fitBounds(group.getBounds().pad(0.1));
            }
        }
    }
    
    addFloweringEventMarker(event, index) {
        const location = event.location || this.currentLocation;
        if (!location) return;
        
        // Determinar color basado en el tipo de evento
        const color = this.getEventColor(event);
        const size = this.getEventSize(event);
        
        // Crear marcador
        const marker = L.circleMarker([location.lat, location.lon], {
            radius: size,
            fillColor: color,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });
        
        // Popup con información del evento
        const popupContent = this.createEventPopup(event, index + 1);
        marker.bindPopup(popupContent, {
            maxWidth: 300,
            className: 'flowering-event-popup'
        });
        
        // Tooltip con información básica
        marker.bindTooltip(
            `${event.event_type || 'Evento'}: ${event.start_date} - ${event.end_date}`,
            { direction: 'top', offset: [0, -10] }
        );
        
        // Agregar al mapa y guardar referencia
        marker.addTo(this.map);
        this.markers.push(marker);
        
        // Efecto de animación al agregar
        setTimeout(() => {
            marker.setStyle({ radius: size * 1.2 });
            setTimeout(() => {
                marker.setStyle({ radius: size });
            }, 200);
        }, index * 100);
    }
    
    getEventColor(event) {
        const now = new Date();
        const startDate = new Date(event.start_date);
        const endDate = new Date(event.end_date);
        
        if (now >= startDate && now <= endDate) {
            return '#e91e63'; // Rosa para eventos activos
        } else if (now < startDate) {
            return '#9c27b0'; // Púrpura para eventos futuros/predichos
        } else {
            return '#607d8b'; // Gris azulado para eventos pasados
        }
    }
    
    getEventSize(event) {
        // Tamaño basado en la intensidad y confianza del evento
        const baseSize = 8;
        const intensityFactor = (event.intensity || 0.1) * 10;
        const confidenceFactor = (event.confidence || 0.5) * 5;
        
        return Math.max(baseSize, Math.min(20, baseSize + intensityFactor + confidenceFactor));
    }
    
    createEventPopup(event, eventNumber) {
        const confidence = ((event.confidence || 0) * 100).toFixed(0);
        const intensity = (event.intensity || 0).toFixed(3);
        
        return `
            <div class="flowering-event-info">
                <h4><i class="fas fa-flower"></i> Evento de Floración #${eventNumber}</h4>
                <div class="event-details">
                    <p><strong>Período:</strong> ${this.formatDisplayDate(event.start_date)} - ${this.formatDisplayDate(event.end_date)}</p>
                    <p><strong>Pico:</strong> ${this.formatDisplayDate(event.peak_date)}</p>
                    <p><strong>Duración:</strong> ${event.duration_days} días</p>
                    <p><strong>Intensidad:</strong> ${intensity}</p>
                    <p><strong>Confianza:</strong> ${confidence}%</p>
                    <p><strong>Tipo:</strong> ${this.translateEventType(event.event_type)}</p>
                </div>
                <div class="event-actions">
                    <button onclick="app.mapManager.zoomToEvent(${event.location?.lat || this.currentLocation?.lat}, ${event.location?.lon || this.currentLocation?.lon})" class="btn-small">
                        <i class="fas fa-search-plus"></i> Zoom
                    </button>
                    <button onclick="app.mapManager.analyzeEvent('${event.start_date}', '${event.end_date}')" class="btn-small">
                        <i class="fas fa-chart-line"></i> Analizar
                    </button>
                </div>
            </div>
        `;
    }
    
    translateEventType(eventType) {
        const translations = {
            'brief_flowering': 'Floración Breve',
            'typical_flowering': 'Floración Típica',
            'extended_flowering': 'Floración Extendida',
            'vegetation_pulse': 'Pulso de Vegetación'
        };
        
        return translations[eventType] || eventType || 'Sin clasificar';
    }
    
    zoomToEvent(lat, lng) {
        this.map.setView([lat, lng], 15);
    }
    
    analyzeEvent(startDate, endDate) {
        // Establecer fechas en los controles
        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');
        
        if (startDateInput) startDateInput.value = startDate;
        if (endDateInput) endDateInput.value = endDate;
        
        // Cambiar a sección de análisis
        if (window.app) {
            window.app.switchSection('analytics');
            setTimeout(() => {
                window.app.performAnalysis();
            }, 500);
        }
    }
    
    clearFloweringEvents() {
        // Remover todos los marcadores de eventos
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
    }
    
    updateMarkersVisibility() {
        const zoom = this.map.getZoom();
        
        // Ajustar visibilidad y tamaño de marcadores según el zoom
        this.markers.forEach(marker => {
            if (zoom < 8) {
                // Zoom lejano: marcadores más pequeños
                marker.setRadius(marker.options.radius * 0.7);
            } else if (zoom > 12) {
                // Zoom cercano: marcadores más grandes
                marker.setRadius(marker.options.radius * 1.3);
            } else {
                // Zoom normal: tamaño original
                marker.setRadius(marker.options.radius);
            }
        });
    }
    
    resize() {
        if (this.map) {
            setTimeout(() => {
                this.map.invalidateSize();
            }, 100);
        }
    }
    
    // Métodos de utilidad
    formatDisplayDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
    
    // Métodos públicos para interacción con otros módulos
    getCurrentBounds() {
        return this.map.getBounds();
    }
    
    getCurrentCenter() {
        return this.map.getCenter();
    }
    
    getCurrentZoom() {
        return this.map.getZoom();
    }
    
    addCustomLayer(name, layer) {
        this.overlayLayers[name] = layer;
    }
    
    removeCustomLayer(name) {
        if (this.overlayLayers[name]) {
            this.map.removeLayer(this.overlayLayers[name]);
            delete this.overlayLayers[name];
        }
    }
}

// Inicializar gestor de mapas cuando se cargue el DOM
document.addEventListener('DOMContentLoaded', () => {
    if (window.app) {
        window.app.mapManager = new MapManager();
    } else {
        // Si la app principal no está lista, esperar un poco
        setTimeout(() => {
            if (window.app) {
                window.app.mapManager = new MapManager();
            }
        }, 100);
    }
});

// Estilos CSS adicionales para marcadores y popups
const mapStyles = `
    .temp-marker {
        color: #ff5722;
        font-size: 16px;
        text-align: center;
        line-height: 20px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        border: 2px solid #ff5722;
    }
    
    .location-marker {
        color: #2e7d32;
        font-size: 20px;
        text-align: center;
        line-height: 25px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        border: 2px solid #2e7d32;
    }
    
    .flowering-event-popup .leaflet-popup-content {
        margin: 8px 12px;
        line-height: 1.4;
    }
    
    .flowering-event-info h4 {
        margin: 0 0 10px 0;
        color: #2e7d32;
        font-size: 14px;
    }
    
    .event-details {
        margin-bottom: 10px;
    }
    
    .event-details p {
        margin: 4px 0;
        font-size: 12px;
    }
    
    .event-actions {
        display: flex;
        gap: 5px;
    }
    
    .btn-small {
        background: #2e7d32;
        color: white;
        border: none;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .btn-small:hover {
        background: #1b5e20;
    }
    
    .leaflet-control-zoom {
        border: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
    }
    
    .leaflet-control-zoom a {
        background: white !important;
        color: #333 !important;
        border: none !important;
        font-weight: bold !important;
    }
    
    .leaflet-control-zoom a:hover {
        background: #f5f5f5 !important;
    }
`;

// Agregar estilos al documento
const mapStyleSheet = document.createElement('style');
mapStyleSheet.textContent = mapStyles;
document.head.appendChild(mapStyleSheet);