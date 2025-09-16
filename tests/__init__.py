"""
Bot Automation Project
=====================

Este módulo contém as funcionalidades principais para automação de bot.
"""

__version__ = "1.0.0"
__author__ = "Seu Nome"
__email__ = "seu.email@exemplo.com"

# Importações principais do projeto
try:
    from .main import main
    from .config import settings
except ImportError:
    # Caso os módulos ainda não existam
    pass

# Configurações do pacote
__all__ = [
    "main",
    "settings",
] 
