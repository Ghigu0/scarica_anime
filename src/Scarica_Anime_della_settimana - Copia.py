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

options = Options()
options.add_argument("--headless")  # Se vuoi eseguirlo in background
driver = webdriver.Chrome(options=options)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
stringhe = []

def chiudi_tutte_tranne_la_prima(driver):

    for handle in driver.window_handles[1:]:  # Salta la prima scheda (indice 0)
        driver.switch_to.window(handle)
        driver.close()
    
    # Torna alla scheda principale (indice 0)
    driver.switch_to.window(driver.window_handles[0])

def get_anime(url):
    print("ciao")
    driver.get(url) #mi posiziono sull'ulr
    print(f"\nci siamo posizionati sul'ulr {url}")
    
    print(f"\n\n se tutto va bene dovremmo avere 1 scheda, numero di schede aperte: {len(driver.window_handles)}") 
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

def scarica_episodio(url):
    print(f"\nURL da stampare:\n{url}")
    

    ########################################################################################################################
    actions = ActionChains(driver)
    actions.move_by_offset(10, 10).click().perform()  # Clicca 10px a destra e 10px in basso

    # eseguo un click per il pop up
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
    iframe = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "embed")))

    # Prendi l'attributo src dell'iframe
    iframe_src = iframe.get_attribute("src")

    print(f"🎯 URL dell'iframe: {iframe_src}")


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
    download_dir = "C:\\Users\\Ghigu\\Downloads"
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
    download_dir = "C:\\Users\\Ghigu\\Downloads"  # Percorso della cartella di download
    
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



def leggi_stringhe():
    for line in sys.stdin:
        line = line.strip()
        if line: 
            stringhe.append(line)
            get_anime(line) # get anime si mette sull'url e in particolare sull'ultimo episodio
            scarica_episodio(driver.current_url) #scarico episodio ( usando ora il modulo requests)
            print("\nCONTROLLO NUMERO DOWNLOAD")
            while (numero_download()):#voglio scaricare solo due episodi per volta
                time.sleep(5)


#elimini tutti i file di tipo CRDOWLOAD dalla cartella download 
elimina_crd()
leggi_stringhe()

