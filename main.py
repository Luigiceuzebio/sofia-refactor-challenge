import asyncio
from brain import SofiaBrain
from config import constants # Importa o nosso novo ficheiro de constantes

async def main():
    """Função principal para iniciar e interagir com a Sofia."""
    print("A carregar a Sofia... Por favor, aguarde.")
    
    # Instancia o cérebro da Sofia, passando as constantes
    sofia = SofiaBrain(app_constants=vars(constants))
    
    print("\n--- Sofia Online ---")
    print("Digite 'sair' a qualquer momento para terminar a conversa.")
    
    user_id = "terminal_user"
    nome_usuario = "Dev"

    while True:
        user_message = input(f"\n{nome_usuario}: ")
        if user_message.lower() == 'sair':
            print("\nSofia: Até à próxima! 👋")
            break
            
        # Obtém a resposta da Sofia
        resposta = await sofia.responder(user_id, user_message, nome_usuario)
        
        print(f"\nSofia: {resposta}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nConversa interrompida pelo utilizador.")