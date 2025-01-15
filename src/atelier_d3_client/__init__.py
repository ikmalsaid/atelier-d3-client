import os
import uuid
import json
import base64
import requests
import tempfile
from PIL import Image
from io import BytesIO
from datetime import datetime
from selenium import webdriver
from importlib import resources
from colorpaws import setup_logger
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AtelierD3Client():
    def __init__(self, log_on=True, log_to=None, save_to="outputs", save_as="webp"):
        """
        Initialize Atelier D3 Client module.

        Parameters:
        - log_on (bool): Enable logging.
        - log_to  (str): Directory to save logs.
        - save_to (str): Directory to save outputs.
        - save_as (str): Output format ('webp', 'jpg').
        """
        self.__logger = setup_logger(
            name=self.__class__.__name__, 
            log_on=log_on, 
            log_to=log_to
        )
        
        self.version = "25.1"
        
        self.__online_check()
        self.__load_preset()
        
        self.__init_checks(save_to, save_as)
        self.__driver = self.__get_webdriver()
        self.__authenticate()
        
        self.__logger.info(f"Atelier D3 Client is now ready!")

    def __init_checks(self, save_to: str, save_as: str):
        """
        Initialize essential checks.
        """
        try:
            self.save_to = save_to if save_to else tempfile.gettempdir()
            self.save_to = os.path.join(self.save_to, "atelier_d3")
            
            if save_as.lower() in ['webp', 'jpg']:
                self.save_as = save_as.lower()
            else:
                self.__logger.warning(f"Invalid save format '{save_as}', defaulting to WEBP")
                self.save_as = 'webp'
        
        except Exception as e:
            error = f"Error in init_checks: {e}"
            self.__logger.error(error)
            raise RuntimeError(error)
   
    def __online_check(self, url: str = 'https://www.google.com', timeout: int = 10):
        """
        Check if there is an active internet connection.
        """
        try:
            requests.get(url, timeout=timeout)
        
        except Exception as e:
            error = f"No internet connection available! Please check your network connection."
            self.__logger.error(error)
            raise RuntimeError(error)
    
    def __load_preset(self, preset_path='__dtr__.py'):
        try: 
            with open(resources.path(__name__, preset_path), 'r', encoding="utf-8") as f:
                __preset = json.load(f)
            
            self.__se = base64.b64decode(__preset["locale"][0]).decode('utf-8')
            self.__au = base64.b64decode(__preset["locale"][1]).decode('utf-8')
            self.__us = base64.b64decode(__preset["locale"][2]).decode('utf-8')
            self.__pa = base64.b64decode(__preset["locale"][3]).decode('utf-8')
        
        except Exception as e:
            error = f"Error in load_preset: {e}"
            self.__logger.error(error)
            raise RuntimeError(error)
    
    def __get_webdriver(self):
        try:            
            options = Options()
            options.add_argument('--disable-gpu')
            options.add_argument("--headless=new")
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
            
            try:
                self.__logger.info('Attempting to use system ChromeDriver!')
                return webdriver.Chrome(options=options)
            
            except WebDriverException as e:
                self.__logger.info('System ChromeDriver not found or incompatible, downloading appropriate version!')
                service = Service(ChromeDriverManager().install())
                return webdriver.Chrome(service=service, options=options)
            
            finally:
                self.__logger.info('Webdriver is ready!')
        
        except Exception as e:
            error = f"Error in get_webdriver: {e}"
            self.__logger.error(error)
            raise RuntimeError(error)

    def __authenticate(self):
        try:
            self.__driver.get(self.__au)
            
            step_a = WebDriverWait(self.__driver, 15).until(EC.visibility_of_element_located((By.ID, "i0116")))
            step_a.send_keys(self.__us)
            
            step_b = WebDriverWait(self.__driver, 15).until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            step_b.click()
            
            step_c = WebDriverWait(self.__driver, 15).until(EC.visibility_of_element_located((By.ID, "i0118")))
            step_c.send_keys(self.__pa)
            
            step_d = WebDriverWait(self.__driver, 15).until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            step_d.click()
            
            step_e = WebDriverWait(self.__driver, 15).until(EC.element_to_be_clickable((By.ID, "acceptButton")))
            step_e.click()
        
        except Exception as e:
            error = f"Error in authenticate: {e}"
            self.__logger.error(error)
            raise RuntimeError(error)

    # def __setup_save_dir(self, save_dir: str):
    #     """Setup save directory"""

    #     try:
    #         if save_dir:
    #             self.local_save = True
    #             self.save_dir = save_dir
    #             os.makedirs(self.save_dir, exist_ok=True)
    #         else:
    #             self.local_save = False
    #             self.save_dir = None
        
    #     except Exception as e:
    #         error = f"Error in setup_save_dir: {e}"
    #         self.__logger.error(error)
    #         raise RuntimeError(error)
    
    def __get_task_id(self):
        """
        Generate a unique task ID for request tracking.
        Returns a truncated UUID (8 characters).
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            uuid_part = str(uuid.uuid4())[:8]
            task_id = f"{timestamp}_{uuid_part}"
            
            self.__logger.info(f"[{task_id}] Created task id from request!")
            return task_id
        
        except Exception as e:
            error = f"Error in get_task_id: {e}"
            self.__logger.error(error)
            raise RuntimeError(error)
                 
    def __save_image(self, url: str, task_id, index: int = 1) -> str:
        """Helper function to save an image from a URL to a temporary file."""
        try:
            date_part = task_id.split('_')[0]
            formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
        
            output_dir = os.path.join(self.save_to, formatted_date)
            os.makedirs(output_dir, exist_ok=True)
            
            response = requests.get(url)
            
            if self.save_as == 'webp':
                try:                
                    img = Image.open(BytesIO(response.content))
                    
                    webp_buffer = BytesIO()
                    img.save(webp_buffer, format='WebP', quality=90)
                    content = webp_buffer.getvalue()
                    suffix = '.webp'
                    
                except Exception as e:
                    self.__logger.warning(f"[{task_id}] Failed to convert to WebP, falling back to JPG!")
                    content = response.content
                    suffix = '.jpg'
            else:
                content = response.content
                suffix = '.jpg'

            filename = f"{task_id}_{index}{suffix}"
            file_path = os.path.join(output_dir, filename)
            
            with open(file_path, 'wb') as output:
                output.write(content)
                
            self.__logger.info(f"[{task_id}] Saved output: {file_path}")
            return file_path
                
        except Exception as e:
            error = f"[{task_id}] Error in save_image: {e}"
            self.__logger.error(error)
            raise RuntimeError(error)

    def __v1(self, prompt, task_id) -> list:
        try:
            self.__driver.get(self.__se)
            self.__driver.refresh()
            
            self.__driver.find_element(By.ID, "sb_form_q").send_keys(prompt)
            self.__driver.find_element(By.ID, "create_btn_c").click()

            try:
                WebDriverWait(self.__driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "gil_err_tc")))
                raise Exception(f'[{task_id}] Request blocked (likely explicit content)')
            
            except TimeoutException:
                pass

            saved_images = []
            while True:
                self.__logger.info(f"[{task_id}] Refreshing request!")
                self.__driver.refresh()

                try:
                    WebDriverWait(self.__driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "img_cont")))
                    divs = self.__driver.find_elements(By.CLASS_NAME, "img_cont")
                    urls = [div.find_element(By.TAG_NAME, "img").get_attribute("src").split("?")[0] for div in divs]
                    self.__logger.info(f'[{task_id}] Found {len(urls)} images!')
                    
                    for idx, url in enumerate(urls, 1):
                        if filename := self.__save_image(url, task_id, idx):
                            saved_images.append(filename)
                    return saved_images
                
                except TimeoutException:
                    try:
                        img = self.__driver.find_element(By.CLASS_NAME, "gir_mmimg")
                        src = img.get_attribute("src").split("?")[0]
                        self.__logger.info(f'[{task_id}] Found 1 image!')
                        
                        if filename := self.__save_image(src, task_id):
                            saved_images.append(filename)
                        return saved_images
                    
                    except NoSuchElementException:
                        raise Exception(f'[{task_id}] Unable to find images!')
        
        except Exception as e:
            error = f"[{task_id}] {e}"
            self.__logger.error(error)
            raise RuntimeError(error)

    def __v2(self, prompt, task_id) -> list:
        try:
            self.__driver.get(self.__se)
            self.__driver.refresh()
            
            self.__driver.find_element(By.ID, "sb_form_q").send_keys(prompt)
            self.__driver.find_element(By.ID, "create_btn_c").click()
            
            try:
                WebDriverWait(self.__driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "gil_err_tc")))
                raise Exception(f'[{task_id}] Request blocked (likely explicit content)')
            
            except TimeoutException:
                pass

            while True:
                self.__logger.info(f"[{task_id}] Refreshing request!")
                self.__driver.refresh()

                try:
                    grid = WebDriverWait(self.__driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.girrgrid.light.seled"))
                    )
                    
                    saved_images = []
                    try:
                        images = grid.find_elements(By.CLASS_NAME, "_4-images")
                        
                        if images:
                            urls = [img.get_attribute("src").split("?")[0] for img in images]
                            self.__logger.info(f'[{task_id}] Found {len(urls)} images!')
                        
                        else:
                            img = grid.find_element(By.CLASS_NAME, "_1-images")
                            urls = [img.get_attribute("src").split("?")[0]]
                            self.__logger.info(f'[{task_id}] Found 1 image!')
                        
                        for idx, url in enumerate(urls, 1):
                            if filename := self.__save_image(url, task_id, idx):
                                saved_images.append(filename)
                        
                        return saved_images
                    
                    except NoSuchElementException:
                        raise Exception(f'[{task_id}] Unable to find images!')
                        
                except TimeoutException:
                    raise Exception(f'[{task_id}] Unable to find target element in time!')
        
        except Exception as e:
            error = f"[{task_id}] {e}"
            self.__logger.error(error)
            raise RuntimeError(error)
        
    def generate_image(self, prompt):
        try:
            self.__driver.get(self.__se)
            self.__driver.refresh()
            
            try:
                task_id = self.__get_task_id()
                self.__driver.find_element(By.CLASS_NAME, "gih_pink")
                self.__logger.info(f"[{task_id}] Processing request in legacy mode!")
                return self.__v1(prompt, task_id)
            
            except NoSuchElementException:
                self.__logger.info(f"[{task_id}] Processing request in new mode!")
                return self.__v2(prompt, task_id)
        
        except Exception as e:
            error = f"[{task_id}] Error in generate_image: {e}"
            self.__logger.error(error)
            raise RuntimeError(error)