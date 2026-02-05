from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import time
import logging

# --- IMPORT CONFIGURATION ---
try:
    import config
except ImportError:
    print("Error: config.py not found. Please copy config_sample.py to config.py and set your password.")
    import sys
    sys.exit(1)

ROUTER_IP = config.ROUTER_IP
USERNAME = config.USERNAME
PASSWORD = config.PASSWORD

# We jump straight to the page where the reboot logic lives
REBOOT_PAGE_URL = f"http://{ROUTER_IP}/cgi-bin/device-management-resets.cgi"

logging.basicConfig(filename='/tmp/router_reboot.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def force_click(driver, element):
    driver.execute_script("arguments[0].click();", element)

def find_element_anywhere(driver, xpath):
    driver.switch_to.default_content()
    try:
        return driver.find_element(By.XPATH, xpath)
    except:
        pass
    frames = driver.find_elements(By.TAG_NAME, "frame") + driver.find_elements(By.TAG_NAME, "iframe")
    for frame in frames:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame)
            return driver.find_element(By.XPATH, xpath)
        except:
            continue
    return None

def reboot_router():
    print("Initializing invisible browser...")
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless") 
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    try:
        print(f"Loading http://{ROUTER_IP}...")
        driver.get(f"http://{ROUTER_IP}")
        time.sleep(5) 

        print("Logging in...")
        user_field = find_element_anywhere(driver, "//input[@type='text']")
        if user_field:
            user_field.clear()
            user_field.send_keys(USERNAME)

        pass_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        pass_field.clear()
        pass_field.send_keys(PASSWORD)
        
        login_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'ENTRAR')] | //input[@value='ENTRAR']")
        force_click(driver, login_btn)
        
        print("   Login clicked. Waiting for session...")
        time.sleep(10) 

        print(f"Jumping to Control Panel: {REBOOT_PAGE_URL}")
        driver.get(REBOOT_PAGE_URL)
        time.sleep(5)

        print("   Injecting Reboot Command...")
        
        reboot_script = """
        var data = {
            restoreFlag: 1,
            RestartBtn: "RESTART"
        };
        $.post('/cgi-bin/device-management-resets.cgi', data, function(){});
        """
        
        driver.execute_script(reboot_script)
        
        print("SUCCESS: JavaScript injection executed.")
        print("The router should be restarting now.")
        logging.info("Reboot injection sent.")
        
        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("debug_crash.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    reboot_router()