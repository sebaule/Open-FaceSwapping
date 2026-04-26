import sys
import os

# Ajoute le dossier du script au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from app import Application

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()