import tkinter as tk
from tkinter import ttk
import threading
from utils import download_full 

# Variabile globale
stop_requested = False

def request_stop(app):
    global stop_requested
    stop_requested = True

def open_ui(app):
    # Gestione visibilità frame: Nascondiamo TUTTI gli altri frame
    if hasattr(app, "latest_frame") and app.latest_frame.winfo_exists():
        app.latest_frame.pack_forget()
    
    if hasattr(app, "partial_frame") and app.partial_frame.winfo_exists():
        app.partial_frame.pack_forget()

    # Se full_frame esiste già, mostralo e basta
    if hasattr(app, "full_frame") and app.full_frame.winfo_exists():
        app.full_frame.pack(fill="both", expand=True, pady=20)
        return

    # Creazione Frame
    app.full_frame = ttk.Frame(app.main_frame, padding=20)
    app.full_frame.pack(fill="both", expand=True, pady=20)

    # Titolo
    ttk.Label(
        app.full_frame, 
        text="Anime da scaricare:", 
        font=("Arial", 12, "bold")
    ).pack(pady=5)
    
    # --- ISTRUZIONI SOPRA ---
    ttk.Label(
        app.full_frame,  # <--- ERA partial_frame, CORRETTO IN full_frame
        text="Inserisci nella casella sottostante il link dal sito di animeunity dell'anime da scaricare.\nNota bene: non è importante su quale episodio sia selezionato il link.",
        font=("Arial", 10),
        foreground="#333333",
        justify="center"
    ).pack(pady=(0, 10))
    # ------------------------------    

    # Entry link
    app.full_entry = ttk.Entry(app.full_frame, width=70)
    app.full_entry.pack(pady=10)

    # Pulsante Avvia
    app.start_full_button = ttk.Button(
        app.full_frame,
        text="Avvia Download Serie",
        command=lambda: start_program(app),
    )
    app.start_full_button.pack(pady=5, ipadx=10, ipady=5)

    # --- ISTRUZIONI SOTTO ---
    ttk.Label(
        app.full_frame, # <--- ERA partial_frame, CORRETTO IN full_frame
        text="Una volta avviato il download, aspetta che la barra di completamento sia piena.\nNota bene: comparirà la scritta 'Serie completata!'",
        font=("Arial", 9, "italic"),
        foreground="#555555",
        justify="center"
    ).pack(pady=(10, 10))


def start_program(app):
    global stop_requested
    stop_requested = False

    link = app.full_entry.get().strip()
    if not link:
        print("Nessun link inserito.")
        return

    # Disabilita interfaccia
    app.full_entry.config(state="disabled")
    
    # Disabilita TUTTI i pulsanti di navigazione
    app.latest_button.config(state="disabled")
    app.full_button.config(state="disabled")
    if hasattr(app, "partial_button"):
        app.partial_button.config(state="disabled")
        
    app.start_full_button.config(state="disabled")

    # Rimuovi label "completato" vecchia
    if hasattr(app, "completed_full_label"):
        app.completed_full_label.destroy()

    # Crea barra progresso (inizia a 0)
    app.progress_full = ttk.Progressbar(app.full_frame, mode="determinate", value=0)
    app.progress_full.pack(fill="x", pady=5)

    # Pulsante Stop
    app.stop_full_button = ttk.Button(
        app.full_frame,
        text="Interrompi",
        command=lambda: request_stop(app)
    )
    app.stop_full_button.pack(pady=5)

    # Avvia logica in background
    threading.Thread(
        target=download_full.run_full_logic,
        args=(app, link, lambda: stop_requested),
        daemon=True
    ).start()