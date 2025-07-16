from flask import Blueprint, request, jsonify, send_file
from src.models.database import (
    db, Equipamento, PontoMedicao, Certificado, Fabricante, 
    TipoEquipamento, Polo, Unidade, ClassificacaoPontoMedicao
)
import pandas as pd
import io
import os
from datetime import datetime

importacao_bp = Blueprint('importacao', __name__)

@importacao_bp.route('/equipamentos', methods=['POST'])
def importar_equipamentos():
    """Importar equipamentos de arquivo Excel"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Formato de arquivo não suportado. Use .xlsx ou .xls'}), 400
        
        # Ler arquivo Excel
        df = pd.read_excel(file)
        
        # Mapear colunas esperadas
        colunas_esperadas = {
            'numero_serie': ['número de série', 'numero_serie', 'serial_number'],
            'tag_equipamento': ['tag equipamento', 'tag_equipamento', 'tag'],
            'nome_equipamento': ['nome equipamento', 'nome_equipamento', 'equipment_name'],
            'fabricante': ['fabricante', 'marca', 'manufacturer'],
            'modelo': ['modelo', 'model'],
            'tipo_equipamento': ['tipo equipamento', 'tipo_equipamento', 'equipment_type']
        }
        
        # Normalizar nomes das colunas
        df.columns = df.columns.str.lower().str.strip()
        
        equipamentos_importados = 0
        equipamentos_erro = 0
        erros = []
        
        for index, row in df.iterrows():
            try:
                # Extrair dados da linha
                numero_serie = None
                for col_name in colunas_esperadas['numero_serie']:
                    if col_name in df.columns:
                        numero_serie = str(row[col_name]).strip()
                        break
                
                if not numero_serie or numero_serie == 'nan':
                    erros.append(f'Linha {index + 2}: Número de série obrigatório')
                    equipamentos_erro += 1
                    continue
                
                # Verificar se equipamento já existe
                if Equipamento.query.filter_by(numero_serie=numero_serie).first():
                    erros.append(f'Linha {index + 2}: Equipamento {numero_serie} já existe')
                    equipamentos_erro += 1
                    continue
                
                # Extrair outros dados
                tag_equipamento = None
                for col_name in colunas_esperadas['tag_equipamento']:
                    if col_name in df.columns:
                        tag_equipamento = str(row[col_name]).strip() if pd.notna(row[col_name]) else None
                        break
                
                nome_equipamento = None
                for col_name in colunas_esperadas['nome_equipamento']:
                    if col_name in df.columns:
                        nome_equipamento = str(row[col_name]).strip() if pd.notna(row[col_name]) else None
                        break
                
                if not nome_equipamento:
                    nome_equipamento = f'Equipamento {numero_serie}'
                
                # Buscar ou criar fabricante
                fabricante_id = None
                for col_name in colunas_esperadas['fabricante']:
                    if col_name in df.columns and pd.notna(row[col_name]):
                        fabricante_nome = str(row[col_name]).strip()
                        fabricante = Fabricante.query.filter_by(nome=fabricante_nome).first()
                        if not fabricante:
                            fabricante = Fabricante(nome=fabricante_nome)
                            db.session.add(fabricante)
                            db.session.flush()
                        fabricante_id = fabricante.id
                        break
                
                # Buscar ou criar tipo de equipamento
                tipo_equipamento_id = None
                for col_name in colunas_esperadas['tipo_equipamento']:
                    if col_name in df.columns and pd.notna(row[col_name]):
                        tipo_nome = str(row[col_name]).strip()
                        tipo = TipoEquipamento.query.filter_by(nome=tipo_nome).first()
                        if not tipo:
                            tipo = TipoEquipamento(nome=tipo_nome)
                            db.session.add(tipo)
                            db.session.flush()
                        tipo_equipamento_id = tipo.id
                        break
                
                # Criar equipamento
                equipamento = Equipamento(
                    numero_serie=numero_serie,
                    tag_equipamento=tag_equipamento,
                    nome_equipamento=nome_equipamento,
                    fabricante_id=fabricante_id,
                    tipo_equipamento_id=tipo_equipamento_id
                )
                
                db.session.add(equipamento)
                equipamentos_importados += 1
                
            except Exception as e:
                erros.append(f'Linha {index + 2}: {str(e)}')
                equipamentos_erro += 1
        
        # Commit das alterações
        db.session.commit()
        
        return jsonify({
            'message': f'Importação concluída',
            'equipamentos_importados': equipamentos_importados,
            'equipamentos_erro': equipamentos_erro,
            'erros': erros[:10]  # Limitar a 10 erros para não sobrecarregar a resposta
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro na importação: {str(e)}'}), 500

@importacao_bp.route('/pontos-medicao', methods=['POST'])
def importar_pontos_medicao():
    """Importar pontos de medição de arquivo Excel"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Formato de arquivo não suportado. Use .xlsx ou .xls'}), 400
        
        # Ler arquivo Excel
        df = pd.read_excel(file)
        
        # Normalizar nomes das colunas
        df.columns = df.columns.str.lower().str.strip()
        
        pontos_importados = 0
        pontos_erro = 0
        erros = []
        
        for index, row in df.iterrows():
            try:
                # Extrair dados obrigatórios
                tag_ponto = str(row.get('tag_ponto_medicao', '')).strip()
                nome_ponto = str(row.get('nome_ponto_medicao', '')).strip()
                
                if not tag_ponto or tag_ponto == 'nan':
                    erros.append(f'Linha {index + 2}: TAG do ponto obrigatória')
                    pontos_erro += 1
                    continue
                
                if not nome_ponto or nome_ponto == 'nan':
                    nome_ponto = f'Ponto {tag_ponto}'
                
                # Verificar se ponto já existe
                if PontoMedicao.query.filter_by(tag_ponto_medicao=tag_ponto).first():
                    erros.append(f'Linha {index + 2}: Ponto {tag_ponto} já existe')
                    pontos_erro += 1
                    continue
                
                # Buscar polo
                polo_id = None
                if 'polo' in df.columns and pd.notna(row['polo']):
                    polo_nome = str(row['polo']).strip()
                    polo = Polo.query.filter_by(nome=polo_nome).first()
                    if not polo:
                        polo = Polo(nome=polo_nome)
                        db.session.add(polo)
                        db.session.flush()
                    polo_id = polo.id
                
                # Buscar classificação
                classificacao_id = None
                if 'classificacao' in df.columns and pd.notna(row['classificacao']):
                    classificacao_nome = str(row['classificacao']).strip()
                    classificacao = ClassificacaoPontoMedicao.query.filter_by(nome=classificacao_nome).first()
                    if not classificacao:
                        classificacao = ClassificacaoPontoMedicao(nome=classificacao_nome)
                        db.session.add(classificacao)
                        db.session.flush()
                    classificacao_id = classificacao.id
                
                # Extrair número de série do equipamento
                numero_serie_equipamento = None
                if 'numero_serie_equipamento' in df.columns and pd.notna(row['numero_serie_equipamento']):
                    numero_serie_equipamento = str(row['numero_serie_equipamento']).strip()
                
                # Criar ponto de medição
                ponto = PontoMedicao(
                    tag_ponto_medicao=tag_ponto,
                    nome_ponto_medicao=nome_ponto,
                    polo_id=polo_id,
                    classificacao_id=classificacao_id,
                    numero_serie_equipamento=numero_serie_equipamento,
                    data_ultima_calibracao=str(row.get('data_ultima_calibracao', '')) if pd.notna(row.get('data_ultima_calibracao')) else None,
                    data_proxima_calibracao=str(row.get('data_proxima_calibracao', '')) if pd.notna(row.get('data_proxima_calibracao')) else None,
                    frequencia_calibracao_anp=int(row.get('frequencia_calibracao_anp', 0)) if pd.notna(row.get('frequencia_calibracao_anp')) else None
                )
                
                db.session.add(ponto)
                pontos_importados += 1
                
            except Exception as e:
                erros.append(f'Linha {index + 2}: {str(e)}')
                pontos_erro += 1
        
        # Commit das alterações
        db.session.commit()
        
        return jsonify({
            'message': f'Importação concluída',
            'pontos_importados': pontos_importados,
            'pontos_erro': pontos_erro,
            'erros': erros[:10]
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro na importação: {str(e)}'}), 500

@importacao_bp.route('/exportar-equipamentos', methods=['GET'])
def exportar_equipamentos():
    """Exportar equipamentos para arquivo Excel"""
    try:
        # Buscar todos os equipamentos
        equipamentos = db.session.query(
            Equipamento.numero_serie,
            Equipamento.tag_equipamento,
            Equipamento.nome_equipamento,
            Fabricante.nome.label('fabricante'),
            TipoEquipamento.nome.label('tipo_equipamento'),
            Unidade.nome.label('unidade'),
            Equipamento.resolucao,
            Equipamento.faixa_minima_equipamento,
            Equipamento.faixa_maxima_equipamento
        ).outerjoin(Fabricante, Equipamento.fabricante_id == Fabricante.id)\
         .outerjoin(TipoEquipamento, Equipamento.tipo_equipamento_id == TipoEquipamento.id)\
         .outerjoin(Unidade, Equipamento.unidade_id == Unidade.id).all()
        
        # Converter para DataFrame
        df = pd.DataFrame([{
            'Número de Série': eq.numero_serie,
            'TAG Equipamento': eq.tag_equipamento,
            'Nome Equipamento': eq.nome_equipamento,
            'Fabricante': eq.fabricante,
            'Tipo Equipamento': eq.tipo_equipamento,
            'Unidade': eq.unidade,
            'Resolução': eq.resolucao,
            'Faixa Mínima': eq.faixa_minima_equipamento,
            'Faixa Máxima': eq.faixa_maxima_equipamento
        } for eq in equipamentos])
        
        # Criar arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Equipamentos', index=False)
        output.seek(0)
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'equipamentos_{timestamp}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': f'Erro na exportação: {str(e)}'}), 500

@importacao_bp.route('/exportar-pontos-medicao', methods=['GET'])
def exportar_pontos_medicao():
    """Exportar pontos de medição para arquivo Excel"""
    try:
        # Buscar todos os pontos de medição
        pontos = db.session.query(
            PontoMedicao.tag_ponto_medicao,
            PontoMedicao.nome_ponto_medicao,
            Polo.nome.label('polo'),
            ClassificacaoPontoMedicao.nome.label('classificacao'),
            PontoMedicao.numero_serie_equipamento,
            PontoMedicao.data_ultima_calibracao,
            PontoMedicao.data_proxima_calibracao,
            PontoMedicao.frequencia_calibracao_anp
        ).outerjoin(Polo, PontoMedicao.polo_id == Polo.id)\
         .outerjoin(ClassificacaoPontoMedicao, PontoMedicao.classificacao_id == ClassificacaoPontoMedicao.id).all()
        
        # Converter para DataFrame
        df = pd.DataFrame([{
            'TAG Ponto Medição': ponto.tag_ponto_medicao,
            'Nome Ponto Medição': ponto.nome_ponto_medicao,
            'Polo': ponto.polo,
            'Classificação': ponto.classificacao,
            'Número Série Equipamento': ponto.numero_serie_equipamento,
            'Data Última Calibração': ponto.data_ultima_calibracao,
            'Data Próxima Calibração': ponto.data_proxima_calibracao,
            'Frequência Calibração ANP (dias)': ponto.frequencia_calibracao_anp
        } for ponto in pontos])
        
        # Criar arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Pontos de Medição', index=False)
        output.seek(0)
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'pontos_medicao_{timestamp}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': f'Erro na exportação: {str(e)}'}), 500

@importacao_bp.route('/template-equipamentos', methods=['GET'])
def template_equipamentos():
    """Gerar template Excel para importação de equipamentos"""
    try:
        # Criar DataFrame com colunas de exemplo
        df = pd.DataFrame({
            'numero_serie': ['EQ001', 'EQ002'],
            'tag_equipamento': ['TAG001', 'TAG002'],
            'nome_equipamento': ['Medidor de Vazão 1', 'Transmissor de Pressão 1'],
            'fabricante': ['Emerson', 'Honeywell'],
            'tipo_equipamento': ['Medidor de Vazão', 'Transmissor de Pressão'],
            'resolucao': [0.1, 0.01],
            'faixa_minima_equipamento': [0, 0],
            'faixa_maxima_equipamento': [1000, 100]
        })
        
        # Criar arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Template Equipamentos', index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='template_equipamentos.xlsx'
        )
    
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar template: {str(e)}'}), 500

@importacao_bp.route('/template-pontos-medicao', methods=['GET'])
def template_pontos_medicao():
    """Gerar template Excel para importação de pontos de medição"""
    try:
        # Criar DataFrame com colunas de exemplo
        df = pd.DataFrame({
            'tag_ponto_medicao': ['PM001', 'PM002'],
            'nome_ponto_medicao': ['Ponto de Medição 1', 'Ponto de Medição 2'],
            'polo': ['Polo Norte', 'Polo Sul'],
            'classificacao': ['Fiscal', 'Operacional'],
            'numero_serie_equipamento': ['EQ001', 'EQ002'],
            'data_ultima_calibracao': ['2024-01-15', '2024-02-20'],
            'data_proxima_calibracao': ['2025-01-15', '2025-02-20'],
            'frequencia_calibracao_anp': [365, 365]
        })
        
        # Criar arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Template Pontos Medição', index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='template_pontos_medicao.xlsx'
        )
    
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar template: {str(e)}'}), 500

