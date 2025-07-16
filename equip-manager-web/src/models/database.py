from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Tabelas de Configuração (Listas)
class Fabricante(db.Model):
    __tablename__ = 'fabricantes'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)
    
    # Relacionamentos
    equipamentos = relationship('Equipamento', back_populates='fabricante')
    placas_orificio = relationship('PlacaOrificio', back_populates='fabricante')
    trechos_retos = relationship('TrechoReto', back_populates='fabricante')

class Modelo(db.Model):
    __tablename__ = 'modelos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)
    fabricante_id = Column(Integer, ForeignKey('fabricantes.id'))
    
    # Relacionamentos
    fabricante = relationship('Fabricante')
    equipamentos = relationship('Equipamento', back_populates='modelo')

class TipoEquipamento(db.Model):
    __tablename__ = 'tipos_equipamento'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)
    
    # Relacionamentos
    equipamentos = relationship('Equipamento', back_populates='tipo_equipamento')

class Polo(db.Model):
    __tablename__ = 'polos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)
    
    # Relacionamentos
    instalacoes = relationship('Instalacao', back_populates='polo')
    pontos_medicao = relationship('PontoMedicao', back_populates='polo')

class Instalacao(db.Model):
    __tablename__ = 'instalacoes'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)
    polo_id = Column(Integer, ForeignKey('polos.id'))
    
    # Relacionamentos
    polo = relationship('Polo', back_populates='instalacoes')
    testes_pocos = relationship('TestePoco', back_populates='instalacao')
    analises_quimicas = relationship('AnaliseQuimica', back_populates='instalacao')
    eventos_cronograma_testes = relationship('EventoCronogramaTeste', back_populates='instalacao')
    eventos_cronograma_analises = relationship('EventoCronogramaAnalise', back_populates='instalacao')

class Unidade(db.Model):
    __tablename__ = 'unidades'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)  # Ex: '°C', 'bar', 'm³/h'
    
    # Relacionamentos
    equipamentos = relationship('Equipamento', back_populates='unidade')

class ClassificacaoPontoMedicao(db.Model):
    __tablename__ = 'classificacoes_ponto_medicao'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)
    
    # Relacionamentos
    pontos_medicao = relationship('PontoMedicao', back_populates='classificacao')

class NaturezaTesteAnalise(db.Model):
    __tablename__ = 'naturezas_teste_analise'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)
    
    # Relacionamentos
    requisitos_metrologicos = relationship('RequisitoMetrologico', back_populates='natureza')
    testes_pocos = relationship('TestePoco', back_populates='natureza')
    analises_quimicas = relationship('AnaliseQuimica', back_populates='natureza')

class StatusCertificadoIncerteza(db.Model):
    __tablename__ = 'status_certificado_incerteza'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)  # Ex: 'Vigente', 'Vencido', 'Aprovado', 'Reprovado'
    
    # Relacionamentos
    certificados = relationship('Certificado', back_populates='status_certificado')
    incertezas_limite = relationship('Incerteza', foreign_keys='Incerteza.status_limite_id', back_populates='status_limite')
    incertezas_emissao = relationship('Incerteza', foreign_keys='Incerteza.status_emissao_id', back_populates='status_emissao')

class ServicoIncerteza(db.Model):
    __tablename__ = 'servicos_incerteza'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)
    
    # Relacionamentos
    incertezas = relationship('Incerteza', back_populates='servico')

class CriterioAceitacao(db.Model):
    __tablename__ = 'criterios_aceitacao'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), unique=True, nullable=False)
    
    # Relacionamentos
    equipamentos = relationship('Equipamento', back_populates='criterio_aceitacao')

# Tabela Principal: Equipamentos
class Equipamento(db.Model):
    __tablename__ = 'equipamentos'
    numero_serie = Column(String(255), primary_key=True)  # Chave primária unívoca
    tag_equipamento = Column(String(255), unique=True)  # Pode ser usado como identificador alternativo
    fabricante_id = Column(Integer, ForeignKey('fabricantes.id'))
    modelo_id = Column(Integer, ForeignKey('modelos.id'))
    nome_equipamento = Column(String(255), nullable=False)
    tipo_equipamento_id = Column(Integer, ForeignKey('tipos_equipamento.id'))
    unidade_id = Column(Integer, ForeignKey('unidades.id'))
    resolucao = Column(Float)
    faixa_minima_equipamento = Column(Float)
    faixa_maxima_equipamento = Column(Float)
    faixa_minima_pam = Column(Float)
    faixa_maxima_pam = Column(Float)
    faixa_minima_calibrada = Column(Float)
    faixa_maxima_calibrada = Column(Float)
    condicoes_ambientais = Column(Text)
    erro_maximo_admissivel = Column(Float)
    criterio_aceitacao_id = Column(Integer, ForeignKey('criterios_aceitacao.id'))
    software_versao = Column(String(255))
    
    # Relacionamentos
    fabricante = relationship('Fabricante', back_populates='equipamentos')
    modelo = relationship('Modelo', back_populates='equipamentos')
    tipo_equipamento = relationship('TipoEquipamento', back_populates='equipamentos')
    unidade = relationship('Unidade', back_populates='equipamentos')
    criterio_aceitacao = relationship('CriterioAceitacao', back_populates='equipamentos')
    pontos_medicao = relationship('PontoMedicao', back_populates='equipamento')
    certificados = relationship('Certificado', back_populates='equipamento')
    placa_orificio = relationship('PlacaOrificio', back_populates='equipamento', uselist=False)
    trecho_reto = relationship('TrechoReto', back_populates='equipamento', uselist=False)

# Tabela: Pontos de Medição
class PontoMedicao(db.Model):
    __tablename__ = 'pontos_medicao'
    id = Column(Integer, primary_key=True, autoincrement=True)
    polo_id = Column(Integer, ForeignKey('polos.id'))
    nome_ponto_medicao = Column(String(255), nullable=False)
    tag_ponto_medicao = Column(String(255), unique=True, nullable=False)
    classificacao_id = Column(Integer, ForeignKey('classificacoes_ponto_medicao.id'))
    numero_serie_equipamento = Column(String(255), ForeignKey('equipamentos.numero_serie'))
    certificado_calibracao_vigente = Column(String(255))
    data_ultima_calibracao = Column(String(10))  # Formato YYYY-MM-DD
    data_proxima_calibracao = Column(String(10))  # Formato YYYY-MM-DD
    frequencia_calibracao_anp = Column(Integer)  # Em dias
    data_retirada = Column(String(10))  # Formato YYYY-MM-DD
    data_recebimento_uso = Column(String(10))  # Formato YYYY-MM-DD
    controle_vencimento = Column(Text)
    solicitacao_calibracao = Column(Text)
    
    # Relacionamentos
    polo = relationship('Polo', back_populates='pontos_medicao')
    classificacao = relationship('ClassificacaoPontoMedicao', back_populates='pontos_medicao')
    equipamento = relationship('Equipamento', back_populates='pontos_medicao')
    analises_quimicas = relationship('AnaliseQuimica', back_populates='ponto_medicao')
    eventos_cronograma_testes = relationship('EventoCronogramaTeste', back_populates='ponto_medicao')
    eventos_cronograma_analises = relationship('EventoCronogramaAnalise', back_populates='ponto_medicao')

# Tabela: Certificados de Calibração (Histórico)
class Certificado(db.Model):
    __tablename__ = 'certificados'
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_serie_equipamento = Column(String(255), ForeignKey('equipamentos.numero_serie'), nullable=False)
    numero_certificado = Column(String(255), nullable=False)
    revisao_certificado = Column(String(50))
    data_certificado = Column(String(10), nullable=False)  # Formato YYYY-MM-DD
    status_certificado_id = Column(Integer, ForeignKey('status_certificado_incerteza.id'))
    caminho_arquivo = Column(String(500))  # Caminho para o arquivo PDF/etc. anexado
    
    __table_args__ = (UniqueConstraint('numero_serie_equipamento', 'numero_certificado', 'revisao_certificado'),)
    
    # Relacionamentos
    equipamento = relationship('Equipamento', back_populates='certificados')
    status_certificado = relationship('StatusCertificadoIncerteza', back_populates='certificados')

# Tabela: Placas de Orifício
class PlacaOrificio(db.Model):
    __tablename__ = 'placas_orificio'
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_serie_equipamento = Column(String(255), ForeignKey('equipamentos.numero_serie'), unique=True, nullable=False)
    numero_serie_standby = Column(String(255))
    fabricante_id = Column(Integer, ForeignKey('fabricantes.id'))
    material = Column(String(255))
    diametro_externo = Column(Float)
    diametro_orificio_20c = Column(Float)
    espessura = Column(Float)
    asa = Column(String(255))
    diametro_nominal_dn = Column(String(255))
    diametro_interno_medio_dm = Column(Float)
    diametro_interno_medio_20c_dr = Column(Float)
    norma = Column(String(255))
    data_inspecao = Column(String(10))  # Formato YYYY-MM-DD
    data_instalacao = Column(String(10))  # Formato YYYY-MM-DD
    carta_numero = Column(String(255))
    data_maxima = Column(String(10))  # Formato YYYY-MM-DD
    data_prevista_calibracao = Column(String(10))  # Formato YYYY-MM-DD
    observacao = Column(Text)
    
    # Relacionamentos
    equipamento = relationship('Equipamento', back_populates='placa_orificio')
    fabricante = relationship('Fabricante', back_populates='placas_orificio')

# Tabela: Trechos Retos
class TrechoReto(db.Model):
    __tablename__ = 'trechos_retos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_serie_equipamento = Column(String(255), ForeignKey('equipamentos.numero_serie'), unique=True, nullable=False)
    fabricante_id = Column(Integer, ForeignKey('fabricantes.id'))
    material_confeccao = Column(String(255))
    diametro_nominal_dn = Column(String(255))
    classe_pressao = Column(String(255))
    diametro_interno_dm = Column(Float)
    diametro_interno_20c_dr = Column(Float)
    envio_tubos_montante_jusante = Column(Boolean)
    espessura_junta_vedacao = Column(Float)
    envio_valvula_porta_placa = Column(Boolean)
    envio_retificador_poco = Column(Boolean)
    envio_junta_anel = Column(Boolean)
    norma = Column(String(255))
    data_instalacao = Column(String(10))  # Formato YYYY-MM-DD
    carta_numero = Column(String(255))
    data_maxima = Column(String(10))  # Formato YYYY-MM-DD
    data_prevista_calibracao = Column(String(10))  # Formato YYYY-MM-DD
    observacao = Column(Text)
    
    # Relacionamentos
    equipamento = relationship('Equipamento', back_populates='trecho_reto')
    fabricante = relationship('Fabricante', back_populates='trechos_retos')

# Tabela: Requisitos Metrológicos
class RequisitoMetrologico(db.Model):
    __tablename__ = 'requisitos_metrologicos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    natureza_id = Column(Integer, ForeignKey('naturezas_teste_analise.id'))
    equipamento_medicao = Column(String(255))
    criterio = Column(Text, nullable=False)
    
    # Relacionamentos
    natureza = relationship('NaturezaTesteAnalise', back_populates='requisitos_metrologicos')

# Tabela: Testes de Poços
class TestePoco(db.Model):
    __tablename__ = 'testes_pocos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    instalacao_id = Column(Integer, ForeignKey('instalacoes.id'))
    poco = Column(String(255), nullable=False)
    natureza_id = Column(Integer, ForeignKey('naturezas_teste_analise.id'))
    data_teste = Column(String(10), nullable=False)  # Formato YYYY-MM-DD
    numero_btp = Column(String(255), unique=True)
    tag_medidor_oleo = Column(String(255))
    rt = Column(String(255))
    data_rt = Column(String(10))  # Formato YYYY-MM-DD
    data_desembarque = Column(String(10))  # Formato YYYY-MM-DD
    data_recebimento_btp = Column(String(10))  # Formato YYYY-MM-DD
    envio_resultado = Column(Boolean)
    bra = Column(String(255))
    validacao = Column(Boolean)
    atualizacao_potencial = Column(String(10))  # Formato YYYY-MM-DD
    observacao = Column(Text)
    
    # Relacionamentos
    instalacao = relationship('Instalacao', back_populates='testes_pocos')
    natureza = relationship('NaturezaTesteAnalise', back_populates='testes_pocos')
    eventos_cronograma = relationship('EventoCronogramaTeste', back_populates='teste_poco')

# Tabela: Cronograma de Testes de Poços (Eventos)
class EventoCronogramaTeste(db.Model):
    __tablename__ = 'eventos_cronograma_testes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    instalacao_id = Column(Integer, ForeignKey('instalacoes.id'), nullable=False)
    tag_ponto_medicao = Column(String(255), ForeignKey('pontos_medicao.tag_ponto_medicao'), nullable=False)
    poco = Column(String(255), nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)  # 1 a 12
    status = Column(String(255))  # Ex: 'Planejado', 'Realizado', 'Atrasado'
    data_realizacao = Column(String(10))  # Formato YYYY-MM-DD
    teste_poco_id = Column(Integer, ForeignKey('testes_pocos.id'))
    
    # Relacionamentos
    instalacao = relationship('Instalacao', back_populates='eventos_cronograma_testes')
    ponto_medicao = relationship('PontoMedicao', back_populates='eventos_cronograma_testes')
    teste_poco = relationship('TestePoco', back_populates='eventos_cronograma')

# Tabela: Análises Químicas (FQ)
class AnaliseQuimica(db.Model):
    __tablename__ = 'analises_quimicas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    instalacao_id = Column(Integer, ForeignKey('instalacoes.id'))
    tag_ponto_medicao = Column(String(255), ForeignKey('pontos_medicao.tag_ponto_medicao'))
    poco = Column(String(255), nullable=False)
    natureza_id = Column(Integer, ForeignKey('naturezas_teste_analise.id'))
    data_coleta = Column(String(10), nullable=False)  # Formato YYYY-MM-DD
    sot = Column(String(255))
    cilindro = Column(String(255))
    rt = Column(String(255))
    data_rt = Column(String(10))  # Formato YYYY-MM-DD
    data_desembarque = Column(String(10))  # Formato YYYY-MM-DD
    data_recebimento_lab = Column(String(10))  # Formato YYYY-MM-DD
    resultado = Column(Text)
    bra = Column(String(255))
    validacao = Column(Boolean)
    data_atualizacao_cv = Column(String(10))  # Formato YYYY-MM-DD
    observacao = Column(Text)
    
    # Relacionamentos
    instalacao = relationship('Instalacao', back_populates='analises_quimicas')
    ponto_medicao = relationship('PontoMedicao', back_populates='analises_quimicas')
    natureza = relationship('NaturezaTesteAnalise', back_populates='analises_quimicas')
    eventos_cronograma = relationship('EventoCronogramaAnalise', back_populates='analise_quimica')

# Tabela: Cronograma de Análises Químicas (Eventos)
class EventoCronogramaAnalise(db.Model):
    __tablename__ = 'eventos_cronograma_analises'
    id = Column(Integer, primary_key=True, autoincrement=True)
    instalacao_id = Column(Integer, ForeignKey('instalacoes.id'), nullable=False)
    tag_ponto_medicao = Column(String(255), ForeignKey('pontos_medicao.tag_ponto_medicao'), nullable=False)
    poco = Column(String(255), nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)  # 1 a 12
    status = Column(String(255))  # Ex: 'Planejado', 'Realizado', 'Atrasado'
    data_realizacao = Column(String(10))  # Formato YYYY-MM-DD
    analise_quimica_id = Column(Integer, ForeignKey('analises_quimicas.id'))
    
    # Relacionamentos
    instalacao = relationship('Instalacao', back_populates='eventos_cronograma_analises')
    ponto_medicao = relationship('PontoMedicao', back_populates='eventos_cronograma_analises')
    analise_quimica = relationship('AnaliseQuimica', back_populates='eventos_cronograma')

# Tabela: Gestão de Incertezas
class Incerteza(db.Model):
    __tablename__ = 'incertezas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sistema_medicao = Column(String(255), nullable=False)
    numero_relatorio = Column(String(255), unique=True, nullable=False)
    data_relatorio = Column(String(10), nullable=False)  # Formato YYYY-MM-DD
    incerteza_expandida = Column(Float)
    status_limite_id = Column(Integer, ForeignKey('status_certificado_incerteza.id'))
    status_emissao_id = Column(Integer, ForeignKey('status_certificado_incerteza.id'))
    estacao = Column(String(255))
    servico_id = Column(Integer, ForeignKey('servicos_incerteza.id'))
    motivo = Column(Text)
    limite_inferior = Column(Float)
    limite_superior = Column(Float)
    
    # Relacionamentos
    status_limite = relationship('StatusCertificadoIncerteza', foreign_keys=[status_limite_id], back_populates='incertezas_limite')
    status_emissao = relationship('StatusCertificadoIncerteza', foreign_keys=[status_emissao_id], back_populates='incertezas_emissao')
    servico = relationship('ServicoIncerteza', back_populates='incertezas')

