"""
Classe de base pour tous les écrans
"""

import tkinter as tk
from PIL import Image, ImageTk
import os


class EcranBase(tk.Frame):
    def __init__(self, parent, app):
        self.app = app
        self.cfg = app.config
        self.cfg_app = app.config["app"]
        super().__init__(parent, bg=self.cfg_app["couleur_fond"])
        self._images_refs = []  # Garder les références images pour éviter GC

    def afficher(self):
        """Appelé après que l'écran est packagé. Override dans les sous-classes."""
        pass

    def creer_titre(self, parent, texte, taille=None):
        """Crée un label titre stylé"""
        police = taille or self.cfg_app["police_titre"]
        label = tk.Label(
            parent,
            text=texte,
            font=police,
            fg=self.cfg_app["couleur_accent"],
            bg=self.cfg_app["couleur_fond"],
            wraplength=900,
            justify="center"
        )
        return label

    def creer_sous_titre(self, parent, texte):
        """Crée un label sous-titre"""
        label = tk.Label(
            parent,
            text=texte,
            font=self.cfg_app["police_texte"],
            fg=self.cfg_app["couleur_texte"],
            bg=self.cfg_app["couleur_fond"],
            wraplength=900,
            justify="center"
        )
        return label

    def creer_bouton(self, parent, texte, commande, couleur=None, largeur=30):
        """Crée un bouton stylé"""
        couleur = couleur or self.cfg_app["couleur_bouton"]
        btn = tk.Button(
            parent,
            text=texte,
            command=commande,
            font=self.cfg_app["police_bouton"],
            fg=self.cfg_app["couleur_bouton_texte"],
            bg=couleur,
            activebackground=couleur,
            activeforeground=self.cfg_app["couleur_bouton_texte"],
            relief="flat",
            cursor="hand2",
            width=largeur,
            pady=15,
            padx=20,
            bd=0
        )
        # Effet hover
        btn.bind("<Enter>", lambda e: btn.config(bg=self._eclaircir(couleur)))
        btn.bind("<Leave>", lambda e: btn.config(bg=couleur))
        return btn

    def _eclaircir(self, couleur_hex):
        """Éclaircit légèrement une couleur hex pour l'effet hover"""
        try:
            r = int(couleur_hex[1:3], 16)
            g = int(couleur_hex[3:5], 16)
            b = int(couleur_hex[5:7], 16)
            r = min(255, r + 30)
            g = min(255, g + 30)
            b = min(255, b + 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return couleur_hex

    def charger_image(self, chemin, largeur=None, hauteur=None):
        """Charge et retourne un ImageTk avec gestion d'erreur"""
        if not os.path.exists(chemin):
            return None
        try:
            img = Image.open(chemin)
            if largeur and hauteur:
                img = img.resize((largeur, hauteur), Image.LANCZOS)
            elif largeur:
                ratio = largeur / img.width
                img = img.resize((largeur, int(img.height * ratio)), Image.LANCZOS)
            elif hauteur:
                ratio = hauteur / img.height
                img = img.resize((int(img.width * ratio), hauteur), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self._images_refs.append(tk_img)
            return tk_img
        except Exception as e:
            print(f"Erreur chargement image {chemin}: {e}")
            return None

    def separateur(self, parent, couleur=None, hauteur=2):
        """Crée une ligne de séparation"""
        couleur = couleur or self.cfg_app["couleur_accent"]
        return tk.Frame(parent, bg=couleur, height=hauteur)
