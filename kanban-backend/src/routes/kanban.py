from flask import Blueprint, jsonify, request, session
from src.models.user import User, Cliente, Quadro, Coluna, Cartao, db
from datetime import datetime

kanban_bp = Blueprint('kanban', __name__)

# Rotas de Quadros
@kanban_bp.route('/quadros', methods=['GET'])
def get_quadros():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    # Gestores veem todos os quadros, colaboradores apenas do seu setor
    if user_permissao == 'Gestor Geral':
        quadros = Quadro.query.all()
    else:
        quadros = Quadro.query.filter_by(setor=user_setor).all()
    
    return jsonify([quadro.to_dict() for quadro in quadros])

@kanban_bp.route('/quadros/setor/<setor>', methods=['GET'])
def get_quadros_por_setor(setor):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    # Verificar permissão para acessar quadros do setor
    if user_permissao != 'Gestor Geral' and user_setor != setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    quadros = Quadro.query.filter_by(setor=setor).all()
    return jsonify([quadro.to_dict() for quadro in quadros])

@kanban_bp.route('/quadros/cliente/<int:cliente_id>', methods=['GET'])
def get_quadros_por_cliente(cliente_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    quadros = Quadro.query.filter_by(cliente_id=cliente_id).all()
    return jsonify([quadro.to_dict() for quadro in quadros])

@kanban_bp.route('/quadros', methods=['POST'])
def create_quadro():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.json
    
    if not data.get('titulo'):
        return jsonify({'error': 'Título é obrigatório'}), 400
    
    if not data.get('tipo') or data['tipo'] not in ['Setor', 'Cliente']:
        return jsonify({'error': 'Tipo deve ser Setor ou Cliente'}), 400
    
    # Verificar permissões baseadas no tipo
    if data['tipo'] == 'Setor':
        if not data.get('setor'):
            return jsonify({'error': 'Setor é obrigatório para quadros por setor'}), 400
        
        # Colaboradores só podem criar quadros do seu setor
        if session.get('user_permissao') != 'Gestor Geral' and session.get('user_setor') != data['setor']:
            return jsonify({'error': 'Permissão negada'}), 403
    
    elif data['tipo'] == 'Cliente':
        if not data.get('cliente_id'):
            return jsonify({'error': 'Cliente é obrigatório para quadros por cliente'}), 400
        
        # Verificar se cliente existe
        cliente = Cliente.query.get(data['cliente_id'])
        if not cliente:
            return jsonify({'error': 'Cliente não encontrado'}), 404
    
    quadro = Quadro(
        titulo=data['titulo'],
        tipo=data['tipo'],
        setor=data.get('setor'),
        cliente_id=data.get('cliente_id')
    )
    
    db.session.add(quadro)
    db.session.flush()  # Para obter o ID do quadro
    
    # Criar colunas padrão
    colunas_padrao = ['A Fazer', 'Em Andamento', 'Aprovação', 'Concluído']
    for i, titulo_coluna in enumerate(colunas_padrao):
        coluna = Coluna(
            titulo=titulo_coluna,
            ordem=i,
            quadro_id=quadro.id
        )
        db.session.add(coluna)
    
    db.session.commit()
    
    return jsonify(quadro.to_dict()), 201

@kanban_bp.route('/quadros/<int:quadro_id>', methods=['GET'])
def get_quadro(quadro_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    quadro = Quadro.query.get_or_404(quadro_id)
    
    # Verificar permissão para acessar o quadro
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    return jsonify(quadro.to_dict())

@kanban_bp.route('/quadros/<int:quadro_id>', methods=['PUT'])
def update_quadro(quadro_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    quadro = Quadro.query.get_or_404(quadro_id)
    
    # Verificar permissão para editar o quadro
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.json
    
    if 'titulo' in data:
        quadro.titulo = data['titulo']
    
    db.session.commit()
    return jsonify(quadro.to_dict())

@kanban_bp.route('/quadros/<int:quadro_id>', methods=['DELETE'])
def delete_quadro(quadro_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    quadro = Quadro.query.get_or_404(quadro_id)
    
    # Verificar permissão para deletar o quadro
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    db.session.delete(quadro)
    db.session.commit()
    return '', 204

# Rotas de Colunas
@kanban_bp.route('/quadros/<int:quadro_id>/colunas', methods=['POST'])
def create_coluna(quadro_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    quadro = Quadro.query.get_or_404(quadro_id)
    
    # Verificar permissão
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.json
    
    if not data.get('titulo'):
        return jsonify({'error': 'Título é obrigatório'}), 400
    
    # Obter próxima ordem
    max_ordem = db.session.query(db.func.max(Coluna.ordem)).filter_by(quadro_id=quadro_id).scalar() or -1
    
    coluna = Coluna(
        titulo=data['titulo'],
        ordem=max_ordem + 1,
        quadro_id=quadro_id
    )
    
    db.session.add(coluna)
    db.session.commit()
    
    return jsonify(coluna.to_dict()), 201

@kanban_bp.route('/colunas/<int:coluna_id>', methods=['PUT'])
def update_coluna(coluna_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    coluna = Coluna.query.get_or_404(coluna_id)
    quadro = coluna.quadro
    
    # Verificar permissão
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.json
    
    if 'titulo' in data:
        coluna.titulo = data['titulo']
    
    if 'ordem' in data:
        coluna.ordem = data['ordem']
    
    db.session.commit()
    return jsonify(coluna.to_dict())

@kanban_bp.route('/colunas/<int:coluna_id>', methods=['DELETE'])
def delete_coluna(coluna_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    coluna = Coluna.query.get_or_404(coluna_id)
    quadro = coluna.quadro
    
    # Verificar permissão
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    # Verificar se há cartões na coluna
    if coluna.cartoes:
        return jsonify({'error': 'Não é possível deletar coluna com cartões'}), 400
    
    db.session.delete(coluna)
    db.session.commit()
    return '', 204

# Rotas de Cartões
@kanban_bp.route('/cartoes', methods=['GET'])
def get_cartoes():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    # Filtros opcionais
    cliente_id = request.args.get('cliente_id', type=int)
    status = request.args.get('status')
    responsavel_id = request.args.get('responsavel_id', type=int)
    setor = request.args.get('setor')
    
    query = Cartao.query
    
    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if responsavel_id:
        query = query.filter_by(responsavel_id=responsavel_id)
    
    if setor:
        # Filtrar por setor através do quadro
        query = query.join(Coluna).join(Quadro).filter(Quadro.setor == setor)
    
    # Aplicar filtros de permissão
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral':
        # Colaboradores veem apenas cartões do seu setor
        query = query.join(Coluna).join(Quadro).filter(Quadro.setor == user_setor)
    
    cartoes = query.all()
    return jsonify([cartao.to_dict() for cartao in cartoes])

@kanban_bp.route('/cartoes', methods=['POST'])
def create_cartao():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.json
    
    required_fields = ['titulo', 'responsavel_id', 'cliente_id', 'coluna_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    # Verificar se coluna existe e se usuário tem permissão
    coluna = Coluna.query.get(data['coluna_id'])
    if not coluna:
        return jsonify({'error': 'Coluna não encontrada'}), 404
    
    quadro = coluna.quadro
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    # Verificar se responsável existe
    responsavel = User.query.get(data['responsavel_id'])
    if not responsavel:
        return jsonify({'error': 'Responsável não encontrado'}), 404
    
    # Verificar se cliente existe
    cliente = Cliente.query.get(data['cliente_id'])
    if not cliente:
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    # Obter próxima ordem na coluna
    max_ordem = db.session.query(db.func.max(Cartao.ordem)).filter_by(coluna_id=data['coluna_id']).scalar() or -1
    
    cartao = Cartao(
        titulo=data['titulo'],
        descricao=data.get('descricao', ''),
        responsavel_id=data['responsavel_id'],
        cliente_id=data['cliente_id'],
        coluna_id=data['coluna_id'],
        ordem=max_ordem + 1,
        comentarios_internos=data.get('comentarios_internos', '')
    )
    
    # Processar prazo de entrega
    if data.get('prazo_entrega'):
        try:
            cartao.prazo_entrega = datetime.fromisoformat(data['prazo_entrega'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Formato de data inválido para prazo_entrega'}), 400
    
    # Processar checklist
    if data.get('checklist'):
        cartao.set_checklist(data['checklist'])
    
    # Processar anexos
    if data.get('anexos'):
        cartao.set_anexos(data['anexos'])
    
    # Adicionar ao histórico
    cartao.add_historico('criado', session['user_id'], 'Cartão criado')
    
    db.session.add(cartao)
    db.session.commit()
    
    return jsonify(cartao.to_dict()), 201

@kanban_bp.route('/cartoes/<int:cartao_id>', methods=['GET'])
def get_cartao(cartao_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    cartao = Cartao.query.get_or_404(cartao_id)
    
    # Verificar permissão
    quadro = cartao.coluna.quadro
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    return jsonify(cartao.to_dict())

@kanban_bp.route('/cartoes/<int:cartao_id>', methods=['PUT'])
def update_cartao(cartao_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    cartao = Cartao.query.get_or_404(cartao_id)
    
    # Verificar permissão
    quadro = cartao.coluna.quadro
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.json
    alteracoes = []
    
    if 'titulo' in data:
        old_value = cartao.titulo
        cartao.titulo = data['titulo']
        alteracoes.append(f'Título alterado de "{old_value}" para "{data["titulo"]}"')
    
    if 'descricao' in data:
        cartao.descricao = data['descricao']
        alteracoes.append('Descrição atualizada')
    
    if 'responsavel_id' in data:
        old_responsavel = cartao.responsavel_user.nome if cartao.responsavel_user else 'N/A'
        responsavel = User.query.get(data['responsavel_id'])
        if not responsavel:
            return jsonify({'error': 'Responsável não encontrado'}), 404
        cartao.responsavel_id = data['responsavel_id']
        alteracoes.append(f'Responsável alterado de "{old_responsavel}" para "{responsavel.nome}"')
    
    if 'prazo_entrega' in data:
        if data['prazo_entrega']:
            try:
                cartao.prazo_entrega = datetime.fromisoformat(data['prazo_entrega'].replace('Z', '+00:00'))
                alteracoes.append('Prazo de entrega atualizado')
            except ValueError:
                return jsonify({'error': 'Formato de data inválido para prazo_entrega'}), 400
        else:
            cartao.prazo_entrega = None
            alteracoes.append('Prazo de entrega removido')
    
    if 'checklist' in data:
        cartao.set_checklist(data['checklist'])
        alteracoes.append('Checklist atualizado')
    
    if 'anexos' in data:
        cartao.set_anexos(data['anexos'])
        alteracoes.append('Anexos atualizados')
    
    if 'comentarios_internos' in data:
        cartao.comentarios_internos = data['comentarios_internos']
        alteracoes.append('Comentários internos atualizados')
    
    if 'status' in data:
        old_status = cartao.status
        cartao.status = data['status']
        alteracoes.append(f'Status alterado de "{old_status}" para "{data["status"]}"')
    
    # Adicionar alterações ao histórico
    if alteracoes:
        cartao.add_historico('atualizado', session['user_id'], '; '.join(alteracoes))
    
    db.session.commit()
    return jsonify(cartao.to_dict())

@kanban_bp.route('/cartoes/<int:cartao_id>/mover', methods=['POST'])
def mover_cartao(cartao_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    cartao = Cartao.query.get_or_404(cartao_id)
    
    # Verificar permissão
    quadro = cartao.coluna.quadro
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.json
    
    if not data.get('coluna_id'):
        return jsonify({'error': 'coluna_id é obrigatório'}), 400
    
    nova_coluna = Coluna.query.get(data['coluna_id'])
    if not nova_coluna:
        return jsonify({'error': 'Coluna não encontrada'}), 404
    
    # Verificar se a nova coluna pertence ao mesmo quadro
    if nova_coluna.quadro_id != quadro.id:
        return jsonify({'error': 'Coluna deve pertencer ao mesmo quadro'}), 400
    
    old_coluna_titulo = cartao.coluna.titulo
    cartao.coluna_id = data['coluna_id']
    
    # Atualizar ordem se fornecida
    if 'ordem' in data:
        cartao.ordem = data['ordem']
    else:
        # Colocar no final da nova coluna
        max_ordem = db.session.query(db.func.max(Cartao.ordem)).filter_by(coluna_id=data['coluna_id']).scalar() or -1
        cartao.ordem = max_ordem + 1
    
    # Adicionar ao histórico
    cartao.add_historico('movido', session['user_id'], f'Movido de "{old_coluna_titulo}" para "{nova_coluna.titulo}"')
    
    db.session.commit()
    return jsonify(cartao.to_dict())

@kanban_bp.route('/cartoes/<int:cartao_id>', methods=['DELETE'])
def delete_cartao(cartao_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    cartao = Cartao.query.get_or_404(cartao_id)
    
    # Verificar permissão
    quadro = cartao.coluna.quadro
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    if user_permissao != 'Gestor Geral' and quadro.setor != user_setor:
        return jsonify({'error': 'Permissão negada'}), 403
    
    db.session.delete(cartao)
    db.session.commit()
    return '', 204

