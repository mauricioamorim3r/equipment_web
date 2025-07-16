// API Configuration
const API_BASE_URL = '';

// API Helper Functions
class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            showLoading();
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            showToast(error.message || 'Erro na comunicação com o servidor', 'error');
            throw error;
        } finally {
            hideLoading();
        }
    }

    static async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    static async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    static async uploadFile(endpoint, formData) {
        const url = `${API_BASE_URL}${endpoint}`;
        try {
            showLoading();
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('Upload Error:', error);
            showToast(error.message || 'Erro no upload do arquivo', 'error');
            throw error;
        } finally {
            hideLoading();
        }
    }
}

// Dashboard API
const DashboardAPI = {
    async getResumo() {
        return API.get('/api/dashboard/resumo');
    },

    async getEstatisticasEquipamentos() {
        return API.get('/api/dashboard/estatisticas-equipamentos');
    },

    async getCronogramaCalibracoes(ano) {
        const endpoint = ano ? `/api/dashboard/cronograma-calibracoes?ano=${ano}` : '/api/dashboard/cronograma-calibracoes';
        return API.get(endpoint);
    },

    async getPontosCriticos(dias = 30) {
        return API.get(`/api/dashboard/pontos-criticos?dias=${dias}`);
    },

    async getIndicadoresPerformance() {
        return API.get('/api/dashboard/indicadores-performance');
    }
};

// Equipamentos API
const EquipamentosAPI = {
    async listar(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/api/equipamentos?${queryString}` : '/api/equipamentos';
        return API.get(endpoint);
    },

    async obter(numeroSerie) {
        return API.get(`/api/equipamentos/${numeroSerie}`);
    },

    async criar(equipamento) {
        return API.post('/api/equipamentos', equipamento);
    },

    async atualizar(numeroSerie, equipamento) {
        return API.put(`/api/equipamentos/${numeroSerie}`, equipamento);
    },

    async deletar(numeroSerie) {
        return API.delete(`/api/equipamentos/${numeroSerie}`);
    },

    async getEstatisticas() {
        return API.get('/api/equipamentos/estatisticas');
    }
};

// Pontos de Medição API
const PontosMedicaoAPI = {
    async listar(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/api/pontos-medicao?${queryString}` : '/api/pontos-medicao';
        return API.get(endpoint);
    },

    async obter(id) {
        return API.get(`/api/pontos-medicao/${id}`);
    },

    async criar(ponto) {
        return API.post('/api/pontos-medicao', ponto);
    },

    async atualizar(id, ponto) {
        return API.put(`/api/pontos-medicao/${id}`, ponto);
    },

    async deletar(id) {
        return API.delete(`/api/pontos-medicao/${id}`);
    },

    async getAlertasCalibacao(dias = 30) {
        return API.get(`/api/pontos-medicao/alertas-calibracao?dias=${dias}`);
    }
};

// Certificados API
const CertificadosAPI = {
    async listar(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/api/certificados?${queryString}` : '/api/certificados';
        return API.get(endpoint);
    },

    async obter(id) {
        return API.get(`/api/certificados/${id}`);
    },

    async criar(certificado) {
        return API.post('/api/certificados', certificado);
    },

    async atualizar(id, certificado) {
        return API.put(`/api/certificados/${id}`, certificado);
    },

    async deletar(id) {
        return API.delete(`/api/certificados/${id}`);
    },

    async listarPorEquipamento(numeroSerie) {
        return API.get(`/api/certificados/equipamento/${numeroSerie}`);
    }
};

// Configurações API
const ConfiguracoesAPI = {
    async obterTodas() {
        return API.get('/api/configuracoes/todas');
    },

    // Fabricantes
    async listarFabricantes() {
        return API.get('/api/configuracoes/fabricantes');
    },

    async criarFabricante(nome) {
        return API.post('/api/configuracoes/fabricantes', { nome });
    },

    async atualizarFabricante(id, nome) {
        return API.put(`/api/configuracoes/fabricantes/${id}`, { nome });
    },

    async deletarFabricante(id) {
        return API.delete(`/api/configuracoes/fabricantes/${id}`);
    },

    // Tipos de Equipamento
    async listarTiposEquipamento() {
        return API.get('/api/configuracoes/tipos-equipamento');
    },

    async criarTipoEquipamento(nome) {
        return API.post('/api/configuracoes/tipos-equipamento', { nome });
    },

    // Polos
    async listarPolos() {
        return API.get('/api/configuracoes/polos');
    },

    async criarPolo(nome) {
        return API.post('/api/configuracoes/polos', { nome });
    },

    // Instalações
    async listarInstalacoes() {
        return API.get('/api/configuracoes/instalacoes');
    },

    async criarInstalacao(dados) {
        return API.post('/api/configuracoes/instalacoes', dados);
    },

    // Unidades
    async listarUnidades() {
        return API.get('/api/configuracoes/unidades');
    },

    async criarUnidade(nome) {
        return API.post('/api/configuracoes/unidades', { nome });
    },

    // Classificações de Ponto de Medição
    async listarClassificacoesPontoMedicao() {
        return API.get('/api/configuracoes/classificacoes-ponto-medicao');
    },

    async criarClassificacaoPontoMedicao(nome) {
        return API.post('/api/configuracoes/classificacoes-ponto-medicao', { nome });
    },

    // Status
    async listarStatus() {
        return API.get('/api/configuracoes/status');
    },

    async criarStatus(nome) {
        return API.post('/api/configuracoes/status', { nome });
    },

    // Critérios de Aceitação
    async listarCriteriosAceitacao() {
        return API.get('/api/configuracoes/criterios-aceitacao');
    },

    async criarCriterioAceitacao(nome) {
        return API.post('/api/configuracoes/criterios-aceitacao', { nome });
    }
};

// Importação/Exportação API
const ImportacaoAPI = {
    async importarEquipamentos(file) {
        const formData = new FormData();
        formData.append('file', file);
        return API.uploadFile('/api/importacao/equipamentos', formData);
    },

    async importarPontosMedicao(file) {
        const formData = new FormData();
        formData.append('file', file);
        return API.uploadFile('/api/importacao/pontos-medicao', formData);
    },

    async exportarEquipamentos() {
        window.open('/api/importacao/exportar-equipamentos', '_blank');
    },

    async exportarPontosMedicao() {
        window.open('/api/importacao/exportar-pontos-medicao', '_blank');
    },

    async downloadTemplateEquipamentos() {
        window.open('/api/importacao/template-equipamentos', '_blank');
    },

    async downloadTemplatePontosMedicao() {
        window.open('/api/importacao/template-pontos-medicao', '_blank');
    }
};

// Cache para configurações
let configuracoesCache = null;
let configuracoesCacheTime = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutos

async function getConfiguracoes(forceRefresh = false) {
    const now = Date.now();
    
    if (!forceRefresh && configuracoesCache && configuracoesCacheTime && (now - configuracoesCacheTime) < CACHE_DURATION) {
        return configuracoesCache;
    }
    
    try {
        configuracoesCache = await ConfiguracoesAPI.obterTodas();
        configuracoesCacheTime = now;
        return configuracoesCache;
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        return configuracoesCache || {
            fabricantes: [],
            tipos_equipamento: [],
            polos: [],
            instalacoes: [],
            unidades: [],
            classificacoes_ponto_medicao: [],
            status: [],
            criterios_aceitacao: []
        };
    }
}

// Função para invalidar cache de configurações
function invalidateConfiguracoesCache() {
    configuracoesCache = null;
    configuracoesCacheTime = null;
}

