"""
Écran 1 - Accueil
"""

import tkinter as tk
from .base import EcranBase


class EcranAccueil(EcranBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.cfg_ecran = app.config["accueil"]
        self._timer_idle = None
        self._animation_id = None
        self._construire_ui()

    def _construire_ui(self):
        # Conteneur centré
        centre = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        centre.place(relx=0.5, rely=0.5, anchor="center")

        # Logo (optionnel)
        logo_path = self.cfg_app.get("logo_path", "")
        logo_img = self.charger_image(logo_path, largeur=300)
        if logo_img:
            tk.Label(centre, image=logo_img, bg=self.cfg_app["couleur_fond"]).pack(pady=20)

        # Titre principal avec animation pulsante
        self.label_titre = self.creer_titre(centre, self.cfg_ecran["titre"], "Arial 64 bold")
        self.label_titre.pack(pady=30)

        # Séparateur
        self.separateur(centre, hauteur=3).pack(fill="x", padx=100, pady=10)

        # Sous-titre
        self.creer_sous_titre(centre, self.cfg_ecran["sous_titre"]).pack(pady=20)

        # Bouton démarrer
        btn = self.creer_bouton(
            centre,
            self.cfg_ecran["texte_bouton"],
            self._demarrer,
            largeur=25
        )
        btn.pack(pady=50)

        # Texte "Touchez l'écran pour commencer" (clignotant)
        self.label_touch = tk.Label(
            centre,
            text="Valider pour commencer",
            font="Arial 18 italic",
            fg="#888888",
            bg=self.cfg_app["couleur_fond"]
        )
        self.label_touch.pack(pady=20)

        # Cliquer n'importe où démarre aussi
        self.bind("<Button-1>", lambda e: self._demarrer())

    def afficher(self):
        """Démarre les animations et le timer idle"""
        self._animer_titre()
        self._animer_clignotement()
        self._demarrer_timer_idle()

    def _animer_titre(self, couleurs=None, index=0):
        """Animation pulsante sur le titre"""
        if not self.cfg_ecran.get("animation_idle", True):
            return
        couleurs = couleurs or [
            self.cfg_app["couleur_accent"],
            "#ff6bc1",
            "#ffffff",
            "#ff6bc1",
        ]
        if not self.winfo_exists():
            return
        try:
            self.label_titre.config(fg=couleurs[index % len(couleurs)])
            self._animation_id = self.after(800, self._animer_titre, couleurs, index + 1)
        except Exception:
            pass

    def _animer_clignotement(self, visible=True):
        """Clignotement du texte invitation"""
        if not self.winfo_exists():
            return
        try:
            couleur = "#888888" if visible else self.cfg_app["couleur_fond"]
            self.label_touch.config(fg=couleur)
            self.after(900, self._animer_clignotement, not visible)
        except Exception:
            pass

    def _demarrer_timer_idle(self):
        """Lance le timer de retour auto si inactif"""
        delai = self.cfg_ecran.get("delai_auto_secondes", 0)
        if delai > 0:
            # Sur l'accueil, le timer sert juste à rafraîchir
            # (pas de retour car on EST à l'accueil)
            pass

    def _demarrer(self):
        """Passe à l'écran disclaimer"""
        # Annuler les animations
        if self._animation_id:
            self.after_cancel(self._animation_id)
        self.app.aller_a("disclaimer")

    def destroy(self):
        """Nettoyage"""
        if self._animation_id:
            try:
                self.after_cancel(self._animation_id)
            except Exception:
                pass
        super().destroy()
        
    def bouton_valider(self):
        self._demarrer()

#    def bouton_suivant(self):
#        self._demarrer()
