# Sistema Kanban - Gestão de Tarefas

Sistema completo de gestão de tarefas em formato Kanban desenvolvido para agências, com controle de permissões por setor e gestão de clientes.

## 🚀 Funcionalidades

- **Autenticação e Controle de Acesso**: Sistema de login com diferentes níveis de permissão
- **Quadros Kanban**: Organização por setor ou cliente
- **Gestão de Tarefas**: Cartões com informações completas (responsável, prazo, status, etc.)
- **Controle de Permissões**: Colaboradores acessam apenas seu setor, gestores têm acesso total
- **Interface Responsiva**: Adaptável para desktop e mobile
- **Histórico de Alterações**: Rastreamento completo de mudanças nos cartões

## 🏗️ Arquitetura

- **Backend**: Flask (Python) com SQLAlchemy
- **Frontend**: React com Vite e shadcn/ui
- **Banco de Dados**: SQLite (pronto para PostgreSQL)
- **Autenticação**: Sistema de sessões Flask

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 20+
- pnpm (ou npm)

## 🛠️ Instalação

### Backend (Flask)

1. Navegue para o diretório do backend:
```bash
cd kanban-backend
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o script de dados de teste:
```bash
python create_sample_data.py
```

5. Inicie o servidor:
```bash
python src/main.py
```

O backend estará rodando em `http://localhost:5001`

### Frontend (React)

1. Navegue para o diretório do frontend:
```bash
cd kanban-frontend
```

2. Instale as dependências:
```bash
pnpm install
```

3. Inicie o servidor de desenvolvimento:
```bash
pnpm run dev --host
```

O frontend estará rodando em `http://localhost:5173`

## 👥 Credenciais de Teste

### Administrador (Gestor Geral)
- **Usuário**: admin
- **Senha**: admin123
- **Permissões**: Acesso total ao sistema

### Colaboradores
- **Social Media**: maria.social / maria123
- **Design**: joao.design / joao123
- **Tráfego Pago**: ana.trafego / ana123
- **Audiovisual**: carlos.video / carlos123
- **Comercial**: lucia.comercial / lucia123

## 📊 Dados de Exemplo

O sistema vem com dados de teste pré-configurados:

- **6 usuários** (1 admin + 5 colaboradores)
- **5 clientes** de exemplo
- **8 quadros** (5 por setor + 3 por cliente)
- **7 tarefas** distribuídas nos quadros

## 🎯 Como Usar

1. **Login**: Acesse `http://localhost:5173` e faça login com uma das credenciais
2. **Navegação**: Use a barra lateral para navegar entre quadros
3. **Visualização**: Veja as tarefas organizadas em colunas Kanban
4. **Filtros**: Use o botão "Filtrar" para filtrar por setor
5. **Perfil**: Clique no avatar para acessar opções do usuário

## 🔧 Estrutura do Projeto

```
kanban-backend/
├── src/
│   ├── models/          # Modelos de dados SQLAlchemy
│   ├── routes/          # Rotas da API Flask
│   ├── static/          # Arquivos estáticos
│   └── main.py          # Arquivo principal
├── create_sample_data.py # Script de dados de teste
└── requirements.txt     # Dependências Python

kanban-frontend/
├── src/
│   ├── components/      # Componentes React
│   ├── contexts/        # Contextos (AuthContext)
│   ├── services/        # Serviços de API
│   └── App.jsx          # Componente principal
├── public/              # Arquivos públicos
└── package.json         # Dependências Node.js
```

## 🌐 API Endpoints

### Autenticação
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Usuário atual

### Usuários
- `GET /api/users` - Listar usuários
- `POST /api/users` - Criar usuário
- `PUT /api/users/{id}` - Atualizar usuário
- `DELETE /api/users/{id}` - Deletar usuário

### Clientes
- `GET /api/clientes` - Listar clientes
- `POST /api/clientes` - Criar cliente
- `PUT /api/clientes/{id}` - Atualizar cliente
- `DELETE /api/clientes/{id}` - Deletar cliente

### Quadros
- `GET /api/quadros` - Listar quadros
- `GET /api/quadros/setor/{setor}` - Quadros por setor
- `GET /api/quadros/cliente/{id}` - Quadros por cliente
- `POST /api/quadros` - Criar quadro
- `PUT /api/quadros/{id}` - Atualizar quadro
- `DELETE /api/quadros/{id}` - Deletar quadro

### Cartões
- `GET /api/cartoes` - Listar cartões (com filtros)
- `POST /api/cartoes` - Criar cartão
- `PUT /api/cartoes/{id}` - Atualizar cartão
- `POST /api/cartoes/{id}/mover` - Mover cartão
- `DELETE /api/cartoes/{id}` - Deletar cartão

## 🔒 Controle de Permissões

- **Gestor Geral**: Acesso total a todos os quadros e funcionalidades administrativas
- **Colaborador**: Acesso apenas aos quadros do seu setor
- **Validações**: Todas as operações são validadas no backend

## 🚀 Deploy

### Backend
1. Configure um servidor WSGI (Gunicorn recomendado)
2. Configure PostgreSQL para produção
3. Defina variáveis de ambiente para configurações sensíveis

### Frontend
1. Execute `pnpm run build` para gerar build de produção
2. Sirva os arquivos estáticos com nginx ou similar
3. Configure proxy reverso para o backend

## 🔄 Próximas Funcionalidades

- [ ] Drag and drop para mover cartões
- [ ] Sistema de notificações em tempo real
- [ ] Relatórios automáticos
- [ ] Integrações (Google Drive, WhatsApp, Calendar)
- [ ] Recursos de IA para automação
- [ ] Filtros avançados e busca
- [ ] Dashboard de métricas

## 🐛 Problemas Conhecidos

- Alguns dropdowns podem não abrir corretamente (componentes UI)
- Funcionalidade de drag and drop ainda não implementada
- Sistema de notificações pendente

## 📝 Licença

Este projeto foi desenvolvido como sistema personalizado para gestão de tarefas em agências.

## 🤝 Suporte

Para suporte ou dúvidas sobre o sistema, consulte a documentação técnica ou entre em contato com a equipe de desenvolvimento.

