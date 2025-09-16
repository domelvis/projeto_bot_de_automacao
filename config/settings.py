 
# Configurações globais do bot
import os

# Caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_DIR = os.path.join(DATA_DIR, 'input')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
SCREENSHOTS_DIR = os.path.join(DATA_DIR, 'screenshots')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates', 'images')

# Configurações do bot
BOT_CONFIG = {
    'delay_between_actions': 1,
    'max_retries': 3,
    'screenshot_on_error': True,
    'failsafe_enabled': True
}