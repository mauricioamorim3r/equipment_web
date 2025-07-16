// Dashboard Module
window.Dashboard = {
    charts: {},
    data: {},

    async init() {
        try {
            await this.loadData();
            this.renderStats();
            this.renderCharts();
            this.renderCriticalPoints();
        } catch (error) {
            handleError(error, 'initializing dashboard');
        }
    },

    async loadData() {
        try {
            // Load all dashboard data in parallel
            const [resumo, estatisticas, cronograma, pontosCriticos] = await Promise.all([
                DashboardAPI.getResumo(),
                DashboardAPI.getEstatisticasEquipamentos(),
                DashboardAPI.getCronogramaCalibracoes(),
                DashboardAPI.getPontosCriticos(30)
            ]);

            this.data = {
                resumo,
                estatisticas,
                cronograma,
                pontosCriticos
            };
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    },

    renderStats() {
        const { resumo } = this.data;
        
        // Update stat cards
        this.updateStatCard('totalEquipamentos', resumo.totais.equipamentos);
        this.updateStatCard('totalPontosMedicao', resumo.totais.pontos_medicao);
        this.updateStatCard('totalCertificados', resumo.totais.certificados);
        this.updateStatCard('totalAlertas', resumo.alertas_calibracao.total_alertas);
    },

    updateStatCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            // Animate number change
            this.animateNumber(element, parseInt(element.textContent) || 0, value);
        }
    },

    animateNumber(element, start, end, duration = 1000) {
        const startTime = performance.now();
        
        function updateNumber(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.round(start + (end - start) * easeOutQuart);
            
            element.textContent = current.toLocaleString('pt-BR');
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        }
        
        requestAnimationFrame(updateNumber);
    },

    renderCharts() {
        this.renderFabricantesChart();
        this.renderCalibracoesChart();
    },

    renderFabricantesChart() {
        const canvas = document.getElementById('fabricantesChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const { estatisticas } = this.data;

        // Destroy existing chart
        if (this.charts.fabricantes) {
            this.charts.fabricantes.destroy();
        }

        // Prepare data
        const fabricantesData = estatisticas.por_fabricante.slice(0, 8); // Top 8
        const labels = fabricantesData.map(item => item.nome);
        const data = fabricantesData.map(item => item.count);
        const colors = this.generateColors(fabricantesData.length);

        this.charts.fabricantes = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    },

    renderCalibracoesChart() {
        const canvas = document.getElementById('calibracoesChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const { cronograma } = this.data;

        // Destroy existing chart
        if (this.charts.calibracoes) {
            this.charts.calibracoes.destroy();
        }

        // Prepare data
        const labels = cronograma.cronograma.map(item => item.mes);
        const data = cronograma.cronograma.map(item => item.calibracoes);

        this.charts.calibracoes = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Calibrações Programadas',
                    data: data,
                    backgroundColor: 'rgba(37, 99, 235, 0.8)',
                    borderColor: 'rgba(37, 99, 235, 1)',
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `${context[0].label} ${cronograma.ano}`;
                            },
                            label: function(context) {
                                return `Calibrações: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    },

    renderCriticalPoints() {
        const tbody = document.getElementById('pontosCriticosBody');
        if (!tbody) return;

        clearElement(tbody);

        const { pontosCriticos } = this.data;
        const allPoints = [
            ...pontosCriticos.pontos_vencidos,
            ...pontosCriticos.pontos_proximos
        ];

        // Sort by days remaining (most critical first)
        allPoints.sort((a, b) => (a.dias_restantes || 0) - (b.dias_restantes || 0));

        // Show top 10 most critical
        const topCritical = allPoints.slice(0, 10);

        if (topCritical.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="6" style="text-align: center; color: var(--text-muted); padding: var(--spacing-xl);">
                    <i class="fas fa-check-circle" style="font-size: 2rem; margin-bottom: var(--spacing-md); color: var(--success-color);"></i>
                    <br>
                    Nenhum ponto crítico encontrado
                </td>
            `;
            tbody.appendChild(row);
            return;
        }

        topCritical.forEach(ponto => {
            const row = document.createElement('tr');
            
            const statusInfo = this.getCalibrationStatus(ponto.dias_restantes);
            const diasText = this.formatDaysRemaining(ponto.dias_restantes);
            
            row.innerHTML = `
                <td>
                    <strong>${ponto.tag_ponto_medicao}</strong>
                </td>
                <td>${truncateText(ponto.nome_ponto_medicao, 30)}</td>
                <td>${ponto.polo || '-'}</td>
                <td>${formatDate(ponto.data_proxima_calibracao)}</td>
                <td>${createStatusBadge(statusInfo)}</td>
                <td>
                    <span class="days-remaining ${statusInfo.class}">
                        ${diasText}
                    </span>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    },

    getCalibrationStatus(diasRestantes) {
        if (diasRestantes === null || diasRestantes === undefined) {
            return { status: 'sem-data', text: 'Sem Data', class: 'sem-data' };
        }
        
        if (diasRestantes < 0) {
            return { status: 'vencido', text: 'Vencido', class: 'vencido' };
        } else if (diasRestantes <= 30) {
            return { status: 'proximo-vencimento', text: 'Próximo Vencimento', class: 'proximo-vencimento' };
        } else {
            return { status: 'vigente', text: 'Vigente', class: 'vigente' };
        }
    },

    formatDaysRemaining(dias) {
        if (dias === null || dias === undefined) {
            return '-';
        }
        
        if (dias < 0) {
            return `${Math.abs(dias)} dias atrás`;
        } else if (dias === 0) {
            return 'Hoje';
        } else if (dias === 1) {
            return '1 dia';
        } else {
            return `${dias} dias`;
        }
    },

    generateColors(count) {
        const baseColors = [
            '#2563eb', '#dc2626', '#059669', '#d97706',
            '#7c3aed', '#db2777', '#0891b2', '#65a30d'
        ];
        
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        
        return colors;
    },

    async refresh() {
        try {
            await this.loadData();
            this.renderStats();
            this.renderCharts();
            this.renderCriticalPoints();
            
            // Update notification badge
            if (window.app) {
                window.app.refreshNotifications();
            }
            
            showToast('Dashboard atualizado com sucesso', 'success');
        } catch (error) {
            handleError(error, 'refreshing dashboard');
        }
    }
};

// Global function for refresh button
window.refreshCriticalPoints = async function() {
    try {
        await window.Dashboard.refresh();
    } catch (error) {
        handleError(error, 'refreshing critical points');
    }
};

// Auto-refresh dashboard every 5 minutes
setInterval(() => {
    if (window.app && window.app.getCurrentSection() === 'dashboard') {
        window.Dashboard.refresh();
    }
}, 5 * 60 * 1000);

// Add custom styles for dashboard
const dashboardStyles = document.createElement('style');
dashboardStyles.textContent = `
    .days-remaining {
        font-weight: 600;
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-sm);
        font-size: 0.75rem;
    }

    .days-remaining.vencido {
        background-color: #fecaca;
        color: #991b1b;
    }

    .days-remaining.proximo-vencimento {
        background-color: #fef3c7;
        color: #92400e;
    }

    .days-remaining.vigente {
        background-color: #dcfce7;
        color: #166534;
    }

    .days-remaining.sem-data {
        background-color: var(--bg-tertiary);
        color: var(--text-muted);
    }

    #fabricantesChart,
    #calibracoesChart {
        height: 300px !important;
    }

    .widget-content canvas {
        max-height: 300px;
    }

    .stat-card {
        cursor: pointer;
        transition: all var(--transition-fast);
    }

    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }

    .stat-card.alert:hover {
        box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.25);
    }

    @media (max-width: 768px) {
        #fabricantesChart,
        #calibracoesChart {
            height: 250px !important;
        }
        
        .widget-content canvas {
            max-height: 250px;
        }
    }
`;
document.head.appendChild(dashboardStyles);

