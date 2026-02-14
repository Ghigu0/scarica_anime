import tkinter as tk
from tkinter import ttk
import threading
import os
from utils import download_latest  # Assicurati che il file si chiami download_latest.py

SAVE_FILE = "saved_links.txt"
stop_requested = False

def request_stop(app):
    global stop_requested
    stop_requested = True

# =====================================================
# INTERFACCIA GRAFICA
# =====================================================

def open_ui(app):
    # Nascondi gli altri frame
    if hasattr(app, "full_frame") and app.full_frame.winfo_exists():
        app.full_frame.pack_forget()
    
    if hasattr(app, "partial_frame") and app.partial_frame.winfo_exists():
        app.partial_frame.pack_forget()

    # Se esiste già latest, mostralo
    if hasattr(app, "latest_frame") and app.latest_frame.winfo_exists():
        app.latest_frame.pack(fill="both", expand=True, pady=20)
        return

    # Creazione pannello
    app.latest_frame = ttk.Frame(app.main_frame, padding=20)
    app.latest_frame.pack(fill="both", expand=True, pady=20)

    # TITOLO (Grassetto)
    ttk.Label(
        app.latest_frame,
        text="Inserisci i link (uno per riga):",
        font=("Arial", 12, "bold")
    ).pack(pady=5)

    # --- ISTRUZIONI SOPRA ---
    ttk.Label(
        app.latest_frame,
        text="Inserisci nella casella sottostante i link di animeunity degli anime da scaricare.\nNota bene: Il programma scaricherà l'ultimo episodio uscito per ogni link. \n i link verranno salvati e saranno presenti alla prossima apertura del programma",
        font=("Arial", 10),
        foreground="#333333",
        justify="center"
    ).pack(pady=(0, 10))
    # ------------------------------

    # Casella di testo
    app.latest_text = tk.Text(app.latest_frame, height=8)
    app.latest_text.pack(fill="both", expand=True, pady=5)

    # =====================================================
    # CARICAMENTO LINK SALVATI O ESEMPI
    # =====================================================
    DEFAULT_EXAMPLE = (
        "https://animeunity.to/anime/esempio-1\n"
        "https://animeunity.to/anime/esempio-2"
    )

    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                contenuto = f.read().strip()
            if contenuto:
                app.latest_text.insert("1.0", contenuto)
            else:
                app.latest_text.insert("1.0", DEFAULT_EXAMPLE)
        except:
            app.latest_text.insert("1.0", DEFAULT_EXAMPLE)
    else:
        app.latest_text.insert("1.0", DEFAULT_EXAMPLE)

    # Pulsante Avvia
    app.start_button = ttk.Button(
        app.latest_frame,
        text="Avvia Download",
        command=lambda: start_program(app),
    )
    app.start_button.pack(pady=5, ipadx=10, ipady=5)

    # --- ISTRUZIONI SOTTO ---
    ttk.Label(
        app.latest_frame,
        text="Una volta avviato il download, aspetta che la barra di completamento sia piena.\nNota bene: comparirà la scritta 'Ciclo completato!'",
        font=("Arial", 9, "italic"),
        foreground="#555555",
        justify="center"
    ).pack(pady=(10, 10))


# =====================================================
# AVVIO THREAD
# =====================================================
def start_program(app):
    global stop_requested
    stop_requested = False

    links = app.latest_text.get("1.0", tk.END).strip().splitlines()

    if not links:
        print("Nessun link inserito.")
        return

    # Disabilita UI
    app.latest_text.config(state="disabled", background="#dddddd")
    
    # Disabilita bottoni di navigazione
    app.latest_button.config(state="disabled")
    app.full_button.config(state="disabled")
    if hasattr(app, "partial_button"):
        app.partial_button.config(state="disabled")

    app.start_button.config(state="disabled")

    # Se esiste la scritta completato vecchia, rimuovila
    if hasattr(app, "completed_label"):
        app.completed_label.destroy()

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

    # Salva i link
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(links))

    # Avvia Thread
    threading.Thread(
        target=download_latest.run_logic,
        args=(app, links, lambda: stop_requested),
        daemon=True
    ).start()