"""
Écran 6 - Résultat avec QR Code
Version améliorée : tout dans l'écran
"""

import tkinter as tk
import qrcode
import os
from PIL import Image, ImageTk
from .base import EcranBase


class EcranResultat(EcranBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.cfg_ecran = app.config["resultat"]
        self._timer_retour = None
        self._temps_restant = 0
        self._construire_ui()

    def _construire_ui(self):
        entete = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        entete.pack(fill="x", padx=30, pady=(15, 5))
        self.creer_titre(entete, self.cfg_ecran["titre"], "Arial 36 bold").pack()
        self.creer_sous_titre(entete, self.cfg_ecran["sous_titre"]).pack(pady=4)
        self.separateur(entete).pack(fill="x", pady=6)

        corps = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        corps.pack(fill="both", expand=True, padx=30, pady=5)
        corps.columnconfigure(0, weight=1)
        corps.columnconfigure(1, weight=1)
        corps.rowconfigure(0, weight=1)

        # Gauche : photo
        cg = tk.Frame(corps, bg=self.cfg_app["couleur_fond"])
        cg.grid(row=0, column=0, sticky="nsew", padx=15)
        tk.Label(cg, text="✨ Votre photo", font="Arial 20 bold",
            fg=self.cfg_app["couleur_accent"], bg=self.cfg_app["couleur_fond"]).pack(pady=(0,8))
        self.label_apercu = tk.Label(cg, bg="#1a1a1a")
        self.label_apercu.pack(expand=True, fill="both")

        # Droite : QR
        cd = tk.Frame(corps, bg=self.cfg_app["couleur_fond"])
        cd.grid(row=0, column=1, sticky="nsew", padx=15)
        tk.Label(cd, text="📱 Téléchargez votre photo", font="Arial 20 bold",
            fg=self.cfg_app["couleur_accent"], bg=self.cfg_app["couleur_fond"]).pack(pady=(0,8))
        self.label_qr = tk.Label(cd, bg=self.cfg_app["couleur_fond"])
        self.label_qr.pack(expand=True)
        self.label_url = tk.Label(cd, text="", font="Arial 12", fg="#888888",
            bg=self.cfg_app["couleur_fond"], wraplength=350)
        self.label_url.pack(pady=5)

        bas = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        bas.pack(fill="x", pady=(5, 15))
        self.label_timer = tk.Label(bas, text="", font="Arial 15",
            fg="#666666", bg=self.cfg_app["couleur_fond"])
        self.label_timer.pack(pady=4)
        boutons = tk.Frame(bas, bg=self.cfg_app["couleur_fond"])
        boutons.pack()
        self.creer_bouton(boutons, self.cfg_ecran["texte_bouton_accueil"],
            self._retour_accueil, couleur="#555555", largeur=18).pack(side="left", padx=15)
        self.creer_bouton(boutons, self.cfg_ecran["texte_bouton_recommencer"],
            lambda: self.app.aller_a("choix_template"), largeur=22).pack(side="left", padx=15)

    def afficher(self):
        self.update_idletasks()
        self.after(150, self._afficher_contenu)

    def _afficher_contenu(self):
        chemin = self.app.donnees_session.get("chemin_resultat", "")
        
        # Debug - affiche tout ce qu'on a en session
        print("=== SESSION ===")
        for k, v in self.app.donnees_session.items():
            print(f"  {k}: {v}")
        print("===============")
        
        url_qr = self.app.donnees_session.get("url_photo_courte", "")
        url_affichage = self.app.donnees_session.get("url_photo_complete", url_qr)
        
        if not url_qr:
            id_photo = self.app.donnees_session.get("id_photo", "demo")
            url_base = self.cfg_ecran.get("texte_url_base", "http://photobooth.baule.fr/photos/")
            url_qr = url_base + id_photo
            url_affichage = url_qr

        print(f"URL QR final : {url_qr}")
        
        # Afficher ou masquer l'URL selon config
        if self.cfg_ecran.get("afficher_url", True):
            self.label_url.config(text=url_qr)
        else:
            self.label_url.pack_forget()
        self._generer_qr(url_qr)
        
        if chemin:
            self._attendre_et_afficher(chemin, tentatives=10)
        
        self._demarrer_timer_retour()        
        
    def _attendre_et_afficher(self, chemin, tentatives):
        """Vérifie que le fichier existe et est lisible avant d'afficher"""
        import os
        if tentatives <= 0:
            self.label_apercu.config(
                text="⚠️ Image non disponible", font="Arial 16", fg="#ff6666")
            return
        
        if os.path.exists(chemin) and os.path.getsize(chemin) > 0:
            try:
                # Tester que l'image est vraiment lisible
                from PIL import Image
                img_test = Image.open(chemin)
                img_test.verify()
                # OK, afficher
                self.after(100, lambda: self._afficher_apercu(chemin))
            except Exception:
                # Fichier pas encore prêt, réessayer
                self.after(500, lambda: self._attendre_et_afficher(chemin, tentatives - 1))
        else:
            # Fichier pas encore là, réessayer dans 500ms
            self.after(500, lambda: self._attendre_et_afficher(chemin, tentatives - 1))
                
    def _generer_qr(self, url):
        self.update_idletasks()
        # Prendre toute la largeur disponible du label QR
        larg = self.label_qr.winfo_width() or 500
        haut = self.label_qr.winfo_height() or 500
        taille = max(300, min(larg, haut, self.cfg_ecran.get("taille_qrcode", 500)))
        try:
            qr = qrcode.QRCode(version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#000000", back_color="#ffffff")
            img = img.resize((taille, taille), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self._images_refs.append(tk_img)
            self.label_qr.config(image=tk_img)
        except Exception as e:
            self.label_qr.config(text=f"QR indispo\n{e}", font="Arial 13", fg="#ff6666")
            
    def _afficher_apercu(self, chemin):
        self.label_apercu.update_idletasks()
        larg = max(200, self.label_apercu.winfo_width() - 10)
        haut = max(200, self.label_apercu.winfo_height() - 10)
        try:
            img = Image.open(chemin)
            img.thumbnail((larg, haut), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self._images_refs.append(tk_img)
            self.label_apercu.config(image=tk_img)
        except Exception as e:
            self.label_apercu.config(text=f"Aperçu indispo\n{e}", font="Arial 13", fg="#ff6666")

    def _demarrer_timer_retour(self):
        self._temps_restant = self.cfg_ecran.get("duree_affichage_secondes", 60)
        self._tick_timer()

    def _tick_timer(self):
        if not self.winfo_exists():
            return
        if self._temps_restant <= 0:
            self._retour_accueil()
            return
        self.label_timer.config(text=f"Retour automatique dans {self._temps_restant}s")
        self._temps_restant -= 1
        self._timer_retour = self.after(1000, self._tick_timer)

    def _retour_accueil(self):
        self._nettoyer_photos()
        self.app.donnees_session = {}
        self.app.aller_a("accueil")

    def _nettoyer_photos(self):
        for cle in ["photo_source", "chemin_resultat"]:
            chemin = self.app.donnees_session.get(cle)
            if chemin and os.path.exists(chemin):
                try: os.remove(chemin)
                except: pass

    def destroy(self):
        if self._timer_retour:
            try: self.after_cancel(self._timer_retour)
            except: pass
        super().destroy()


#    def bouton_precedent(self):
#        self._retour_accueil()


    def bouton_annuler(self):
        self._retour_accueil()

    def bouton_valider(self):
        self.app.aller_a("choix_template")
