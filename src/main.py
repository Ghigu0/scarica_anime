import tkinter as tk
from tkinter import ttk, filedialog
import os
import latest_episodes
import full_episodes

DOWNLOAD_PATH_FILE = "download_path.txt"


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Scarica i tuoi anime!")
        self.geometry("800x900")
        self.configure(bg="#05425d")

        # Frame principale stabile
        self.main_frame = ttk.Frame(self, padding=40)
        self.main_frame.pack(fill="both", expand=True)

        # Titolo
        self.title_label = ttk.Label(
            self.main_frame,
            text="Cosa vuoi scaricare?",
            font=("Arial", 16)
        )
        self.title_label.pack(pady=20)

        # Pulsante selezione cartella
        self.path_button = ttk.Button(
            self.main_frame,
            text="Seleziona cartella download",
            command=self.select_download_folder
        )
        self.path_button.pack(pady=10)

        # Label percorso attuale
        self.path_label = ttk.Label(
            self.main_frame,
            text="Nessuna cartella selezionata",
            foreground="red"
        )
        self.path_label.pack(pady=5)

        # Pulsante Ultimi Episodi
        self.latest_button = ttk.Button(
            self.main_frame,
            text="Ultimi Episodi",
            command=self.run_latest,
            state="disabled"
        )
        self.latest_button.pack(pady=10, ipadx=20, ipady=10)

        # Pulsante Tutti gli Episodi
        self.full_button = ttk.Button(
            self.main_frame,
            text="Tutti gli Episodi",
            command=self.run_full,
            state="disabled"
        )
        self.full_button.pack(pady=10, ipadx=20, ipady=10)

        # Controllo se esiste già un percorso salvato
        self.load_saved_download_path()

    # =====================================================
    # GESTIONE CARTELLA DOWNLOAD
    # =====================================================

    def select_download_folder(self):

        folder = filedialog.askdirectory()

        if folder:
            with open(DOWNLOAD_PATH_FILE, "w", encoding="utf-8") as f:
                f.write(folder)

            self.path_label.config(
                text=f"Cartella: {folder}",
                foreground="green"
            )

            # abilita bottoni
            self.latest_button.config(state="normal")
            self.full_button.config(state="normal")

    def load_saved_download_path(self):

        if os.path.exists(DOWNLOAD_PATH_FILE):
            with open(DOWNLOAD_PATH_FILE, "r", encoding="utf-8") as f:
                folder = f.read().strip()

            if folder and os.path.exists(folder):
                self.path_label.config(
                    text=f"Cartella: {folder}",
                    foreground="green"
                )

                self.latest_button.config(state="normal")
                self.full_button.config(state="normal")
            else:
                self.path_label.config(
                    text="Cartella salvata non valida",
                    foreground="red"
                )

    # =====================================================
    # NAVIGAZIONE
    # =====================================================

    def run_latest(self):
        latest_episodes.open_ui(self)

    def run_full(self):
        full_episodes.open_ui(self)

    def show_home(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.__init__()  # ricrea interfaccia pulita


# =====================================================
# AVVIO PROGRAMMA
# =====================================================

if __name__ == "__main__":
    app = App()
    app.mainloop()
