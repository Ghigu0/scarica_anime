import tkinter as tk
from tkinter import ttk
import threading
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import requests
from bs4 import BeautifulSoup
import sys  
import time
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchWindowException
from selenium.webdriver.common.action_chains import ActionChains
import re
from tkinter import messagebox
from tkinter import filedialog



DOWNLOAD_PATH_FILE = "download_path.txt"


SAVE_FILE = "saved_links.txt"
stop_requested = False



# =====================================================
# file del downlaod 
# =====================================================

def get_download_path():
    if os.path.exists(DOWNLOAD_PATH_FILE):
        with open(DOWNLOAD_PATH_FILE, "r", encoding="utf-8") as f:
            path = f.read().strip()
            if path:
                return path
    return None



# =====================================================
# INTERFACCIA GRAFICA
# =====================================================

def open_ui(app):

    # Se esiste il pannello full, nascondilo
    if hasattr(app, "full_frame") and app.full_frame.winfo_exists():
        app.full_frame.pack_forget()

    # Se esiste già latest, mostralo
    if hasattr(app, "latest_frame") and app.latest_frame.winfo_exists():
        app.latest_frame.pack(fill="both", expand=True, pady=20)
        return

     # ===== CREA SEMPRE IL FRAME QUI =====
    app.latest_frame = ttk.Frame(app.main_frame, padding=20)
    app.latest_frame.pack(fill="both", expand=True, pady=20)

    # Carica cartella se già salvata
   



    # Creazione pannello
    app.latest_frame = ttk.Frame(app.main_frame, padding=20)
    app.latest_frame.pack(fill="both", expand=True, pady=20)

    titolo = ttk.Label(
        app.latest_frame,
        text="Inserisci i link (uno per riga)",
        font=("Arial", 12)
    )
    titolo.pack(pady=5)

    app.latest_text = tk.Text(app.latest_frame, height=8)
    app.latest_text.pack(fill="both", expand=True, pady=5)

    # =====================================================
    # CARICAMENTO LINK SALVATI O ESEMPI
    # =====================================================

    DEFAULT_EXAMPLE = (
        "https://esempio-sito.com/anime1\n"
        "https://esempio-sito.com/anime2"
    )

    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            contenuto = f.read().strip()

        if contenuto:
            app.latest_text.insert("1.0", contenuto)
        else:
            app.latest_text.insert("1.0", DEFAULT_EXAMPLE)
    else:
        app.latest_text.insert("1.0", DEFAULT_EXAMPLE)

    # Pulsante Avvia
    app.start_button = ttk.Button(
    app.latest_frame,
    text="Avvia",
    command=lambda: start_program(app),
    )

    app.start_button.pack(pady=5, ipadx=10, ipady=5)

  





def request_stop(app):
    global stop_requested
    stop_requested = True

# =====================================================
# AVVIO THREAD
# =====================================================
def start_program(app):

    global stop_requested
    stop_requested = False

    app.latest_text.config(state="disabled", background="#dddddd")
    app.full_button.config(state="disabled")


    # Se esiste la scritta completato, rimuovila
    if hasattr(app, "completed_label"):
        app.completed_label.destroy()

    links = app.latest_text.get("1.0", tk.END).strip().splitlines()

    if not links:
        print("Nessun link inserito.")
        return

    app.start_button.config(state="disabled")

    # Crea barra progresso
    app.progress = ttk.Progressbar(app.latest_frame, mode="determinate")
    app.progress.pack(fill="x", pady=5)

    app.progress["maximum"] = len(links)
    app.progress["value"] = 0

    # Pulsante interrompi
    app.stop_button = ttk.Button(
        app.latest_frame,
        text="Interrompi",
        command=lambda: request_stop(app)
    )
    app.stop_button.pack(pady=5)

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(links))

    threading.Thread(
        target=run_logic,
        args=(app, links),
        daemon=True
    ).start()




# =====================================================
# funzioni di supporto per la run_logic
# =====================================================

def chiudi_tutte_tranne_la_prima(driver):

    for handle in driver.window_handles[1:]:  # Salta la prima scheda (indice 0)
        driver.switch_to.window(handle)
        driver.close()
    
    # Torna alla scheda principale (indice 0)
    driver.switch_to.window(driver.window_handles[0])

def get_anime(driver, url):
    print("ciao")
    driver.get(url) #mi posiziono sull'ulr
    print(f"\nci siamo posizionati sul'ulr {url}")
    
    print(f"\n\n se tutto va bene dovremmo avere 1 scheda, numero di schede aperte: {len(driver.window_handles)}") 
    if stop_requested:
        return
    
    while True: 
        try: 
            wait = WebDriverWait(driver,10)
            lista_episodi = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".d-inline-block.text-center")))

            ultimo_episodio = lista_episodi[-1]
            ultimo_episodio.click()
            print(f"\n\n\nse tutto è andato bene, siamo all'url {driver.current_url}")
            
            print(f"\n\n Sono sospettoso, numero di schede aperte: {len(driver.window_handles)}") 
            current_tab_index = driver.window_handles.index(driver.current_window_handle)
            print(f"Scheda corrente: {current_tab_index}")  
            
            break
        
        except ElementClickInterceptedException :  #ovvero è presente un pop-up
            print("\n\npop-up intercettato")
            
            print(f"\n\n se tutto va bene dovremmo avere 1 scheda, numero di schede aperte: {len(driver.window_handles)}") 
            # e infatti è cosi
            current_tab_index = driver.window_handles.index(driver.current_window_handle)
            print(f"Scheda corrente: {current_tab_index}")  
            actions = ActionChains(driver)
            actions.move_by_offset(10, 10).click().perform()  # Clicca 10px a destra e 10px in basso

            print(f"\n\nsecondo me siamo a un url di pubblicità:  {driver.current_url}")
            print(f"\n\n Sono sospettoso ( dopo il click ), numero di schede aperte: {len(driver.window_handles)}") 
            if (len(driver.window_handles) > 1) : 
                chiudi_tutte_tranne_la_prima(driver)
            print(f"\n\n Dopo la funzione che chiude , numero di schede aperte: {len(driver.window_handles)}") 
                
            current_tab_index = driver.window_handles.index(driver.current_window_handle)
            print(f"Scheda corrente: {current_tab_index}")  
            print(f"con url = {driver.current_url}")
            time.sleep(10)

            #dal momento in cui andava sospettavo rimanesse sulla scheda corrente, ma è strano

def scarica_episodio(driver, url):
    print(f"\nURL da stampare:\n{url}")
    

    ########################################################################################################################
    actions = ActionChains(driver)
    actions.move_by_offset(10, 10).click().perform()  # Clicca 10px a destra e 10px in basso

    # eseguo un click per il pop up
    if stop_requested:
        return
    
    while (len(driver.window_handles) > 1) : #se mi ha aperto una scheda, entro in un ciclo e chiudo tutto fino a che non eseguo click senza pop up 
        if (len(driver.window_handles) > 1) : 
            chiudi_tutte_tranne_la_prima(driver)
            print(f"\n\n Dopo la funzione che chiude , numero di schede aperte: {len(driver.window_handles)}")
        actions.move_by_offset(10, 10).click().perform()
        time.sleep(1)
    
    ###NON LO DICI NEL FOGLIO SCRITTO TE LO DICO QUA
    #       Mi sono accorto che si posizionava sull'ulr dell'ultimo episodio 
    #       Ma scaricava SEMPRE il PRIMO episodio. Mi è venuto in mente che l'ulr del primo episodio fosse in qualche modo 
    #       staticamente presente nella pagina html di default per quell'anime
    #       Allora clicllo sullo schermo per attivare il codice javbascript che inietta l'ulr dell'episodio corrente
    #       eseguo i click necessari stando attento ai pop up
    #       mi stringo la mano non so come mi sia venuta l'idea. Bravo io 
    #       attenzione ha risolto l'errore solo in modo parziale non so perchè
    ########################################################################################################################
    if stop_requested:
        return
    
    iframe = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "embed")))

    # Prendi l'attributo src dell'iframe
    iframe_src = iframe.get_attribute("src")

    print(f"🎯 URL dell'iframe: {iframe_src}")


    if stop_requested:
        return
    response = requests.get(iframe_src, stream=True)  # Abilita il download in streaming
    if response.status_code == 200:
        with open("episodio.txt", "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):  # Scarica 1 KB alla volta
                if chunk:
                    file.write(chunk)
        print(f"✅ Download completato:")
    else:
        print(f"❌ Errore nel download. Codice di stato: {response.status_code}")

    print("ora inizio il download")
    # Percorso del file di testo
    file_path = 'episodio.txt'

    if stop_requested:
        return
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()


        # Usa una regular expression per trovare l'URL che segue 'window.downloadUrl ='
        match = re.search(r"window\.downloadUrl\s*=\s*'(https?://[^\s]+)'", content)
    file.close()
    if match:
              # Restituisce l'URL trovato
        print("trovato")
        driver.get(match.group(1))
        try:
            os.remove(file_path)  # Elimina il file
            print(f"File eliminato: {file}")
        except Exception as e:
            print(f"Errore nell'eliminare {file}: {e}")
            #elimina il file episodio.txt
        time.sleep(3) #3 secondi per far partire il download
    else:
        print("non trovato")

   

def numero_download():
    download_dir = get_download_path()
    if not download_dir:
        return False

    num = 0
    files = os.listdir(download_dir)
    for file in files:
        if file.endswith("load"):  # Verifica se un file sta ancora scaricando
            num = num + 1

    print(f"\n NUMERO DOWNLOAD = {num}")
    if num == 2 :
        return True
    else : 
        return False

def elimina_crd() : 
    download_dir = get_download_path()
    if not download_dir:
        return False

    
    # Elenco di tutti i file nella cartella di download
    files = os.listdir(download_dir)
    
    # Ciclo attraverso tutti i file
    for file in files:
        # Controlla se il file ha l'estensione .crdownload
        if file.endswith(".crdownload"):
            file_path = os.path.join(download_dir, file)  # Costruisci il percorso completo del file
            try:
                os.remove(file_path)  # Elimina il file
                print(f"File eliminato: {file}")
            except Exception as e:
                print(f"Errore nell'eliminare {file}: {e}")

def wait_for_last_downloads():

    download_dir =get_download_path()
    while True:
        files = os.listdir(download_dir)
        if any(file.endswith(".crdownload") for file in files):
            time.sleep(2)
        else:
            break


def process_links(app, driver, links):

    global stop_requested

    for index, link in enumerate(links):

        if stop_requested:
            print("Interrotto dall'utente")
            break

        link = link.strip()
        if link:
            get_anime(driver, link)
            scarica_episodio(driver, driver.current_url)

            while numero_download():
                if stop_requested:
                    break
                time.sleep(5)

        # aggiorna barra progresso
        app.after(0, lambda v=index+1: app.progress.config(value=v))

    if not stop_requested:
        wait_for_last_downloads()



# =====================================================
# LOGICA PRINCIPALE
# =====================================================
def run_logic(app, links):

    download_path = get_download_path()

    if not download_path:
        print("Cartella download non impostata.")
        return

    global stop_requested

   

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

   

    download_path = get_download_path()

    if not download_path:
        print("Cartella download non impostata.")
        return

    # Normalizza percorso Windows
    download_path = os.path.abspath(download_path)
    download_path = download_path.replace("/", "\\")

    # Assicurati che esista
    os.makedirs(download_path, exist_ok=True)


    prefs = {
        "download.default_directory": os.path.normpath(download_path),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    options.add_experimental_option("prefs", prefs)


    driver = webdriver.Chrome(options=options)

    try:
        elimina_crd()
        process_links(app, driver, links)

    finally:
        driver.quit()

        # PULIZIA GUI (thread-safe)
        def cleanup():

            # Distruggi barra
            if hasattr(app, "progress"):
                app.progress.destroy()

            # Distruggi pulsante stop
            if hasattr(app, "stop_button"):
                app.stop_button.destroy()

            app.latest_text.config(state="normal", background="white")
            app.full_button.config(state="normal")


            # Mostra scritta completato SOLO se non interrotto
            if not stop_requested:
                app.completed_label = ttk.Label(
                    app.latest_frame,
                    text="Download completato",
                    foreground="green",
                    font=("Arial", 12, "bold")
                )
                app.completed_label.pack(pady=5)

            app.start_button.config(state="normal")


        app.after(0, cleanup)
