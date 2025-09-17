# simple_test.py - Teste simples da integração com API
import requests
import time

class SimpleBot:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.bot_id = None
        self.execution_id = None
    
    def test_api_connection(self):
        """Testa se API está funcionando"""
        try:
            response = requests.get(f"{self.api_url}/")
            if response.status_code == 200:
                print("✅ API conectada com sucesso!")
                print(f"📡 Resposta: {response.json()}")
                return True
            else:
                print(f"❌ API retornou status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao conectar com API: {e}")
            print("🐳 Certifique-se que o Docker container está rodando!")
            return False
    
    def create_test_bot(self):
        """Cria um bot de teste"""
        try:
            bot_data = {
                "name": "Bot de Teste",
                "description": "Bot criado para testar integração"
            }
            
            response = requests.post(f"{self.api_url}/bots/", json=bot_data)
            if response.status_code == 200:
                result = response.json()
                self.bot_id = result['bot_id']
                print(f"✅ Bot criado com ID: {self.bot_id}")
                return True
            else:
                print(f"❌ Erro ao criar bot: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao criar bot: {e}")
            return False
    
    def start_test_execution(self):
        """Inicia uma execução de teste"""
        try:
            response = requests.post(f"{self.api_url}/bots/{self.bot_id}/start")
            if response.status_code == 200:
                result = response.json()
                self.execution_id = result['execution_id']
                print(f"✅ Execução iniciada com ID: {self.execution_id}")
                return True
            else:
                print(f"❌ Erro ao iniciar execução: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao iniciar execução: {e}")
            return False
    
    def simulate_work(self):
        """Simula trabalho do bot"""
        print("🤖 Simulando trabalho do bot...")
        for i in range(3):
            print(f"   📋 Processando item {i+1}/3...")
            time.sleep(1)
        print("✅ Trabalho simulado concluído!")
    
    def stop_execution(self):
        """Para a execução"""
        try:
            response = requests.post(f"{self.api_url}/bots/{self.bot_id}/stop")
            if response.status_code == 200:
                print("✅ Execução finalizada!")
                return True
            else:
                print(f"❌ Erro ao finalizar execução: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao finalizar execução: {e}")
            return False
    
    def get_stats(self):
        """Mostra estatísticas do sistema"""
        try:
            response = requests.get(f"{self.api_url}/stats")
            if response.status_code == 200:
                stats = response.json()
                print("📊 Estatísticas do Sistema:")
                print(f"   🤖 Total de bots: {stats['total_bots']}")
                print(f"   ⚡ Total de execuções: {stats['total_executions']}")
                print(f"   ✅ Execuções bem-sucedidas: {stats['successful_executions']}")
                print(f"   📈 Taxa de sucesso: {stats['success_rate']}")
                return True
            else:
                print(f"❌ Erro ao obter stats: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao obter stats: {e}")
            return False
    
    def run_full_test(self):
        """Executa teste completo"""
        print("🚀 Iniciando teste completo da integração...")
        print("="*50)
        
        # 1. Testar conexão
        if not self.test_api_connection():
            return False
        
        # 2. Criar bot
        if not self.create_test_bot():
            return False
        
        # 3. Iniciar execução
        if not self.start_test_execution():
            return False
        
        # 4. Simular trabalho
        self.simulate_work()
        
        # 5. Finalizar execução
        if not self.stop_execution():
            return False
        
        # 6. Mostrar estatísticas
        self.get_stats()
        
        print("="*50)
        print("🎉 TESTE COMPLETO FINALIZADO COM SUCESSO!")
        print("✅ Sua integração bot + API está funcionando perfeitamente!")
        return True

if __name__ == "__main__":
    bot = SimpleBot()
    bot.run_full_test()