# models.py - Estrutura do Banco de Dados SQLite
import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_path="data/bot_database.db"):
        self.db_path = db_path
        # Criar pasta data se não existir
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Retorna conexão com o banco"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Cria as tabelas no banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de Bots (cada bot que você criar)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'stopped',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP
            )
        ''')
        
        # Tabela de Execuções (histórico de cada execução)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id INTEGER,
                status TEXT DEFAULT 'running',
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                error_message TEXT,
                screenshots_count INTEGER DEFAULT 0,
                FOREIGN KEY (bot_id) REFERENCES bots (id)
            )
        ''')
        
        # Tabela de Screenshots (capturas de tela)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER,
                filename TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (execution_id) REFERENCES executions (id)
            )
        ''')
        
        # Tabela de Configurações (settings do bot)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id INTEGER,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (bot_id) REFERENCES bots (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Banco de dados criado com sucesso!")
    
    def create_bot(self, name, description):
        """Cria um novo bot"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bots (name, description) 
            VALUES (?, ?)
        ''', (name, description))
        
        bot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return bot_id
    
    def start_execution(self, bot_id):
        """Inicia uma nova execução"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO executions (bot_id) 
            VALUES (?)
        ''', (bot_id,))
        
        execution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return execution_id
    
    def finish_execution(self, execution_id, status='completed', error_message=None):
        """Finaliza uma execução"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE executions 
            SET status = ?, end_time = CURRENT_TIMESTAMP, error_message = ?
            WHERE id = ?
        ''', (status, error_message, execution_id))
        
        conn.commit()
        conn.close()
    
    def save_screenshot(self, execution_id, filename, description=""):
        """Salva informação de screenshot no banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO screenshots (execution_id, filename, description) 
            VALUES (?, ?, ?)
        ''', (execution_id, filename, description))
        
        conn.commit()
        conn.close()
    
    def get_bot_history(self, bot_id):
        """Retorna histórico de execuções de um bot"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM executions 
            WHERE bot_id = ? 
            ORDER BY start_time DESC
        ''', (bot_id,))
        
        results = cursor.fetchall()
        conn.close()
        return results

# Exemplo de uso
if __name__ == "__main__":
    # Criar banco
    db = Database()
    
    # Criar um bot de exemplo
    bot_id = db.create_bot("Bot Teste", "Bot para testes de automação")
    print(f"Bot criado com ID: {bot_id}")
    
    # Simular uma execução
    execution_id = db.start_execution(bot_id)
    db.save_screenshot(execution_id, "screenshot_001.png", "Tela inicial")
    db.finish_execution(execution_id, "completed")
    
    print("✅ Teste do banco concluído!")