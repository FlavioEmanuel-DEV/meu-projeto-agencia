from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from src.models.user import db, Notificacao, User, Cartao, Quadro
from sqlalchemy import and_, or_

notificacoes_bp = Blueprint('notificacoes', __name__)

@notificacoes_bp.route('/notificacoes', methods=['GET'])
def get_notificacoes():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    apenas_nao_lidas = request.args.get('apenas_nao_lidas', 'false').lower() == 'true'
    
    query = Notificacao.query.filter_by(usuario_id=user_id)
    
    if apenas_nao_lidas:
        query = query.filter_by(lida=False)
    
    notificacoes = query.order_by(Notificacao.data_criacao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'notificacoes': [n.to_dict() for n in notificacoes.items],
        'total': notificacoes.total,
        'pages': notificacoes.pages,
        'current_page': page,
        'nao_lidas': Notificacao.query.filter_by(usuario_id=user_id, lida=False).count()
    })

@notificacoes_bp.route('/notificacoes/<int:notificacao_id>/marcar-lida', methods=['POST'])
def marcar_notificacao_lida(notificacao_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    notificacao = Notificacao.query.filter_by(
        id=notificacao_id, 
        usuario_id=session['user_id']
    ).first_or_404()
    
    notificacao.lida = True
    notificacao.data_leitura = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Notificação marcada como lida'})

@notificacoes_bp.route('/notificacoes/marcar-todas-lidas', methods=['POST'])
def marcar_todas_lidas():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    Notificacao.query.filter_by(
        usuario_id=session['user_id'], 
        lida=False
    ).update({
        'lida': True,
        'data_leitura': datetime.utcnow()
    })
    
    db.session.commit()
    
    return jsonify({'message': 'Todas as notificações foram marcadas como lidas'})

@notificacoes_bp.route('/notificacoes/verificar-prazos', methods=['POST'])
def verificar_prazos():
    """Endpoint para verificar prazos e criar notificações automáticas"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_permissao = session.get('user_permissao')
    if user_permissao != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    hoje = datetime.utcnow().date()
    amanha = hoje + timedelta(days=1)
    em_3_dias = hoje + timedelta(days=3)
    
    # Buscar cartões com prazos próximos
    cartoes_urgentes = Cartao.query.filter(
        and_(
            Cartao.prazo_entrega <= amanha,
            Cartao.status.in_(['pendente', 'em_andamento']),
            Cartao.prazo_entrega >= hoje
        )
    ).all()
    
    cartoes_proximos = Cartao.query.filter(
        and_(
            Cartao.prazo_entrega <= em_3_dias,
            Cartao.prazo_entrega > amanha,
            Cartao.status.in_(['pendente', 'em_andamento'])
        )
    ).all()
    
    notificacoes_criadas = 0
    
    # Criar notificações para cartões urgentes
    for cartao in cartoes_urgentes:
        # Verificar se já existe notificação recente
        notificacao_existente = Notificacao.query.filter(
            and_(
                Notificacao.usuario_id == cartao.responsavel_id,
                Notificacao.tipo == 'prazo_urgente',
                Notificacao.referencia_id == cartao.id,
                Notificacao.data_criacao >= datetime.utcnow() - timedelta(hours=24)
            )
        ).first()
        
        if not notificacao_existente:
            notificacao = Notificacao(
                usuario_id=cartao.responsavel_id,
                tipo='prazo_urgente',
                titulo='Prazo Urgente!',
                mensagem=f'O cartão "{cartao.titulo}" vence hoje ou amanhã!',
                referencia_tipo='cartao',
                referencia_id=cartao.id
            )
            db.session.add(notificacao)
            notificacoes_criadas += 1
    
    # Criar notificações para cartões próximos do prazo
    for cartao in cartoes_proximos:
        # Verificar se já existe notificação recente
        notificacao_existente = Notificacao.query.filter(
            and_(
                Notificacao.usuario_id == cartao.responsavel_id,
                Notificacao.tipo == 'prazo_proximo',
                Notificacao.referencia_id == cartao.id,
                Notificacao.data_criacao >= datetime.utcnow() - timedelta(days=2)
            )
        ).first()
        
        if not notificacao_existente:
            dias_restantes = (cartao.prazo_entrega - hoje).days
            notificacao = Notificacao(
                usuario_id=cartao.responsavel_id,
                tipo='prazo_proximo',
                titulo='Prazo Próximo',
                mensagem=f'O cartão "{cartao.titulo}" vence em {dias_restantes} dias.',
                referencia_tipo='cartao',
                referencia_id=cartao.id
            )
            db.session.add(notificacao)
            notificacoes_criadas += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'{notificacoes_criadas} notificações criadas',
        'cartoes_urgentes': len(cartoes_urgentes),
        'cartoes_proximos': len(cartoes_proximos)
    })

def criar_notificacao(usuario_id, tipo, titulo, mensagem, referencia_tipo=None, referencia_id=None):
    """Função auxiliar para criar notificações"""
    notificacao = Notificacao(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        referencia_tipo=referencia_tipo,
        referencia_id=referencia_id
    )
    db.session.add(notificacao)
    return notificacao

def notificar_atribuicao_cartao(cartao_id, responsavel_id, atribuidor_nome):
    """Notificar quando um cartão é atribuído a um usuário"""
    cartao = Cartao.query.get(cartao_id)
    if cartao:
        criar_notificacao(
            usuario_id=responsavel_id,
            tipo='atribuicao',
            titulo='Nova Tarefa Atribuída',
            mensagem=f'Você foi designado para o cartão "{cartao.titulo}" por {atribuidor_nome}',
            referencia_tipo='cartao',
            referencia_id=cartao_id
        )

def notificar_mudanca_status(cartao_id, novo_status, usuario_modificador):
    """Notificar quando o status de um cartão é alterado"""
    cartao = Cartao.query.get(cartao_id)
    if cartao and cartao.responsavel_id:
        status_texto = {
            'pendente': 'Pendente',
            'em_andamento': 'Em Andamento',
            'aprovado': 'Em Aprovação',
            'concluido': 'Concluído'
        }.get(novo_status, novo_status)
        
        criar_notificacao(
            usuario_id=cartao.responsavel_id,
            tipo='mudanca_status',
            titulo='Status Alterado',
            mensagem=f'O cartão "{cartao.titulo}" foi movido para "{status_texto}" por {usuario_modificador}',
            referencia_tipo='cartao',
            referencia_id=cartao_id
        )

def notificar_comentario(cartao_id, comentario_autor, comentario_texto):
    """Notificar quando um comentário é adicionado a um cartão"""
    cartao = Cartao.query.get(cartao_id)
    if cartao and cartao.responsavel_id:
        criar_notificacao(
            usuario_id=cartao.responsavel_id,
            tipo='comentario',
            titulo='Novo Comentário',
            mensagem=f'{comentario_autor} comentou no cartão "{cartao.titulo}": {comentario_texto[:100]}...',
            referencia_tipo='cartao',
            referencia_id=cartao_id
        )

