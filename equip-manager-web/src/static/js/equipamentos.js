// Equipamentos Module
window.Equipamentos = {
    data: [],
    filteredData: [],
    currentPage: 1,
    itemsPerPage: 20,
    totalPages: 1,
    filters: {
        search: '',
        fabricante: '',
        tipo: ''
    },
    configuracoes: null,

    async init() {
        try {
            await this.loadConfiguracoes();
            this.setupEventListeners();
            this.setupFilters();
            await this.loadData();
            this.render();
        } catch (error) {
            handleError(error, 'initializing equipamentos');
        }
    },

    async loadConfiguracoes() {
        this.configuracoes = await getConfiguracoes();
        this.populateSelectOptions();
    },

    populateSelectOptions() {
        // Populate fabricante filter
        const fabricanteFilter = document.getElementById('fabricanteFilter');
        if (fabricanteFilter) {
            clearElement(fabricanteFilter);
            fabricanteFilter.innerHTML = '<option value="">Todos os Fabricantes</option>';
            this.configuracoes.fabricantes.forEach(fabricante => {
                const option = document.createElement('option');
                option.value = fabricante.id;
                option.textContent = fabricante.nome;
                fabricanteFilter.appendChild(option);
            });
        }

        // Populate tipo filter
        const tipoFilter = document.getElementById('tipoEquipamentoFilter');
        if (tipoFilter) {
            clearElement(tipoFilter);
            tipoFilter.innerHTML = '<option value="">Todos os Tipos</option>';
            this.configuracoes.tipos_equipamento.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id;
                option.textContent = tipo.nome;
                tipoFilter.appendChild(option);
            });
        }

        // Populate modal selects
        this.populateModalSelects();
    },

    populateModalSelects() {
        // Fabricante select in modal
        const fabricanteSelect = document.getElementById('fabricanteSelect');
        if (fabricanteSelect) {
            clearElement(fabricanteSelect);
            fabricanteSelect.innerHTML = '<option value="">Selecione...</option>';
            this.configuracoes.fabricantes.forEach(fabricante => {
                const option = document.createElement('option');
                option.value = fabricante.id;
                option.textContent = fabricante.nome;
                fabricanteSelect.appendChild(option);
            });
        }

        // Tipo select in modal
        const tipoSelect = document.getElementById('tipoEquipamentoSelect');
        if (tipoSelect) {
            clearElement(tipoSelect);
            tipoSelect.innerHTML = '<option value="">Selecione...</option>';
            this.configuracoes.tipos_equipamento.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo.id;
                option.textContent = tipo.nome;
                tipoSelect.appendChild(option);
            });
        }

        // Unidade select in modal
        const unidadeSelect = document.getElementById('unidadeSelect');
        if (unidadeSelect) {
            clearElement(unidadeSelect);
            unidadeSelect.innerHTML = '<option value="">Selecione...</option>';
            this.configuracoes.unidades.forEach(unidade => {
                const option = document.createElement('option');
                option.value = unidade.id;
                option.textContent = unidade.nome;
                unidadeSelect.appendChild(option);
            });
        }
    },

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('equipamentosSearch');
        if (searchInput) {
            searchInput.addEventListener('input', debounce((e) => {
                this.filters.search = e.target.value;
                this.applyFilters();
            }, 300));
        }

        // Filter selects
        const fabricanteFilter = document.getElementById('fabricanteFilter');
        if (fabricanteFilter) {
            fabricanteFilter.addEventListener('change', (e) => {
                this.filters.fabricante = e.target.value;
                this.applyFilters();
            });
        }

        const tipoFilter = document.getElementById('tipoEquipamentoFilter');
        if (tipoFilter) {
            tipoFilter.addEventListener('change', (e) => {
                this.filters.tipo = e.target.value;
                this.applyFilters();
            });
        }

        // Form submission
        const form = document.getElementById('equipamentoForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit();
            });
        }
    },

    setupFilters() {
        // Load filters from URL or localStorage
        const urlParams = getURLParams();
        this.filters = {
            search: urlParams.search || '',
            fabricante: urlParams.fabricante || '',
            tipo: urlParams.tipo || ''
        };

        // Apply filters to UI
        this.updateFilterUI();
    },

    updateFilterUI() {
        const searchInput = document.getElementById('equipamentosSearch');
        if (searchInput) searchInput.value = this.filters.search;

        const fabricanteFilter = document.getElementById('fabricanteFilter');
        if (fabricanteFilter) fabricanteFilter.value = this.filters.fabricante;

        const tipoFilter = document.getElementById('tipoEquipamentoFilter');
        if (tipoFilter) tipoFilter.value = this.filters.tipo;
    },

    async loadData() {
        try {
            const params = {
                page: this.currentPage,
                per_page: this.itemsPerPage,
                search: this.filters.search,
                fabricante_id: this.filters.fabricante,
                tipo_equipamento_id: this.filters.tipo
            };

            // Remove empty params
            Object.keys(params).forEach(key => {
                if (!params[key]) delete params[key];
            });

            const response = await EquipamentosAPI.listar(params);
            
            this.data = response.equipamentos || [];
            this.totalPages = response.pages || 1;
            this.currentPage = response.current_page || 1;
            
        } catch (error) {
            console.error('Error loading equipamentos:', error);
            this.data = [];
            this.totalPages = 1;
        }
    },

    applyFilters() {
        this.currentPage = 1;
        this.loadData().then(() => {
            this.render();
            this.updateURL();
        });
    },

    updateURL() {
        const params = {};
        if (this.filters.search) params.search = this.filters.search;
        if (this.filters.fabricante) params.fabricante = this.filters.fabricante;
        if (this.filters.tipo) params.tipo = this.filters.tipo;
        if (this.currentPage > 1) params.page = this.currentPage;
        
        updateURLParams(params);
    },

    render() {
        this.renderTable();
        this.renderPagination();
    },

    renderTable() {
        const tbody = document.getElementById('equipamentosBody');
        if (!tbody) return;

        clearElement(tbody);

        if (this.data.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="6" style="text-align: center; padding: var(--spacing-xl); color: var(--text-muted);">
                    <i class="fas fa-search" style="font-size: 2rem; margin-bottom: var(--spacing-md);"></i>
                    <br>
                    Nenhum equipamento encontrado
                </td>
            `;
            tbody.appendChild(row);
            return;
        }

        this.data.forEach(equipamento => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <strong>${equipamento.numero_serie}</strong>
                </td>
                <td>${equipamento.tag_equipamento || '-'}</td>
                <td>${truncateText(equipamento.nome_equipamento, 40)}</td>
                <td>${equipamento.fabricante || '-'}</td>
                <td>${equipamento.tipo_equipamento || '-'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline" onclick="Equipamentos.viewEquipamento('${equipamento.numero_serie}')" title="Visualizar">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="Equipamentos.editEquipamento('${equipamento.numero_serie}')" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-error" onclick="Equipamentos.deleteEquipamento('${equipamento.numero_serie}')" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    },

    renderPagination() {
        const container = document.getElementById('equipamentosPagination');
        createPagination(container, this.currentPage, this.totalPages, (page) => {
            this.currentPage = page;
            this.loadData().then(() => {
                this.render();
                this.updateURL();
            });
        });
    },

    async viewEquipamento(numeroSerie) {
        try {
            const equipamento = await EquipamentosAPI.obter(numeroSerie);
            this.showEquipamentoDetails(equipamento);
        } catch (error) {
            handleError(error, 'loading equipamento details');
        }
    },

    showEquipamentoDetails(equipamento) {
        const detailsHtml = `
            <div class="equipamento-details">
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>Número de Série:</label>
                        <span>${equipamento.numero_serie}</span>
                    </div>
                    <div class="detail-item">
                        <label>TAG:</label>
                        <span>${equipamento.tag_equipamento || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Nome:</label>
                        <span>${equipamento.nome_equipamento}</span>
                    </div>
                    <div class="detail-item">
                        <label>Fabricante:</label>
                        <span>${equipamento.fabricante || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Tipo:</label>
                        <span>${equipamento.tipo_equipamento || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Modelo:</label>
                        <span>${equipamento.modelo || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Unidade:</label>
                        <span>${equipamento.unidade || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Resolução:</label>
                        <span>${formatNumber(equipamento.resolucao) || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Faixa Mínima:</label>
                        <span>${formatNumber(equipamento.faixa_minima_equipamento) || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Faixa Máxima:</label>
                        <span>${formatNumber(equipamento.faixa_maxima_equipamento) || '-'}</span>
                    </div>
                </div>
            </div>
        `;

        if (window.app) {
            window.app.showTempPopup(detailsHtml);
        }
    },

    editEquipamento(numeroSerie) {
        this.openModal('edit', numeroSerie);
    },

    async deleteEquipamento(numeroSerie) {
        if (!confirm('Tem certeza que deseja excluir este equipamento?')) {
            return;
        }

        try {
            await EquipamentosAPI.deletar(numeroSerie);
            showToast('Equipamento excluído com sucesso', 'success');
            await this.loadData();
            this.render();
        } catch (error) {
            handleError(error, 'deleting equipamento');
        }
    },

    async openModal(mode = 'create', numeroSerie = null) {
        const modal = document.getElementById('equipamentoModal');
        const title = document.getElementById('equipamentoModalTitle');
        const form = document.getElementById('equipamentoForm');

        if (!modal || !form) return;

        // Set modal title
        if (title) {
            title.textContent = mode === 'create' ? 'Novo Equipamento' : 'Editar Equipamento';
        }

        // Clear form
        clearForm(form);

        // Load data for edit mode
        if (mode === 'edit' && numeroSerie) {
            try {
                const equipamento = await EquipamentosAPI.obter(numeroSerie);
                setFormData(form, equipamento);
                
                // Disable numero_serie field in edit mode
                const numeroSerieField = form.elements.numero_serie;
                if (numeroSerieField) {
                    numeroSerieField.readOnly = true;
                }
            } catch (error) {
                handleError(error, 'loading equipamento for edit');
                return;
            }
        } else {
            // Enable numero_serie field in create mode
            const numeroSerieField = form.elements.numero_serie;
            if (numeroSerieField) {
                numeroSerieField.readOnly = false;
            }
        }

        // Store mode and id
        form.dataset.mode = mode;
        form.dataset.numeroSerie = numeroSerie || '';

        // Show modal
        modal.classList.add('active');
    },

    closeModal() {
        const modal = document.getElementById('equipamentoModal');
        if (modal) {
            modal.classList.remove('active');
        }
    },

    async handleFormSubmit() {
        const form = document.getElementById('equipamentoForm');
        if (!form) return;

        const mode = form.dataset.mode;
        const numeroSerie = form.dataset.numeroSerie;

        // Validate form
        const validation = validateForm(form, {
            numero_serie: {
                required: true,
                requiredMessage: 'Número de série é obrigatório'
            },
            nome_equipamento: {
                required: true,
                requiredMessage: 'Nome do equipamento é obrigatório'
            }
        });

        if (!validation.isValid) {
            showToast('Por favor, corrija os erros no formulário', 'error');
            return;
        }

        try {
            const formData = getFormData(form);
            
            // Convert empty strings to null for optional fields
            Object.keys(formData).forEach(key => {
                if (formData[key] === '') {
                    formData[key] = null;
                }
            });

            if (mode === 'create') {
                await EquipamentosAPI.criar(formData);
                showToast('Equipamento criado com sucesso', 'success');
            } else {
                await EquipamentosAPI.atualizar(numeroSerie, formData);
                showToast('Equipamento atualizado com sucesso', 'success');
            }

            this.closeModal();
            await this.loadData();
            this.render();

        } catch (error) {
            handleError(error, `${mode === 'create' ? 'creating' : 'updating'} equipamento`);
        }
    },

    search(searchTerm) {
        this.filters.search = searchTerm;
        const searchInput = document.getElementById('equipamentosSearch');
        if (searchInput) {
            searchInput.value = searchTerm;
        }
        this.applyFilters();
    }
};

// Global functions for HTML onclick handlers
window.openEquipamentoModal = function() {
    window.Equipamentos.openModal('create');
};

window.closeEquipamentoModal = function() {
    window.Equipamentos.closeModal();
};

// Add custom styles for equipamentos
const equipamentosStyles = document.createElement('style');
equipamentosStyles.textContent = `
    .action-buttons {
        display: flex;
        gap: var(--spacing-xs);
        justify-content: center;
    }

    .action-buttons .btn {
        padding: var(--spacing-xs);
        min-width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .equipamento-details {
        max-width: 600px;
    }

    .detail-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--spacing-md);
    }

    .detail-item {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-xs);
    }

    .detail-item label {
        font-weight: 600;
        color: var(--text-secondary);
        font-size: 0.875rem;
    }

    .detail-item span {
        color: var(--text-primary);
        font-size: 0.875rem;
        padding: var(--spacing-sm);
        background-color: var(--bg-secondary);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-color);
    }

    @media (max-width: 768px) {
        .action-buttons {
            flex-direction: column;
        }
        
        .detail-grid {
            grid-template-columns: 1fr;
        }
    }
`;
document.head.appendChild(equipamentosStyles);

