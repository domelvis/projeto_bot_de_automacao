import time
import os
import requests
from datetime import datetime
from data_handler import DataHandler
from screen_capture import ScreenController
from utils import setup_logging, safe_click, take_screenshot
import sys
sys.path.append('../config')
try:
    from settings import BOT_CONFIG, TEMPLATES_DIR
except ImportError:
    BOT_CONFIG = {}
    TEMPLATES_DIR = "templates"

logger = setup_logging()

class AutomationBot:
    def __init__(self, api_url="http://localhost:8000"):
        self.data_handler = DataHandler()
        self.screen_controller = ScreenController()
        self.is_logged_in = False
        self.current_index = 0
        self.api_url = api_url
        
        # Dados da execução atual
        self.bot_id = None
        self.execution_id = None
        
    def register_bot_if_needed(self, bot_name="Bot de Automação", description="Bot para cadastro de produtos"):
        """Registra o bot na API se ainda não existir"""
        try:
            # Verificar se já existe um bot
            response = requests.get(f"{self.api_url}/bots/")
            if response.status_code == 200:
                bots = response.json().get('bots', [])
                
                # Procurar bot existente
                for bot in bots:
                    if bot['name'] == bot_name:
                        self.bot_id = bot['id']
                        logger.info(f"Bot encontrado: ID {self.bot_id}")
                        return self.bot_id
            
            # Criar novo bot se não existir
            bot_data = {
                "name": bot_name,
                "description": description
            }
            response = requests.post(f"{self.api_url}/bots/", json=bot_data)
            if response.status_code == 200:
                self.bot_id = response.json()['bot_id']
                logger.info(f"Novo bot criado: ID {self.bot_id}")
                return self.bot_id
            
        except Exception as e:
            logger.warning(f"Erro ao registrar bot na API: {e}")
            logger.info("Continuando sem integração com API...")
        
        return None
    
    def start_execution(self):
        """Inicia uma nova execução na API"""
        if not self.bot_id:
            return None
            
        try:
            response = requests.post(f"{self.api_url}/bots/{self.bot_id}/start")
            if response.status_code == 200:
                self.execution_id = response.json()['execution_id']
                logger.info(f"Execução iniciada: ID {self.execution_id}")
                return self.execution_id
        except Exception as e:
            logger.warning(f"Erro ao iniciar execução na API: {e}")
        
        return None
    
    def finish_execution(self, status="completed", error_message=None):
        """Finaliza a execução na API"""
        if not self.execution_id:
            return
            
        try:
            # Finalizar execução via API
            requests.post(f"{self.api_url}/bots/{self.bot_id}/stop")
            logger.info(f"Execução finalizada: {status}")
        except Exception as e:
            logger.warning(f"Erro ao finalizar execução na API: {e}")
    
    def save_screenshot_to_api(self, filename, description=""):
        """Salva informação do screenshot na API"""
        if not self.execution_id:
            return
            
        try:
            # Aqui você pode implementar upload do arquivo se quiser
            # Por enquanto só registra o nome do arquivo
            logger.info(f"Screenshot salvo: {filename} - {description}")
        except Exception as e:
            logger.warning(f"Erro ao salvar screenshot na API: {e}")
        
    def login(self, username, password):
        """Executa processo de login"""
        try:
            logger.info("Iniciando processo de login...")
            
            # Registrar bot e iniciar execução
            self.register_bot_if_needed("Bot Login", "Bot para processo de login")
            self.start_execution()
            
            # Capturar screenshot inicial
            initial_screenshot = take_screenshot("login_start")
            self.save_screenshot_to_api(initial_screenshot, "Início do processo de login")
            
            # AQUI VOCÊ VAI PERSONALIZAR PARA SEU SISTEMA
            # Por enquanto vamos simular um login básico
            
            logger.info("Aguardando 3 segundos...")
            time.sleep(3)
            
            # Exemplo: digitar usuário
            self.screen_controller.type_text(username)
            time.sleep(1)
            
            # Tab para próximo campo
            import pyautogui
            pyautogui.press('tab')
            time.sleep(1)
            
            # Digitar senha
            self.screen_controller.type_text(password)
            time.sleep(1)
            
            # Enter para login
            pyautogui.press('enter')
            time.sleep(3)
            
            # Screenshot após login
            login_screenshot = take_screenshot("login_success")
            self.save_screenshot_to_api(login_screenshot, "Login realizado com sucesso")
            
            self.is_logged_in = True
            logger.info("Login realizado com sucesso")
            return True
                
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            error_screenshot = take_screenshot("login_error")
            self.save_screenshot_to_api(error_screenshot, f"Erro no login: {str(e)}")
            self.finish_execution("failed", str(e))
            return False
    
    def process_all_products(self, csv_filename):
        """Processa todos os produtos do CSV"""
        try:
            # Registrar bot para processamento de produtos
            self.register_bot_if_needed("Bot Produtos", f"Processamento de produtos do arquivo {csv_filename}")
            self.start_execution()
            
            if not self.data_handler.load_csv(csv_filename):
                self.finish_execution("failed", "Erro ao carregar arquivo CSV")
                return False
            
            total_products = self.data_handler.get_total_products()
            successful_count = 0
            
            logger.info(f"Iniciando processamento de {total_products} produtos")
            
            # Screenshot inicial
            start_screenshot = take_screenshot("processing_start")
            self.save_screenshot_to_api(start_screenshot, f"Início do processamento de {total_products} produtos")
            
            for i in range(total_products):
                try:
                    product_data = self.data_handler.get_product_data(i)
                    
                    if product_data:
                        product_name = product_data.get('nome', 'N/A')
                        logger.info(f"Processando produto {i+1}/{total_products}: {product_name}")
                        
                        # AQUI VOCÊ VAI PERSONALIZAR O CADASTRO
                        # Por enquanto só simula o processo
                        time.sleep(2)
                        successful_count += 1
                        
                        # Screenshot a cada 10 produtos processados
                        if (i + 1) % 10 == 0:
                            progress_screenshot = take_screenshot(f"progress_{i+1}")
                            self.save_screenshot_to_api(
                                progress_screenshot, 
                                f"Progresso: {i+1}/{total_products} produtos processados"
                            )
                        
                        # Salvar progresso
                        self.data_handler.save_progress(successful_count)
                        
                except Exception as e:
                    logger.error(f"Erro no produto {i+1}: {e}")
                    error_screenshot = take_screenshot(f"product_{i+1}_error")
                    self.save_screenshot_to_api(error_screenshot, f"Erro no produto {i+1}: {str(e)}")
            
            # Screenshot final
            final_screenshot = take_screenshot("processing_complete")
            self.save_screenshot_to_api(
                final_screenshot, 
                f"Processamento concluído: {successful_count}/{total_products} produtos"
            )
            
            logger.info(f"Processamento concluído: {successful_count}/{total_products} produtos")
            
            # Finalizar execução com sucesso
            if successful_count == total_products:
                self.finish_execution("completed")
            else:
                self.finish_execution("completed_with_errors", f"{total_products - successful_count} produtos falharam")
            
            return successful_count
            
        except Exception as e:
            logger.error(f"Erro no processamento geral: {e}")
            self.finish_execution("failed", str(e))
            return False
    
    def get_execution_stats(self):
        """Retorna estatísticas da execução atual"""
        if not self.execution_id:
            return None
            
        try:
            response = requests.get(f"{self.api_url}/bots/{self.bot_id}/executions")
            if response.status_code == 200:
                executions = response.json().get('executions', [])
                if executions:
                    return executions[0]  # Última execução
        except Exception as e:
            logger.warning(f"Erro ao obter estatísticas: {e}")
        
        return None
    
    def run_full_automation(self, username, password, csv_filename):
        """Executa a automação completa: login + processamento"""
        logger.info("=== INICIANDO AUTOMAÇÃO COMPLETA ===")
        
        try:
            # Step 1: Login
            if not self.login(username, password):
                logger.error("Falha no login. Interrompendo automação.")
                return False
            
            # Step 2: Processar produtos
            successful_count = self.process_all_products(csv_filename)
            
            # Step 3: Relatório final
            stats = self.get_execution_stats()
            if stats:
                logger.info(f"Estatísticas finais: {stats}")
            
            logger.info("=== AUTOMAÇÃO COMPLETA FINALIZADA ===")
            return successful_count > 0
            
        except Exception as e:
            logger.error(f"Erro na automação completa: {e}")
            return False

# Exemplo de uso
if __name__ == "__main__":
    bot = AutomationBot()
    
    # Teste simples
    # bot.run_full_automation("usuario_teste", "senha_teste", "produtos.csv")
    
    print("Bot integrado com API pronto para uso!")