from flask import Blueprint, request, jsonify
from src.models.database import db, PontoMedicao, Polo, ClassificacaoPontoMedicao, Equipamento
from sqlalchemy import or_
from datetime import datetime, timedelta

pontos_medicao_bp = Blueprint('pontos_medicao', __name__)

@pontos_medicao_bp.route('/', methods=['GET'])
def listar_pontos_medicao():
    """Listar todos os pontos de medição com filtros opcionais"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        polo_id = request.args.get('polo_id', type=int)
        classificacao_id = request.args.get('classificacao_id', type=int)
        vencimento_proximo = request.args.get('vencimento_proximo', type=bool)
        
        query = PontoMedicao.query
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    PontoMedicao.nome_ponto_medicao.contains(search),
                    PontoMedicao.tag_ponto_medicao.contains(search),
                    PontoMedicao.numero_serie_equipamento.contains(search)
                )
            )
        
        if polo_id:
            query = query.filter(PontoMedicao.polo_id == polo_id)
        
        if classificacao_id:
            query = query.filter(PontoMedicao.classificacao_id == classificacao_id)
        
        # Filtro para calibrações próximas do vencimento (próximos 30 dias)
        if vencimento_proximo:
            data_limite = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            query = query.filter(
                PontoMedicao.data_proxima_calibracao.isnot(None),
                PontoMedicao.data_proxima_calibracao <= data_limite
            )
        
        # Paginação
        pontos_paginados = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        pontos = []
        for ponto in pontos_paginados.items:
            # Calcular status de calibração
            status_calibracao = calcular_status_calibracao(ponto.data_proxima_calibracao)
            
            ponto_data = {
                'id': ponto.id,
                'nome_ponto_medicao': ponto.nome_ponto_medicao,
                'tag_ponto_medicao': ponto.tag_ponto_medicao,
                'polo': ponto.polo.nome if ponto.polo else None,
                'classificacao': ponto.classificacao.nome if ponto.classificacao else None,
                'numero_serie_equipamento': ponto.numero_serie_equipamento,
                'equipamento_nome': ponto.equipamento.nome_equipamento if ponto.equipamento else None,
                'certificado_calibracao_vigente': ponto.certificado_calibracao_vigente,
                'data_ultima_calibracao': ponto.data_ultima_calibracao,
                'data_proxima_calibracao': ponto.data_proxima_calibracao,
                'frequencia_calibracao_anp': ponto.frequencia_calibracao_anp,
                'data_retirada': ponto.data_retirada,
                'data_recebimento_uso': ponto.data_recebimento_uso,
                'controle_vencimento': ponto.controle_vencimento,
                'solicitacao_calibracao': ponto.solicitacao_calibracao,
                'status_calibracao': status_calibracao
            }
            pontos.append(ponto_data)
        
        return jsonify({
            'pontos_medicao': pontos,
            'total': pontos_paginados.total,
            'pages': pontos_paginados.pages,
            'current_page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pontos_medicao_bp.route('/', methods=['POST'])
def criar_ponto_medicao():
    """Criar um novo ponto de medição"""
    try:
        data = request.get_json()
        
        # Verificar se a TAG já existe
        if PontoMedicao.query.filter_by(tag_ponto_medicao=data['tag_ponto_medicao']).first():
            return jsonify({'error': 'TAG do ponto de medição já existe'}), 400
        
        ponto = PontoMedicao(
            polo_id=data.get('polo_id'),
            nome_ponto_medicao=data['nome_ponto_medicao'],
            tag_ponto_medicao=data['tag_ponto_medicao'],
            classificacao_id=data.get('classificacao_id'),
            numero_serie_equipamento=data.get('numero_serie_equipamento'),
            certificado_calibracao_vigente=data.get('certificado_calibracao_vigente'),
            data_ultima_calibracao=data.get('data_ultima_calibracao'),
            data_proxima_calibracao=data.get('data_proxima_calibracao'),
            frequencia_calibracao_anp=data.get('frequencia_calibracao_anp'),
            data_retirada=data.get('data_retirada'),
            data_recebimento_uso=data.get('data_recebimento_uso'),
            controle_vencimento=data.get('controle_vencimento'),
            solicitacao_calibracao=data.get('solicitacao_calibracao')
        )
        
        db.session.add(ponto)
        db.session.commit()
        
        return jsonify({'message': 'Ponto de medição criado com sucesso', 'id': ponto.id}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pontos_medicao_bp.route('/<int:ponto_id>', methods=['GET'])
def obter_ponto_medicao(ponto_id):
    """Obter um ponto de medição específico"""
    try:
        ponto = PontoMedicao.query.get_or_404(ponto_id)
        
        status_calibracao = calcular_status_calibracao(ponto.data_proxima_calibracao)
        
        ponto_data = {
            'id': ponto.id,
            'polo_id': ponto.polo_id,
            'polo': ponto.polo.nome if ponto.polo else None,
            'nome_ponto_medicao': ponto.nome_ponto_medicao,
            'tag_ponto_medicao': ponto.tag_ponto_medicao,
            'classificacao_id': ponto.classificacao_id,
            'classificacao': ponto.classificacao.nome if ponto.classificacao else None,
            'numero_serie_equipamento': ponto.numero_serie_equipamento,
            'equipamento_nome': ponto.equipamento.nome_equipamento if ponto.equipamento else None,
            'certificado_calibracao_vigente': ponto.certificado_calibracao_vigente,
            'data_ultima_calibracao': ponto.data_ultima_calibracao,
            'data_proxima_calibracao': ponto.data_proxima_calibracao,
            'frequencia_calibracao_anp': ponto.frequencia_calibracao_anp,
            'data_retirada': ponto.data_retirada,
            'data_recebimento_uso': ponto.data_recebimento_uso,
            'controle_vencimento': ponto.controle_vencimento,
            'solicitacao_calibracao': ponto.solicitacao_calibracao,
            'status_calibracao': status_calibracao
        }
        
        return jsonify(ponto_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pontos_medicao_bp.route('/<int:ponto_id>', methods=['PUT'])
def atualizar_ponto_medicao(ponto_id):
    """Atualizar um ponto de medição existente"""
    try:
        ponto = PontoMedicao.query.get_or_404(ponto_id)
        data = request.get_json()
        
        # Verificar se a nova TAG já existe (se fornecida e diferente da atual)
        if data.get('tag_ponto_medicao') and data['tag_ponto_medicao'] != ponto.tag_ponto_medicao:
            if PontoMedicao.query.filter_by(tag_ponto_medicao=data['tag_ponto_medicao']).first():
                return jsonify({'error': 'TAG do ponto de medição já existe'}), 400
        
        # Atualizar campos
        ponto.polo_id = data.get('polo_id', ponto.polo_id)
        ponto.nome_ponto_medicao = data.get('nome_ponto_medicao', ponto.nome_ponto_medicao)
        ponto.tag_ponto_medicao = data.get('tag_ponto_medicao', ponto.tag_ponto_medicao)
        ponto.classificacao_id = data.get('classificacao_id', ponto.classificacao_id)
        ponto.numero_serie_equipamento = data.get('numero_serie_equipamento', ponto.numero_serie_equipamento)
        ponto.certificado_calibracao_vigente = data.get('certificado_calibracao_vigente', ponto.certificado_calibracao_vigente)
        ponto.data_ultima_calibracao = data.get('data_ultima_calibracao', ponto.data_ultima_calibracao)
        ponto.data_proxima_calibracao = data.get('data_proxima_calibracao', ponto.data_proxima_calibracao)
        ponto.frequencia_calibracao_anp = data.get('frequencia_calibracao_anp', ponto.frequencia_calibracao_anp)
        ponto.data_retirada = data.get('data_retirada', ponto.data_retirada)
        ponto.data_recebimento_uso = data.get('data_recebimento_uso', ponto.data_recebimento_uso)
        ponto.controle_vencimento = data.get('controle_vencimento', ponto.controle_vencimento)
        ponto.solicitacao_calibracao = data.get('solicitacao_calibracao', ponto.solicitacao_calibracao)
        
        db.session.commit()
        
        return jsonify({'message': 'Ponto de medição atualizado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pontos_medicao_bp.route('/<int:ponto_id>', methods=['DELETE'])
def deletar_ponto_medicao(ponto_id):
    """Deletar um ponto de medição"""
    try:
        ponto = PontoMedicao.query.get_or_404(ponto_id)
        
        # Verificar se há dependências (análises químicas, eventos de cronograma, etc.)
        if ponto.analises_quimicas or ponto.eventos_cronograma_testes or ponto.eventos_cronograma_analises:
            return jsonify({'error': 'Não é possível deletar ponto de medição com dependências'}), 400
        
        db.session.delete(ponto)
        db.session.commit()
        
        return jsonify({'message': 'Ponto de medição deletado com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pontos_medicao_bp.route('/alertas-calibracao', methods=['GET'])
def alertas_calibracao():
    """Obter pontos de medição com calibração próxima do vencimento"""
    try:
        dias_alerta = request.args.get('dias', 30, type=int)
        
        data_limite = (datetime.now() + timedelta(days=dias_alerta)).strftime('%Y-%m-%d')
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        # Pontos com calibração vencida
        pontos_vencidos = PontoMedicao.query.filter(
            PontoMedicao.data_proxima_calibracao.isnot(None),
            PontoMedicao.data_proxima_calibracao < data_hoje
        ).all()
        
        # Pontos com calibração próxima do vencimento
        pontos_proximos = PontoMedicao.query.filter(
            PontoMedicao.data_proxima_calibracao.isnot(None),
            PontoMedicao.data_proxima_calibracao >= data_hoje,
            PontoMedicao.data_proxima_calibracao <= data_limite
        ).all()
        
        def formatar_ponto_alerta(ponto):
            return {
                'id': ponto.id,
                'tag_ponto_medicao': ponto.tag_ponto_medicao,
                'nome_ponto_medicao': ponto.nome_ponto_medicao,
                'data_proxima_calibracao': ponto.data_proxima_calibracao,
                'numero_serie_equipamento': ponto.numero_serie_equipamento,
                'equipamento_nome': ponto.equipamento.nome_equipamento if ponto.equipamento else None,
                'polo': ponto.polo.nome if ponto.polo else None,
                'dias_restantes': calcular_dias_restantes(ponto.data_proxima_calibracao)
            }
        
        return jsonify({
            'pontos_vencidos': [formatar_ponto_alerta(p) for p in pontos_vencidos],
            'pontos_proximos_vencimento': [formatar_ponto_alerta(p) for p in pontos_proximos],
            'total_vencidos': len(pontos_vencidos),
            'total_proximos': len(pontos_proximos)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calcular_status_calibracao(data_proxima_calibracao):
    """Calcular o status da calibração baseado na data"""
    if not data_proxima_calibracao:
        return 'sem_data'
    
    try:
        data_calibracao = datetime.strptime(data_proxima_calibracao, '%Y-%m-%d')
        data_hoje = datetime.now()
        
        if data_calibracao < data_hoje:
            return 'vencido'
        elif (data_calibracao - data_hoje).days <= 30:
            return 'proximo_vencimento'
        else:
            return 'vigente'
    except:
        return 'data_invalida'

def calcular_dias_restantes(data_proxima_calibracao):
    """Calcular quantos dias restam para a calibração"""
    if not data_proxima_calibracao:
        return None
    
    try:
        data_calibracao = datetime.strptime(data_proxima_calibracao, '%Y-%m-%d')
        data_hoje = datetime.now()
        return (data_calibracao - data_hoje).days
    except:
        return None

