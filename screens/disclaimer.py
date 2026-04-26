"""
Écran 2 - Disclaimer / Consentement
"""

import tkinter as tk
from .base import EcranBase


class EcranDisclaimer(EcranBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.cfg_ecran = app.config["disclaimer"]
        self._construire_ui()

    def _construire_ui(self):
        # Conteneur principal centré verticalement
        conteneur = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        conteneur.place(relx=0.5, rely=0.5, anchor="center")

        # Titre
        self.creer_titre(conteneur, self.cfg_ecran["titre"]).pack(pady=30)

        # Séparateur
        self.separateur(conteneur).pack(fill="x", padx=50, pady=10)

        # Cadre texte avec bordure
        cadre_texte = tk.Frame(
            conteneur,
            bg="#1a1a2e",
            relief="flat",
            bd=0
        )
        cadre_texte.pack(padx=60, pady=20, fill="x")

        tk.Label(
            cadre_texte,
            text=self.cfg_ecran["texte"],
            font="Arial 18",
            fg=self.cfg_app["couleur_texte"],
            bg="#1a1a2e",
            wraplength=800,
            justify="left",
            pady=20,
            padx=30
        ).pack()

        # Checkbox de consentement (si activée)
        if self.cfg_ecran.get("checkbox_obligatoire", True):
            self.var_checkbox = tk.BooleanVar(value=False)
            cadre_check = tk.Frame(conteneur, bg=self.cfg_app["couleur_fond"])
            cadre_check.pack(pady=20)

            self.cb = tk.Checkbutton(
                cadre_check,
                text="  Je certifie avoir lu et j'accepte les conditions ci-dessus",
                variable=self.var_checkbox,
                font="Arial 18",
                fg=self.cfg_app["couleur_texte"],
                bg=self.cfg_app["couleur_fond"],
                activebackground=self.cfg_app["couleur_fond"],
                activeforeground=self.cfg_app["couleur_texte"],
                selectcolor="#333333",
                command=self._maj_bouton,
                cursor="hand2"
            )
            self.cb.pack()
        else:
            self.var_checkbox = None

        # Boutons
        cadre_boutons = tk.Frame(conteneur, bg=self.cfg_app["couleur_fond"])
        cadre_boutons.pack(pady=30)

        # Bouton Refuser (gris)
        self.creer_bouton(
            cadre_boutons,
            self.cfg_ecran["texte_refuser"],
            self._refuser,
            couleur="#555555",
            largeur=20
        ).pack(side="left", padx=20)

        # Bouton Accepter
        self.btn_accepter = self.creer_bouton(
            cadre_boutons,
            self.cfg_ecran["texte_accepter"],
            self._accepter,
            largeur=28
        )
        self.btn_accepter.pack(side="left", padx=20)

        # Griser le bouton si checkbox obligatoire
        self._maj_bouton()

    def _maj_bouton(self):
        """Active/désactive le bouton selon la checkbox"""
        if self.var_checkbox is None:
            return
        if self.var_checkbox.get():
            self.btn_accepter.config(
                state="normal",
                bg=self.cfg_app["couleur_bouton"]
            )
        else:
            self.btn_accepter.config(state="disabled", bg="#444444")

    def afficher(self):
        pass

    def _accepter(self):
        """L'utilisateur accepte → écran choix template"""
        self.app.donnees_session["consentement"] = True
        self.app.aller_a("choix_template")

    def _refuser(self):
        """L'utilisateur refuse → retour accueil"""
        self.app.donnees_session["consentement"] = False
        self.app.aller_a("accueil")


#    def bouton_precedent(self):
#        self._refuser()

    def bouton_annuler(self):
        self._refuser()

    def bouton_valider(self):
        if self.var_checkbox is None or self.var_checkbox.get():
            self._accepter()
        else:
            self.var_checkbox.set(True)
            self._maj_bouton()
