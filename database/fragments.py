"""
Este módulo contém as funções responsáveis por consultar a base de dados
e gerar os "fragmentos" de texto. Cada fragmento é um pedaço de contexto
que será injetado no prompt do sistema da OpenAI para tornar as respostas
da Sofia mais precisas e contextualizadas.
"""

from sqlalchemy.orm import Session
from . import models 

def gerar_fragmento_persona(db: Session) -> str:
    """Busca a descrição da persona da IA na base de dados."""
    try:
        persona = db.query(models.Persona).first()
        if persona:
            return f"### Sua Persona\n{persona.descricao}"
    except Exception as e:
        print(f"Erro ao buscar fragmento de persona: {e}")
    return ""

def gerar_fragmento_empresa(db: Session) -> str:
    """Busca a descrição da empresa na base de dados."""
    try:
        empresa = db.query(models.Empresa).first()
        if empresa:
            return f"### Sobre a Empresa ({empresa.nome})\n{empresa.descricao}"
    except Exception as e:
        print(f"Erro ao buscar fragmento de empresa: {e}")
    return ""

def gerar_fragmento_setores(db: Session) -> str:
    """Busca e formata a lista de setores da empresa."""
    try:
        setores = db.query(models.Setor).all()
        if not setores:
            return ""
        
        lista_setores = "\n".join([f"- **{s.nome}**: {s.descricao}" for s in setores])
        return f"### Setores da Empresa\n{lista_setores}"
    except Exception as e:
        print(f"Erro ao buscar fragmento de setores: {e}")
    return ""

def gerar_fragmento_funcionarios(db: Session) -> str:
    """Busca e formata a lista de alguns funcionários."""
    try:
        funcionarios = db.query(models.Funcionario).limit(15).all()
        if not funcionarios:
            return ""
            
        lista_funcionarios = ", ".join([f.nome for f in funcionarios])
        return f"### Alguns Membros da Equipa\nEstes são alguns dos membros da equipa: {lista_funcionarios}."
    except Exception as e:
        print(f"Erro ao buscar fragmento de funcionários: {e}")
    return ""

def gerar_fragmento_gerentes(db: Session) -> str:
    """Busca e formata a lista de gerentes."""
    try:
        gerentes = db.query(models.Gerente).all()
        if not gerentes:
            return ""
            
        lista_gerentes = "\n".join([f"- {g.nome} (Líder de {g.area})" for g in gerentes])
        return f"### Liderança\n{lista_gerentes}"
    except Exception as e:
        print(f"Erro ao buscar fragmento de gerentes: {e}")
    return ""

def gerar_fragmento_projetos(db: Session) -> str:
    """Busca e formata a lista de projetos ativos."""
    try:
        projetos = db.query(models.Projeto).filter_by(status="Ativo").all()
        if not projetos:
            return ""
            
        lista_projetos = "\n".join([f"- **{p.nome}**: {p.descricao}" for p in projetos])
        return f"### Principais Projetos Atuais\n{lista_projetos}"
    except Exception as e:
        print(f"Erro ao buscar fragmento de projetos: {e}")
    return ""

def gerar_fragmento_participacoes(db: Session) -> str:
    """Busca e formata a participação de funcionários em projetos."""
    try:
        projetos_com_participantes = db.query(models.Projeto).filter(models.Projeto.participantes.any()).limit(5).all()
        if not projetos_com_participantes:
            return ""

        texto_participacoes = ""
        for projeto in projetos_com_participantes:
            nomes_participantes = ", ".join([p.nome for p in projeto.participantes])
            texto_participacoes += f"- No projeto **{projeto.nome}** participam: {nomes_participantes}.\n"
        
        return f"### Exemplo de Participação em Projetos\n{texto_participacoes}"
    except Exception as e:
        print(f"Erro ao buscar fragmento de participações: {e}")
    return ""

def gerar_fragmento_conhecimentos(db: Session) -> str:
    """Busca e formata alguns conhecimentos manuais para dar contexto à IA."""
    try:
        conhecimentos = db.query(models.ConhecimentoManual).limit(10).all()
        if not conhecimentos:
            return ""
            
        lista_conhecimentos = "\n".join([f"- Se perguntarem '{c.pergunta}', a resposta é relacionada a '{c.resposta[:50]}...'" for c in conhecimentos])
        return f"### Base de Conhecimento Rápido\n{lista_conhecimentos}"
    except Exception as e:
        print(f"Erro ao buscar fragmento de conhecimentos: {e}")
    return ""

def gerar_fragmento_cerimonias(db: Session) -> str:
    """Busca e formata as cerimónias ou rituais da empresa."""
    try:
        cerimonias = db.query(models.Cerimonia).all()
        if not cerimonias:
            return ""
            
        lista_cerimonias = "\n".join([f"- **{c.nome}**: {c.descricao}" for c in cerimonias])
        return f"### Rituais e Cerimónias\n{lista_cerimonias}"
    except Exception as e:
        print(f"Erro ao buscar fragmento de cerimónias: {e}")
    return ""
