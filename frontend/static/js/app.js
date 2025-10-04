/**
 * FloraWatch - Aplicación Principal JavaScript
 * Maneja la lógica general de la interfaz y coordinación entre módulos
 */

class FloraWatchApp {
    constructor() {
        this.currentLocation = null;
        this.currentData = null;
        this.activeSection = 'map';
        this.analysisInProgress = false;
        
        // Referencias a otros módulos
        this.mapManager = null;
        this.chartManager = null;
        this.apiClient = null;
        
        this.init();
    }
    
    init() {
        console.log('🌸 Inicializando FloraWatch...');
        
        // Inicializar componentes
        this.setupEventListeners();
        this.initializeDefaults();
        this.updateStats();
        
        // Los otros módulos se inicializarán cuando se carguen sus scripts
        console.log('✅ FloraWatch inicializado correctamente');
    }
    
    setupEventListeners() {
        // Navegación entre secciones
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.target.getAttribute('data-section');
                this.switchSection(section);
            });
        });
        
        // Controles de ubicación
        const locationSearch = document.getElementById('location-search');
        const currentLocationBtn = document.getElementById('current-location');
        const latInput = document.getElementById('lat-input');
        const lonInput = document.getElementById('lon-input');
        
        if (locationSearch) {
            locationSearch.addEventListener('input', this.debounce((e) => {
                this.searchLocation(e.target.value);
            }, 500));
        }
        
        if (currentLocationBtn) {
            currentLocationBtn.addEventListener('click', () => {
                this.getCurrentLocation();
            });
        }
        
        if (latInput && lonInput) {
            latInput.addEventListener('change', () => this.updateLocationFromCoords());
            lonInput.addEventListener('change', () => this.updateLocationFromCoords());
        }
        
        // Controles de fecha
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const days = parseInt(e.target.getAttribute('data-days'));
                this.setDatePreset(days);
            });
        });
        
        // Botón de análisis
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                this.performAnalysis();
            });
        }
        
        // Controles de predicciones
        const generatePredictionsBtn = document.getElementById('generate-predictions');
        if (generatePredictionsBtn) {
            generatePredictionsBtn.addEventListener('click', () => {
                this.generatePredictions();
            });
        }
        
        // Slider de días de predicción
        const predictionDaysSlider = document.getElementById('prediction-days');
        const predictionDaysValue = document.getElementById('prediction-days-value');
        if (predictionDaysSlider && predictionDaysValue) {
            predictionDaysSlider.addEventListener('input', (e) => {
                predictionDaysValue.textContent = e.target.value;
            });
        }
        
        // Control de alertas
        const refreshAlertsBtn = document.getElementById('refresh-alerts');
        if (refreshAlertsBtn) {
            refreshAlertsBtn.addEventListener('click', () => {
                this.refreshAlerts();
            });
        }
        
        // Auto-refresh
        const autoRefreshCheckbox = document.getElementById('auto-refresh');
        if (autoRefreshCheckbox) {
            autoRefreshCheckbox.addEventListener('change', (e) => {
                this.toggleAutoRefresh(e.target.checked);
            });
        }
    }
    
    initializeDefaults() {
        // Establecer fechas por defecto
        const endDate = new Date();
        const startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 3); // 3 meses atrás
        
        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');
        
        if (startDateInput) startDateInput.value = this.formatDate(startDate);
        if (endDateInput) endDateInput.value = this.formatDate(endDate);
        
        // Intentar obtener ubicación actual
        this.getCurrentLocation();
    }
    
    switchSection(sectionName) {
        // Actualizar navegación
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
        
        // Mostrar sección correspondiente
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-section`).classList.add('active');
        
        this.activeSection = sectionName;
        
        // Acciones específicas por sección
        switch (sectionName) {
            case 'map':
                if (this.mapManager) {
                    setTimeout(() => this.mapManager.resize(), 100);
                }
                break;
            case 'analytics':
                if (this.chartManager && this.currentData) {
                    this.chartManager.updateCharts(this.currentData);
                }
                break;
            case 'predictions':
                // Cargar predicciones si no están cargadas
                break;
            case 'alerts':
                this.refreshAlerts();
                break;
        }
    }
    
    async getCurrentLocation() {
        if (!navigator.geolocation) {
            this.showNotification('Geolocalización no disponible', 'warning');
            return;
        }
        
        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    timeout: 10000,
                    enableHighAccuracy: true
                });
            });
            
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            this.setLocation(lat, lon);
            this.showNotification('Ubicación actual obtenida', 'success');
            
        } catch (error) {
            console.warn('Error obteniendo ubicación:', error);
            this.showNotification('No se pudo obtener la ubicación actual', 'warning');
        }
    }
    
    setLocation(lat, lon) {
        this.currentLocation = { lat, lon };
        
        // Actualizar inputs
        const latInput = document.getElementById('lat-input');
        const lonInput = document.getElementById('lon-input');
        
        if (latInput) latInput.value = lat.toFixed(4);
        if (lonInput) lonInput.value = lon.toFixed(4);
        
        // Actualizar mapa si está disponible
        if (this.mapManager) {
            this.mapManager.setLocation(lat, lon);
        }
        
        // Actualizar información de ubicación
        this.updateLocationInfo(lat, lon);
    }
    
    updateLocationFromCoords() {
        const latInput = document.getElementById('lat-input');
        const lonInput = document.getElementById('lon-input');
        
        if (latInput && lonInput) {
            const lat = parseFloat(latInput.value);
            const lon = parseFloat(lonInput.value);
            
            if (!isNaN(lat) && !isNaN(lon) && 
                lat >= -90 && lat <= 90 && 
                lon >= -180 && lon <= 180) {
                this.setLocation(lat, lon);
            }
        }
    }
    
    async searchLocation(query) {
        if (!query || query.length < 3) return;
        
        try {
            // Usar un servicio de geocoding (ejemplo con Nominatim)
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5`
            );
            const results = await response.json();
            
            if (results.length > 0) {
                const result = results[0];
                const lat = parseFloat(result.lat);
                const lon = parseFloat(result.lon);
                
                this.setLocation(lat, lon);
                
                // Actualizar campo de búsqueda
                const locationSearch = document.getElementById('location-search');
                if (locationSearch) {
                    locationSearch.value = result.display_name;
                }
            }
        } catch (error) {
            console.error('Error buscando ubicación:', error);
        }
    }
    
    updateLocationInfo(lat, lon) {
        const infoContent = document.getElementById('location-info');
        if (!infoContent) return;
        
        infoContent.innerHTML = `
            <div class="location-details">
                <h4><i class="fas fa-map-marker-alt"></i> Ubicación Seleccionada</h4>
                <p><strong>Coordenadas:</strong> ${lat.toFixed(4)}°, ${lon.toFixed(4)}°</p>
                <p><strong>Estado:</strong> Listo para análisis</p>
                <div class="location-actions">
                    <button onclick="app.performAnalysis()" class="btn-small">
                        <i class="fas fa-search"></i> Analizar
                    </button>
                </div>
            </div>
        `;
    }
    
    setDatePreset(days) {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        
        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');
        
        if (startDateInput) startDateInput.value = this.formatDate(startDate);
        if (endDateInput) endDateInput.value = this.formatDate(endDate);
    }
    
    async performAnalysis() {
        if (this.analysisInProgress) return;
        
        if (!this.currentLocation) {
            this.showNotification('Selecciona una ubicación primero', 'warning');
            return;
        }
        
        this.analysisInProgress = true;
        this.showLoading(true);
        
        try {
            const params = this.gatherAnalysisParameters();
            console.log('Iniciando análisis con parámetros:', params);
            
            // Usar el API client cuando esté disponible
            if (this.apiClient) {
                const data = await this.apiClient.getFloweringEvents(params);
                this.handleAnalysisResults(data);
            } else {
                // Fallback: datos simulados
                const data = await this.simulateAnalysis(params);
                this.handleAnalysisResults(data);
            }
            
        } catch (error) {
            console.error('Error en análisis:', error);
            this.showNotification('Error al realizar el análisis', 'error');
        } finally {
            this.analysisInProgress = false;
            this.showLoading(false);
        }
    }
    
    gatherAnalysisParameters() {
        const startDate = document.getElementById('start-date')?.value;
        const endDate = document.getElementById('end-date')?.value;
        const species = document.getElementById('species-select')?.value || 'general';
        
        return {
            lat: this.currentLocation.lat,
            lon: this.currentLocation.lon,
            start_date: startDate,
            end_date: endDate,
            species: species,
            radius: 10 // km
        };
    }
    
    async simulateAnalysis(params) {
        // Simular demora de API
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Generar datos simulados
        const events = [];
        const startDate = new Date(params.start_date);
        const endDate = new Date(params.end_date);
        const daysDiff = (endDate - startDate) / (1000 * 60 * 60 * 24);
        
        // Generar algunos eventos aleatorios
        const numEvents = Math.floor(Math.random() * 3) + 1;
        
        for (let i = 0; i < numEvents; i++) {
            const eventDate = new Date(startDate.getTime() + Math.random() * daysDiff * 24 * 60 * 60 * 1000);
            const duration = Math.floor(Math.random() * 20) + 10;
            const endEventDate = new Date(eventDate.getTime() + duration * 24 * 60 * 60 * 1000);
            
            events.push({
                start_date: this.formatDate(eventDate),
                end_date: this.formatDate(endEventDate),
                peak_date: this.formatDate(new Date(eventDate.getTime() + (duration / 2) * 24 * 60 * 60 * 1000)),
                duration_days: duration,
                peak_value: Math.random() * 0.3 + 0.6,
                intensity: Math.random() * 0.2 + 0.1,
                confidence: Math.random() * 0.3 + 0.7,
                event_type: 'typical_flowering',
                description: `Evento de floración típico en ${params.lat.toFixed(2)}°, ${params.lon.toFixed(2)}°`
            });
        }
        
        return {
            location: { lat: params.lat, lon: params.lon },
            period: { start: params.start_date, end: params.end_date },
            events_detected: events.length,
            events: events,
            time_series: this.generateTimeSeries(startDate, endDate),
            metadata: {
                data_source: 'NASA MODIS (simulated)',
                algorithm: 'Spectral Index Analysis',
                processed_at: new Date().toISOString()
            }
        };
    }
    
    generateTimeSeries(startDate, endDate) {
        const dates = [];
        const values = [];
        const currentDate = new Date(startDate);
        
        while (currentDate <= endDate) {
            dates.push(this.formatDate(currentDate));
            
            // Generar valor NDVI simulado con patrón estacional
            const dayOfYear = this.getDayOfYear(currentDate);
            const seasonalPattern = 0.5 + 0.3 * Math.sin(2 * Math.PI * (dayOfYear - 80) / 365);
            const noise = (Math.random() - 0.5) * 0.1;
            const value = Math.max(0, Math.min(1, seasonalPattern + noise));
            
            values.push(parseFloat(value.toFixed(4)));
            
            // Avanzar 16 días (frecuencia MODIS)
            currentDate.setDate(currentDate.getDate() + 16);
        }
        
        return {
            dates: dates,
            values: values,
            units: 'NDVI',
            quality_flags: values.map(() => 'good')
        };
    }
    
    handleAnalysisResults(data) {
        this.currentData = data;
        
        console.log('Resultados del análisis:', data);
        
        // Actualizar información en la interfaz
        this.updateLocationInfo(data.location.lat, data.location.lon);
        
        // Actualizar mapa con eventos
        if (this.mapManager) {
            this.mapManager.showFloweringEvents(data.events);
        }
        
        // Actualizar gráficos si estamos en la sección de análisis
        if (this.activeSection === 'analytics' && this.chartManager) {
            this.chartManager.updateCharts(data);
        }
        
        // Actualizar métricas
        this.updateMetrics(data);
        
        this.showNotification(`${data.events_detected} eventos de floración detectados`, 'success');
    }
    
    updateMetrics(data) {
        const events = data.events || [];
        const timeSeries = data.time_series || {};
        
        // Calcular métricas básicas
        if (events.length > 0) {
            const firstEvent = events.reduce((earliest, event) => 
                event.start_date < earliest.start_date ? event : earliest
            );
            const lastEvent = events.reduce((latest, event) => 
                event.end_date > latest.end_date ? event : latest
            );
            const peakEvent = events.reduce((highest, event) => 
                event.peak_value > highest.peak_value ? event : highest
            );
            
            document.getElementById('season-start').textContent = 
                this.formatDisplayDate(firstEvent.start_date);
            document.getElementById('season-peak').textContent = 
                this.formatDisplayDate(peakEvent.peak_date);
            document.getElementById('season-length').textContent = 
                `${(new Date(lastEvent.end_date) - new Date(firstEvent.start_date)) / (1000 * 60 * 60 * 24)} días`;
            document.getElementById('max-intensity').textContent = 
                peakEvent.peak_value.toFixed(3);
        } else {
            // Sin eventos detectados
            document.getElementById('season-start').textContent = 'N/A';
            document.getElementById('season-peak').textContent = 'N/A';
            document.getElementById('season-length').textContent = 'N/A';
            document.getElementById('max-intensity').textContent = 'N/A';
        }
    }
    
    async generatePredictions() {
        const region = document.getElementById('prediction-region')?.value || 'current';
        const daysAhead = parseInt(document.getElementById('prediction-days')?.value) || 30;
        
        try {
            this.showLoading(true, 'Generando predicciones...');
            
            let predictions;
            if (this.apiClient) {
                predictions = await this.apiClient.getPredictions({
                    region: region === 'current' ? 'global' : region,
                    days_ahead: daysAhead,
                    species: document.getElementById('species-select')?.value || 'general'
                });
            } else {
                // Predicciones simuladas
                predictions = await this.simulatePredictions(daysAhead);
            }
            
            this.displayPredictions(predictions);
            
        } catch (error) {
            console.error('Error generando predicciones:', error);
            this.showNotification('Error al generar predicciones', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async simulatePredictions(daysAhead) {
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const predictions = [];
        const startDate = new Date();
        
        for (let i = 1; i <= daysAhead; i++) {
            const date = new Date(startDate.getTime() + i * 24 * 60 * 60 * 1000);
            predictions.push({
                date: this.formatDate(date),
                predicted_ndvi: Math.random() * 0.4 + 0.4,
                confidence: Math.random() * 0.3 + 0.6,
                flowering_probability: Math.random() * 0.8
            });
        }
        
        return {
            predictions: predictions,
            confidence: 'medium',
            generated_at: new Date().toISOString()
        };
    }
    
    displayPredictions(predictionsData) {
        const container = document.getElementById('predictions-results');
        if (!container) return;
        
        const predictions = predictionsData.predictions || [];
        
        let html = `
            <h3><i class="fas fa-chart-line"></i> Predicciones de Floración</h3>
            <p>Predicciones para los próximos ${predictions.length} días (Confianza: ${predictionsData.confidence})</p>
        `;
        
        if (predictions.length > 0) {
            html += `
                <div class="predictions-list">
            `;
            
            predictions.forEach(pred => {
                const floweringProb = (pred.flowering_probability * 100).toFixed(1);
                const confidence = (pred.confidence * 100).toFixed(1);
                
                html += `
                    <div class="prediction-item">
                        <div class="prediction-date">${this.formatDisplayDate(pred.date)}</div>
                        <div class="prediction-metrics">
                            <span class="metric">
                                <label>NDVI:</label>
                                <span class="value">${pred.predicted_ndvi.toFixed(3)}</span>
                            </span>
                            <span class="metric">
                                <label>Prob. Floración:</label>
                                <span class="value">${floweringProb}%</span>
                            </span>
                            <span class="metric">
                                <label>Confianza:</label>
                                <span class="value">${confidence}%</span>
                            </span>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
        } else {
            html += `<p>No hay predicciones disponibles para este período.</p>`;
        }
        
        container.innerHTML = html;
    }
    
    async refreshAlerts() {
        try {
            const severity = document.getElementById('alert-severity')?.value || 'all';
            
            let alerts;
            if (this.apiClient) {
                alerts = await this.apiClient.getAlerts({ severity });
            } else {
                alerts = await this.simulateAlerts(severity);
            }
            
            this.displayAlerts(alerts);
            
        } catch (error) {
            console.error('Error cargando alertas:', error);
            this.showNotification('Error al cargar alertas', 'error');
        }
    }
    
    async simulateAlerts(severity) {
        const alerts = [
            {
                id: 'alert_001',
                type: 'flowering_event',
                severity: 'high',
                title: 'Floración masiva detectada en California',
                description: 'Floración inusualmente intensa de amapolas en el valle central de California. Los valores NDVI han aumentado un 35% por encima del promedio histórico.',
                location: { lat: 36.7378, lon: -119.7871 },
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                species: 'amapola',
                confidence: 0.92
            },
            {
                id: 'alert_002',
                type: 'early_flowering',
                severity: 'medium',
                title: 'Floración temprana en Europa',
                description: 'Los cerezos en Alemania están floreciendo 2 semanas antes de lo normal debido a temperaturas inusualmente cálidas en marzo.',
                location: { lat: 50.1109, lon: 8.6821 },
                timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
                species: 'cherry_blossom',
                confidence: 0.85
            },
            {
                id: 'alert_003',
                type: 'delayed_flowering',
                severity: 'low',
                title: 'Retraso en floración de almendros',
                description: 'La temporada de floración de almendros en España se ha retrasado debido a las bajas temperaturas de febrero.',
                location: { lat: 40.4168, lon: -3.7038 },
                timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
                species: 'almond',
                confidence: 0.78
            }
        ];
        
        const filteredAlerts = severity === 'all' ? 
            alerts : alerts.filter(alert => alert.severity === severity);
        
        return {
            alerts: filteredAlerts,
            count: filteredAlerts.length
        };
    }
    
    displayAlerts(alertsData) {
        const container = document.getElementById('alerts-container');
        if (!container) return;
        
        const alerts = alertsData.alerts || [];
        
        if (alerts.length === 0) {
            container.innerHTML = `
                <div class="no-alerts">
                    <i class="fas fa-check-circle"></i>
                    <h3>No hay alertas activas</h3>
                    <p>Todo parece estar funcionando normalmente.</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        alerts.forEach(alert => {
            const timeAgo = this.timeAgo(new Date(alert.timestamp));
            
            html += `
                <div class="alert-item ${alert.severity}-priority">
                    <div class="alert-header">
                        <div>
                            <div class="alert-title">${alert.title}</div>
                            <div class="alert-time">${timeAgo}</div>
                        </div>
                        <div class="alert-severity ${alert.severity}">${alert.severity}</div>
                    </div>
                    <div class="alert-description">${alert.description}</div>
                    <div class="alert-location">
                        <i class="fas fa-map-marker-alt"></i>
                        ${alert.location.lat.toFixed(2)}°, ${alert.location.lon.toFixed(2)}°
                        ${alert.species ? `• ${alert.species}` : ''}
                        • Confianza: ${(alert.confidence * 100).toFixed(0)}%
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // Actualizar contador en header
        document.getElementById('active-alerts').textContent = alerts.length;
    }
    
    toggleAutoRefresh(enabled) {
        if (enabled) {
            this.autoRefreshInterval = setInterval(() => {
                if (this.currentLocation && !this.analysisInProgress) {
                    this.performAnalysis();
                }
                this.refreshAlerts();
            }, 5 * 60 * 1000); // Cada 5 minutos
            
            this.showNotification('Auto-actualización activada', 'info');
        } else {
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
                this.autoRefreshInterval = null;
            }
            this.showNotification('Auto-actualización desactivada', 'info');
        }
    }
    
    async updateStats() {
        try {
            let stats;
            if (this.apiClient) {
                stats = await this.apiClient.getStatistics();
            } else {
                stats = {
                    total_events_detected: 15847,
                    active_alerts: 3
                };
            }
            
            document.getElementById('total-events').textContent = 
                stats.total_events_detected?.toLocaleString() || '-';
            document.getElementById('active-alerts').textContent = 
                stats.active_alerts || '-';
                
        } catch (error) {
            console.error('Error actualizando estadísticas:', error);
        }
    }
    
    showLoading(show, message = 'Analizando datos satelitales...') {
        const loadingElement = document.getElementById('loading-indicator');
        const loadingText = loadingElement?.querySelector('p');
        
        if (loadingElement) {
            if (show) {
                loadingElement.classList.remove('hidden');
                if (loadingText) loadingText.textContent = message;
            } else {
                loadingElement.classList.add('hidden');
            }
        }
        
        // Deshabilitar botón de análisis
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.disabled = show;
        }
    }
    
    showNotification(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="close-btn">&times;</button>
        `;
        
        // Agregar al DOM
        document.body.appendChild(notification);
        
        // Mostrar con animación
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
        
        // Botón de cerrar
        notification.querySelector('.close-btn').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    // Utilidades
    formatDate(date) {
        return date.toISOString().split('T')[0];
    }
    
    formatDisplayDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
    
    getDayOfYear(date) {
        const start = new Date(date.getFullYear(), 0, 0);
        const diff = date - start;
        return Math.floor(diff / (1000 * 60 * 60 * 24));
    }
    
    timeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return `hace ${diffInSeconds}s`;
        if (diffInSeconds < 3600) return `hace ${Math.floor(diffInSeconds / 60)}m`;
        if (diffInSeconds < 86400) return `hace ${Math.floor(diffInSeconds / 3600)}h`;
        return `hace ${Math.floor(diffInSeconds / 86400)}d`;
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Inicializar aplicación cuando se cargue el DOM
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FloraWatchApp();
});

// Estilos para notificaciones (agregar al CSS)
const notificationStyles = `
    .notification {
        position: fixed;
        top: 100px;
        right: 20px;
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        min-width: 300px;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        z-index: 10000;
        border-left: 4px solid #2196f3;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification.success {
        border-left-color: #4caf50;
        color: #2e7d32;
    }
    
    .notification.error {
        border-left-color: #f44336;
        color: #c62828;
    }
    
    .notification.warning {
        border-left-color: #ff9800;
        color: #e65100;
    }
    
    .notification.info {
        border-left-color: #2196f3;
        color: #1565c0;
    }
    
    .notification .close-btn {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0.7;
        margin-left: auto;
    }
    
    .notification .close-btn:hover {
        opacity: 1;
    }
    
    .no-alerts {
        text-align: center;
        padding: 3rem;
        color: #666;
    }
    
    .no-alerts i {
        font-size: 3rem;
        color: #4caf50;
        margin-bottom: 1rem;
    }
    
    .predictions-list {
        display: grid;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .prediction-item {
        background: var(--surface-variant);
        padding: 1rem;
        border-radius: var(--border-radius);
        display: grid;
        grid-template-columns: 120px 1fr;
        gap: 1rem;
        align-items: center;
    }
    
    .prediction-date {
        font-weight: 600;
        color: var(--primary-color);
    }
    
    .prediction-metrics {
        display: flex;
        gap: 1.5rem;
    }
    
    .prediction-metrics .metric {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .prediction-metrics .metric label {
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .prediction-metrics .metric .value {
        font-weight: 600;
        color: var(--on-surface);
    }
`;

// Agregar estilos al documento
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);