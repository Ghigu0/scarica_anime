import tkinter as tk
from tkinter import ttk
import threading
from utils import download_partials

stop_requested = False

def request_stop(app):
    global stop_requested
    stop_requested = True

def close_ui(app):
    """Funzione di utility per nascondere questo frame da main.py"""
    if hasattr(app, "partial_frame") and app.partial_frame.winfo_exists():
        app.partial_frame.pack_forget()

def open_ui(app):
    # Nascondi altri frame
    if hasattr(app, "latest_frame") and app.latest_frame.winfo_exists():
        app.latest_frame.pack_forget()
    if hasattr(app, "full_frame") and app.full_frame.winfo_exists():
        app.full_frame.pack_forget()

    # Mostra frame partial se esiste già
    if hasattr(app, "partial_frame") and app.partial_frame.winfo_exists():
        app.partial_frame.pack(fill="both", expand=True, pady=20)
        return

    # Crea il frame
    app.partial_frame = ttk.Frame(app.main_frame, padding=20)
    app.partial_frame.pack(fill="both", expand=True, pady=20)

    # TITOLO (Grassetto)
    ttk.Label(
        app.partial_frame, 
        text="Anime da scaricare:", 
        font=("Arial", 12, "bold")
    ).pack(pady=5)
    
    # --- ISTRUZIONI SOPRA ---
    ttk.Label(
        app.partial_frame,
        text="Inserisci nella casella sottostante il link dal sito di animeunity dell'anime da scaricare.\nNota bene: non è importante su quale episodio sia selezionato il link.",
        font=("Arial", 10),
        foreground="#333333",  # Colore grigio scuro
        justify="center"       # Centra il testo
    ).pack(pady=(0, 10))       # Spazio sotto
    # ------------------------------    

    # Casella di testo Link
    app.partial_link_entry = ttk.Entry(app.partial_frame, width=70)
    app.partial_link_entry.pack(pady=5)

    # AREA RANGE EPISODI
    range_frame = ttk.Frame(app.partial_frame)
    range_frame.pack(pady=10)

    ttk.Label(range_frame, text="Dal n°:").pack(side="left", padx=5)
    app.start_ep_entry = ttk.Entry(range_frame, width=5)
    app.start_ep_entry.pack(side="left", padx=5)

    ttk.Label(range_frame, text="Al n°:").pack(side="left", padx=5)
    app.end_ep_entry = ttk.Entry(range_frame, width=5)
    app.end_ep_entry.pack(side="left", padx=5)

    # PULSANTE AVVIA
    app.start_partial_button = ttk.Button(
        app.partial_frame,
        text="Avvia Download",
        command=lambda: start_program(app),
    )
    app.start_partial_button.pack(pady=10, ipadx=10, ipady=5)

    # --- ISTRUZIONI SOTTO ---
    ttk.Label(
        app.partial_frame,
        text="Una volta avviato il download, aspetta che la barra di completamento sia piena.\nNota bene: comparirà la scritta 'Range scaricato!'",
        font=("Arial", 9, "italic"),
        foreground="#555555",
        justify="center"
    ).pack(pady=(0, 10))
    # ------------------------------


def start_program(app):
    global stop_requested
    stop_requested = False

    link = app.partial_link_entry.get().strip()
    start_ep_str = app.start_ep_entry.get().strip()
    end_ep_str = app.end_ep_entry.get().strip()

    # Validazione base
    if not link:
        print("Link mancante.")
        return
    if not start_ep_str.isdigit() or not end_ep_str.isdigit():
        print("Inserisci numeri validi per gli episodi.")
        return

    start_ep = int(start_ep_str)
    end_ep = int(end_ep_str)

    if start_ep > end_ep:
        print("L'episodio iniziale deve essere minore o uguale a quello finale.")
        return

    # Disabilita UI
    app.partial_link_entry.config(state="disabled")
    app.start_ep_entry.config(state="disabled")
    app.end_ep_entry.config(state="disabled")
    
    # Disabilita bottoni navigazione main
    app.latest_button.config(state="disabled")
    app.full_button.config(state="disabled")
    if hasattr(app, "partial_button"):
        app.partial_button.config(state="disabled")
        
    app.start_partial_button.config(state="disabled")

    # Rimuovi label completato precedente
    if hasattr(app, "completed_partial_label"):
        app.completed_partial_label.destroy()

    # Barra progresso
    total_to_download = end_ep - start_ep + 1
    app.progress_partial = ttk.Progressbar(app.partial_frame, mode="determinate", maximum=total_to_download, value=0)
    app.progress_partial.pack(fill="x", pady=5)

    # Pulsante Stop
    app.stop_partial_button = ttk.Button(
        app.partial_frame,
        text="Interrompi",
        command=lambda: request_stop(app)
    )
    app.stop_partial_button.pack(pady=5)

    # Thread
    threading.Thread(
        target=download_partials.run_partial_logic,
        args=(app, link, start_ep, end_ep, lambda: stop_requested),
        daemon=True
    ).start()