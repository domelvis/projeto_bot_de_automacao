// script.js - Dashboard Logic
class BotDashboard {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.bots = [];
        this.executions = [];
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        console.log('🚀 Iniciando Bot Dashboard...');
        this.bindEvents();
        this.loadData();
        this.startAutoUpdate();
    }
    
    bindEvents() {
        // Botões principais
        document.getElementById('refreshBtn').addEventListener('click', () => this.loadData());
        document.getElementById('createBotBtn').addEventListener('click', () => this.showCreateBotModal());
        
        // Modal
        document.getElementById('closeModal').addEventListener('click', () => this.hideCreateBotModal());
        document.getElementById('cancelBtn').addEventListener('click', () => this.hideCreateBotModal());
        document.getElementById('createBotForm').addEventListener('submit', (e) => this.createBot(e));
        
        // Filtros
        document.getElementById('filterStatus').addEventListener('change', (e) => this.filterBots(e.target.value));
        
        // Fechar modal clicando fora
        document.getElementById('createBotModal').addEventListener('click', (e) => {
            if (e.target.id === 'createBotModal') {
                this.hideCreateBotModal();
            }
        });
    }
    
    async loadData() {
        this.showLoading(true);
        try {
            await Promise.all([
                this.loadStats(),
                this.loadBots(),
                this.loadRecentExecutions()
            ]);
            this.showToast('Dados atualizados com sucesso!', 'success');
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
            this.showToast('Erro ao carregar dados', 'error');
        }
        this.showLoading(false);
    }
    
    async loadStats() {
        try {
            const response = await fetch(`${this.apiUrl}/stats`);
            const stats = await response.json();
            
            document.getElementById('totalBots').textContent = stats.total_bots;
            document.getElementById('totalExecutions').textContent = stats.total_executions;
            document.getElementById('successfulExecutions').textContent = stats.successful_executions;
            document.getElementById('successRate').textContent = stats.success_rate;
            
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    }
    
    async loadBots() {
        try {
            const response = await fetch(`${this.apiUrl}/bots/`);
            const data = await response.json();
            this.bots = data.bots || [];
            this.renderBots();
            
        } catch (error) {
            console.error('Erro ao carregar bots:', error);
        }
    }
    
    async loadRecentExecutions() {
        try {
            // Carregar execuções de todos os bots
            let allExecutions = [];
            
            for (const bot of this.bots) {
                try {
                    const response = await fetch(`${this.apiUrl}/bots/${bot.id}/executions`);
                    const data = await response.json();
                    const executions = data.executions.map(exec => ({
                        ...exec,
                        bot_name: bot.name
                    }));
                    allExecutions = allExecutions.concat(executions);
                } catch (error) {
                    console.error(`Erro ao carregar execuções do bot ${bot.id}:`, error);
                }
            }
            
            // Ordenar por data mais recente
            this.executions = allExecutions.sort((a, b) => 
                new Date(b.start_time) - new Date(a.start_time)
            ).slice(0, 10); // Últimas 10
            
            this.renderExecutions();
            
        } catch (error) {
            console.error('Erro ao carregar execuções:', error);
        }
    }
    
    renderBots(filter = 'all') {
        const container = document.getElementById('botsGrid');
        let filteredBots = this.bots;
        
        if (filter !== 'all') {
            filteredBots = this.bots.filter(bot => bot.status === filter);
        }
        
        if (filteredBots.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                    <i class="fas fa-robot" style="font-size: 3rem; color: var(--text-secondary); margin-bottom: 1rem;"></i>
                    <p style="color: var(--text-secondary);">Nenhum bot encontrado</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = filteredBots.map(bot => `
            <div class="bot-card" data-bot-id="${bot.id}">
                <div class="bot-header">
                    <div>
                        <div class="bot-title">${bot.name}</div>
                        <div class="bot-description">${bot.description || 'Sem descrição'}</div>
                    </div>
                    <span class="bot-status status-${bot.status}">${this.getStatusText(bot.status)}</span>
                </div>
                
                <div class="bot-info">
                    <small style="color: var(--text-secondary);">
                        <i class="fas fa-clock"></i>
                        Criado: ${this.formatDate(bot.created_at)}
                    </small>
                    ${bot.last_run ? `
                        <small style="color: var(--text-secondary);">
                            <i class="fas fa-play"></i>
                            Última execução: ${this.formatDate(bot.last_run)}
                        </small>
                    ` : ''}
                </div>
                
                <div class="bot-actions">
                    ${bot.status === 'running' 
                        ? `<button class="btn btn-danger btn-sm" onclick="dashboard.stopBot(${bot.id})">
                               <i class="fas fa-stop"></i> Parar
                           </button>`
                        : `<button class="btn btn-success btn-sm" onclick="dashboard.startBot(${bot.id})">
                               <i class="fas fa-play"></i> Iniciar
                           </button>`
                    }
                    <button class="btn btn-secondary btn-sm" onclick="dashboard.viewBotDetails(${bot.id})">
                        <i class="fas fa-eye"></i> Detalhes
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    renderExecutions() {
        const tbody = document.getElementById('executionsTableBody');
        
        if (this.executions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; color: var(--text-secondary); padding: 2rem;">
                        <i class="fas fa-history"></i>
                        Nenhuma execução encontrada
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = this.executions.map(exec => `
            <tr>
                <td>#${exec.id}</td>
                <td>${exec.bot_name}</td>
                <td>
                    <span class="bot-status status-${exec.status}">
                        ${this.getStatusText(exec.status)}
                    </span>
                </td>
                <td>${this.formatDate(exec.start_time)}</td>
                <td>${this.calculateDuration(exec.start_time, exec.end_time)}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="dashboard.viewExecutionDetails(${exec.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    async startBot(botId) {
        try {
            const response = await fetch(`${this.apiUrl}/bots/${botId}/start`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showToast('Bot iniciado com sucesso!', 'success');
                await this.loadData();
            } else {
                this.showToast('Erro ao iniciar bot', 'error');
            }
        } catch (error) {
            console.error('Erro ao iniciar bot:', error);
            this.showToast('Erro ao iniciar bot', 'error');
        }
    }
    
    async stopBot(botId) {
        try {
            const response = await fetch(`${this.apiUrl}/bots/${botId}/stop`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showToast('Bot parado com sucesso!', 'success');
                await this.loadData();
            } else {
                this.showToast('Erro ao parar bot', 'error');
            }
        } catch (error) {
            console.error('Erro ao parar bot:', error);
            this.showToast('Erro ao parar bot', 'error');
        }
    }
    
    showCreateBotModal() {
        document.getElementById('createBotModal').style.display = 'block';
    }
    
    hideCreateBotModal() {
        document.getElementById('createBotModal').style.display = 'none';
        document.getElementById('createBotForm').reset();
    }
    
    async createBot(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('botName').value,
            description: document.getElementById('botDescription').value
        };
        
        try {
            const response = await fetch(`${this.apiUrl}/bots/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                this.showToast('Bot criado com sucesso!', 'success');
                this.hideCreateBotModal();
                await this.loadData();
            } else {
                this.showToast('Erro ao criar bot', 'error');
            }
        } catch (error) {
            console.error('Erro ao criar bot:', error);
            this.showToast('Erro ao criar bot', 'error');
        }
    }
    
    filterBots(status) {
        this.renderBots(status);
    }
    
    viewBotDetails(botId) {
        // TODO: Implementar modal de detalhes do bot
        console.log('Visualizar detalhes do bot:', botId);
        this.showToast('Funcionalidade em desenvolvimento', 'info');
    }
    
    viewExecutionDetails(execId) {
        // TODO: Implementar modal de detalhes da execução
        console.log('Visualizar detalhes da execução:', execId);
        this.showToast('Funcionalidade em desenvolvimento', 'info');
    }
    
    startAutoUpdate() {
        // Atualizar dados a cada 30 segundos
        this.updateInterval = setInterval(() => {
            this.loadStats();
        }, 30000);
    }
    
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
    
    // Utility functions
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    }
    
    calculateDuration(startTime, endTime) {
        if (!startTime) return 'N/A';
        if (!endTime) return 'Em execução...';
        
        const start = new Date(startTime);
        const end = new Date(endTime);
        const diff = end - start;
        
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        
        return `${minutes}m ${seconds}s`;
    }
    
    getStatusText(status) {
        const statusMap = {
            'running': 'Rodando',
            'stopped': 'Parado',
            'completed': 'Completo',
            'failed': 'Falhou'
        };
        return statusMap[status] || status;
    }
    
    showLoading(show) {
        document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none';
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                ${message}
            </div>
        `;
        
        document.getElementById('toastContainer').appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Inicializar dashboard quando página carregar
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new BotDashboard();
});

// Cleanup ao fechar página
window.addEventListener('beforeunload', () => {
    if (dashboard) {
        dashboard.stopAutoUpdate();
    }
});