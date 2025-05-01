document.addEventListener('DOMContentLoaded', function() {
    // 1. Mejorar interactividad de gráficos Plotly
    enhancePlotlyCharts();
    
    // 2. Configurar botones de descarga
    setupDownloadButtons();
    
    // 3. Efectos hover para tarjetas
    setupCardHoverEffects();
    
    // 4. Tooltips para elementos importantes
    setupTooltips();
    
    // 5. Control de tamaño de gráficos
    setupGraphResizing();
    
    // 6. Configurar filtros interactivos
    setupGraphFilters();
});

// ==================== Funciones principales ====================

function enhancePlotlyCharts() {
    // Añadir funcionalidad de hover mejorado
    document.querySelectorAll('.js-plotly-plot').forEach(plot => {
        plot.on('plotly_hover', function(data) {
            const point = data.points[0];
            console.log('Punto seleccionado:', point);
            
            // Puedes añadir aquí lógica para mostrar tooltips personalizados
        });
        
        plot.on('plotly_click', function(data) {
            const point = data.points[0];
            console.log('Punto clickeado:', point);
            
            // Puedes añadir aquí lógica para interactuar con los puntos
        });
    });
}

function setupDownloadButtons() {
    // Añadir botones de descarga a cada gráfico
    document.querySelectorAll('.plot-container').forEach(container => {
        // Verificar si ya tiene un botón de descarga
        if (container.querySelector('.download-btn')) return;
        
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'btn btn-sm btn-outline-secondary download-btn';
        downloadBtn.innerHTML = '<i class="fas fa-download me-1"></i> Descargar';
        
        downloadBtn.addEventListener('click', function() {
            const plot = container.querySelector('.js-plotly-plot');
            if (plot) {
                Plotly.downloadImage(plot, {
                    format: 'png',
                    width: 1000,
                    height: 600,
                    filename: 'grafico_marketing'
                });
            } else {
                // Para gráficos matplotlib convertidos a imagen
                const img = container.querySelector('img');
                if (img) {
                    const link = document.createElement('a');
                    link.href = img.src;
                    link.download = 'grafico_marketing.png';
                    link.click();
                }
            }
        });
        
        // Posicionar el botón
        container.style.position = 'relative';
        downloadBtn.style.position = 'absolute';
        downloadBtn.style.top = '15px';
        downloadBtn.style.right = '15px';
        downloadBtn.style.zIndex = '1000';
        
        container.appendChild(downloadBtn);
    });
}

function setupCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}

function setupTooltips() {
    // Tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Tooltips personalizados para gráficos
    document.querySelectorAll('.graph-info-icon').forEach(icon => {
        icon.addEventListener('mouseover', function() {
            const tooltipText = this.dataset.tooltip;
            if (!tooltipText) return;
            
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = tooltipText;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = `${rect.left + window.scrollX}px`;
            tooltip.style.top = `${rect.top + window.scrollY - 40}px`;
            
            this.tooltipElement = tooltip;
        });
        
        icon.addEventListener('mouseout', function() {
            if (this.tooltipElement) {
                this.tooltipElement.remove();
            }
        });
    });
}

function setupGraphResizing() {
    document.querySelectorAll('.resize-graph').forEach(btn => {
        btn.addEventListener('click', function() {
            const graphContainer = this.closest('.graph-container');
            const plot = graphContainer.querySelector('.js-plotly-plot');
            
            if (plot) {
                const currentWidth = plot.offsetWidth;
                const newWidth = currentWidth === 800 ? 1200 : 800;
                
                Plotly.relayout(plot, {
                    width: newWidth
                });
                
                this.innerHTML = newWidth === 800 ? 
                    '<i class="fas fa-expand me-1"></i> Expandir' : 
                    '<i class="fas fa-compress me-1"></i> Reducir';
            }
        });
    });
}

function setupGraphFilters() {
    document.querySelectorAll('.graph-filter').forEach(filter => {
        filter.addEventListener('change', function() {
            const graphId = this.dataset.graphId;
            const filterValue = this.value;
            
            console.log(`Filtrar gráfico ${graphId} por ${filterValue}`);
            // Aquí iría la lógica para actualizar los gráficos según los filtros
            // Necesitarías implementar llamadas AJAX o actualizaciones directas
        });
    });
}

// ==================== Funciones auxiliares ====================

function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

// Hacer funciones accesibles desde la consola para debugging
window.app = {
    enhancePlotlyCharts,
    setupDownloadButtons,
    setupCardHoverEffects,
    setupTooltips,
    setupGraphResizing,
    setupGraphFilters
};