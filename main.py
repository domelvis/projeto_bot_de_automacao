 
#!/usr/bin/env python3
"""
Bot de Automação de Cadastro de Produtos
Versão: 1.0
"""

import sys
import os
from src.bot_controller import AutomationBot
from src.utils import setup_logging
from config.settings import BOT_CONFIG

logger = setup_logging()

def main():
    """Função principal"""
    try:
        # Inicializar bot
        bot = AutomationBot()
        
        # Credenciais (MUDE AQUI SUAS CREDENCIAIS)
        username = "seu_usuario"
        password = "sua_senha"
        csv_filename = "produtos.csv"
        
        logger.info("=== INICIANDO BOT DE AUTOMAÇÃO ===")
        print("🤖 Bot de Automação iniciado!")
        print("⚠️  Pressione Ctrl+C para parar a qualquer momento")
        
        # Fazer login
        print("\n🔐 Fazendo login...")
        if not bot.login(username, password):
            logger.error("Falha no login. Encerrando...")
            print("❌ Falha no login!")
            return False
        
        print("✅ Login realizado com sucesso!")
        
        # Processar produtos
        print(f"\n📦 Processando produtos do arquivo: {csv_filename}")
        success_count = bot.process_all_products(csv_filename)
        
        if success_count > 0:
            print(f"🎉 Automação concluída! {success_count} produtos processados")
            logger.info(f"Automação concluída com sucesso: {success_count} produtos processados")
            return True
        else:
            print("❌ Nenhum produto foi processado")
            logger.error("Nenhum produto foi processado com sucesso")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️  Automação interrompida pelo usuário")
        logger.info("Automação interrompida pelo usuário")
        return False
    except Exception as e:
        print(f"💥 Erro fatal: {e}")
        logger.error(f"Erro fatal: {e}")
        return False

if __name__ == "__main__":
    success = main()
    input("\nPressione Enter para sair...")
    sys.exit(0 if success else 1)