 
import pandas as pd
import os
from config.settings import INPUT_DIR, OUTPUT_DIR
from src.utils import setup_logging

logger = setup_logging()

class DataHandler:
    def __init__(self):
        self.data = None
        self.processed_count = 0
        
    def load_csv(self, filename):
        """Carrega dados do CSV"""
        try:
            filepath = os.path.join(INPUT_DIR, filename)
            self.data = pd.read_csv(filepath, encoding='utf-8')
            logger.info(f"Dados carregados: {len(self.data)} registros")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {e}")
            return False
    
    def get_product_data(self, index):
        """Retorna dados do produto por índice"""
        if self.data is not None and index < len(self.data):
            return self.data.iloc[index].to_dict()
        return None
    
    def get_total_products(self):
        """Retorna total de produtos"""
        return len(self.data) if self.data is not None else 0
    
    def save_progress(self, processed_items):
        """Salva progresso da execução"""
        progress_file = os.path.join(OUTPUT_DIR, 'progress.txt')
        with open(progress_file, 'w') as f:
            f.write(f"Processados: {processed_items}\n")
            f.write(f"Total: {self.get_total_products()}\n")