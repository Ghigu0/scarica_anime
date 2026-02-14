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
from selenium.common.exceptions import ElementClickInterceptedException
from tkinter import ttk

DOWNLOAD_PATH_FILE = "download_path.txt"

# =====================================================
# UTILS (Identiche a download_latest)
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
# FUNZIONE SCARICA (Copia esatta di download_latest)
# =====================================================

def scarica_episodio(driver, url, stop_flag):
    print(f"\nProcessing URL: {url}")
    
    # Se l'URL non è quello corrente (può capitare), vacci
    if driver.current_url != url:
        driver.get(url)

    # --- POPUP HANDLING ---
    actions = ActionChains(driver)
    actions.move_by_offset(10, 10).click().perform() 

    if stop_flag(): return

    while (len(driver.window_handles) > 1): 
        chiudi_tutte_tranne_la_prima(driver, stop_flag)
        actions.move_by_offset(10, 10).click().perform()
        time.sleep(1)
    
    # --- IFRAME ---
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "embed"))
        )
        iframe_src = iframe.get_attribute("src")
        print(f"🎯 Iframe: {iframe_src}")

        if stop_flag(): return

        response = requests.get(iframe_src)
        match = re.search(r"window\.downloadUrl\s*=\s*'(https?://[^\s]+)'", response.text)
        
        if match:
            final_url = match.group(1)
            print(f"✅ Link trovato. Download...")
            driver.get(final_url)
            time.sleep(6) # Pausa critica
        else:
            print("❌ Link downloadUrl non trovato.")

    except Exception as e:
        print(f"Errore download episodio: {e}")

# =====================================================
# LOGICA FULL (Ciclo sugli episodi)
# =====================================================

def run_full_logic(app, main_link, stop_flag):
    
    download_path = get_download_path()
    if not download_path:
        print("Manca path download")
        return

    # Setup Driver
    options = Options()
    options.add_argument("--headless") # Togli commento se vuoi nascosto
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Normalizzazione path
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

        # 1. CONTIAMO GLI EPISODI
        try:
            wait = WebDriverWait(driver, 15)
            # Usiamo lo stesso selettore di latest_episodes
            elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".d-inline-block.text-center")))
            total_episodes = len(elements)
            print(f"Totale episodi trovati: {total_episodes}")
        except Exception as e:
            print(f"Impossibile trovare la lista episodi: {e}")
            return

        # Impostiamo la barra di progresso ora che sappiamo il numero
        if total_episodes > 0:
            app.after(0, lambda: app.progress_full.config(maximum=total_episodes, value=0))
        
        # 2. CICLO SUGLI EPISODI
        for i in range(total_episodes):
            if stop_flag(): break
            
            print(f"\n--- Gestione episodio {i+1} di {total_episodes} ---")

            # A. Torniamo alla pagina principale per resettare il DOM
            # (Se siamo già lì, non ricarica, ma meglio essere sicuri)
            driver.get(main_link)
            
            # B. Gestione click "preventivo" sulla home (per eventuali popup sulla home)
            try:
                actions = ActionChains(driver)
                actions.move_by_offset(10, 10).click().perform()
                if len(driver.window_handles) > 1:
                    chiudi_tutte_tranne_la_prima(driver, stop_flag)
            except: pass

            # C. Ritroviamo la lista (il DOM è cambiato dopo il refresh)
            try:
                wait = WebDriverWait(driver, 15)
                elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".d-inline-block.text-center")))
                
                # D. Clicchiamo l'episodio numero i
                target_ep = elements[i]
                target_ep.click()
                print("Click episodio effettuato.")
                
                # Piccola pausa per caricamento pagina episodio
                time.sleep(3)

                # E. Ora siamo sulla pagina dell'episodio -> SCARICA
                # Passiamo l'URL corrente a scarica_episodio
                scarica_episodio(driver, driver.current_url, stop_flag)

            except Exception as e:
                print(f"Errore nel ciclo episodio {i+1}: {e}")
                continue

            # Aggiorna UI
            app.after(0, lambda v=i+1: app.progress_full.config(value=v))

            # F. Controllo download paralleli
            while numero_download():
                if stop_flag(): break
                time.sleep(5)
        
        if not stop_flag():
            wait_for_last_downloads()

    finally:
        driver.quit()
        app.after(0, lambda: cleanup_ui(app, stop_flag))

def cleanup_ui(app, stop_flag):
    if hasattr(app, "progress_full"): app.progress_full.destroy()
    if hasattr(app, "stop_full_button"): app.stop_full_button.destroy()
    
    app.full_entry.config(state="normal")
    app.latest_button.config(state="normal")
    app.start_full_button.config(state="normal")
    
    if not stop_flag():
        app.completed_full_label = ttk.Label(
            app.full_frame, 
            text="Serie completata!", 
            foreground="green", 
            font=("Arial", 12, "bold")
        )
        app.completed_full_label.pack(pady=5)