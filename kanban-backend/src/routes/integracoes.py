from flask import Blueprint, request, jsonify, session
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from src.models.user import db, Cartao, User, Cliente

integracoes_bp = Blueprint('integracoes', __name__)

# Configurações de integração (em produção, usar variáveis de ambiente)
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

@integracoes_bp.route('/integracoes/slack/webhook', methods=['POST'])
def configurar_slack_webhook():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_permissao = session.get('user_permissao')
    if user_permissao != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.get_json()
    webhook_url = data.get('webhook_url')
    
    if not webhook_url:
        return jsonify({'error': 'URL do webhook é obrigatória'}), 400
    
    # Testar webhook
    try:
        test_message = {
            "text": "🎉 Integração com Slack configurada com sucesso!",
            "username": "Sistema Kanban",
            "icon_emoji": ":kanban:"
        }
        
        response = requests.post(webhook_url, json=test_message, timeout=10)
        
        if response.status_code == 200:
            # Salvar configuração (em produção, criptografar e salvar no banco)
            # global SLACK_WEBHOOK_URL
            # SLACK_WEBHOOK_URL = webhook_url
            
            return jsonify({
                'message': 'Webhook do Slack configurado com sucesso',
                'status': 'ativo'
            })
        else:
            return jsonify({
                'error': 'Falha ao testar webhook',
                'status_code': response.status_code
            }), 400
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Erro ao conectar com Slack: {str(e)}'}), 400

@integracoes_bp.route('/integracoes/slack/notificar', methods=['POST'])
def notificar_slack():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    if not SLACK_WEBHOOK_URL:
        return jsonify({'error': 'Webhook do Slack não configurado'}), 400
    
    data = request.get_json()
    cartao_id = data.get('cartao_id')
    evento = data.get('evento')  # 'criado', 'movido', 'vencendo', 'vencido'
    
    if not cartao_id or not evento:
        return jsonify({'error': 'cartao_id e evento são obrigatórios'}), 400
    
    cartao = Cartao.query.get_or_404(cartao_id)
    
    # Preparar mensagem baseada no evento
    messages = {
        'criado': {
            'text': f"📝 *Novo cartão criado*\n*{cartao.titulo}*\nResponsável: {cartao.responsavel.nome if cartao.responsavel else 'Não definido'}\nCliente: {cartao.cliente.nome if cartao.cliente else 'Não definido'}",
            'color': 'good'
        },
        'movido': {
            'text': f"🔄 *Cartão movido*\n*{cartao.titulo}*\nNovo status: {cartao.status.replace('_', ' ').title()}\nResponsável: {cartao.responsavel.nome if cartao.responsavel else 'Não definido'}",
            'color': 'warning'
        },
        'vencendo': {
            'text': f"⏰ *Cartão vencendo*\n*{cartao.titulo}*\nPrazo: {cartao.prazo_entrega.strftime('%d/%m/%Y') if cartao.prazo_entrega else 'Não definido'}\nResponsável: {cartao.responsavel.nome if cartao.responsavel else 'Não definido'}",
            'color': 'warning'
        },
        'vencido': {
            'text': f"🚨 *Cartão vencido*\n*{cartao.titulo}*\nPrazo: {cartao.prazo_entrega.strftime('%d/%m/%Y') if cartao.prazo_entrega else 'Não definido'}\nResponsável: {cartao.responsavel.nome if cartao.responsavel else 'Não definido'}",
            'color': 'danger'
        }
    }
    
    message_data = messages.get(evento)
    if not message_data:
        return jsonify({'error': 'Evento inválido'}), 400
    
    slack_message = {
        "username": "Sistema Kanban",
        "icon_emoji": ":kanban:",
        "attachments": [
            {
                "color": message_data['color'],
                "text": message_data['text'],
                "footer": "Sistema Kanban",
                "ts": int(datetime.utcnow().timestamp())
            }
        ]
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=slack_message, timeout=10)
        
        if response.status_code == 200:
            return jsonify({'message': 'Notificação enviada para Slack'})
        else:
            return jsonify({
                'error': 'Falha ao enviar notificação',
                'status_code': response.status_code
            }), 400
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Erro ao enviar para Slack: {str(e)}'}), 400

@integracoes_bp.route('/integracoes/email/configurar', methods=['POST'])
def configurar_email():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_permissao = session.get('user_permissao')
    if user_permissao != 'Gestor Geral':
        return jsonify({'error': 'Permissão negada'}), 403
    
    data = request.get_json()
    smtp_server = data.get('smtp_server', SMTP_SERVER)
    smtp_port = data.get('smtp_port', SMTP_PORT)
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    # Testar configuração SMTP
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        
        # Enviar email de teste
        test_msg = MIMEMultipart()
        test_msg['From'] = username
        test_msg['To'] = username
        test_msg['Subject'] = "Teste de Configuração - Sistema Kanban"
        
        body = """
        Olá!
        
        Este é um email de teste para confirmar que a integração de email do Sistema Kanban foi configurada corretamente.
        
        Atenciosamente,
        Sistema Kanban
        """
        
        test_msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server.send_message(test_msg)
        server.quit()
        
        # Salvar configuração (em produção, criptografar e salvar no banco)
        # global SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
        # SMTP_SERVER = smtp_server
        # SMTP_PORT = smtp_port
        # SMTP_USERNAME = username
        # SMTP_PASSWORD = password
        
        return jsonify({
            'message': 'Configuração de email salva e testada com sucesso',
            'status': 'ativo'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao configurar email: {str(e)}'}), 400

@integracoes_bp.route('/integracoes/email/enviar', methods=['POST'])
def enviar_email():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return jsonify({'error': 'Email não configurado'}), 400
    
    data = request.get_json()
    destinatario = data.get('destinatario')
    assunto = data.get('assunto')
    corpo = data.get('corpo')
    cartao_id = data.get('cartao_id')
    
    if not destinatario or not assunto or not corpo:
        return jsonify({'error': 'Destinatário, assunto e corpo são obrigatórios'}), 400
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = destinatario
        msg['Subject'] = assunto
        
        # Se cartao_id for fornecido, incluir informações do cartão
        if cartao_id:
            cartao = Cartao.query.get(cartao_id)
            if cartao:
                corpo += f"""
                
                ---
                Detalhes do Cartão:
                Título: {cartao.titulo}
                Status: {cartao.status.replace('_', ' ').title()}
                Responsável: {cartao.responsavel.nome if cartao.responsavel else 'Não definido'}
                Cliente: {cartao.cliente.nome if cartao.cliente else 'Não definido'}
                Prazo: {cartao.prazo_entrega.strftime('%d/%m/%Y') if cartao.prazo_entrega else 'Não definido'}
                """
        
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        server.send_message(msg)
        server.quit()
        
        return jsonify({'message': 'Email enviado com sucesso'})
        
    except Exception as e:
        return jsonify({'error': f'Erro ao enviar email: {str(e)}'}), 400

@integracoes_bp.route('/integracoes/webhook/receber', methods=['POST'])
def receber_webhook():
    """Endpoint para receber webhooks de sistemas externos"""
    data = request.get_json()
    headers = dict(request.headers)
    
    # Log do webhook recebido (em produção, usar logging adequado)
    webhook_log = {
        'timestamp': datetime.utcnow().isoformat(),
        'headers': headers,
        'data': data,
        'ip': request.remote_addr
    }
    
    # Processar webhook baseado no tipo/origem
    origem = headers.get('X-Webhook-Source', 'unknown')
    
    if origem == 'external-system':
        # Processar webhook de sistema externo
        # Exemplo: criar cartão automaticamente
        if data.get('action') == 'create_task':
            try:
                # Criar cartão baseado nos dados do webhook
                novo_cartao = Cartao(
                    titulo=data.get('title', 'Tarefa Externa'),
                    descricao=data.get('description', ''),
                    status='pendente',
                    data_criacao=datetime.utcnow()
                )
                
                # Definir responsável se fornecido
                if data.get('assignee_email'):
                    responsavel = User.query.filter_by(email=data['assignee_email']).first()
                    if responsavel:
                        novo_cartao.responsavel_id = responsavel.id
                
                db.session.add(novo_cartao)
                db.session.commit()
                
                return jsonify({
                    'message': 'Cartão criado via webhook',
                    'cartao_id': novo_cartao.id
                })
                
            except Exception as e:
                return jsonify({'error': f'Erro ao processar webhook: {str(e)}'}), 400
    
    return jsonify({
        'message': 'Webhook recebido',
        'timestamp': webhook_log['timestamp']
    })

@integracoes_bp.route('/integracoes/status', methods=['GET'])
def status_integracoes():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    return jsonify({
        'slack': {
            'configurado': bool(SLACK_WEBHOOK_URL),
            'status': 'ativo' if SLACK_WEBHOOK_URL else 'inativo'
        },
        'email': {
            'configurado': bool(SMTP_USERNAME and SMTP_PASSWORD),
            'status': 'ativo' if SMTP_USERNAME and SMTP_PASSWORD else 'inativo',
            'servidor': SMTP_SERVER if SMTP_USERNAME else None
        },
        'webhook': {
            'endpoint': '/api/integracoes/webhook/receber',
            'metodos': ['POST'],
            'status': 'ativo'
        }
    })

def notificar_integracao_automatica(cartao_id, evento):
    """Função auxiliar para notificar integrações automaticamente"""
    if SLACK_WEBHOOK_URL:
        try:
            # Notificar Slack automaticamente
            requests.post(
                f"http://localhost:5001/api/integracoes/slack/notificar",
                json={'cartao_id': cartao_id, 'evento': evento},
                timeout=5
            )
        except:
            pass  # Falha silenciosa para não interromper o fluxo principal

