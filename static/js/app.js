// JavaScript for the 3D City Generator web interface

class CityGeneratorApp {
    constructor() {
        this.currentCityData = null;
        this.isGenerating = false;
        
        this.initializeEventListeners();
        this.updatePercentageDisplay();
        this.loadDefaultConfig();
    }
    
    initializeEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Zone distribution sliders
        document.querySelectorAll('.zone-control input[type="range"]').forEach(slider => {
            slider.addEventListener('input', () => this.updatePercentageDisplay());
        });
        
        // Main action buttons
        document.getElementById('generate-btn').addEventListener('click', () => this.generateCity());
        document.getElementById('export-json-btn').addEventListener('click', () => this.exportCity('json'));
        document.getElementById('export-obj-btn').addEventListener('click', () => this.exportCity('obj'));
        
        // Auto-resize handler
        window.addEventListener('resize', () => this.handleResize());
    }
    
    async loadDefaultConfig() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            
            // Populate form with default values
            document.getElementById('width').value = config.width;
            document.getElementById('height').value = config.height;
            document.getElementById('main_road_width').value = config.main_road_width;
            document.getElementById('secondary_road_width').value = config.secondary_road_width;
            document.getElementById('local_road_width').value = config.local_road_width;
            
            // Set zone distribution sliders
            Object.entries(config.zone_distribution).forEach(([zoneType, percentage]) => {
                const slider = document.getElementById(zoneType);
                if (slider) {
                    slider.value = percentage;
                }
            });
            
            this.updatePercentageDisplay();
            
        } catch (error) {
            console.error('Error loading default config:', error);
            this.showError('Erreur lors du chargement de la configuration par défaut');
        }
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
        
        // Special handling for 3D view
        if (tabName === '3d-view' && this.currentCityData) {
            this.render3DView();
        }
    }
    
    updatePercentageDisplay() {
        const zones = ['residential', 'commercial', 'business', 'leisure', 'parks', 'industrial'];
        let total = 0;
        
        zones.forEach(zone => {
            const slider = document.getElementById(zone);
            const valueSpan = document.getElementById(`${zone}-value`);
            if (slider && valueSpan) {
                const value = parseInt(slider.value);
                valueSpan.textContent = `${value}%`;
                total += value;
            }
        });
        
        const totalSpan = document.getElementById('total-percentage');
        if (totalSpan) {
            totalSpan.textContent = `${total}%`;
            totalSpan.style.color = total === 100 ? '#38a169' : '#e53e3e';
        }
    }
    
    async generateCity() {
        if (this.isGenerating) return;
        
        this.isGenerating = true;
        this.showLoading(true);
        
        try {
            const config = this.getConfigFromForm();
            
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Ville générée avec succès!');
                await this.loadCityData();
                await this.updatePreview();
                this.updateStats(result.stats);
                this.enableExportButtons(true);
            } else {
                this.showError(result.message);
            }
            
        } catch (error) {
            console.error('Error generating city:', error);
            this.showError('Erreur lors de la génération de la ville');
        } finally {
            this.isGenerating = false;
            this.showLoading(false);
        }
    }
    
    getConfigFromForm() {
        const zoneDistribution = {};
        ['residential', 'commercial', 'business', 'leisure', 'parks', 'industrial'].forEach(zone => {
            const slider = document.getElementById(zone);
            if (slider) {
                zoneDistribution[zone] = parseInt(slider.value);
            }
        });
        
        return {
            width: parseInt(document.getElementById('width').value),
            height: parseInt(document.getElementById('height').value),
            main_road_width: parseFloat(document.getElementById('main_road_width').value),
            secondary_road_width: parseFloat(document.getElementById('secondary_road_width').value),
            local_road_width: parseFloat(document.getElementById('local_road_width').value),
            zone_distribution: zoneDistribution
        };
    }
    
    async loadCityData() {
        try {
            const response = await fetch('/api/city-data');
            if (response.ok) {
                this.currentCityData = await response.json();
                console.log('City data loaded:', this.currentCityData);
            } else {
                throw new Error('Failed to load city data');
            }
        } catch (error) {
            console.error('Error loading city data:', error);
            this.showError('Erreur lors du chargement des données de la ville');
        }
    }
    
    async updatePreview() {
        try {
            const response = await fetch('/api/preview');
            const result = await response.json();
            
            if (result.image) {
                const previewImg = document.getElementById('city-preview');
                const placeholder = document.querySelector('#preview-container .placeholder');
                
                previewImg.src = result.image;
                previewImg.style.display = 'block';
                placeholder.style.display = 'none';
            } else {
                this.showError(result.error || 'Erreur lors de la génération de l\'aperçu');
            }
            
        } catch (error) {
            console.error('Error updating preview:', error);
            this.showError('Erreur lors de la mise à jour de l\'aperçu');
        }
    }
    
    updateStats(stats) {
        const statsContainer = document.getElementById('stats-container');
        const placeholder = statsContainer.querySelector('.placeholder');
        
        if (placeholder) {
            placeholder.style.display = 'none';
        }
        
        // Create stats HTML
        const statsHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>🏙️ Zones Totales</h4>
                    <div class="stat-value">${stats.total_zones}</div>
                </div>
                <div class="stat-card">
                    <h4>🏢 Bâtiments Totaux</h4>
                    <div class="stat-value">${stats.total_buildings}</div>
                </div>
                <div class="stat-card">
                    <h4>🛣️ Routes Totales</h4>
                    <div class="stat-value">${stats.total_roads}</div>
                </div>
                <div class="stat-card">
                    <h4>⚡ Intersections</h4>
                    <div class="stat-value">${stats.total_intersections}</div>
                </div>
                <div class="stat-card">
                    <h4>📏 Taille de la Ville</h4>
                    <div class="stat-value">${stats.city_size}</div>
                </div>
            </div>
            
            <div class="zone-stats">
                <h4>📊 Détails par Zone</h4>
                ${Object.entries(stats.zone_stats).map(([zoneType, data]) => `
                    <div class="zone-stat-item">
                        <span>${this.getZoneIcon(zoneType)} ${this.getZoneName(zoneType)}</span>
                        <span>${data.zones} zones, ${data.buildings} bâtiments</span>
                    </div>
                `).join('')}
            </div>
        `;
        
        statsContainer.innerHTML = statsHTML;
    }
    
    getZoneIcon(zoneType) {
        const icons = {
            'residential': '🏠',
            'commercial': '🏪',
            'business': '🏢',
            'leisure': '🎪',
            'parks': '🌳',
            'industrial': '🏭'
        };
        return icons[zoneType] || '🏙️';
    }
    
    getZoneName(zoneType) {
        const names = {
            'residential': 'Résidentiel',
            'commercial': 'Commercial',
            'business': 'Business',
            'leisure': 'Loisirs',
            'parks': 'Parcs',
            'industrial': 'Industriel'
        };
        return names[zoneType] || zoneType;
    }
    
    async exportCity(format) {
        try {
            const response = await fetch(`/api/export/${format}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = format === 'json' ? 'city_data.json' : 'city_model.obj';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showSuccess(`Export ${format.toUpperCase()} réussi!`);
            } else {
                const error = await response.json();
                this.showError(error.error || `Erreur lors de l'export ${format.toUpperCase()}`);
            }
            
        } catch (error) {
            console.error('Error exporting city:', error);
            this.showError(`Erreur lors de l'export ${format.toUpperCase()}`);
        }
    }
    
    render3DView() {
        // Placeholder for 3D rendering
        // This would use Three.js to create an interactive 3D view
        console.log('3D view rendering not yet implemented');
    }
    
    enableExportButtons(enabled) {
        document.getElementById('export-json-btn').disabled = !enabled;
        document.getElementById('export-obj-btn').disabled = !enabled;
    }
    
    showLoading(show) {
        const loadingElement = document.getElementById('loading');
        loadingElement.style.display = show ? 'flex' : 'none';
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1001;
            animation: slideIn 0.3s ease;
            max-width: 400px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        `;
        
        if (type === 'success') {
            notification.style.background = '#38a169';
        } else {
            notification.style.background = '#e53e3e';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }
        }, 5000);
        
        // Add CSS animations if not already present
        if (!document.querySelector('#notification-animations')) {
            const style = document.createElement('style');
            style.id = 'notification-animations';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    handleResize() {
        // Handle responsive behavior
        const mainContent = document.querySelector('.main-content');
        const controlsPanel = document.querySelector('.controls-panel');
        
        if (window.innerWidth <= 1024) {
            mainContent.style.gridTemplateColumns = '1fr';
        } else {
            mainContent.style.gridTemplateColumns = '350px 1fr';
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new CityGeneratorApp();
    console.log('City Generator App initialized');
});