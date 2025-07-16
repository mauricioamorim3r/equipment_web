from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from models.database import db
import os
import pandas as pd
from datetime import datetime, timedelta

def create_app():
    app = Flask(__name__, static_folder='static')
    
    # Configurações
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configurar CORS para permitir requisições do frontend
    CORS(app, origins="*")
    
    # Inicializar banco de dados
    db.init_app(app)
    
    # Registrar blueprints
    from routes.equipamentos import equipamentos_bp
    from routes.pontos_medicao import pontos_medicao_bp
    from routes.certificados import certificados_bp
    from routes.configuracoes import configuracoes_bp
    from routes.dashboard import dashboard_bp
    from routes.importacao import importacao_bp
    
    app.register_blueprint(equipamentos_bp, url_prefix='/api/equipamentos')
    app.register_blueprint(pontos_medicao_bp, url_prefix='/api/pontos-medicao')
    app.register_blueprint(certificados_bp, url_prefix='/api/certificados')
    app.register_blueprint(configuracoes_bp, url_prefix='/api/configuracoes')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(importacao_bp, url_prefix='/api/importacao')
    
    # Rota principal para servir o frontend
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    # Rota para servir arquivos estáticos
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)
    
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
        # Inserir dados iniciais se necessário
        insert_initial_data()
    
    return app

def insert_initial_data():
    """Inserir dados iniciais no banco de dados"""
    from models.database import (
        Fabricante, TipoEquipamento, Polo, Instalacao, Unidade,
        ClassificacaoPontoMedicao, NaturezaTesteAnalise, 
        StatusCertificadoIncerteza, ServicoIncerteza, CriterioAceitacao
    )
    
    # Verificar se já existem dados
    if Fabricante.query.first():
        return
    
    # Dados iniciais para fabricantes
    fabricantes_iniciais = [
        'Emerson', 'Honeywell', 'Yokogawa', 'Endress+Hauser', 
        'ABB', 'Siemens', 'Schneider Electric', 'Krohne'
    ]
    
    for nome in fabricantes_iniciais:
        fabricante = Fabricante(nome=nome)
        db.session.add(fabricante)
    
    # Dados iniciais para tipos de equipamento
    tipos_equipamento_iniciais = [
        'Medidor de Vazão', 'Transmissor de Pressão', 'Transmissor de Temperatura',
        'Medidor Ultrassônico', 'Placa de Orifício', 'Trecho Reto',
        'Computador de Vazão', 'Densímetro', 'Cromatógrafo'
    ]
    
    for nome in tipos_equipamento_iniciais:
        tipo = TipoEquipamento(nome=nome)
        db.session.add(tipo)
    
    # Dados iniciais para polos
    polos_iniciais = ['Polo Norte', 'Polo Sul', 'Polo Leste', 'Polo Oeste']
    
    for nome in polos_iniciais:
        polo = Polo(nome=nome)
        db.session.add(polo)
    
    # Dados iniciais para unidades
    unidades_iniciais = [
        '°C', 'bar', 'm³/h', 'kg/m³', 'Pa', 'kPa', 'MPa',
        'L/min', 'm³/s', 'kg/h', '%', 'ppm', 'V', 'mA'
    ]
    
    for nome in unidades_iniciais:
        unidade = Unidade(nome=nome)
        db.session.add(unidade)
    
    # Dados iniciais para classificações de ponto de medição
    classificacoes_iniciais = [
        'Fiscal', 'Operacional', 'Transferência de Custódia',
        'Alocação', 'Controle de Processo'
    ]
    
    for nome in classificacoes_iniciais:
        classificacao = ClassificacaoPontoMedicao(nome=nome)
        db.session.add(classificacao)
    
    # Dados iniciais para naturezas de teste/análise
    naturezas_iniciais = [
        'Petróleo', 'Gás Natural', 'Água Produzida', 'Condensado',
        'GLP', 'Óleo Combustível'
    ]
    
    for nome in naturezas_iniciais:
        natureza = NaturezaTesteAnalise(nome=nome)
        db.session.add(natureza)
    
    # Dados iniciais para status
    status_iniciais = [
        'Vigente', 'Vencido', 'Aprovado', 'Reprovado', 'Pendente',
        'Em Análise', 'Cancelado'
    ]
    
    for nome in status_iniciais:
        status = StatusCertificadoIncerteza(nome=nome)
        db.session.add(status)
    
    # Dados iniciais para serviços de incerteza
    servicos_iniciais = [
        'Calibração', 'Verificação', 'Manutenção', 'Inspeção',
        'Análise de Incerteza', 'Validação'
    ]
    
    for nome in servicos_iniciais:
        servico = ServicoIncerteza(nome=nome)
        db.session.add(servico)
    
    # Dados iniciais para critérios de aceitação
    criterios_iniciais = [
        '±0.1%', '±0.2%', '±0.5%', '±1.0%', '±2.0%',
        'Conforme Norma', 'Especificação do Fabricante'
    ]
    
    for nome in criterios_iniciais:
        criterio = CriterioAceitacao(nome=nome)
        db.session.add(criterio)
    
    try:
        db.session.commit()
        print("Dados iniciais inseridos com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inserir dados iniciais: {e}")

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

