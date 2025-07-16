from flask import Blueprint, request, jsonify
from src.models.database import (
    db, Fabricante, Modelo, TipoEquipamento, Polo, Instalacao, 
    Unidade, ClassificacaoPontoMedicao, NaturezaTesteAnalise, 
    StatusCertificadoIncerteza, ServicoIncerteza, CriterioAceitacao
)

configuracoes_bp = Blueprint('configuracoes', __name__)

# Rotas para Fabricantes
@configuracoes_bp.route('/fabricantes', methods=['GET'])
def listar_fabricantes():
    """Listar todos os fabricantes"""
    try:
        fabricantes = Fabricante.query.order_by(Fabricante.nome).all()
        return jsonify([{'id': f.id, 'nome': f.nome} for f in fabricantes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/fabricantes', methods=['POST'])
def criar_fabricante():
    """Criar um novo fabricante"""
    try:
        data = request.get_json()
        
        if Fabricante.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Fabricante já existe'}), 400
        
        fabricante = Fabricante(nome=data['nome'])
        db.session.add(fabricante)
        db.session.commit()
        
        return jsonify({'message': 'Fabricante criado com sucesso', 'id': fabricante.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/fabricantes/<int:fabricante_id>', methods=['PUT'])
def atualizar_fabricante(fabricante_id):
    """Atualizar um fabricante"""
    try:
        fabricante = Fabricante.query.get_or_404(fabricante_id)
        data = request.get_json()
        
        # Verificar se o novo nome já existe
        if data['nome'] != fabricante.nome:
            if Fabricante.query.filter_by(nome=data['nome']).first():
                return jsonify({'error': 'Nome do fabricante já existe'}), 400
        
        fabricante.nome = data['nome']
        db.session.commit()
        
        return jsonify({'message': 'Fabricante atualizado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/fabricantes/<int:fabricante_id>', methods=['DELETE'])
def deletar_fabricante(fabricante_id):
    """Deletar um fabricante"""
    try:
        fabricante = Fabricante.query.get_or_404(fabricante_id)
        
        # Verificar se há equipamentos usando este fabricante
        if fabricante.equipamentos:
            return jsonify({'error': 'Não é possível deletar fabricante com equipamentos associados'}), 400
        
        db.session.delete(fabricante)
        db.session.commit()
        
        return jsonify({'message': 'Fabricante deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Tipos de Equipamento
@configuracoes_bp.route('/tipos-equipamento', methods=['GET'])
def listar_tipos_equipamento():
    """Listar todos os tipos de equipamento"""
    try:
        tipos = TipoEquipamento.query.order_by(TipoEquipamento.nome).all()
        return jsonify([{'id': t.id, 'nome': t.nome} for t in tipos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/tipos-equipamento', methods=['POST'])
def criar_tipo_equipamento():
    """Criar um novo tipo de equipamento"""
    try:
        data = request.get_json()
        
        if TipoEquipamento.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Tipo de equipamento já existe'}), 400
        
        tipo = TipoEquipamento(nome=data['nome'])
        db.session.add(tipo)
        db.session.commit()
        
        return jsonify({'message': 'Tipo de equipamento criado com sucesso', 'id': tipo.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Polos
@configuracoes_bp.route('/polos', methods=['GET'])
def listar_polos():
    """Listar todos os polos"""
    try:
        polos = Polo.query.order_by(Polo.nome).all()
        return jsonify([{'id': p.id, 'nome': p.nome} for p in polos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/polos', methods=['POST'])
def criar_polo():
    """Criar um novo polo"""
    try:
        data = request.get_json()
        
        if Polo.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Polo já existe'}), 400
        
        polo = Polo(nome=data['nome'])
        db.session.add(polo)
        db.session.commit()
        
        return jsonify({'message': 'Polo criado com sucesso', 'id': polo.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Instalações
@configuracoes_bp.route('/instalacoes', methods=['GET'])
def listar_instalacoes():
    """Listar todas as instalações"""
    try:
        instalacoes = Instalacao.query.order_by(Instalacao.nome).all()
        return jsonify([{
            'id': i.id, 
            'nome': i.nome,
            'polo_id': i.polo_id,
            'polo': i.polo.nome if i.polo else None
        } for i in instalacoes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/instalacoes', methods=['POST'])
def criar_instalacao():
    """Criar uma nova instalação"""
    try:
        data = request.get_json()
        
        if Instalacao.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Instalação já existe'}), 400
        
        instalacao = Instalacao(
            nome=data['nome'],
            polo_id=data.get('polo_id')
        )
        db.session.add(instalacao)
        db.session.commit()
        
        return jsonify({'message': 'Instalação criada com sucesso', 'id': instalacao.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Unidades
@configuracoes_bp.route('/unidades', methods=['GET'])
def listar_unidades():
    """Listar todas as unidades"""
    try:
        unidades = Unidade.query.order_by(Unidade.nome).all()
        return jsonify([{'id': u.id, 'nome': u.nome} for u in unidades])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/unidades', methods=['POST'])
def criar_unidade():
    """Criar uma nova unidade"""
    try:
        data = request.get_json()
        
        if Unidade.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Unidade já existe'}), 400
        
        unidade = Unidade(nome=data['nome'])
        db.session.add(unidade)
        db.session.commit()
        
        return jsonify({'message': 'Unidade criada com sucesso', 'id': unidade.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Classificações de Ponto de Medição
@configuracoes_bp.route('/classificacoes-ponto-medicao', methods=['GET'])
def listar_classificacoes_ponto_medicao():
    """Listar todas as classificações de ponto de medição"""
    try:
        classificacoes = ClassificacaoPontoMedicao.query.order_by(ClassificacaoPontoMedicao.nome).all()
        return jsonify([{'id': c.id, 'nome': c.nome} for c in classificacoes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/classificacoes-ponto-medicao', methods=['POST'])
def criar_classificacao_ponto_medicao():
    """Criar uma nova classificação de ponto de medição"""
    try:
        data = request.get_json()
        
        if ClassificacaoPontoMedicao.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Classificação já existe'}), 400
        
        classificacao = ClassificacaoPontoMedicao(nome=data['nome'])
        db.session.add(classificacao)
        db.session.commit()
        
        return jsonify({'message': 'Classificação criada com sucesso', 'id': classificacao.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Naturezas de Teste/Análise
@configuracoes_bp.route('/naturezas-teste-analise', methods=['GET'])
def listar_naturezas_teste_analise():
    """Listar todas as naturezas de teste/análise"""
    try:
        naturezas = NaturezaTesteAnalise.query.order_by(NaturezaTesteAnalise.nome).all()
        return jsonify([{'id': n.id, 'nome': n.nome} for n in naturezas])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/naturezas-teste-analise', methods=['POST'])
def criar_natureza_teste_analise():
    """Criar uma nova natureza de teste/análise"""
    try:
        data = request.get_json()
        
        if NaturezaTesteAnalise.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Natureza já existe'}), 400
        
        natureza = NaturezaTesteAnalise(nome=data['nome'])
        db.session.add(natureza)
        db.session.commit()
        
        return jsonify({'message': 'Natureza criada com sucesso', 'id': natureza.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Status
@configuracoes_bp.route('/status', methods=['GET'])
def listar_status():
    """Listar todos os status"""
    try:
        status = StatusCertificadoIncerteza.query.order_by(StatusCertificadoIncerteza.nome).all()
        return jsonify([{'id': s.id, 'nome': s.nome} for s in status])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/status', methods=['POST'])
def criar_status():
    """Criar um novo status"""
    try:
        data = request.get_json()
        
        if StatusCertificadoIncerteza.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Status já existe'}), 400
        
        status = StatusCertificadoIncerteza(nome=data['nome'])
        db.session.add(status)
        db.session.commit()
        
        return jsonify({'message': 'Status criado com sucesso', 'id': status.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rotas para Critérios de Aceitação
@configuracoes_bp.route('/criterios-aceitacao', methods=['GET'])
def listar_criterios_aceitacao():
    """Listar todos os critérios de aceitação"""
    try:
        criterios = CriterioAceitacao.query.order_by(CriterioAceitacao.nome).all()
        return jsonify([{'id': c.id, 'nome': c.nome} for c in criterios])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@configuracoes_bp.route('/criterios-aceitacao', methods=['POST'])
def criar_criterio_aceitacao():
    """Criar um novo critério de aceitação"""
    try:
        data = request.get_json()
        
        if CriterioAceitacao.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Critério já existe'}), 400
        
        criterio = CriterioAceitacao(nome=data['nome'])
        db.session.add(criterio)
        db.session.commit()
        
        return jsonify({'message': 'Critério criado com sucesso', 'id': criterio.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Rota para obter todas as configurações de uma vez
@configuracoes_bp.route('/todas', methods=['GET'])
def obter_todas_configuracoes():
    """Obter todas as configurações em uma única requisição"""
    try:
        return jsonify({
            'fabricantes': [{'id': f.id, 'nome': f.nome} for f in Fabricante.query.order_by(Fabricante.nome).all()],
            'tipos_equipamento': [{'id': t.id, 'nome': t.nome} for t in TipoEquipamento.query.order_by(TipoEquipamento.nome).all()],
            'polos': [{'id': p.id, 'nome': p.nome} for p in Polo.query.order_by(Polo.nome).all()],
            'instalacoes': [{'id': i.id, 'nome': i.nome, 'polo_id': i.polo_id} for i in Instalacao.query.order_by(Instalacao.nome).all()],
            'unidades': [{'id': u.id, 'nome': u.nome} for u in Unidade.query.order_by(Unidade.nome).all()],
            'classificacoes_ponto_medicao': [{'id': c.id, 'nome': c.nome} for c in ClassificacaoPontoMedicao.query.order_by(ClassificacaoPontoMedicao.nome).all()],
            'naturezas_teste_analise': [{'id': n.id, 'nome': n.nome} for n in NaturezaTesteAnalise.query.order_by(NaturezaTesteAnalise.nome).all()],
            'status': [{'id': s.id, 'nome': s.nome} for s in StatusCertificadoIncerteza.query.order_by(StatusCertificadoIncerteza.nome).all()],
            'criterios_aceitacao': [{'id': c.id, 'nome': c.nome} for c in CriterioAceitacao.query.order_by(CriterioAceitacao.nome).all()]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

