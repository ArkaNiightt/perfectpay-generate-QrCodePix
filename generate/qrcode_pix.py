"""
Módulo para geração de PIX através do sistema Perfect Pay.

Este módulo fornece uma interface automatizada para gerar códigos PIX
utilizando Selenium WebDriver para interagir com o checkout do Perfect Pay.
"""

import base64
import io
import logging
import os
import sys
import time
from typing import Optional

import cuid
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class PerfectPayPixGenerator:
    """
    Classe para gerar códigos PIX através do sistema Perfect Pay.

    Esta classe automatiza o processo de checkout e geração de PIX
    utilizando Selenium WebDriver com configurações anti-detecção.
    """

    def __init__(
        self,
        base_url: str,
        headless: bool = False,
        user_agent: Optional[str] = None,
        timeout: int = 10
    ):
        """
        Inicializa o gerador de PIX.

        Args:
            base_url: URL base do checkout Perfect Pay
            headless: Se deve executar em modo headless
            user_agent: User agent customizado para o navegador
            timeout: Timeout padrão para esperas (em segundos)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.driver = None
        self.wait = None

        self._setup_driver(headless, user_agent)
        self._create_logs_dir()
        self._setup_logging()

    def _create_logs_dir(self):
        """Cria o diretório de logs se não existir."""
        # Cria diretórios apenas se não existirem
        if not os.path.exists('logs'):
            os.makedirs('logs')
        if not os.path.exists('images'):
            os.makedirs('images')
        if not os.path.exists('images/prints'):
            os.makedirs('images/prints')

        # Cria arquivo de log apenas se não existir
        if not os.path.exists('logs/generate_qrcode_pix.log'):
            with open('logs/generate_qrcode_pix.log', 'w') as f:
                f.write('')  # Cria o arquivo vazio

    def _setup_logging(self):
        """Configura o sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/generate_qrcode_pix.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)

    def _setup_driver(self, headless: bool, user_agent: Optional[str]):
        """Configura o WebDriver com as opções necessárias."""
        chrome_options = self._create_chrome_options(headless, user_agent)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, self.timeout)

        # Remove propriedades que identificam automação
        self._remove_automation_properties()

    def _create_chrome_options(self, headless: bool, user_agent: Optional[str]) -> Options:
        """Cria as opções do Chrome com configurações anti-detecção."""
        options = Options()

        if headless:
            options.add_argument("--headless")

        # Configurações básicas de segurança e performance
        basic_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-logging",
            "--log-level=3",
            "--silent",
            "--disable-default-apps",
            "--disable-background-timer-throttling",
            "--disable-background-networking",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--enable-unsafe-swiftshader"
        ]

        for arg in basic_args:
            options.add_argument(arg)

        # Configurações anti-detecção
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if user_agent:
            options.add_argument(f"user-agent={user_agent}")

        return options

    def _remove_automation_properties(self):
        """Remove propriedades que identificam automação."""
        script = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        self.driver.execute_script(script)

    def generate_pix(
        self,
        email: str,
        name: str,
        phone: str,
        cpf: str
    ) -> str:
        """
        Gera um código PIX através do sistema Perfect Pay.

        Args:
            email: Email do cliente
            name: Nome do cliente
            phone: Telefone do cliente
            cpf: CPF do cliente (padrão para testes)

        Returns:
            Código PIX gerado ou string vazia em caso de erro

        Raises:
            Exception: Quando não é possível gerar o PIX
        """
        try:
            self.logger.info(f"Iniciando geração de PIX para: {email}")

            # Navega para a página de checkout
            self._navigate_to_checkout(email, name, phone)

            # Preenche o formulário
            self._fill_cpf_field(cpf)

            # Finaliza a compra
            self._finish_purchase()

            # Verifica se há PIX já gerado
            self._handle_existing_pix()

            # Aguarda e captura o QR Code
            qr_code = self._capture_qr_code()

            # Captura e exibe a imagem do QR Code no terminal
            qr_image_base64 = self.capture_and_display_qr_image(cpf=cpf)

            self.logger.info(f"PIX gerado com sucesso para: {email}")
            return qr_code

        except Exception as e:
            self.logger.error(f"Erro ao gerar PIX: {str(e)}")
            self._take_screenshot("error_screenshot")
            return ""

    def _navigate_to_checkout(self, email: str, name: str, phone: str):
        """Navega para a página de checkout com os parâmetros."""
        url = f"{self.base_url}?email={email}&name={name}&phone={phone}"
        self.driver.get(url)
        time.sleep(1)
        self.logger.info(f"Navegando para checkout: {url}")

    def _fill_cpf_field(self, cpf: str):
        """Preenche o campo de CPF."""
        cpf_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "identification-number"))
        )
        cpf_field.send_keys(cpf)
        self.logger.info("Campo CPF preenchido")

    def _finish_purchase(self):
        """Clica no botão de finalizar compra."""
        try:
            finish_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "finish-buy-btn"))
            )

            # Scroll para o botão e clica
            self.driver.execute_script("arguments[0].scrollIntoView(true);", finish_btn)
            time.sleep(1)

            try:
                finish_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", finish_btn)

            self.logger.info("Botão de finalizar compra clicado")

        except Exception as e:
            self.logger.error(f"Erro ao clicar no botão de finalizar: {str(e)}")
            # Tentativa alternativa
            try:
                finish_btn = self.driver.find_element(By.ID, "finish-buy-btn")
                self.driver.execute_script("arguments[0].click();", finish_btn)
                self.logger.info("Botão clicado com JavaScript")
            except:
                raise Exception("Não foi possível clicar no botão de finalizar compra")

    def _handle_existing_pix(self):
        """Verifica e trata PIX já gerado."""
        time.sleep(3)

        try:
            # Tenta encontrar botão de PIX já gerado
            pix_selectors = [
                "//a[contains(@class, 'btn-primary') and contains(text(), 'Abrir')]",
                "//a[contains(@href, '/payments/thanks')]",
                "//a[contains(., 'Abrir') and contains(., 'Pix') and contains(., 'já gerado')"
            ]

            pix_button = None
            for selector in pix_selectors:
                try:
                    pix_button = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue

            if pix_button:
                self.logger.info("PIX já gerado detectado. Clicando no botão...")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", pix_button)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", pix_button)
                time.sleep(3)
            else:
                self.logger.info("Nenhum PIX já gerado encontrado")

        except Exception as e:
            self.logger.info(f"Erro ao verificar PIX já gerado: {str(e)}")

    def _capture_qr_code(self) -> str:
        """Captura o QR Code da página."""
        time.sleep(3)

        # Verifica se ainda está na página de confirmação
        current_url = self.driver.current_url
        if "/payment/" in current_url:
            self.logger.info("Aguardando redirecionamento...")
            time.sleep(5)
            current_url = self.driver.current_url
            self.logger.info(f"URL após aguardar: {current_url}")

        # Aguarda e captura o QR Code
        try:
            qr_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "qrCode"))
            )
            qr_code = qr_element.get_attribute("value")
            self.logger.info("QR Code capturado com sucesso")
            return qr_code

        except Exception:
            self.logger.error("QR Code não encontrado após 15 segundos")
            self._take_screenshot("qr_code_not_found")
            raise Exception("QR Code não foi encontrado na página")

    def capture_and_display_qr_image(self, cpf: str) -> Optional[str]:
        """
        Captura a imagem do QR Code da página e salva em arquivo.

        Returns:
            Base64 da imagem do QR Code ou None se não encontrada
        """
        try:
            self.logger.info("Capturando imagem do QR Code...")

            # Aguarda a imagem do QR Code aparecer
            qr_image = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='data:image']"))
            )

            # Obtém o src da imagem (base64)
            img_src = qr_image.get_attribute("src")

            if not img_src or not img_src.startswith("data:image"):
                self.logger.error("Imagem do QR Code não encontrada ou formato inválido")
                return None

            # Extrai o base64 da string data URL
            base64_data = img_src.split(",")[1]

            # Decodifica o base64 para bytes
            image_bytes = base64.b64decode(base64_data)

            # Cria uma imagem PIL
            image = Image.open(io.BytesIO(image_bytes))

            # Salva a imagem em arquivo
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"images/qrcode_pix_{cpf}_{timestamp}.png"
            image.save(filename)

            # Exibe informações no terminal
            print("\n🔄 QR Code PIX Capturado:")
            print(f"📁 Arquivo salvo: {filename}")
            print(f"📏 Dimensões: {image.width}x{image.height} pixels")
            print(f"💾 Tamanho: {len(image_bytes)} bytes")
            print("\n✅ Imagem salva com sucesso!\n")

            self.logger.info(f"Imagem do QR Code salva: {filename}")
            return base64_data

        except Exception as e:
            self.logger.error(f"Erro ao capturar e salvar imagem do QR Code: {str(e)}")
            return None

    def _take_screenshot(self, filename: str):
        """Tira um screenshot da página atual."""
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            full_filename = f"images/prints/{filename}_{timestamp}.png"

            # Cria o diretório apenas se não existir
            dir_path = os.path.dirname(full_filename)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            self.driver.save_screenshot(full_filename)
            self.logger.info(f"Screenshot salvo: {full_filename}")

        except Exception as e:
            self.logger.error(f"Erro ao salvar screenshot: {str(e)}")

    def navigate_to(self, url: str):
        """Navega para uma URL específica."""
        self.driver.get(url)
        self.logger.info(f"Navegando para: {url}")

    def execute_javascript(self, script: str):
        """Executa um script JavaScript na página."""
        return self.driver.execute_script(script)

    def wait_for_element(self, selector: str, by=By.CSS_SELECTOR, timeout: int = None):
        """Aguarda e retorna um elemento específico."""
        if timeout is None:
            timeout = self.timeout

        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element

    def close(self):
        """Fecha o navegador e libera recursos."""
        if self.driver:
            self.driver.quit()
            self.logger.info("Navegador fechado")


def generate_random_string() -> str:
    """
    Gera uma string aleatória usando cuid.

    Returns:
        String aleatória única
    """
    return cuid.cuid()
