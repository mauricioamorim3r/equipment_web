from flask import Blueprint, request, jsonify
from src.models.database import db, Certificado, Equipamento, StatusCertificadoIncerteza
from sqlalchemy import or_
from datetime import datetime

certificados_bp = Blueprint('certificados', __name__)

@certificados_bp.route('/', methods=['GET'])
def listar_certificados():
    """Listar todos os certificados com filtros opcionais"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        numero_serie = request.args.get('numero_serie', '')
        status_id = request.args.get('status_id', type=int)
        
        query = Certificado.query
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Certificado.numero_certificado.contains(search),
                    Certificado.numero_serie_equipamento.contains(search)
                )
            )
        
        if numero_serie:
            query = query.filter(Certificado.numero_serie_equipamento == numero_serie)
        
        if status_id:
            query = query.filter(Certificado.status_certificado_id == status_id)
        
        # Ordenar por data mais recente
        query = query.order_by(Certificado.data_certificado.desc())
        
        # Paginação
        certificados_paginados = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        certificados = []
        for cert in certificados_paginados.items:
            certificado_data = {
                'id': cert.id,
                'numero_serie_equipamento': cert.numero_serie_equipamento,
                'equipamento_nome': cert.equipamento.nome_equipamento if cert.equipamento else None,
                'numero_certificado': cert.numero_certificado,
                'revisao_certificado': cert.revisao_certificado,
                'data_certificado': cert.data_certificado,
                'status_certificado': cert.status_certificado.nome if cert.status_certificado else None,
                'caminho_arquivo': cert.caminho_arquivo
            }
            certificados.append(certificado_data)
        
        return jsonify({
            'certificados': certificados,
            'total': certificados_paginados.total,
            'pages': certificados_paginados.pages,
            'current_page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@certificados_bp.route('/', methods=['POST'])
def criar_certificado():
    """Criar um novo certificado"""
    try:
        data = request.get_json()
        
        # Verificar se já existe certificado com mesmo número, série e revisão
        certificado_existente = Certificado.query.filter_by(
            numero_serie_equipamento=data['numero_serie_equipamento'],
            numero_certificado=data['numero_certificado'],
            revisao_certificado=data.get('revisao_certificado', '')
        ).first()
        
        if certificado_existente:
            return jsonify({'error': 'Certificado já existe para este equipamento'}), 400
        
        certificado = Certificado(
            numero_serie_equipamento=data['numero_serie_equipamento'],
            numero_certificado=data['numero_certificado'],
            revisao_certificado=data.get('revisao_certificado'),
            data_certificado=data['data_certificado'],
            status_certificado_id=data.get('status_certificado_id'),
            caminho_arquivo=data.get('caminho_arquivo')
        )
        
        db.session.add(certificado)
        db.session.commit()
        
        return jsonify({'message': 'Certificado criado com sucesso', 'id': certificado.id}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@certificados_bp.route('/<int:certificado_id>', methods=['GET'])
def obter_certificado(certificado_id):
    """Obter um certificado específico"""
    try:
        certificado = Certificado.query.get_or_404(certificado_id)
        
        certificado_data = {
            'id': certificado.id,
            'numero_serie_equipamento': certificado.numero_serie_equipamento,
            'equipamento_nome': certificado.equipamento.nome_equipamento if certificado.equipamento else None,
            'numero_certificado': certificado.numero_certificado,
            'revisao_certificado': certificado.revisao_certificado,
            'data_certificado': certificado.data_certificado,
            'status_certificado_id': certificado.status_certificado_id,
            'status_certificado': certificado.status_certificado.nome if certificado.status_certificado else None,
            'caminho_arquivo': certificado.caminho_arquivo
        }
        
        return jsonify(certificado_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@certificados_bp.route('/<int:certificado_id>', methods=['PUT'])
def atualizar_certificado(certificado_id):
    """Atualizar um certificado existente"""
    try:
        certificado = Certificado.query.get_or_404(certificado_id)
        data = request.get_json()
        
        # Atualizar campos
        certificado.numero_certificado = data.get('numero_certificado', certificado.numero_certificado)
        certificado.revisao_certificado = data.get('revisao_certificado', certificado.revisao_certificado)
        certificado.data_certificado = data.get('data_certificado', certificado.data_certificado)
        certificado.status_certificado_id = data.get('status_certificado_id', certificado.status_certificado_id)
        certificado.caminho_arquivo = data.get('caminho_arquivo', certificado.caminho_arquivo)
        
        db.session.commit()
        
        return jsonify({'message': 'Certificado atualizado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@certificados_bp.route('/<int:certificado_id>', methods=['DELETE'])
def deletar_certificado(certificado_id):
    """Deletar um certificado"""
    try:
        certificado = Certificado.query.get_or_404(certificado_id)
        
        db.session.delete(certificado)
        db.session.commit()
        
        return jsonify({'message': 'Certificado deletado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@certificados_bp.route('/equipamento/<numero_serie>', methods=['GET'])
def certificados_por_equipamento(numero_serie):
    """Obter todos os certificados de um equipamento específico"""
    try:
        certificados = Certificado.query.filter_by(
            numero_serie_equipamento=numero_serie
        ).order_by(Certificado.data_certificado.desc()).all()
        
        certificados_data = []
        for cert in certificados:
            certificado_data = {
                'id': cert.id,
                'numero_certificado': cert.numero_certificado,
                'revisao_certificado': cert.revisao_certificado,
                'data_certificado': cert.data_certificado,
                'status_certificado': cert.status_certificado.nome if cert.status_certificado else None,
                'caminho_arquivo': cert.caminho_arquivo
            }
            certificados_data.append(certificado_data)
        
        return jsonify({
            'certificados': certificados_data,
            'numero_serie_equipamento': numero_serie,
            'total': len(certificados_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

