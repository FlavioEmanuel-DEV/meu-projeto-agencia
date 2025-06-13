#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User, Cliente, Quadro, Coluna, Cartao
from src.main import app
from datetime import datetime, timedelta

def create_sample_data():
    with app.app_context():
        # Limpar dados existentes
        db.drop_all()
        db.create_all()
        
        print("Criando usuários de exemplo...")
        
        # Criar usuários
        usuarios = [
            {
                'username': 'admin',
                'email': 'admin@agencia.com',
                'password': 'admin123',
                'nome': 'Administrador',
                'setor': 'Gestão',
                'permissao': 'Gestor Geral'
            },
            {
                'username': 'maria.social',
                'email': 'maria@agencia.com',
                'password': 'maria123',
                'nome': 'Maria Silva',
                'setor': 'Social Media',
                'permissao': 'Colaborador'
            },
            {
                'username': 'joao.design',
                'email': 'joao@agencia.com',
                'password': 'joao123',
                'nome': 'João Santos',
                'setor': 'Design',
                'permissao': 'Colaborador'
            },
            {
                'username': 'ana.trafego',
                'email': 'ana@agencia.com',
                'password': 'ana123',
                'nome': 'Ana Costa',
                'setor': 'Tráfego Pago',
                'permissao': 'Colaborador'
            },
            {
                'username': 'carlos.video',
                'email': 'carlos@agencia.com',
                'password': 'carlos123',
                'nome': 'Carlos Oliveira',
                'setor': 'Audiovisual',
                'permissao': 'Colaborador'
            },
            {
                'username': 'lucia.comercial',
                'email': 'lucia@agencia.com',
                'password': 'lucia123',
                'nome': 'Lúcia Ferreira',
                'setor': 'Comercial',
                'permissao': 'Colaborador'
            }
        ]
        
        user_objects = []
        for user_data in usuarios:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                nome=user_data['nome'],
                setor=user_data['setor'],
                permissao=user_data['permissao']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            user_objects.append(user)
        
        db.session.commit()
        print(f"Criados {len(user_objects)} usuários")
        
        # Criar clientes
        print("Criando clientes de exemplo...")
        clientes_data = [
            {
                'nome': 'Empresa ABC Ltda',
                'descricao': 'Empresa de tecnologia especializada em soluções digitais'
            },
            {
                'nome': 'Restaurante Sabor & Arte',
                'descricao': 'Rede de restaurantes com foco em culinária regional'
            },
            {
                'nome': 'Clínica Vida Saudável',
                'descricao': 'Clínica médica com especialidades diversas'
            },
            {
                'nome': 'Loja Fashion Style',
                'descricao': 'E-commerce de moda feminina e masculina'
            },
            {
                'nome': 'Academia FitLife',
                'descricao': 'Rede de academias com foco em qualidade de vida'
            }
        ]
        
        cliente_objects = []
        for cliente_data in clientes_data:
            cliente = Cliente(
                nome=cliente_data['nome'],
                descricao=cliente_data['descricao']
            )
            db.session.add(cliente)
            cliente_objects.append(cliente)
        
        db.session.commit()
        print(f"Criados {len(cliente_objects)} clientes")
        
        # Criar quadros por setor
        print("Criando quadros por setor...")
        setores = ['Social Media', 'Design', 'Tráfego Pago', 'Audiovisual', 'Comercial']
        quadro_objects = []
        
        for setor in setores:
            quadro = Quadro(
                titulo=f'Quadro {setor}',
                tipo='Setor',
                setor=setor
            )
            db.session.add(quadro)
            quadro_objects.append(quadro)
        
        # Criar alguns quadros por cliente
        for i, cliente in enumerate(cliente_objects[:3]):  # Apenas os 3 primeiros clientes
            quadro = Quadro(
                titulo=f'Projetos {cliente.nome}',
                tipo='Cliente',
                cliente_id=cliente.id
            )
            db.session.add(quadro)
            quadro_objects.append(quadro)
        
        db.session.commit()
        print(f"Criados {len(quadro_objects)} quadros")
        
        # Criar colunas padrão para cada quadro
        print("Criando colunas padrão...")
        colunas_padrao = ['A Fazer', 'Em Andamento', 'Aprovação', 'Concluído']
        coluna_objects = []
        
        for quadro in quadro_objects:
            for i, titulo_coluna in enumerate(colunas_padrao):
                coluna = Coluna(
                    titulo=titulo_coluna,
                    ordem=i,
                    quadro_id=quadro.id
                )
                db.session.add(coluna)
                coluna_objects.append(coluna)
        
        db.session.commit()
        print(f"Criadas {len(coluna_objects)} colunas")
        
        # Criar cartões de exemplo
        print("Criando cartões de exemplo...")
        cartoes_exemplo = [
            {
                'titulo': 'Criar posts para Instagram',
                'descricao': 'Desenvolver 10 posts para o feed do Instagram do cliente ABC',
                'responsavel': 'maria.social',
                'cliente': 'Empresa ABC Ltda',
                'setor': 'Social Media',
                'coluna': 'Em Andamento',
                'prazo_dias': 3
            },
            {
                'titulo': 'Design de logo',
                'descricao': 'Criar nova identidade visual para o Restaurante Sabor & Arte',
                'responsavel': 'joao.design',
                'cliente': 'Restaurante Sabor & Arte',
                'setor': 'Design',
                'coluna': 'A Fazer',
                'prazo_dias': 7
            },
            {
                'titulo': 'Campanha Google Ads',
                'descricao': 'Configurar e otimizar campanha de tráfego pago para a Clínica',
                'responsavel': 'ana.trafego',
                'cliente': 'Clínica Vida Saudável',
                'setor': 'Tráfego Pago',
                'coluna': 'Aprovação',
                'prazo_dias': 5
            },
            {
                'titulo': 'Vídeo institucional',
                'descricao': 'Produzir vídeo de apresentação da Loja Fashion Style',
                'responsavel': 'carlos.video',
                'cliente': 'Loja Fashion Style',
                'setor': 'Audiovisual',
                'coluna': 'A Fazer',
                'prazo_dias': 14
            },
            {
                'titulo': 'Proposta comercial',
                'descricao': 'Elaborar proposta para novo cliente Academia FitLife',
                'responsavel': 'lucia.comercial',
                'cliente': 'Academia FitLife',
                'setor': 'Comercial',
                'coluna': 'Em Andamento',
                'prazo_dias': 2
            },
            {
                'titulo': 'Stories promocionais',
                'descricao': 'Criar stories para promoção de fim de ano',
                'responsavel': 'maria.social',
                'cliente': 'Loja Fashion Style',
                'setor': 'Social Media',
                'coluna': 'Concluído',
                'prazo_dias': -2  # Já passou
            },
            {
                'titulo': 'Banner para site',
                'descricao': 'Desenvolver banner promocional para homepage',
                'responsavel': 'joao.design',
                'cliente': 'Empresa ABC Ltda',
                'setor': 'Design',
                'coluna': 'Aprovação',
                'prazo_dias': 1
            }
        ]
        
        for cartao_data in cartoes_exemplo:
            # Encontrar responsável
            responsavel = User.query.filter_by(username=cartao_data['responsavel']).first()
            
            # Encontrar cliente
            cliente = Cliente.query.filter_by(nome=cartao_data['cliente']).first()
            
            # Encontrar quadro do setor
            quadro = Quadro.query.filter_by(setor=cartao_data['setor'], tipo='Setor').first()
            
            # Encontrar coluna
            coluna = Coluna.query.filter_by(quadro_id=quadro.id, titulo=cartao_data['coluna']).first()
            
            if responsavel and cliente and coluna:
                cartao = Cartao(
                    titulo=cartao_data['titulo'],
                    descricao=cartao_data['descricao'],
                    responsavel_id=responsavel.id,
                    cliente_id=cliente.id,
                    coluna_id=coluna.id,
                    prazo_entrega=datetime.now() + timedelta(days=cartao_data['prazo_dias']),
                    ordem=len([c for c in coluna.cartoes]) + 1
                )
                
                # Definir status baseado na coluna
                status_map = {
                    'A Fazer': 'pendente',
                    'Em Andamento': 'em_andamento',
                    'Aprovação': 'aprovado',
                    'Concluído': 'concluido'
                }
                cartao.status = status_map.get(cartao_data['coluna'], 'pendente')
                
                # Adicionar histórico inicial
                cartao.add_historico('criado', responsavel.id, 'Cartão criado automaticamente')
                
                db.session.add(cartao)
        
        db.session.commit()
        print("Cartões de exemplo criados")
        
        print("\n=== DADOS DE TESTE CRIADOS COM SUCESSO ===")
        print("\nUsuários criados:")
        for user in User.query.all():
            print(f"- {user.username} ({user.nome}) - {user.setor} - {user.permissao}")
        
        print(f"\nClientes: {Cliente.query.count()}")
        print(f"Quadros: {Quadro.query.count()}")
        print(f"Colunas: {Coluna.query.count()}")
        print(f"Cartões: {Cartao.query.count()}")
        
        print("\n=== CREDENCIAIS DE ACESSO ===")
        print("Administrador:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nColaboradores:")
        print("  Username: maria.social | Password: maria123")
        print("  Username: joao.design | Password: joao123")
        print("  Username: ana.trafego | Password: ana123")
        print("  Username: carlos.video | Password: carlos123")
        print("  Username: lucia.comercial | Password: lucia123")

if __name__ == '__main__':
    create_sample_data()

