const API_BASE_URL = 'http://localhost:5001/api';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Erro na requisição');
      }

      return data;
    } catch (error) {
      console.error(`Erro na requisição para ${endpoint}:`, error);
      throw error;
    }
  }

  // Métodos de autenticação
  async login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async logout() {
    return this.request('/auth/logout', { method: 'POST' });
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  // Métodos de clientes
  async getClientes() {
    return this.request('/clientes');
  }

  async createCliente(clienteData) {
    return this.request('/clientes', {
      method: 'POST',
      body: JSON.stringify(clienteData),
    });
  }

  async updateCliente(clienteId, clienteData) {
    return this.request(`/clientes/${clienteId}`, {
      method: 'PUT',
      body: JSON.stringify(clienteData),
    });
  }

  async deleteCliente(clienteId) {
    return this.request(`/clientes/${clienteId}`, { method: 'DELETE' });
  }

  // Métodos de quadros
  async getQuadros() {
    return this.request('/quadros');
  }

  async getQuadrosPorSetor(setor) {
    return this.request(`/quadros/setor/${setor}`);
  }

  async getQuadrosPorCliente(clienteId) {
    return this.request(`/quadros/cliente/${clienteId}`);
  }

  async getQuadro(quadroId) {
    return this.request(`/quadros/${quadroId}`);
  }

  async createQuadro(quadroData) {
    return this.request('/quadros', {
      method: 'POST',
      body: JSON.stringify(quadroData),
    });
  }

  async updateQuadro(quadroId, quadroData) {
    return this.request(`/quadros/${quadroId}`, {
      method: 'PUT',
      body: JSON.stringify(quadroData),
    });
  }

  async deleteQuadro(quadroId) {
    return this.request(`/quadros/${quadroId}`, { method: 'DELETE' });
  }

  // Métodos de cartões
  async getCartoes(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    
    const queryString = params.toString();
    const endpoint = queryString ? `/cartoes?${queryString}` : '/cartoes';
    
    return this.request(endpoint);
  }

  async getCartao(cartaoId) {
    return this.request(`/cartoes/${cartaoId}`);
  }

  async createCartao(cartaoData) {
    return this.request('/cartoes', {
      method: 'POST',
      body: JSON.stringify(cartaoData),
    });
  }

  async updateCartao(cartaoId, cartaoData) {
    return this.request(`/cartoes/${cartaoId}`, {
      method: 'PUT',
      body: JSON.stringify(cartaoData),
    });
  }

  async moverCartao(cartaoId, moveData) {
    return this.request(`/cartoes/${cartaoId}/mover`, {
      method: 'POST',
      body: JSON.stringify(moveData),
    });
  }

  async deleteCartao(cartaoId) {
    return this.request(`/cartoes/${cartaoId}`, { method: 'DELETE' });
  }

  // Métodos de usuários
  async getUsers() {
    return this.request('/users');
  }

  async createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(userId, userData) {
    return this.request(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(userId) {
    return this.request(`/users/${userId}`, { method: 'DELETE' });
  }
}

export default new ApiService();


  // Método para mover cartão
  async moveCartao(cartaoId, colunaId, posicao = 0) {
    return this.request(`/cartoes/${cartaoId}/mover`, {
      method: 'POST',
      body: JSON.stringify({ 
        coluna_id: colunaId, 
        posicao: posicao 
      }),
    });
  }


  // Métodos de notificações
  async getNotificacoes(page = 1, perPage = 20, apenasNaoLidas = false) {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
      apenas_nao_lidas: apenasNaoLidas.toString()
    });
    return this.request(`/notificacoes?${params}`);
  }

  async marcarNotificacaoLida(notificacaoId) {
    return this.request(`/notificacoes/${notificacaoId}/marcar-lida`, {
      method: 'POST',
    });
  }

  async marcarTodasNotificacoesLidas() {
    return this.request('/notificacoes/marcar-todas-lidas', {
      method: 'POST',
    });
  }

  async verificarPrazos() {
    return this.request('/notificacoes/verificar-prazos', {
      method: 'POST',
    });
  }


  // Métodos de relatórios
  async getDashboardRelatorio(dataInicio, dataFim) {
    const params = new URLSearchParams();
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    return this.request(`/relatorios/dashboard?${params}`);
  }

  async getProdutividadeRelatorio(periodo = '30') {
    return this.request(`/relatorios/produtividade?periodo=${periodo}`);
  }

  async getPrazosRelatorio() {
    return this.request('/relatorios/prazos');
  }

  async exportarRelatorio(tipo, formato = 'json') {
    return this.request('/relatorios/exportar', {
      method: 'POST',
      body: JSON.stringify({ tipo, formato }),
    });
  }

