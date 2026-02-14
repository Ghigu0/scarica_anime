import os
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from tkinter import ttk

DOWNLOAD_PATH_FILE = "download_path.txt"

# =====================================================
# UTILS (Standard)
# =====================================================

def get_download_path():
    if os.path.exists(DOWNLOAD_PATH_FILE):
        with open(DOWNLOAD_PATH_FILE, "r", encoding="utf-8") as f:
            path = f.read().strip()
            if path: return path
    return None

def chiudi_tutte_tranne_la_prima(driver, stop_flag):
    try:
        for handle in driver.window_handles[1:]:
            driver.switch_to.window(handle)
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
    except: pass

def numero_download():
    download_dir = get_download_path()
    if not download_dir: return False
    num = 0
    try:
        files = os.listdir(download_dir)
        for file in files:
            if file.endswith("crdownload"): num += 1
    except: pass
    return num >= 2

def elimina_crd(): 
    download_dir = get_download_path()
    if not download_dir: return
    try:
        for file in os.listdir(download_dir):
            if file.endswith(".crdownload"):
                try: os.remove(os.path.join(download_dir, file))
                except: pass
    except: pass

def wait_for_last_downloads():
    download_dir = get_download_path()
    while True:
        try:
            if any(file.endswith(".crdownload") for file in os.listdir(download_dir)):
                time.sleep(2)
            else: break
        except: break

# =====================================================
# FUNZIONE SCARICA SINGOLO (Standard)
# =====================================================

def scarica_episodio(driver, url, stop_flag):
    print(f"\nProcessing URL: {url}")
    if driver.current_url != url:
        driver.get(url)

    actions = ActionChains(driver)
    actions.move_by_offset(10, 10).click().perform() 

    if stop_flag(): return

    while (len(driver.window_handles) > 1): 
        chiudi_tutte_tranne_la_prima(driver, stop_flag)
        actions.move_by_offset(10, 10).click().perform()
        time.sleep(1)
    
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "embed"))
        )
        iframe_src = iframe.get_attribute("src")
        
        if stop_flag(): return

        response = requests.get(iframe_src)
        match = re.search(r"window\.downloadUrl\s*=\s*'(https?://[^\s]+)'", response.text)
        
        if match:
            final_url = match.group(1)
            print(f"✅ Avvio download...")
            driver.get(final_url)
            time.sleep(6) 
        else:
            print("❌ Link downloadUrl non trovato.")

    except Exception as e:
        print(f"Errore download episodio: {e}")

# =====================================================
# LOGICA PARTIAL (Range specifico)
# =====================================================

def run_partial_logic(app, main_link, start_ep, end_ep, stop_flag):
    
    download_path = get_download_path()
    if not download_path:
        print("Manca path download")
        return

    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    download_path = os.path.abspath(download_path).replace("/", "\\")
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)

    try:
        elimina_crd()

        print("Caricamento pagina serie...")
        driver.get(main_link)

        # 1. Recupera lista episodi per capire quanti ce ne sono
        try:
            wait = WebDriverWait(driver, 15)
            # Recupera tutti gli episodi
            all_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".d-inline-block.text-center")))
            total_available = len(all_elements)
            print(f"Totale episodi disponibili nel sito: {total_available}")
        except Exception as e:
            print(f"Impossibile trovare lista episodi: {e}")
            return

        # 2. Validazione Indici
        # Se l'utente chiede episodio 100 ma ce ne sono 12, fermiamo tutto.
        if start_ep < 1: start_ep = 1
        if end_ep > total_available: 
            print(f"Attenzione: Richiesto ep {end_ep}, ma disponibili solo {total_available}. Adatto il range.")
            end_ep = total_available

        # Calcolo indici Python (0-based)
        # Esempio: Start=1 -> Index=0. End=2 -> Index=1.
        start_index = start_ep - 1
        end_index = end_ep - 1 

        current_progress = 0

        # 3. CICLO SUL RANGE
        # range(a, b+1) perché range è esclusivo sull'ultimo numero
        for i in range(start_index, end_index + 1):
            if stop_flag(): break
            
            # Numero "umano" dell'episodio
            ep_num = i + 1
            print(f"\n--- Gestione episodio {ep_num} (Target: {start_ep}-{end_ep}) ---")

            # Reset pagina
            driver.get(main_link)
            
            # Click preventivo
            try:
                actions = ActionChains(driver)
                actions.move_by_offset(10, 10).click().perform()
                if len(driver.window_handles) > 1:
                    chiudi_tutte_tranne_la_prima(driver, stop_flag)
            except: pass

            # Ritrovo lista e clicco l'episodio specifico (indice i)
            try:
                wait = WebDriverWait(driver, 15)
                elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".d-inline-block.text-center")))
                
                target_ep_elem = elements[i]
                target_ep_elem.click()
                print(f"Click su episodio {ep_num} effettuato.")
                
                time.sleep(3)
                scarica_episodio(driver, driver.current_url, stop_flag)

            except Exception as e:
                print(f"Errore su episodio {ep_num}: {e}")
                continue

            # Aggiorna UI
            current_progress += 1
            app.after(0, lambda v=current_progress: app.progress_partial.config(value=v))

            # Controllo download paralleli
            while numero_download():
                if stop_flag(): break
                time.sleep(5)
        
        if not stop_flag():
            wait_for_last_downloads()

    finally:
        driver.quit()
        app.after(0, lambda: cleanup_ui(app, stop_flag))

def cleanup_ui(app, stop_flag):
    if hasattr(app, "progress_partial"): app.progress_partial.destroy()
    if hasattr(app, "stop_partial_button"): app.stop_partial_button.destroy()
    
    # Riabilita Inputs
    app.partial_link_entry.config(state="normal")
    app.start_ep_entry.config(state="normal")
    app.end_ep_entry.config(state="normal")
    
    # Riabilita Pulsanti Main
    app.latest_button.config(state="normal")
    app.full_button.config(state="normal")
    app.partial_button.config(state="normal")
    app.start_partial_button.config(state="normal")
    
    if not stop_flag():
        app.completed_partial_label = ttk.Label(
            app.partial_frame, 
            text="download completato!", 
            foreground="green", 
            font=("Arial", 12, "bold")
        )
        app.completed_partial_label.pack(pady=5)