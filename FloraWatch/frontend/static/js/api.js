/**
 * FloraWatch - Cliente API
 * Maneja las comunicaciones con el backend de FloraWatch
 */

class APIClient {
    constructor() {
        this.baseURL = window.location.origin;
        this.endpoints = {
            health: '/api/health',
            floweringEvents: '/api/flowering-events',
            predictions: '/api/predictions',
            alerts: '/api/alerts',
            statistics: '/api/statistics',
            regions: '/api/regions',
            species: '/api/species'
        };
        
        this.init();
    }
    
    init() {
        console.log('🔌 Cliente API inicializado');
        this.checkHealth();
    }
    
    async checkHealth() {
        try {
            const response = await this.get(this.endpoints.health);
            console.log('✅ API Backend disponible:', response);
            return response;
        } catch (error) {
            console.warn('⚠️ API Backend no disponible, usando datos simulados');
            return null;
        }
    }
    
    async get(endpoint, params = {}) {
        const url = new URL(endpoint, this.baseURL);
        
        // Agregar parámetros de consulta
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                url.searchParams.append(key, params[key]);
            }
        });
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    async post(endpoint, data = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    async getFloweringEvents(params) {
        try {
            return await this.get(this.endpoints.floweringEvents, params);
        } catch (error) {
            console.error('Error obteniendo eventos de floración:', error);
            throw error;
        }
    }
    
    async getPredictions(params) {
        try {
            return await this.get(this.endpoints.predictions, params);
        } catch (error) {
            console.error('Error obteniendo predicciones:', error);
            throw error;
        }
    }
    
    async getAlerts(params = {}) {
        try {
            return await this.get(this.endpoints.alerts, params);
        } catch (error) {
            console.error('Error obteniendo alertas:', error);
            throw error;
        }
    }
    
    async getStatistics() {
        try {
            return await this.get(this.endpoints.statistics);
        } catch (error) {
            console.error('Error obteniendo estadísticas:', error);
            throw error;
        }
    }
    
    async getRegions() {
        try {
            return await this.get(this.endpoints.regions);
        } catch (error) {
            console.error('Error obteniendo regiones:', error);
            return { regions: [] };
        }
    }
    
    async getSpecies() {
        try {
            return await this.get(this.endpoints.species);
        } catch (error) {
            console.error('Error obteniendo especies:', error);
            return { species: [] };
        }
    }
}

// Inicializar cliente API
document.addEventListener('DOMContentLoaded', () => {
    if (window.app) {
        window.app.apiClient = new APIClient();
    } else {
        setTimeout(() => {
            if (window.app) {
                window.app.apiClient = new APIClient();
            }
        }, 100);
    }
});