from flask import Blueprint, request, jsonify
from models.database import db, Equipamento, Fabricante, TipoEquipamento, Unidade
from sqlalchemy import or_
from datetime import datetimequipamentos_bp = Blueprint('equipamentos', __name__)

@equipamentos_bp.route('/', methods=['GET'])
def listar_equipamentos():
    """Listar todos os equipamentos com filtros opcionais"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        fabricante_id = request.args.get('fabricante_id', type=int)
        tipo_equipamento_id = request.args.get('tipo_equipamento_id', type=int)
        
        query = Equipamento.query
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Equipamento.numero_serie.contains(search),
                    Equipamento.tag_equipamento.contains(search),
                    Equipamento.nome_equipamento.contains(search)
                )
            )
        
        if fabricante_id:
            query = query.filter(Equipamento.fabricante_id == fabricante_id)
        
        if tipo_equipamento_id:
            query = query.filter(Equipamento.tipo_equipamento_id == tipo_equipamento_id)
        
        # Paginação
        equipamentos_paginados = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        equipamentos = []
        for equip in equipamentos_paginados.items:
            equipamento_data = {
                'numero_serie': equip.numero_serie,
                'tag_equipamento': equip.tag_equipamento,
                'nome_equipamento': equip.nome_equipamento,
                'fabricante': equip.fabricante.nome if equip.fabricante else None,
                'modelo': equip.modelo.nome if equip.modelo else None,
                'tipo_equipamento': equip.tipo_equipamento.nome if equip.tipo_equipamento else None,
                'unidade': equip.unidade.nome if equip.unidade else None,
                'resolucao': equip.resolucao,
                'faixa_minima_equipamento': equip.faixa_minima_equipamento,
                'faixa_maxima_equipamento': equip.faixa_maxima_equipamento,
                'faixa_minima_pam': equip.faixa_minima_pam,
                'faixa_maxima_pam': equip.faixa_maxima_pam,
                'faixa_minima_calibrada': equip.faixa_minima_calibrada,
                'faixa_maxima_calibrada': equip.faixa_maxima_calibrada,
                'condicoes_ambientais': equip.condicoes_ambientais,
                'erro_maximo_admissivel': equip.erro_maximo_admissivel,
                'criterio_aceitacao': equip.criterio_aceitacao.nome if equip.criterio_aceitacao else None,
                'software_versao': equip.software_versao
            }
            equipamentos.append(equipamento_data)
        
        return jsonify({
            'equipamentos': equipamentos,
            'total': equipamentos_paginados.total,
            'pages': equipamentos_paginados.pages,
            'current_page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipamentos_bp.route('/', methods=['POST'])
def criar_equipamento():
    """Criar um novo equipamento"""
    try:
        data = request.get_json()
        
        # Verificar se o número de série já existe
        if Equipamento.query.filter_by(numero_serie=data['numero_serie']).first():
            return jsonify({'error': 'Número de série já existe'}), 400
        
        # Verificar se a TAG já existe (se fornecida)
        if data.get('tag_equipamento'):
            if Equipamento.query.filter_by(tag_equipamento=data['tag_equipamento']).first():
                return jsonify({'error': 'TAG do equipamento já existe'}), 400
        
        equipamento = Equipamento(
            numero_serie=data['numero_serie'],
            tag_equipamento=data.get('tag_equipamento'),
            fabricante_id=data.get('fabricante_id'),
            modelo_id=data.get('modelo_id'),
            nome_equipamento=data['nome_equipamento'],
            tipo_equipamento_id=data.get('tipo_equipamento_id'),
            unidade_id=data.get('unidade_id'),
            resolucao=data.get('resolucao'),
            faixa_minima_equipamento=data.get('faixa_minima_equipamento'),
            faixa_maxima_equipamento=data.get('faixa_maxima_equipamento'),
            faixa_minima_pam=data.get('faixa_minima_pam'),
            faixa_maxima_pam=data.get('faixa_maxima_pam'),
            faixa_minima_calibrada=data.get('faixa_minima_calibrada'),
            faixa_maxima_calibrada=data.get('faixa_maxima_calibrada'),
            condicoes_ambientais=data.get('condicoes_ambientais'),
            erro_maximo_admissivel=data.get('erro_maximo_admissivel'),
            criterio_aceitacao_id=data.get('criterio_aceitacao_id'),
            software_versao=data.get('software_versao')
        )
        
        db.session.add(equipamento)
        db.session.commit()
        
        return jsonify({'message': 'Equipamento criado com sucesso', 'numero_serie': equipamento.numero_serie}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipamentos_bp.route('/<numero_serie>', methods=['GET'])
def obter_equipamento(numero_serie):
    """Obter um equipamento específico"""
    try:
        equipamento = Equipamento.query.get_or_404(numero_serie)
        
        equipamento_data = {
            'numero_serie': equipamento.numero_serie,
            'tag_equipamento': equipamento.tag_equipamento,
            'nome_equipamento': equipamento.nome_equipamento,
            'fabricante_id': equipamento.fabricante_id,
            'fabricante': equipamento.fabricante.nome if equipamento.fabricante else None,
            'modelo_id': equipamento.modelo_id,
            'modelo': equipamento.modelo.nome if equipamento.modelo else None,
            'tipo_equipamento_id': equipamento.tipo_equipamento_id,
            'tipo_equipamento': equipamento.tipo_equipamento.nome if equipamento.tipo_equipamento else None,
            'unidade_id': equipamento.unidade_id,
            'unidade': equipamento.unidade.nome if equipamento.unidade else None,
            'resolucao': equipamento.resolucao,
            'faixa_minima_equipamento': equipamento.faixa_minima_equipamento,
            'faixa_maxima_equipamento': equipamento.faixa_maxima_equipamento,
            'faixa_minima_pam': equipamento.faixa_minima_pam,
            'faixa_maxima_pam': equipamento.faixa_maxima_pam,
            'faixa_minima_calibrada': equipamento.faixa_minima_calibrada,
            'faixa_maxima_calibrada': equipamento.faixa_maxima_calibrada,
            'condicoes_ambientais': equipamento.condicoes_ambientais,
            'erro_maximo_admissivel': equipamento.erro_maximo_admissivel,
            'criterio_aceitacao_id': equipamento.criterio_aceitacao_id,
            'criterio_aceitacao': equipamento.criterio_aceitacao.nome if equipamento.criterio_aceitacao else None,
            'software_versao': equipamento.software_versao
        }
        
        return jsonify(equipamento_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipamentos_bp.route('/<numero_serie>', methods=['PUT'])
def atualizar_equipamento(numero_serie):
    """Atualizar um equipamento existente"""
    try:
        equipamento = Equipamento.query.get_or_404(numero_serie)
        data = request.get_json()
        
        # Verificar se a nova TAG já existe (se fornecida e diferente da atual)
        if data.get('tag_equipamento') and data['tag_equipamento'] != equipamento.tag_equipamento:
            if Equipamento.query.filter_by(tag_equipamento=data['tag_equipamento']).first():
                return jsonify({'error': 'TAG do equipamento já existe'}), 400
        
        # Atualizar campos
        equipamento.tag_equipamento = data.get('tag_equipamento', equipamento.tag_equipamento)
        equipamento.fabricante_id = data.get('fabricante_id', equipamento.fabricante_id)
        equipamento.modelo_id = data.get('modelo_id', equipamento.modelo_id)
        equipamento.nome_equipamento = data.get('nome_equipamento', equipamento.nome_equipamento)
        equipamento.tipo_equipamento_id = data.get('tipo_equipamento_id', equipamento.tipo_equipamento_id)
        equipamento.unidade_id = data.get('unidade_id', equipamento.unidade_id)
        equipamento.resolucao = data.get('resolucao', equipamento.resolucao)
        equipamento.faixa_minima_equipamento = data.get('faixa_minima_equipamento', equipamento.faixa_minima_equipamento)
        equipamento.faixa_maxima_equipamento = data.get('faixa_maxima_equipamento', equipamento.faixa_maxima_equipamento)
        equipamento.faixa_minima_pam = data.get('faixa_minima_pam', equipamento.faixa_minima_pam)
        equipamento.faixa_maxima_pam = data.get('faixa_maxima_pam', equipamento.faixa_maxima_pam)
        equipamento.faixa_minima_calibrada = data.get('faixa_minima_calibrada', equipamento.faixa_minima_calibrada)
        equipamento.faixa_maxima_calibrada = data.get('faixa_maxima_calibrada', equipamento.faixa_maxima_calibrada)
        equipamento.condicoes_ambientais = data.get('condicoes_ambientais', equipamento.condicoes_ambientais)
        equipamento.erro_maximo_admissivel = data.get('erro_maximo_admissivel', equipamento.erro_maximo_admissivel)
        equipamento.criterio_aceitacao_id = data.get('criterio_aceitacao_id', equipamento.criterio_aceitacao_id)
        equipamento.software_versao = data.get('software_versao', equipamento.software_versao)
        
        db.session.commit()
        
        return jsonify({'message': 'Equipamento atualizado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipamentos_bp.route('/<numero_serie>', methods=['DELETE'])
def deletar_equipamento(numero_serie):
    """Deletar um equipamento"""
    try:
        equipamento = Equipamento.query.get_or_404(numero_serie)
        
        # Verificar se há dependências (pontos de medição, certificados, etc.)
        if equipamento.pontos_medicao or equipamento.certificados:
            return jsonify({'error': 'Não é possível deletar equipamento com dependências (pontos de medição ou certificados)'}), 400
        
        db.session.delete(equipamento)
        db.session.commit()
        
        return jsonify({'message': 'Equipamento deletado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipamentos_bp.route('/estatisticas', methods=['GET'])
def estatisticas_equipamentos():
    """Obter estatísticas dos equipamentos"""
    try:
        total_equipamentos = Equipamento.query.count()
        
        # Equipamentos por fabricante
        fabricantes_stats = db.session.query(
            Fabricante.nome,
            db.func.count(Equipamento.numero_serie).label('count')
        ).join(Equipamento).group_by(Fabricante.nome).all()
        
        # Equipamentos por tipo
        tipos_stats = db.session.query(
            TipoEquipamento.nome,
            db.func.count(Equipamento.numero_serie).label('count')
        ).join(Equipamento).group_by(TipoEquipamento.nome).all()
        
        return jsonify({
            'total_equipamentos': total_equipamentos,
            'por_fabricante': [{'nome': fab, 'count': count} for fab, count in fabricantes_stats],
            'por_tipo': [{'nome': tipo, 'count': count} for tipo, count in tipos_stats]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

