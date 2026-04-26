"""
Écran 3 - Choix du template
Version améliorée : grille adaptative, tout dans l'écran
"""

import tkinter as tk
import os
from PIL import Image, ImageTk, ImageDraw
from .base import EcranBase


class EcranChoixTemplate(EcranBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.cfg_ecran = app.config["choix_template"]
        self.template_selectionne = None
        self.cadres_templates = []
        self._construire_ui()

    def _construire_ui(self):
        entete = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        entete.pack(fill="x", padx=30, pady=(20, 5))
        self.creer_titre(entete, self.cfg_ecran["titre"], "Arial 36 bold").pack()
        self.creer_sous_titre(entete, self.cfg_ecran["sous_titre"]).pack(pady=4)
        self.separateur(entete).pack(fill="x", pady=6)

        self.cadre_grille = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        self.cadre_grille.pack(fill="both", expand=True, padx=30, pady=5)

        bas = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        bas.pack(fill="x", pady=(5, 15))

        self.label_selection = tk.Label(
            bas, text="Sélectionnez un personnage pour continuer",
            font="Arial 16 italic", fg="#888888", bg=self.cfg_app["couleur_fond"]
        )
        self.label_selection.pack(pady=4)

        boutons = tk.Frame(bas, bg=self.cfg_app["couleur_fond"])
        boutons.pack()

        self.creer_bouton(boutons, "← Retour",
            lambda: self.app.aller_a("disclaimer"),
            couleur="#555555", largeur=15).pack(side="left", padx=15)

        self.btn_valider = self.creer_bouton(boutons,
            self.cfg_ecran["texte_bouton_suivant"], self._valider, largeur=22)
        self.btn_valider.pack(side="left", padx=15)
        self.btn_valider.config(state="disabled", bg="#444444")

    def afficher(self):
        self.update_idletasks()
        self.after(100, self._charger_templates)

    def _charger_templates(self):
        dossier = self.cfg_ecran["templates_dossier"]
        extensions = (".jpg", ".jpeg", ".png", ".webp")
        fichiers = [os.path.join(dossier, f) for f in sorted(os.listdir(dossier))
                    if f.lower().endswith(extensions)] if os.path.exists(dossier) else []

        if not fichiers:
            tk.Label(self.cadre_grille, text="⚠️ Aucun template trouvé\n" + dossier,
                font="Arial 18", fg="#ff6666", bg=self.cfg_app["couleur_fond"]).pack(pady=40)
            return

        nb = len(fichiers)
        colonnes = 3 if nb <= 6 else 4
        lignes = (nb + colonnes - 1) // colonnes

        self.cadre_grille.update_idletasks()
        larg = self.cadre_grille.winfo_width() or 900
        haut = self.cadre_grille.winfo_height() or 550

        marge = 12
        taille_w = (larg - marge * (colonnes + 1)) // colonnes
        taille_h = (haut - marge * (lignes + 1) - lignes * 38) // lignes
        taille = max(80, min(taille_w, taille_h, 280))

        for c in range(colonnes):
            self.cadre_grille.columnconfigure(c, weight=1)
        for r in range(lignes):
            self.cadre_grille.rowconfigure(r, weight=1)

        for i, chemin in enumerate(fichiers):
            ligne, col = i // colonnes, i % colonnes
            tk_img = self._creer_vignette(chemin, taille)
            nom = os.path.splitext(os.path.basename(chemin))[0].replace("_", " ").title()

            cadre = tk.Frame(self.cadre_grille, bg=self.cfg_app["couleur_fond"],
                             cursor="hand2", pady=4, padx=4)
            cadre.grid(row=ligne, column=col, padx=marge//2, pady=marge//2, sticky="nsew")

            if tk_img:
                lbl = tk.Label(cadre, image=tk_img, bg=self.cfg_app["couleur_fond"], cursor="hand2")
                lbl.pack()
                lbl.bind("<Button-1>", lambda e, c=chemin, f=cadre: self._selectionner(c, f))

            lnm = tk.Label(cadre, text=nom, font=f"Arial {max(11, taille//16)} bold",
                           fg=self.cfg_app["couleur_texte"], bg=self.cfg_app["couleur_fond"], cursor="hand2")
            lnm.pack(pady=2)
            lnm.bind("<Button-1>", lambda e, c=chemin, f=cadre: self._selectionner(c, f))
            cadre.bind("<Button-1>", lambda e, c=chemin, f=cadre: self._selectionner(c, f))
            self.cadres_templates.append((chemin, cadre))

    def _creer_vignette(self, chemin, taille):
        try:
            img = Image.open(chemin).convert("RGBA")
            w, h = img.size
            c = min(w, h)
            img = img.crop(((w-c)//2, (h-c)//2, (w+c)//2, (h+c)//2))
            img = img.resize((taille, taille), Image.LANCZOS)
            masque = Image.new("L", (taille, taille), 0)
            ImageDraw.Draw(masque).ellipse((0, 0, taille, taille), fill=255)
            img.putalpha(masque)
            fond = Image.new("RGBA", (taille, taille), self.cfg_app["couleur_fond"])
            fond.paste(img, mask=img.split()[3])
            tk_img = ImageTk.PhotoImage(fond)
            self._images_refs.append(tk_img)
            return tk_img
        except Exception:
            return None

    def _selectionner(self, chemin, cadre_sel):
        self.template_selectionne = chemin
        for _, c in self.cadres_templates:
            c.config(bg=self.cfg_app["couleur_fond"])
            for w in c.winfo_children():
                try: w.config(bg=self.cfg_app["couleur_fond"])
                except: pass
        cadre_sel.config(bg=self.cfg_app["couleur_accent"])
        for w in cadre_sel.winfo_children():
            try: w.config(bg=self.cfg_app["couleur_accent"])
            except: pass
        nom = os.path.splitext(os.path.basename(chemin))[0].replace("_", " ").title()
        self.label_selection.config(text=f"✅ Sélectionné : {nom}", fg=self.cfg_app["couleur_accent"])
        self.btn_valider.config(state="normal", bg=self.cfg_app["couleur_bouton"])

    def _valider(self):
        if self.template_selectionne:
            self.app.aller_a("webcam", template=self.template_selectionne)
            
    def bouton_valider(self):
        self._valider()

    def bouton_annuler(self):
        self.app.aller_a("disclaimer"),
        
    def bouton_suivant(self):
        """Sélectionne le template suivant"""
        if not self.cadres_templates:
            return
        idx = 0
        for i, (chemin, _) in enumerate(self.cadres_templates):
            if chemin == self.template_selectionne:
                idx = (i + 1) % len(self.cadres_templates)
                break
        chemin, cadre = self.cadres_templates[idx]
        self._selectionner(chemin, cadre)

    def bouton_precedent(self):
        """Sélectionne le template précédent"""
        if not self.cadres_templates:
            return
        idx = 0
        for i, (chemin, _) in enumerate(self.cadres_templates):
            if chemin == self.template_selectionne:
                idx = (i - 1) % len(self.cadres_templates)
                break
        chemin, cadre = self.cadres_templates[idx]
        self._selectionner(chemin, cadre)
