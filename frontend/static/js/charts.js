/**
 * FloraWatch - Gestor de Gráficos
 * Maneja la visualización de datos en gráficos interactivos
 */

class ChartManager {
    constructor() {
        this.charts = {};
        this.currentData = null;
        
        this.init();
    }
    
    init() {
        console.log('📊 Gestor de gráficos inicializado');
    }
    
    updateCharts(data) {
        this.currentData = data;
        
        if (data.time_series) {
            this.createNDVIChart(data.time_series);
        }
        
        if (data.events) {
            this.createEventsChart(data.events);
        }
    }
    
    createNDVIChart(timeSeries) {
        const ctx = document.getElementById('ndvi-chart');
        if (!ctx) return;
        
        // Destruir gráfico anterior si existe
        if (this.charts.ndvi) {
            this.charts.ndvi.destroy();
        }
        
        const dates = timeSeries.dates.map(date => new Date(date));
        const values = timeSeries.values;
        
        this.charts.ndvi = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'NDVI',
                    data: values,
                    borderColor: '#4caf50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM YYYY'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Fecha'
                        }
                    },
                    y: {
                        min: 0,
                        max: 1,
                        title: {
                            display: true,
                            text: 'Valor NDVI'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `NDVI: ${context.parsed.y.toFixed(3)}`;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
    
    createEventsChart(events) {
        const ctx = document.getElementById('events-chart');
        if (!ctx) return;
        
        // Destruir gráfico anterior si existe
        if (this.charts.events) {
            this.charts.events.destroy();
        }
        
        // Procesar eventos para el gráfico
        const eventData = this.processEventsForChart(events);
        
        this.charts.events = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: eventData.labels,
                datasets: [{
                    label: 'Intensidad de Floración',
                    data: eventData.intensities,
                    backgroundColor: eventData.colors,
                    borderColor: eventData.colors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Eventos de Floración'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Intensidad'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `Evento ${context[0].dataIndex + 1}`;
                            },
                            label: function(context) {
                                const event = events[context.dataIndex];
                                return [
                                    `Intensidad: ${context.parsed.y.toFixed(3)}`,
                                    `Período: ${event.start_date} - ${event.end_date}`,
                                    `Duración: ${event.duration_days} días`,
                                    `Confianza: ${(event.confidence * 100).toFixed(0)}%`
                                ];
                            }
                        }
                    }
                }
            }
        });
    }
    
    processEventsForChart(events) {
        const labels = events.map((event, index) => `Evento ${index + 1}`);
        const intensities = events.map(event => event.intensity || 0);
        
        // Colores basados en la intensidad
        const colors = intensities.map(intensity => {
            if (intensity > 0.15) return 'rgba(233, 30, 99, 0.7)'; // Rosa fuerte
            if (intensity > 0.10) return 'rgba(255, 152, 0, 0.7)'; // Naranja
            return 'rgba(76, 175, 80, 0.7)'; // Verde
        });
        
        return { labels, intensities, colors };
    }
    
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Inicializar gestor de gráficos
document.addEventListener('DOMContentLoaded', () => {
    if (window.app) {
        window.app.chartManager = new ChartManager();
    } else {
        setTimeout(() => {
            if (window.app) {
                window.app.chartManager = new ChartManager();
            }
        }, 100);
    }
});