from flask import Blueprint, jsonify, request, session
from src.models.user import User, Cliente, Quadro, Coluna, Cartao, Notificacao, Relatorio, db
from datetime import datetime
import json

user_bp = Blueprint('user', __name__)

# Rotas de Autenticação
@user_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['user_setor'] = user.setor
        session['user_permissao'] = user.permissao
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Credenciais inválidas'}), 401

@user_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@user_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    
    required_fields = ['username', 'email', 'password', 'nome', 'setor']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    # Verificar se usuário já existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username já existe'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já existe'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        nome=data['nome'],
        setor=data['setor'],
        permissao=data.get('permissao', 'Colaborador')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Usuário criado com sucesso',
        'user': user.to_dict()
    }), 201

@user_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    return jsonify(user.to_dict()), 200

# Rotas de Usuários
@user_bp.route('/users', methods=['GET'])
def get_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    # Apenas gestores podem ver todos os usuários
    if session.get('user_permissao') != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    # Apenas gestores podem criar usuários
    if session.get('user_permissao') != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.json
    
    required_fields = ['username', 'email', 'password', 'nome', 'setor']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    # Verificar se usuário já existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username já existe'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já existe'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        nome=data['nome'],
        setor=data['setor'],
        permissao=data.get('permissao', 'Colaborador')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user = User.query.get_or_404(user_id)
    
    # Usuários podem ver apenas seu próprio perfil, gestores podem ver todos
    if session['user_id'] != user_id and session.get('user_permissao') != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user = User.query.get_or_404(user_id)
    
    # Usuários podem editar apenas seu próprio perfil, gestores podem editar todos
    if session['user_id'] != user_id and session.get('user_permissao') != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.json
    
    # Campos que podem ser atualizados
    if 'username' in data:
        # Verificar se username já existe (exceto o próprio usuário)
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Username já existe'}), 400
        user.username = data['username']
    
    if 'email' in data:
        # Verificar se email já existe (exceto o próprio usuário)
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email já existe'}), 400
        user.email = data['email']
    
    if 'nome' in data:
        user.nome = data['nome']
    
    if 'setor' in data:
        user.setor = data['setor']
    
    # Apenas gestores podem alterar permissões
    if 'permissao' in data and session.get('user_permissao') == 'Gestor Geral':
        user.permissao = data['permissao']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    # Apenas gestores podem deletar usuários
    if session.get('user_permissao') != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Não permitir deletar a si mesmo
    if session['user_id'] == user_id:
        return jsonify({'error': 'Não é possível deletar seu próprio usuário'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return '', 204

# Rotas de Clientes
@user_bp.route('/clientes', methods=['GET'])
def get_clientes():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    clientes = Cliente.query.all()
    return jsonify([cliente.to_dict() for cliente in clientes])

@user_bp.route('/clientes', methods=['POST'])
def create_cliente():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    # Apenas gestores podem criar clientes
    if session.get('user_permissao') != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.json
    
    if not data.get('nome'):
        return jsonify({'error': 'Nome é obrigatório'}), 400
    
    cliente = Cliente(
        nome=data['nome'],
        descricao=data.get('descricao', '')
    )
    
    db.session.add(cliente)
    db.session.commit()
    
    return jsonify(cliente.to_dict()), 201

@user_bp.route('/clientes/<int:cliente_id>', methods=['GET'])
def get_cliente(cliente_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    cliente = Cliente.query.get_or_404(cliente_id)
    return jsonify(cliente.to_dict())

@user_bp.route('/clientes/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    # Apenas gestores podem editar clientes
    if session.get('user_permissao') != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    cliente = Cliente.query.get_or_404(cliente_id)
    data = request.json
    
    if 'nome' in data:
        cliente.nome = data['nome']
    if 'descricao' in data:
        cliente.descricao = data['descricao']
    
    db.session.commit()
    return jsonify(cliente.to_dict())

@user_bp.route('/clientes/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    # Apenas gestores podem deletar clientes
    if session.get('user_permissao') != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    cliente = Cliente.query.get_or_404(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    return '', 204

