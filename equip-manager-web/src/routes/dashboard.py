from flask import Blueprint, request, jsonify
from src.models.database import (
    db, Equipamento, PontoMedicao, Certificado, 
    Fabricante, TipoEquipamento, Polo
)
from datetime import datetime, timedelta
from sqlalchemy import func, and_

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/resumo', methods=['GET'])
def resumo_geral():
    """Obter resumo geral do sistema"""
    try:
        # Contadores básicos
        total_equipamentos = Equipamento.query.count()
        total_pontos_medicao = PontoMedicao.query.count()
        total_certificados = Certificado.query.count()
        
        # Pontos de medição com calibração próxima do vencimento (30 dias)
        data_limite = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        pontos_vencidos = PontoMedicao.query.filter(
            PontoMedicao.data_proxima_calibracao.isnot(None),
            PontoMedicao.data_proxima_calibracao < data_hoje
        ).count()
        
        pontos_proximos_vencimento = PontoMedicao.query.filter(
            PontoMedicao.data_proxima_calibracao.isnot(None),
            PontoMedicao.data_proxima_calibracao >= data_hoje,
            PontoMedicao.data_proxima_calibracao <= data_limite
        ).count()
        
        return jsonify({
            'totais': {
                'equipamentos': total_equipamentos,
                'pontos_medicao': total_pontos_medicao,
                'certificados': total_certificados
            },
            'alertas_calibracao': {
                'vencidos': pontos_vencidos,
                'proximos_vencimento': pontos_proximos_vencimento,
                'total_alertas': pontos_vencidos + pontos_proximos_vencimento
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/estatisticas-equipamentos', methods=['GET'])
def estatisticas_equipamentos():
    """Obter estatísticas detalhadas dos equipamentos"""
    try:
        # Equipamentos por fabricante
        fabricantes_stats = db.session.query(
            Fabricante.nome,
            func.count(Equipamento.numero_serie).label('count')
        ).join(Equipamento, Equipamento.fabricante_id == Fabricante.id)\
         .group_by(Fabricante.nome)\
         .order_by(func.count(Equipamento.numero_serie).desc()).all()
        
        # Equipamentos por tipo
        tipos_stats = db.session.query(
            TipoEquipamento.nome,
            func.count(Equipamento.numero_serie).label('count')
        ).join(Equipamento, Equipamento.tipo_equipamento_id == TipoEquipamento.id)\
         .group_by(TipoEquipamento.nome)\
         .order_by(func.count(Equipamento.numero_serie).desc()).all()
        
        # Equipamentos por polo (através dos pontos de medição)
        polos_stats = db.session.query(
            Polo.nome,
            func.count(PontoMedicao.id).label('count')
        ).join(PontoMedicao, PontoMedicao.polo_id == Polo.id)\
         .group_by(Polo.nome)\
         .order_by(func.count(PontoMedicao.id).desc()).all()
        
        return jsonify({
            'por_fabricante': [{'nome': fab, 'count': count} for fab, count in fabricantes_stats],
            'por_tipo': [{'nome': tipo, 'count': count} for tipo, count in tipos_stats],
            'por_polo': [{'nome': polo, 'count': count} for polo, count in polos_stats]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/cronograma-calibracoes', methods=['GET'])
def cronograma_calibracoes():
    """Obter cronograma de calibrações por mês"""
    try:
        # Obter ano atual ou ano especificado
        ano = request.args.get('ano', datetime.now().year, type=int)
        
        # Inicializar dados para todos os meses
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        cronograma = []
        
        for i, mes_nome in enumerate(meses, 1):
            # Criar datas de início e fim do mês
            if i == 12:
                data_inicio = f"{ano}-{i:02d}-01"
                data_fim = f"{ano + 1}-01-01"
            else:
                data_inicio = f"{ano}-{i:02d}-01"
                data_fim = f"{ano}-{i+1:02d}-01"
            
            # Contar calibrações programadas para o mês
            calibracoes_mes = PontoMedicao.query.filter(
                PontoMedicao.data_proxima_calibracao.isnot(None),
                PontoMedicao.data_proxima_calibracao >= data_inicio,
                PontoMedicao.data_proxima_calibracao < data_fim
            ).count()
            
            cronograma.append({
                'mes': mes_nome,
                'numero_mes': i,
                'calibracoes': calibracoes_mes
            })
        
        return jsonify({
            'ano': ano,
            'cronograma': cronograma,
            'total_ano': sum(item['calibracoes'] for item in cronograma)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/pontos-criticos', methods=['GET'])
def pontos_criticos():
    """Obter pontos de medição críticos (vencidos ou próximos do vencimento)"""
    try:
        limite_dias = request.args.get('dias', 30, type=int)
        
        data_limite = (datetime.now() + timedelta(days=limite_dias)).strftime('%Y-%m-%d')
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        # Pontos vencidos
        pontos_vencidos = PontoMedicao.query.filter(
            PontoMedicao.data_proxima_calibracao.isnot(None),
            PontoMedicao.data_proxima_calibracao < data_hoje
        ).order_by(PontoMedicao.data_proxima_calibracao).all()
        
        # Pontos próximos do vencimento
        pontos_proximos = PontoMedicao.query.filter(
            PontoMedicao.data_proxima_calibracao.isnot(None),
            PontoMedicao.data_proxima_calibracao >= data_hoje,
            PontoMedicao.data_proxima_calibracao <= data_limite
        ).order_by(PontoMedicao.data_proxima_calibracao).all()
        
        def formatar_ponto_critico(ponto):
            dias_restantes = None
            if ponto.data_proxima_calibracao:
                try:
                    data_calibracao = datetime.strptime(ponto.data_proxima_calibracao, '%Y-%m-%d')
                    dias_restantes = (data_calibracao - datetime.now()).days
                except:
                    pass
            
            return {
                'id': ponto.id,
                'tag_ponto_medicao': ponto.tag_ponto_medicao,
                'nome_ponto_medicao': ponto.nome_ponto_medicao,
                'data_proxima_calibracao': ponto.data_proxima_calibracao,
                'dias_restantes': dias_restantes,
                'polo': ponto.polo.nome if ponto.polo else None,
                'equipamento': ponto.equipamento.nome_equipamento if ponto.equipamento else None,
                'numero_serie_equipamento': ponto.numero_serie_equipamento
            }
        
        return jsonify({
            'pontos_vencidos': [formatar_ponto_critico(p) for p in pontos_vencidos],
            'pontos_proximos': [formatar_ponto_critico(p) for p in pontos_proximos],
            'resumo': {
                'total_vencidos': len(pontos_vencidos),
                'total_proximos': len(pontos_proximos),
                'total_criticos': len(pontos_vencidos) + len(pontos_proximos)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/ultimas-atividades', methods=['GET'])
def ultimas_atividades():
    """Obter últimas atividades do sistema"""
    try:
        limite = request.args.get('limite', 10, type=int)
        
        # Últimos certificados adicionados
        ultimos_certificados = Certificado.query.order_by(
            Certificado.data_certificado.desc()
        ).limit(limite).all()
        
        # Últimos equipamentos adicionados (assumindo que temos uma data de criação)
        # Como não temos data de criação, vamos usar os últimos por ID
        ultimos_equipamentos = Equipamento.query.order_by(
            Equipamento.numero_serie.desc()
        ).limit(limite).all()
        
        atividades = []
        
        # Adicionar certificados às atividades
        for cert in ultimos_certificados:
            atividades.append({
                'tipo': 'certificado',
                'descricao': f'Certificado {cert.numero_certificado} adicionado para equipamento {cert.numero_serie_equipamento}',
                'data': cert.data_certificado,
                'detalhes': {
                    'numero_certificado': cert.numero_certificado,
                    'numero_serie_equipamento': cert.numero_serie_equipamento,
                    'equipamento_nome': cert.equipamento.nome_equipamento if cert.equipamento else None
                }
            })
        
        # Ordenar atividades por data (mais recentes primeiro)
        atividades.sort(key=lambda x: x['data'], reverse=True)
        
        return jsonify({
            'atividades': atividades[:limite],
            'total': len(atividades)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/indicadores-performance', methods=['GET'])
def indicadores_performance():
    """Obter indicadores de performance do sistema"""
    try:
        # Percentual de pontos com calibração em dia
        total_pontos = PontoMedicao.query.filter(
            PontoMedicao.data_proxima_calibracao.isnot(None)
        ).count()
        
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        pontos_em_dia = PontoMedicao.query.filter(
            PontoMedicao.data_proxima_calibracao.isnot(None),
            PontoMedicao.data_proxima_calibracao >= data_hoje
        ).count()
        
        percentual_em_dia = (pontos_em_dia / total_pontos * 100) if total_pontos > 0 else 0
        
        # Certificados por status (assumindo que temos status)
        certificados_por_status = db.session.query(
            func.coalesce(db.session.query(db.literal('Sem Status')), 'Sem Status').label('status'),
            func.count(Certificado.id).label('count')
        ).group_by('status').all()
        
        return jsonify({
            'calibracoes': {
                'total_pontos': total_pontos,
                'pontos_em_dia': pontos_em_dia,
                'percentual_em_dia': round(percentual_em_dia, 2)
            },
            'certificados_por_status': [
                {'status': status, 'count': count} 
                for status, count in certificados_por_status
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

