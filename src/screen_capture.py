 
import pyautogui
import time
import os
from src.utils import setup_logging, take_screenshot

logger = setup_logging()

class ScreenController:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        
    def find_element_by_image(self, template_path, confidence=0.8):
        """Localiza elemento na tela por imagem"""
        try:
            location = pyautogui.locateOnScreen(
                template_path, 
                confidence=confidence
            )
            if location:
                center = pyautogui.center(location)
                return center.x, center.y
            return None, None
        except Exception as e:
            logger.error(f"Erro ao localizar elemento: {e}")
            take_screenshot("_element_not_found")
            return None, None
    
    def wait_for_element(self, template_path, timeout=30, confidence=0.8):
        """Aguarda elemento aparecer na tela"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            x, y = self.find_element_by_image(template_path, confidence)
            if x and y:
                return x, y
            time.sleep(1)
        return None, None
    
    def type_text(self, text, interval=0.1):
        """Digita texto com intervalo entre caracteres"""
        pyautogui.write(str(text), interval=interval)
    
    def clear_field(self):
        """Limpa campo selecionado"""
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.press('delete')