import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager

# --- IMPORT CONFIGURATION ---
try:
    import config
except ImportError:
    print("Error: config.py not found. Please copy config_sample.py to config.py and set your password.")
    sys.exit(1)

ROUTER_IP = config.ROUTER_IP
USERNAME = config.USERNAME
PASSWORD = config.PASSWORD
REBOOT_PAGE_URL = f"http://{ROUTER_IP}/cgi-bin/device-management-resets.cgi"

# File to store the date of the last reboot
HISTORY_FILE = os.path.expanduser("~/.router_last_run")

def should_run_today():
    """Checks if the script has already run today."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            last_run = f.read().strip()
        
        if last_run == today:
            print(f"Skipping: Router already rebooted today ({today}).")
            return False
            
    return True

def mark_as_run():
    """Updates the history file with today's date."""
    today = datetime.now().strftime("%Y-%m-%d")
    with open(HISTORY_FILE, 'w') as f:
        f.write(today)

def force_click(driver, element):
    driver.execute_script("arguments[0].click();", element)

def find_element_anywhere(driver, xpath):
    """
    Scans the main page and EVERY frame for an element.
    Returns the element if found, or None.
    """
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
    if not should_run_today():
        sys.exit(0)

    print("System just started. Waiting 60s for Wi-Fi to stabilize...")
    time.sleep(60)

    print("Initializing invisible browser...")
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless") 
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    try:
        # 3. LOGIN
        print(f"Loading http://{ROUTER_IP}...")
        driver.get(f"http://{ROUTER_IP}")
        time.sleep(5) 

        print("Logging in...")
        
        # We use the helper to find the fields inside frames
        user_field = find_element_anywhere(driver, "//input[@type='text']")
        if user_field:
            user_field.clear()
            user_field.send_keys(USERNAME)

        # Note: We use the helper for the password too, just to be safe
        pass_field = find_element_anywhere(driver, "//input[@type='password']")
        if pass_field:
            pass_field.clear()
            pass_field.send_keys(PASSWORD)
        else:
             raise Exception("Password field not found in any frame!")
        
        # Click Entrar
        login_btn = find_element_anywhere(driver, "//*[contains(text(), 'ENTRAR')] | //input[@value='ENTRAR']")
        if login_btn:
            force_click(driver, login_btn)
        else:
             raise Exception("Login button not found!")
        
        print("   Login clicked. Waiting for session...")
        time.sleep(10) 

        # INJECT REBOOT COMMAND
        print(f"Jumping to Control Panel: {REBOOT_PAGE_URL}")
        driver.get(REBOOT_PAGE_URL)
        time.sleep(5)

        print("   Injecting Reboot Command...")
        reboot_script = """
        var data = { restoreFlag: 1, RestartBtn: "RESTART" };
        $.post('/cgi-bin/device-management-resets.cgi', data, function(){});
        """
        driver.execute_script(reboot_script)
        
        print("SUCCESS: Router is restarting.")
        
        # UPDATE HISTORY FILE
        mark_as_run()
        
        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")
        # We do NOT mark as run if it failed, so it tries again next login
    finally:
        driver.quit()

if __name__ == "__main__":
    reboot_router()