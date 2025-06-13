from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(50), nullable=False)  # Social Media, Design, Tráfego Pago, Audiovisual, Comercial, Gestão
    permissao = db.Column(db.String(20), nullable=False, default='Colaborador')  # Colaborador, Gestor Geral
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cartoes_responsavel = db.relationship('Cartao', backref='responsavel_user', lazy=True, foreign_keys='Cartao.responsavel_id')
    notificacoes = db.relationship('Notificacao', backref='destinatario_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nome': self.nome,
            'setor': self.setor,
            'permissao': self.permissao,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    quadros = db.relationship('Quadro', backref='cliente', lazy=True)
    cartoes = db.relationship('Cartao', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Quadro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # Setor ou Cliente
    setor = db.Column(db.String(50))  # Social Media, Design, Tráfego Pago, Audiovisual, Comercial, Gestão
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    colunas = db.relationship('Coluna', backref='quadro', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Quadro {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'tipo': self.tipo,
            'setor': self.setor,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'colunas': [coluna.to_dict() for coluna in self.colunas]
        }

class Coluna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    ordem = db.Column(db.Integer, nullable=False, default=0)
    quadro_id = db.Column(db.Integer, db.ForeignKey('quadro.id'), nullable=False)
    
    # Relacionamentos
    cartoes = db.relationship('Cartao', backref='coluna', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Coluna {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'ordem': self.ordem,
            'quadro_id': self.quadro_id,
            'cartoes': [cartao.to_dict() for cartao in self.cartoes]
        }

class Cartao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prazo_entrega = db.Column(db.DateTime)
    checklist = db.Column(db.Text)  # JSON string
    anexos = db.Column(db.Text)  # JSON string com links do Google Drive
    comentarios_internos = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pendente')  # pendente, em_andamento, aprovado, concluido
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    coluna_id = db.Column(db.Integer, db.ForeignKey('coluna.id'), nullable=False)
    ordem = db.Column(db.Integer, nullable=False, default=0)
    historico_alteracoes = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_checklist(self):
        if self.checklist:
            try:
                return json.loads(self.checklist)
            except:
                return []
        return []

    def set_checklist(self, checklist_data):
        self.checklist = json.dumps(checklist_data)

    def get_anexos(self):
        if self.anexos:
            try:
                return json.loads(self.anexos)
            except:
                return []
        return []

    def set_anexos(self, anexos_data):
        self.anexos = json.dumps(anexos_data)

    def get_historico(self):
        if self.historico_alteracoes:
            try:
                return json.loads(self.historico_alteracoes)
            except:
                return []
        return []

    def add_historico(self, acao, usuario_id, detalhes=None):
        historico = self.get_historico()
        entrada = {
            'timestamp': datetime.utcnow().isoformat(),
            'acao': acao,
            'usuario_id': usuario_id,
            'detalhes': detalhes
        }
        historico.append(entrada)
        self.historico_alteracoes = json.dumps(historico)

    def __repr__(self):
        return f'<Cartao {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'responsavel_id': self.responsavel_id,
            'responsavel_nome': self.responsavel_user.nome if self.responsavel_user else None,
            'prazo_entrega': self.prazo_entrega.isoformat() if self.prazo_entrega else None,
            'checklist': self.get_checklist(),
            'anexos': self.get_anexos(),
            'comentarios_internos': self.comentarios_internos,
            'status': self.status,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            'coluna_id': self.coluna_id,
            'ordem': self.ordem,
            'historico_alteracoes': self.get_historico(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # email, whatsapp
    conteudo = db.Column(db.Text, nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pendente')  # pendente, enviado, lido
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Notificacao {self.tipo} para {self.destinatario_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'conteudo': self.conteudo,
            'destinatario_id': self.destinatario_id,
            'destinatario_nome': self.destinatario_user.nome if self.destinatario_user else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }

class Relatorio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # cliente, departamento, produtividade
    conteudo = db.Column(db.Text, nullable=False)  # JSON string
    periodo_inicio = db.Column(db.DateTime, nullable=False)
    periodo_fim = db.Column(db.DateTime, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    setor = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_conteudo(self):
        if self.conteudo:
            try:
                return json.loads(self.conteudo)
            except:
                return {}
        return {}

    def set_conteudo(self, conteudo_data):
        self.conteudo = json.dumps(conteudo_data)

    def __repr__(self):
        return f'<Relatorio {self.tipo} - {self.created_at}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'conteudo': self.get_conteudo(),
            'periodo_inicio': self.periodo_inicio.isoformat() if self.periodo_inicio else None,
            'periodo_fim': self.periodo_fim.isoformat() if self.periodo_fim else None,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            'setor': self.setor,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

