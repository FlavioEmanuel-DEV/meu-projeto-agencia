from flask import Blueprint, request, jsonify, session
from datetime import datetime
import openai
import os
import json
from src.models.user import db, Cartao, User, Cliente, Quadro, Coluna

ia_bp = Blueprint('ia', __name__)

# Configuração da OpenAI (em produção, usar variáveis de ambiente)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

@ia_bp.route('/ia/configurar', methods=['POST'])
def configurar_ia():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_permissao = session.get('user_permissao')
    if user_permissao != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.get_json()
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key é obrigatória'}), 400
    
    # Testar API key
    try:
        openai.api_key = api_key
        
        # Fazer uma chamada simples para testar
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Teste"}],
            max_tokens=10
        )
        
        # Salvar configuração
        global OPENAI_API_KEY
        OPENAI_API_KEY = api_key
        
        return jsonify({
            'message': 'API key configurada com sucesso',
            'status': 'ativo'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao testar API key: {str(e)}'}), 400

@ia_bp.route('/ia/sugerir-titulo', methods=['POST'])
def sugerir_titulo():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    if not OPENAI_API_KEY:
        return jsonify({'error': 'IA não configurada'}), 400
    
    data = request.get_json()
    descricao = data.get('descricao', '')
    cliente = data.get('cliente', '')
    setor = data.get('setor', '')
    
    if not descricao:
        return jsonify({'error': 'Descrição é obrigatória'}), 400
    
    try:
        prompt = f"""
        Com base nas informações abaixo, sugira 3 títulos concisos e profissionais para uma tarefa:
        
        Descrição: {descricao}
        Cliente: {cliente}
        Setor: {setor}
        
        Os títulos devem ser:
        - Claros e objetivos
        - Máximo 50 caracteres
        - Profissionais
        - Específicos para o contexto
        
        Retorne apenas os 3 títulos, um por linha, sem numeração.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        titulos = response.choices[0].message.content.strip().split('\n')
        titulos = [titulo.strip() for titulo in titulos if titulo.strip()]
        
        return jsonify({
            'titulos': titulos[:3]  # Garantir máximo 3 títulos
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar títulos: {str(e)}'}), 400

@ia_bp.route('/ia/melhorar-descricao', methods=['POST'])
def melhorar_descricao():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    if not OPENAI_API_KEY:
        return jsonify({'error': 'IA não configurada'}), 400
    
    data = request.get_json()
    descricao_original = data.get('descricao', '')
    contexto = data.get('contexto', '')
    
    if not descricao_original:
        return jsonify({'error': 'Descrição original é obrigatória'}), 400
    
    try:
        prompt = f"""
        Melhore a seguinte descrição de tarefa para torná-la mais clara, específica e acionável:
        
        Descrição original: {descricao_original}
        Contexto adicional: {contexto}
        
        A descrição melhorada deve:
        - Ser clara e específica
        - Incluir objetivos mensuráveis quando possível
        - Manter o tom profissional
        - Ser concisa mas completa
        - Incluir critérios de aceitação se relevante
        
        Retorne apenas a descrição melhorada.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5
        )
        
        descricao_melhorada = response.choices[0].message.content.strip()
        
        return jsonify({
            'descricao_melhorada': descricao_melhorada
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao melhorar descrição: {str(e)}'}), 400

@ia_bp.route('/ia/estimar-prazo', methods=['POST'])
def estimar_prazo():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    if not OPENAI_API_KEY:
        return jsonify({'error': 'IA não configurada'}), 400
    
    data = request.get_json()
    titulo = data.get('titulo', '')
    descricao = data.get('descricao', '')
    setor = data.get('setor', '')
    complexidade = data.get('complexidade', 'média')  # baixa, média, alta
    
    if not titulo and not descricao:
        return jsonify({'error': 'Título ou descrição são obrigatórios'}), 400
    
    try:
        prompt = f"""
        Com base nas informações da tarefa abaixo, estime um prazo realista para conclusão:
        
        Título: {titulo}
        Descrição: {descricao}
        Setor: {setor}
        Complexidade: {complexidade}
        
        Considere:
        - Tipo de trabalho (criativo, técnico, administrativo)
        - Complexidade indicada
        - Padrões da indústria para o setor
        - Possíveis dependências e revisões
        
        Retorne apenas um número de dias úteis (exemplo: 3, 7, 14).
        Se não for possível estimar, retorne "indefinido".
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.3
        )
        
        estimativa = response.choices[0].message.content.strip()
        
        # Tentar extrair número de dias
        try:
            dias = int(''.join(filter(str.isdigit, estimativa)))
            if dias > 0 and dias <= 365:  # Validação básica
                return jsonify({
                    'dias_estimados': dias,
                    'explicacao': f"Estimativa baseada na complexidade {complexidade} e tipo de trabalho do setor {setor}"
                })
        except:
            pass
        
        return jsonify({
            'dias_estimados': None,
            'explicacao': 'Não foi possível estimar um prazo específico para esta tarefa'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao estimar prazo: {str(e)}'}), 400

@ia_bp.route('/ia/analisar-produtividade', methods=['POST'])
def analisar_produtividade():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    if not OPENAI_API_KEY:
        return jsonify({'error': 'IA não configurada'}), 400
    
    user_permissao = session.get('user_permissao')
    if user_permissao != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.get_json()
    periodo_dias = data.get('periodo_dias', 30)
    
    try:
        # Buscar dados de produtividade
        data_inicio = datetime.utcnow() - timedelta(days=periodo_dias)
        
        # Estatísticas por usuário
        usuarios_stats = db.session.query(
            User.nome,
            User.setor,
            func.count(Cartao.id).label('total_cartoes'),
            func.sum(func.case([(Cartao.status == 'concluido', 1)], else_=0)).label('concluidos'),
            func.avg(
                func.case([
                    (Cartao.status == 'concluido', 
                     func.julianday(Cartao.data_atualizacao) - func.julianday(Cartao.data_criacao))
                ])
            ).label('tempo_medio')
        ).join(Cartao, User.id == Cartao.responsavel_id)\
         .filter(Cartao.data_criacao >= data_inicio)\
         .group_by(User.id).all()
        
        # Preparar dados para análise
        dados_produtividade = []
        for user_stat in usuarios_stats:
            taxa_conclusao = (user_stat.concluidos or 0) / user_stat.total_cartoes * 100 if user_stat.total_cartoes > 0 else 0
            dados_produtividade.append({
                'nome': user_stat.nome,
                'setor': user_stat.setor,
                'total_cartoes': user_stat.total_cartoes,
                'concluidos': user_stat.concluidos or 0,
                'taxa_conclusao': round(taxa_conclusao, 1),
                'tempo_medio': round(user_stat.tempo_medio or 0, 1)
            })
        
        prompt = f"""
        Analise os dados de produtividade da equipe abaixo e forneça insights acionáveis:
        
        Período: {periodo_dias} dias
        Dados: {json.dumps(dados_produtividade, indent=2)}
        
        Forneça uma análise que inclua:
        1. Principais insights sobre a produtividade da equipe
        2. Identificação de padrões ou tendências
        3. Recomendações específicas para melhorar a produtividade
        4. Identificação de membros que podem precisar de suporte
        5. Reconhecimento de bons desempenhos
        
        Mantenha a análise profissional e construtiva.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        analise = response.choices[0].message.content.strip()
        
        return jsonify({
            'analise': analise,
            'dados_base': dados_produtividade,
            'periodo_dias': periodo_dias
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao analisar produtividade: {str(e)}'}), 400

@ia_bp.route('/ia/sugerir-otimizacoes', methods=['POST'])
def sugerir_otimizacoes():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    if not OPENAI_API_KEY:
        return jsonify({'error': 'IA não configurada'}), 400
    
    data = request.get_json()
    quadro_id = data.get('quadro_id')
    
    if not quadro_id:
        return jsonify({'error': 'ID do quadro é obrigatório'}), 400
    
    try:
        # Buscar dados do quadro
        quadro = Quadro.query.get_or_404(quadro_id)
        
        # Estatísticas do quadro
        cartoes = []
        for coluna in quadro.colunas:
            for cartao in coluna.cartoes:
                cartoes.append({
                    'titulo': cartao.titulo,
                    'status': cartao.status,
                    'dias_criacao': (datetime.utcnow() - cartao.data_criacao).days,
                    'tem_prazo': bool(cartao.prazo_entrega),
                    'vencido': cartao.prazo_entrega < datetime.utcnow().date() if cartao.prazo_entrega else False
                })
        
        prompt = f"""
        Analise o quadro Kanban abaixo e sugira otimizações para melhorar o fluxo de trabalho:
        
        Quadro: {quadro.titulo}
        Setor: {quadro.setor}
        Total de cartões: {len(cartoes)}
        
        Dados dos cartões: {json.dumps(cartoes, indent=2)}
        
        Forneça sugestões específicas para:
        1. Melhorar o fluxo de trabalho
        2. Reduzir gargalos
        3. Otimizar a distribuição de tarefas
        4. Melhorar o cumprimento de prazos
        5. Organização das colunas/status
        
        Seja específico e prático nas recomendações.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7
        )
        
        sugestoes = response.choices[0].message.content.strip()
        
        return jsonify({
            'sugestoes': sugestoes,
            'quadro': quadro.titulo,
            'total_cartoes': len(cartoes)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar sugestões: {str(e)}'}), 400

@ia_bp.route('/ia/status', methods=['GET'])
def status_ia():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    return jsonify({
        'configurado': bool(OPENAI_API_KEY),
        'status': 'ativo' if OPENAI_API_KEY else 'inativo',
        'funcionalidades': [
            'Sugestão de títulos',
            'Melhoria de descrições',
            'Estimativa de prazos',
            'Análise de produtividade',
            'Sugestões de otimização'
        ]
    })

