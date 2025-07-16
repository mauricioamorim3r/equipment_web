// Main Application Controller
class App {
    constructor() {
        this.currentSection = 'dashboard';
        this.sidebar = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSidebar();
        this.loadInitialData();
        this.showSection('dashboard');
    }

    setupEventListeners() {
        // Navigation
        document.addEventListener('click', (e) => {
            const navLink = e.target.closest('.nav-link');
            if (navLink) {
                e.preventDefault();
                const section = navLink.dataset.section;
                if (section) {
                    this.showSection(section);
                }
            }
        });

        // Mobile menu toggle
        const menuToggle = document.getElementById('menuToggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }

        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                this.toggleSidebarCollapse();
            });
        }

        // Global search
        const globalSearch = document.getElementById('globalSearch');
        if (globalSearch) {
            globalSearch.addEventListener('input', debounce((e) => {
                this.handleGlobalSearch(e.target.value);
            }, 300));
        }

        // Notification button
        const notificationBtn = document.getElementById('notificationBtn');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', () => {
                this.showNotifications();
            });
        }

        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Handle escape key for modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    setupSidebar() {
        this.sidebar = document.getElementById('sidebar');
        
        // Load sidebar state from localStorage
        const sidebarState = loadFromLocalStorage('sidebarState', 'expanded');
        if (sidebarState === 'collapsed') {
            this.sidebar.classList.add('collapsed');
        }

        // Auto-collapse on mobile
        if (window.innerWidth <= 1024) {
            this.sidebar.classList.remove('open');
        }
    }

    showSection(sectionName) {
        // Update current section
        this.currentSection = sectionName;

        // Hide all sections
        const sections = document.querySelectorAll('.section');
        sections.forEach(section => {
            section.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update navigation
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
        });

        const activeNavLink = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeNavLink) {
            activeNavLink.classList.add('active');
        }

        // Update page title
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) {
            pageTitle.textContent = this.getSectionTitle(sectionName);
        }

        // Load section data
        this.loadSectionData(sectionName);

        // Close sidebar on mobile after navigation
        if (window.innerWidth <= 1024) {
            this.sidebar.classList.remove('open');
        }

        // Update URL
        updateURLParams({ section: sectionName });
    }

    getSectionTitle(sectionName) {
        const titles = {
            dashboard: 'Dashboard',
            equipamentos: 'Equipamentos',
            'pontos-medicao': 'Pontos de Medição',
            certificados: 'Certificados',
            importacao: 'Importação/Exportação',
            configuracoes: 'Configurações'
        };
        return titles[sectionName] || 'Sistema';
    }

    async loadSectionData(sectionName) {
        try {
            switch (sectionName) {
                case 'dashboard':
                    if (window.Dashboard) {
                        await window.Dashboard.init();
                    }
                    break;
                case 'equipamentos':
                    if (window.Equipamentos) {
                        await window.Equipamentos.init();
                    }
                    break;
                case 'pontos-medicao':
                    if (window.PontosMedicao) {
                        await window.PontosMedicao.init();
                    }
                    break;
                case 'certificados':
                    if (window.Certificados) {
                        await window.Certificados.init();
                    }
                    break;
                case 'importacao':
                    if (window.Importacao) {
                        await window.Importacao.init();
                    }
                    break;
                case 'configuracoes':
                    if (window.Configuracoes) {
                        await window.Configuracoes.init();
                    }
                    break;
            }
        } catch (error) {
            handleError(error, `loading ${sectionName} section`);
        }
    }

    toggleSidebar() {
        if (this.sidebar) {
            this.sidebar.classList.toggle('open');
        }
    }

    toggleSidebarCollapse() {
        if (this.sidebar) {
            this.sidebar.classList.toggle('collapsed');
            
            // Save state to localStorage
            const isCollapsed = this.sidebar.classList.contains('collapsed');
            saveToLocalStorage('sidebarState', isCollapsed ? 'collapsed' : 'expanded');
        }
    }

    handleResize() {
        if (window.innerWidth <= 1024) {
            // Mobile view
            this.sidebar.classList.remove('collapsed');
            this.sidebar.classList.remove('open');
        } else {
            // Desktop view
            this.sidebar.classList.remove('open');
            
            // Restore collapsed state
            const sidebarState = loadFromLocalStorage('sidebarState', 'expanded');
            if (sidebarState === 'collapsed') {
                this.sidebar.classList.add('collapsed');
            }
        }
    }

    handleGlobalSearch(searchTerm) {
        // Implement global search across all sections
        console.log('Global search:', searchTerm);
        
        // For now, just trigger search in current section
        switch (this.currentSection) {
            case 'equipamentos':
                if (window.Equipamentos && window.Equipamentos.search) {
                    window.Equipamentos.search(searchTerm);
                }
                break;
            case 'pontos-medicao':
                if (window.PontosMedicao && window.PontosMedicao.search) {
                    window.PontosMedicao.search(searchTerm);
                }
                break;
            case 'certificados':
                if (window.Certificados && window.Certificados.search) {
                    window.Certificados.search(searchTerm);
                }
                break;
        }
    }

    async showNotifications() {
        try {
            // Get critical points and alerts
            const pontosCriticos = await DashboardAPI.getPontosCriticos(30);
            
            let notificationHtml = '<div class="notifications-dropdown">';
            notificationHtml += '<h4>Alertas de Calibração</h4>';
            
            if (pontosCriticos.resumo.total_criticos === 0) {
                notificationHtml += '<p>Nenhum alerta no momento</p>';
            } else {
                // Show vencidos
                if (pontosCriticos.pontos_vencidos.length > 0) {
                    notificationHtml += '<div class="notification-group">';
                    notificationHtml += '<h5>Vencidos</h5>';
                    pontosCriticos.pontos_vencidos.slice(0, 5).forEach(ponto => {
                        notificationHtml += `
                            <div class="notification-item error">
                                <strong>${ponto.tag_ponto_medicao}</strong>
                                <span>Vencido há ${Math.abs(ponto.dias_restantes)} dias</span>
                            </div>
                        `;
                    });
                    notificationHtml += '</div>';
                }
                
                // Show próximos
                if (pontosCriticos.pontos_proximos.length > 0) {
                    notificationHtml += '<div class="notification-group">';
                    notificationHtml += '<h5>Próximos do Vencimento</h5>';
                    pontosCriticos.pontos_proximos.slice(0, 5).forEach(ponto => {
                        notificationHtml += `
                            <div class="notification-item warning">
                                <strong>${ponto.tag_ponto_medicao}</strong>
                                <span>${ponto.dias_restantes} dias restantes</span>
                            </div>
                        `;
                    });
                    notificationHtml += '</div>';
                }
            }
            
            notificationHtml += '</div>';
            
            // Show in a temporary popup
            this.showTempPopup(notificationHtml);
            
        } catch (error) {
            handleError(error, 'loading notifications');
        }
    }

    showTempPopup(content) {
        // Remove existing popup
        const existingPopup = document.querySelector('.temp-popup');
        if (existingPopup) {
            existingPopup.remove();
        }

        // Create popup
        const popup = document.createElement('div');
        popup.className = 'temp-popup';
        popup.innerHTML = `
            <div class="temp-popup-content">
                ${content}
                <button class="temp-popup-close" onclick="this.closest('.temp-popup').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(popup);

        // Auto remove after 10 seconds
        setTimeout(() => {
            if (popup.parentNode) {
                popup.remove();
            }
        }, 10000);
    }

    closeAllModals() {
        const modals = document.querySelectorAll('.modal.active');
        modals.forEach(modal => {
            modal.classList.remove('active');
        });
    }

    async loadInitialData() {
        try {
            // Load configurations cache
            await getConfiguracoes();
            
            // Update notification badge
            await this.updateNotificationBadge();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async updateNotificationBadge() {
        try {
            const pontosCriticos = await DashboardAPI.getPontosCriticos(30);
            const badge = document.getElementById('notificationBadge');
            
            if (badge) {
                const totalAlertas = pontosCriticos.resumo.total_criticos;
                badge.textContent = totalAlertas;
                badge.style.display = totalAlertas > 0 ? 'block' : 'none';
            }
        } catch (error) {
            console.error('Error updating notification badge:', error);
        }
    }

    // Public methods for other modules
    refreshNotifications() {
        this.updateNotificationBadge();
    }

    getCurrentSection() {
        return this.currentSection;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    
    // Check for section in URL
    const urlParams = getURLParams();
    if (urlParams.section) {
        window.app.showSection(urlParams.section);
    }
});

// Add CSS for notifications and temp popup
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .temp-popup {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 5000;
        backdrop-filter: blur(4px);
    }

    .temp-popup-content {
        background-color: var(--bg-primary);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-xl);
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        position: relative;
        padding: var(--spacing-xl);
    }

    .temp-popup-close {
        position: absolute;
        top: var(--spacing-md);
        right: var(--spacing-md);
        background: none;
        border: none;
        color: var(--text-muted);
        cursor: pointer;
        padding: var(--spacing-sm);
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
    }

    .temp-popup-close:hover {
        background-color: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .notifications-dropdown h4 {
        margin-bottom: var(--spacing-lg);
        color: var(--text-primary);
        font-size: 1.25rem;
    }

    .notification-group {
        margin-bottom: var(--spacing-lg);
    }

    .notification-group h5 {
        margin-bottom: var(--spacing-md);
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 600;
    }

    .notification-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-md);
        border-radius: var(--radius-md);
        margin-bottom: var(--spacing-sm);
        border-left: 4px solid;
    }

    .notification-item.error {
        background-color: #fef2f2;
        border-left-color: var(--error-color);
    }

    .notification-item.warning {
        background-color: #fffbeb;
        border-left-color: var(--warning-color);
    }

    .notification-item strong {
        color: var(--text-primary);
    }

    .notification-item span {
        color: var(--text-secondary);
        font-size: 0.875rem;
    }
`;
document.head.appendChild(notificationStyles);

