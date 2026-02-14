import os
import sys
import re
import threading
from urllib.parse import urlsplit, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import tkinter as tk
from tkinter import ttk
import threading


def open_ui(app):

    # Se esiste latest, nascondilo
    if hasattr(app, "latest_frame") and app.latest_frame.winfo_exists():
        app.latest_frame.pack_forget()

    # Se esiste già full, mostralo
    if hasattr(app, "full_frame") and app.full_frame.winfo_exists():
        app.full_frame.pack(fill="both", expand=True, pady=20)
        return

    # Crealo
    app.full_frame = ttk.Frame(app.main_frame, padding=20)
    app.full_frame.pack(fill="both", expand=True, pady=20)

    titolo = ttk.Label(
        app.full_frame,
        text="Inserisci il link della serie",
        font=("Arial", 12)
    )
    titolo.pack(pady=5)

    app.full_entry = ttk.Entry(app.full_frame, width=60)
    app.full_entry.pack(pady=10)

    ttk.Button(
        app.full_frame,
        text="Avvia",
        command=lambda: start_program(app.full_entry.get()),
    ).pack(pady=5)

  


def start_program(link):
    print("Avvio full episodes con link:", link)
    # Qui metterai la logica
