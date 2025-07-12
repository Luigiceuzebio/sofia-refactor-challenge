"""
Este módulo define os modelos de dados (tabelas) da aplicação usando SQLAlchemy.
Cada classe aqui representa uma tabela na base de dados que armazena o
conhecimento de longo prazo da Sofia.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

# Base declarativa que será usada por todos os modelos
Base = declarative_base()

# Tabela de Associação para a relação Muitos-para-Muitos entre Funcionários e Projetos
participacao_projeto_tabela = Table('participacao_projeto', Base.metadata,
    Column('funcionario_id', Integer, ForeignKey('funcionarios.id'), primary_key=True),
    Column('projeto_id', Integer, ForeignKey('projetos.id'), primary_key=True)
)

class Persona(Base):
    __tablename__ = 'persona'
    id = Column(Integer, primary_key=True)
    descricao = Column(Text, nullable=False, comment="Descrição de como a IA deve se comportar, seu tom, etc.")

class Empresa(Base):
    __tablename__ = 'empresa'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, comment="Missão, visão, valores e descrição geral da empresa.")

class Setor(Base):
    __tablename__ = 'setores'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(Text, comment="Descrição das responsabilidades do setor.")

class Funcionario(Base):
    __tablename__ = 'funcionarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False)
    cargo = Column(String(100))
    setor_id = Column(Integer, ForeignKey('setores.id'))
    setor = relationship("Setor")
    # Relação com projetos
    projetos = relationship("Projeto",
                            secondary=participacao_projeto_tabela,
                            back_populates="participantes")

class Gerente(Base):
    __tablename__ = 'gerentes'
    id = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False)
    area = Column(String(100), comment="A área ou setor que o gerente lidera.")

class Projeto(Base):
    __tablename__ = 'projetos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(150), unique=True, nullable=False)
    descricao = Column(Text)
    status = Column(String(50), default="Ativo")
    # Relação com funcionários
    participantes = relationship("Funcionario",
                                 secondary=participacao_projeto_tabela,
                                 back_populates="projetos")

class ConhecimentoManual(Base):
    __tablename__ = 'conhecimentos_manuais'
    id = Column(Integer, primary_key=True)
    pergunta = Column(Text, unique=True, nullable=False)
    resposta = Column(Text, nullable=False)

class Cerimonia(Base):
    __tablename__ = 'cerimonias'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, comment="Objetivo, frequência e participantes da cerimónia.")
