# database/setup.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Persona, Empresa, Setor, Funcionario, Gerente, Projeto, ConhecimentoManual, Cerimonia

# Define o caminho da base de dados
DATABASE_URL = "sqlite:///./sofia.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_database():
    """Cria todas as tabelas na base de dados."""
    print("A criar tabelas da base de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")

def populate_initial_data():
    """Popula a base de dados com alguns dados iniciais para teste."""
    db = SessionLocal()
    try:
        # Verifica se os dados já existem
        if db.query(Persona).count() == 0:
            print("A popular dados iniciais...")
            # Adiciona dados de exemplo
            db.add(Persona(descricao="Você é Sofia, uma IA assistente da Sonar. Você é amigável, eficiente e proativa."))
            db.add(Empresa(nome="Sonar", descricao="A Sonar é uma empresa de tecnologia focada em soluções inovadoras de gestão."))
            db.add(Setor(nome="Engenharia", descricao="Responsável pelo desenvolvimento e manutenção dos produtos."))
            db.add(Setor(nome="Design", descricao="Responsável pela experiência do utilizador e interface dos produtos."))
            db.commit()
            print("Dados iniciais populados.")
        else:
            print("A base de dados já contém dados.")
    finally:
        db.close()

if __name__ == "__main__":
    create_database()
    populate_initial_data()