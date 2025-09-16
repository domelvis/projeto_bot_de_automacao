 
import time
import logging
import pyautogui
import os
from datetime import datetime
from config.settings import BOT_CONFIG, SCREENSHOTS_DIR

def setup_logging():
    """Configura sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def safe_click(x, y, retries=3):
    """Clique seguro com retry"""
    for attempt in range(retries):
        try:
            pyautogui.click(x, y)
            time.sleep(BOT_CONFIG['delay_between_actions'])
            return True
        except Exception as e:
            logging.error(f"Erro no clique (tentativa {attempt + 1}): {e}")
            if attempt == retries - 1:
                return False
    return False

def take_screenshot(name_suffix=""):
    """Captura screenshot para debug"""
    if BOT_CONFIG['screenshot_on_error']:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}{name_suffix}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        pyautogui.screenshot(filepath)
        return filepath
    return None