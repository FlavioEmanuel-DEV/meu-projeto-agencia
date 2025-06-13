from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from src.models.user import db, User, Cartao, Quadro, Cliente, Coluna
from sqlalchemy import func, and_, or_
import json

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorios/dashboard', methods=['GET'])
def dashboard_relatorio():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    # Filtros de data
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    if not data_inicio:
        data_inicio = (datetime.utcnow() - timedelta(days=30)).date()
    else:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    
    if not data_fim:
        data_fim = datetime.utcnow().date()
    else:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
    
    # Query base para cartões
    cartoes_query = Cartao.query.filter(
        Cartao.data_criacao >= data_inicio,
        Cartao.data_criacao <= data_fim + timedelta(days=1)
    )
    
    # Filtrar por setor se não for gestor geral
    if user_permissao != 'Gestor Geral':
        quadros_setor = Quadro.query.filter_by(setor=user_setor).all()
        quadro_ids = [q.id for q in quadros_setor]
        colunas_setor = Coluna.query.filter(Coluna.quadro_id.in_(quadro_ids)).all()
        coluna_ids = [c.id for c in colunas_setor]
        cartoes_query = cartoes_query.filter(Cartao.coluna_id.in_(coluna_ids))
    
    # Estatísticas gerais
    total_cartoes = cartoes_query.count()
    cartoes_concluidos = cartoes_query.filter_by(status='concluido').count()
    cartoes_em_andamento = cartoes_query.filter_by(status='em_andamento').count()
    cartoes_pendentes = cartoes_query.filter_by(status='pendente').count()
    cartoes_aprovacao = cartoes_query.filter_by(status='aprovado').count()
    
    # Cartões por status
    status_stats = {
        'pendente': cartoes_pendentes,
        'em_andamento': cartoes_em_andamento,
        'aprovado': cartoes_aprovacao,
        'concluido': cartoes_concluidos
    }
    
    # Produtividade por usuário
    produtividade_usuarios = db.session.query(
        User.nome,
        User.setor,
        func.count(Cartao.id).label('total_cartoes'),
        func.sum(func.case([(Cartao.status == 'concluido', 1)], else_=0)).label('concluidos'),
        func.sum(func.case([(Cartao.status == 'em_andamento', 1)], else_=0)).label('em_andamento')
    ).join(Cartao, User.id == Cartao.responsavel_id)\
     .filter(
         Cartao.data_criacao >= data_inicio,
         Cartao.data_criacao <= data_fim + timedelta(days=1)
     )
    
    if user_permissao != 'Gestor Geral':
        produtividade_usuarios = produtividade_usuarios.filter(User.setor == user_setor)
    
    produtividade_usuarios = produtividade_usuarios.group_by(User.id).all()
    
    # Cartões por setor
    cartoes_por_setor = db.session.query(
        Quadro.setor,
        func.count(Cartao.id).label('total'),
        func.sum(func.case([(Cartao.status == 'concluido', 1)], else_=0)).label('concluidos')
    ).join(Coluna, Quadro.id == Coluna.quadro_id)\
     .join(Cartao, Coluna.id == Cartao.coluna_id)\
     .filter(
         Cartao.data_criacao >= data_inicio,
         Cartao.data_criacao <= data_fim + timedelta(days=1)
     )
    
    if user_permissao != 'Gestor Geral':
        cartoes_por_setor = cartoes_por_setor.filter(Quadro.setor == user_setor)
    
    cartoes_por_setor = cartoes_por_setor.group_by(Quadro.setor).all()
    
    # Cartões por cliente
    cartoes_por_cliente = db.session.query(
        Cliente.nome,
        func.count(Cartao.id).label('total'),
        func.sum(func.case([(Cartao.status == 'concluido', 1)], else_=0)).label('concluidos')
    ).join(Cartao, Cliente.id == Cartao.cliente_id)\
     .filter(
         Cartao.data_criacao >= data_inicio,
         Cartao.data_criacao <= data_fim + timedelta(days=1)
     )
    
    if user_permissao != 'Gestor Geral':
        quadros_setor = Quadro.query.filter_by(setor=user_setor).all()
        quadro_ids = [q.id for q in quadros_setor]
        colunas_setor = Coluna.query.filter(Coluna.quadro_id.in_(quadro_ids)).all()
        coluna_ids = [c.id for c in colunas_setor]
        cartoes_por_cliente = cartoes_por_cliente.filter(Cartao.coluna_id.in_(coluna_ids))
    
    cartoes_por_cliente = cartoes_por_cliente.group_by(Cliente.id).all()
    
    # Cartões próximos do prazo
    hoje = datetime.utcnow().date()
    cartoes_prazo_urgente = cartoes_query.filter(
        and_(
            Cartao.prazo_entrega <= hoje + timedelta(days=2),
            Cartao.prazo_entrega >= hoje,
            Cartao.status.in_(['pendente', 'em_andamento'])
        )
    ).count()
    
    # Taxa de conclusão
    taxa_conclusao = (cartoes_concluidos / total_cartoes * 100) if total_cartoes > 0 else 0
    
    # Tempo médio de conclusão (aproximado)
    cartoes_concluidos_obj = cartoes_query.filter_by(status='concluido').all()
    tempo_medio_conclusao = 0
    if cartoes_concluidos_obj:
        tempos = []
        for cartao in cartoes_concluidos_obj:
            if cartao.data_atualizacao and cartao.data_criacao:
                tempo = (cartao.data_atualizacao - cartao.data_criacao).days
                tempos.append(tempo)
        tempo_medio_conclusao = sum(tempos) / len(tempos) if tempos else 0
    
    return jsonify({
        'periodo': {
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat()
        },
        'resumo': {
            'total_cartoes': total_cartoes,
            'cartoes_concluidos': cartoes_concluidos,
            'cartoes_em_andamento': cartoes_em_andamento,
            'cartoes_pendentes': cartoes_pendentes,
            'cartoes_aprovacao': cartoes_aprovacao,
            'cartoes_prazo_urgente': cartoes_prazo_urgente,
            'taxa_conclusao': round(taxa_conclusao, 1),
            'tempo_medio_conclusao': round(tempo_medio_conclusao, 1)
        },
        'status_stats': status_stats,
        'produtividade_usuarios': [
            {
                'nome': p.nome,
                'setor': p.setor,
                'total_cartoes': p.total_cartoes,
                'concluidos': p.concluidos or 0,
                'em_andamento': p.em_andamento or 0,
                'taxa_conclusao': round((p.concluidos or 0) / p.total_cartoes * 100, 1) if p.total_cartoes > 0 else 0
            }
            for p in produtividade_usuarios
        ],
        'cartoes_por_setor': [
            {
                'setor': s.setor,
                'total': s.total,
                'concluidos': s.concluidos or 0,
                'taxa_conclusao': round((s.concluidos or 0) / s.total * 100, 1) if s.total > 0 else 0
            }
            for s in cartoes_por_setor
        ],
        'cartoes_por_cliente': [
            {
                'cliente': c.nome,
                'total': c.total,
                'concluidos': c.concluidos or 0,
                'taxa_conclusao': round((c.concluidos or 0) / c.total * 100, 1) if c.total > 0 else 0
            }
            for c in cartoes_por_cliente
        ]
    })

@relatorios_bp.route('/relatorios/produtividade', methods=['GET'])
def relatorio_produtividade():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    # Parâmetros
    periodo = request.args.get('periodo', '30')  # dias
    usuario_id = request.args.get('usuario_id')
    
    data_inicio = datetime.utcnow() - timedelta(days=int(periodo))
    
    # Query base
    query = db.session.query(
        User.id,
        User.nome,
        User.setor,
        func.count(Cartao.id).label('total_cartoes'),
        func.sum(func.case([(Cartao.status == 'concluido', 1)], else_=0)).label('concluidos'),
        func.sum(func.case([(Cartao.status == 'em_andamento', 1)], else_=0)).label('em_andamento'),
        func.sum(func.case([(Cartao.status == 'pendente', 1)], else_=0)).label('pendentes'),
        func.avg(
            func.case([
                (Cartao.status == 'concluido', 
                 func.julianday(Cartao.data_atualizacao) - func.julianday(Cartao.data_criacao))
            ])
        ).label('tempo_medio_conclusao')
    ).join(Cartao, User.id == Cartao.responsavel_id)\
     .filter(Cartao.data_criacao >= data_inicio)
    
    # Filtros
    if user_permissao != 'Gestor Geral':
        query = query.filter(User.setor == user_setor)
    
    if usuario_id:
        query = query.filter(User.id == usuario_id)
    
    resultados = query.group_by(User.id).all()
    
    # Calcular rankings
    usuarios_produtividade = []
    for r in resultados:
        taxa_conclusao = (r.concluidos or 0) / r.total_cartoes * 100 if r.total_cartoes > 0 else 0
        tempo_medio = r.tempo_medio_conclusao or 0
        
        usuarios_produtividade.append({
            'usuario_id': r.id,
            'nome': r.nome,
            'setor': r.setor,
            'total_cartoes': r.total_cartoes,
            'concluidos': r.concluidos or 0,
            'em_andamento': r.em_andamento or 0,
            'pendentes': r.pendentes or 0,
            'taxa_conclusao': round(taxa_conclusao, 1),
            'tempo_medio_conclusao': round(tempo_medio, 1)
        })
    
    # Ordenar por taxa de conclusão
    usuarios_produtividade.sort(key=lambda x: x['taxa_conclusao'], reverse=True)
    
    return jsonify({
        'periodo_dias': int(periodo),
        'usuarios': usuarios_produtividade
    })

@relatorios_bp.route('/relatorios/prazos', methods=['GET'])
def relatorio_prazos():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_setor = session.get('user_setor')
    user_permissao = session.get('user_permissao')
    
    hoje = datetime.utcnow().date()
    
    # Query base
    cartoes_query = Cartao.query.filter(Cartao.prazo_entrega.isnot(None))
    
    # Filtrar por setor se necessário
    if user_permissao != 'Gestor Geral':
        quadros_setor = Quadro.query.filter_by(setor=user_setor).all()
        quadro_ids = [q.id for q in quadros_setor]
        colunas_setor = Coluna.query.filter(Coluna.quadro_id.in_(quadro_ids)).all()
        coluna_ids = [c.id for c in colunas_setor]
        cartoes_query = cartoes_query.filter(Cartao.coluna_id.in_(coluna_ids))
    
    # Cartões vencidos
    cartoes_vencidos = cartoes_query.filter(
        and_(
            Cartao.prazo_entrega < hoje,
            Cartao.status.in_(['pendente', 'em_andamento', 'aprovado'])
        )
    ).all()
    
    # Cartões vencendo hoje
    cartoes_vencendo_hoje = cartoes_query.filter(
        and_(
            Cartao.prazo_entrega == hoje,
            Cartao.status.in_(['pendente', 'em_andamento', 'aprovado'])
        )
    ).all()
    
    # Cartões vencendo em 3 dias
    cartoes_vencendo_3_dias = cartoes_query.filter(
        and_(
            Cartao.prazo_entrega <= hoje + timedelta(days=3),
            Cartao.prazo_entrega > hoje,
            Cartao.status.in_(['pendente', 'em_andamento', 'aprovado'])
        )
    ).all()
    
    # Cartões vencendo em 7 dias
    cartoes_vencendo_7_dias = cartoes_query.filter(
        and_(
            Cartao.prazo_entrega <= hoje + timedelta(days=7),
            Cartao.prazo_entrega > hoje + timedelta(days=3),
            Cartao.status.in_(['pendente', 'em_andamento', 'aprovado'])
        )
    ).all()
    
    def cartao_to_dict(cartao):
        return {
            'id': cartao.id,
            'titulo': cartao.titulo,
            'prazo_entrega': cartao.prazo_entrega.isoformat() if cartao.prazo_entrega else None,
            'status': cartao.status,
            'responsavel_nome': cartao.responsavel.nome if cartao.responsavel else None,
            'cliente_nome': cartao.cliente.nome if cartao.cliente else None,
            'dias_restantes': (cartao.prazo_entrega - hoje).days if cartao.prazo_entrega else None
        }
    
    return jsonify({
        'data_referencia': hoje.isoformat(),
        'vencidos': [cartao_to_dict(c) for c in cartoes_vencidos],
        'vencendo_hoje': [cartao_to_dict(c) for c in cartoes_vencendo_hoje],
        'vencendo_3_dias': [cartao_to_dict(c) for c in cartoes_vencendo_3_dias],
        'vencendo_7_dias': [cartao_to_dict(c) for c in cartoes_vencendo_7_dias],
        'resumo': {
            'total_vencidos': len(cartoes_vencidos),
            'total_vencendo_hoje': len(cartoes_vencendo_hoje),
            'total_vencendo_3_dias': len(cartoes_vencendo_3_dias),
            'total_vencendo_7_dias': len(cartoes_vencendo_7_dias)
        }
    })

@relatorios_bp.route('/relatorios/exportar', methods=['POST'])
def exportar_relatorio():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.get_json()
    tipo_relatorio = data.get('tipo')  # 'dashboard', 'produtividade', 'prazos'
    formato = data.get('formato', 'json')  # 'json', 'csv'
    
    # Por enquanto, retornar apenas JSON
    # Em uma implementação completa, seria gerado CSV ou PDF
    
    if tipo_relatorio == 'dashboard':
        relatorio_data = dashboard_relatorio()
    elif tipo_relatorio == 'produtividade':
        relatorio_data = relatorio_produtividade()
    elif tipo_relatorio == 'prazos':
        relatorio_data = relatorio_prazos()
    else:
        return jsonify({'error': 'Tipo de relatório inválido'}), 400
    
    return jsonify({
        'tipo': tipo_relatorio,
        'formato': formato,
        'data_exportacao': datetime.utcnow().isoformat(),
        'dados': relatorio_data.get_json()
    })

