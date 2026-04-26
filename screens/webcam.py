"""
Écran 4 - Webcam & capture photo
Version améliorée : tout dans l'écran, vidéo adaptative
"""

import tkinter as tk
import cv2
import os
import uuid
import numpy
from PIL import Image, ImageTk
from .base import EcranBase


class EcranWebcam(EcranBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.cfg_ecran = app.config["webcam"]
        self.cap = None
        self.photo_prise = False
        self.photo_path = None
        self.nb_essais = 0
        self._camera_id = None
        self._compte_rebours_id = None
        self._en_cours_decompte = False
        self._video_w = 640
        self._video_h = 400
        self._construire_ui()
        self._last_tk_img = None
        self._canvas_img_id = None
        self._canvas_texte_id = None

    def _construire_ui(self):
        # === EN-TÊTE compact ===
        entete = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        entete.pack(fill="x", padx=30, pady=(15, 5))
        self.creer_titre(entete, self.cfg_ecran["titre"], "Arial 36 bold").pack()
        self.label_instructions = self.creer_sous_titre(entete, self.cfg_ecran["instructions"])
        self.label_instructions.pack(pady=4)
        self.separateur(entete).pack(fill="x", pady=6)

        # === ZONE VIDÉO ===
        self.cadre_video = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        self.cadre_video.pack(fill="both", expand=True, padx=0, pady=5)

        # Un seul Canvas pour la vidéo ET le compte à rebours
        self.canvas_video = tk.Canvas(
            self.cadre_video,
            bg="black",
            highlightthickness=0,
            bd=0
        )
        self.canvas_video.pack(fill="both", expand=True)
        self._canvas_img_id = None
        self._canvas_texte_id = None

        # === BAS DE PAGE : boutons toujours visibles ===
        bas = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        bas.pack(fill="x", pady=(5, 15))

        self.cadre_boutons = tk.Frame(bas, bg=self.cfg_app["couleur_fond"])
        self.cadre_boutons.pack(pady=5)

        self.btn_photo = self.creer_bouton(
            self.cadre_boutons,
            self.cfg_ecran["texte_bouton_photo"],
            self._lancer_decompte,
            largeur=26
        )
        self.btn_photo.pack(pady=5)

        self.btn_recommencer = self.creer_bouton(
            self.cadre_boutons,
            self.cfg_ecran["texte_bouton_recommencer"],
            self._recommencer,
            couleur="#555555",
            largeur=20
        )
        self.btn_recommencer.pack_forget()

        self.btn_valider = self.creer_bouton(
            self.cadre_boutons,
            self.cfg_ecran["texte_bouton_valider"],
            self._valider_photo,
            largeur=26
        )
        self.btn_valider.pack_forget()

        self.creer_bouton(
            bas,
            "← Changer de personnage",
            lambda: self._nettoyer_et_aller("choix_template"),
            couleur="#444444",
            largeur=24
        ).pack(pady=2)

    def afficher(self):
        """Attend le rendu puis démarre la caméra avec les bonnes dimensions"""
        self.update_idletasks()
        self.after(100, self._demarrer_camera)
        self.after(200, self._afficher_vignette_template)

    def _demarrer_camera(self):
        self.cadre_video.update_idletasks()
        larg = self.cadre_video.winfo_width()
        haut = self.cadre_video.winfo_height()

        ratio = 16 / 9
        if larg / haut > ratio:
            self._video_h = haut - 10
            self._video_w = int(self._video_h * ratio)
        else:
            self._video_w = larg - 10
            self._video_h = int(self._video_w / ratio)

        self._video_w = max(320, self._video_w)
        self._video_h = max(180, self._video_h)

        index = self.cfg_ecran.get("index_camera", 0)
        self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.cap.isOpened():
            self.label_instructions.config(
                text=f"⚠️ Caméra introuvable (index {index})", fg="#ff6666")
            return

        # Détecter automatiquement la colonne du trait noir
        self._colonne_trait = self._detecter_trait()
        self._actualiser_camera()

    def _detecter_trait(self):
        """Capture quelques frames et trouve la colonne la plus sombre = le trait"""
        for _ in range(5):  # ignorer les premières frames instables
            self.cap.read()
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Convertir en niveaux de gris
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(float)
        
        # Moyenne de luminosité par colonne
        moy_col = gris.mean(axis=0)
        
        # La colonne du trait = la plus sombre si elle est vraiment anormalement sombre
        col_min = int(moy_col.argmin())
        val_min = moy_col[col_min]
        val_moy = moy_col.mean()
        
        # Ne corriger que si le trait est vraiment anormal (30% plus sombre que la moyenne)
        if val_min < val_moy * 0.7:
            print(f"Trait détecté à la colonne {col_min} (luminosité {val_min:.1f} vs moyenne {val_moy:.1f})")
            return col_min
        
        print("Aucun trait anormal détecté")
        return None

    def _actualiser_camera(self):
        """Boucle d'affichage du flux caméra"""
        if self.cap is None or not self.cap.isOpened():
            return
        if not self.winfo_exists():
            return
        if self.photo_prise:
            return

        ret, frame = self.cap.read()
        if ret:
            if self.cfg_ecran.get("miroir", True):
                frame = cv2.flip(frame, 1)
            self._afficher_frame(frame)

        self._camera_id = self.after(33, self._actualiser_camera)
            
    def _afficher_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((self._video_w, self._video_h), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        self._last_tk_img = tk_img  # garder référence

        cw = self.canvas_video.winfo_width()
        ch = self.canvas_video.winfo_height()
        cx = cw // 2
        cy = ch // 2

        if self._canvas_img_id:
            self.canvas_video.itemconfig(self._canvas_img_id, image=tk_img)
            self.canvas_video.coords(self._canvas_img_id, cx, cy)
        else:
            self._canvas_img_id = self.canvas_video.create_image(
                cx, cy, anchor="center", image=tk_img)        
                
    def _lancer_decompte(self):
        if self._en_cours_decompte:
            return
        self._en_cours_decompte = True
        self.btn_photo.config(state="disabled", bg="#444444")
        self._decompte(self.cfg_ecran.get("compte_a_rebours", 5))

    def _decompte(self, secondes):
        if not self.winfo_exists():
            return
        
        # Effacer l'ancien texte
        if self._canvas_texte_id:
            self.canvas_video.delete(self._canvas_texte_id)
            self._canvas_texte_id = None

        if secondes > 0:
            cw = self.canvas_video.winfo_width()
            ch = self.canvas_video.winfo_height()
            self._canvas_texte_id = self.canvas_video.create_text(
                cw // 2, ch // 2,
                text=str(secondes),
                font="Arial 100 bold",
                fill=self.cfg_app["couleur_accent"]
            )
            self._compte_rebours_id = self.after(1000, self._decompte, secondes - 1)
        else:
            cw = self.canvas_video.winfo_width()
            ch = self.canvas_video.winfo_height()
            self._canvas_texte_id = self.canvas_video.create_text(
                cw // 2, ch // 2,
                text="📸",
                font="Arial 100 bold",
                fill=self.cfg_app["couleur_accent"]
            )
            self.after(300, self._prendre_photo)
            
    def _prendre_photo(self):
        # Effacer le texte 📸 du canvas
        if self._canvas_texte_id:
            self.canvas_video.delete(self._canvas_texte_id)
            self._canvas_texte_id = None

        if self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self.label_instructions.config(text="⚠️ Erreur capture, réessayez", fg="#ff6666")
            self._reinitialiser_decompte()
            return

        if self.cfg_ecran.get("miroir", True):
            frame = cv2.flip(frame, 1)

        # Sauvegarde pleine résolution
        dossier = self.app.config["traitement"]["output_dossier"]
        os.makedirs(dossier, exist_ok=True)
        self.photo_path = os.path.join(dossier, f"source_{uuid.uuid4().hex[:8]}.jpg")
        
        # frame = self._ameliorer_photo(frame)
        cv2.imwrite(self.photo_path, frame)

        # Arrêter le flux
        self.photo_prise = True
        if self._camera_id:
            self.after_cancel(self._camera_id)

        # Afficher la photo sur le canvas
        self._afficher_frame(frame)

        # Afficher ✅ sur le canvas
        cw = self.canvas_video.winfo_width()
        ch = self.canvas_video.winfo_height()
        self._canvas_texte_id = self.canvas_video.create_text(
            cw // 2, ch // 2,
            text="✅",
            font="Arial 100 bold",
            fill="#88ff88"
        )
        self.after(800, lambda: self.canvas_video.delete(self._canvas_texte_id) 
                   if self._canvas_texte_id else None)

        self.label_instructions.config(
            text="Photo prise ! Êtes-vous satisfait(e) ?", fg="#88ff88")

        # Basculer les boutons
        self.btn_photo.pack_forget()
        self.btn_recommencer.pack(side="left", padx=15, pady=5)
        self.btn_valider.pack(side="left", padx=15, pady=5)
        self._en_cours_decompte = False
        
    def _recommencer(self):
        self.nb_essais += 1
        if self.nb_essais >= self.cfg_ecran.get("nb_essais_max", 3):
            self._nettoyer_et_aller("choix_template")
            return

        self.photo_prise = False
        self.photo_path = None
        self.btn_recommencer.pack_forget()
        self.btn_valider.pack_forget()
        self.btn_photo.config(state="normal", bg=self.cfg_app["couleur_bouton"])
        self.btn_photo.pack(pady=5)
        self.label_instructions.config(
            text=self.cfg_ecran["instructions"], fg=self.cfg_app["couleur_texte"])
        self._actualiser_camera()

    def _valider_photo(self):
        self._nettoyer_et_aller("traitement", photo_source=self.photo_path)

    def _nettoyer_et_aller(self, ecran, **kwargs):
        self._arreter_camera()
        self.app.aller_a(ecran, **kwargs)

    def _arreter_camera(self):
        for attr in ["_camera_id", "_compte_rebours_id"]:
            val = getattr(self, attr, None)
            if val:
                try: self.after_cancel(val)
                except: pass
        if self.cap:
            self.cap.release()
            self.cap = None

    def _reinitialiser_decompte(self):
        self._en_cours_decompte = False
        if self._canvas_texte_id:
            self.canvas_video.delete(self._canvas_texte_id)
            self._canvas_texte_id = None
        self.btn_photo.config(state="normal", bg=self.cfg_app["couleur_bouton"])

    def destroy(self):
        self._arreter_camera()
        super().destroy()
        
    def _ameliorer_photo(self, frame):
        """Améliore la photo avant le face swap"""
        # Correction gamma si image sombre
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
        
        # Légère netteté
        kernel = numpy.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
        frame = cv2.filter2D(frame, -1, kernel)
        
        return frame
        
    def bouton_photo(self):
        self._lancer_decompte()

#    def bouton_precedent(self):
#        self._nettoyer_et_aller("choix_template")

    def bouton_annuler(self):
        if self.photo_prise:
            self._recommencer()
        else:
            self._nettoyer_et_aller("choix_template")

    def bouton_valider(self):
        if self.photo_prise:
            self._valider_photo()
        else:
            self._lancer_decompte()
            
            
    def _afficher_vignette_template(self):
        """Affiche la vignette du template centrée à droite de la zone vidéo"""
        template = self.app.donnees_session.get("template")
        if not template or not os.path.exists(template):
            return

        try:
            from PIL import Image, ImageTk

            taille = 150

            # Charger et recadrer en carré
            img = Image.open(template).convert("RGBA")
            w, h = img.size
            c = min(w, h)
            img = img.crop(((w-c)//2, (h-c)//2, (w+c)//2, (h+c)//2))
            img = img.resize((taille, taille), Image.LANCZOS)

            # Bordure rose
            bordure = Image.new("RGBA", (taille+6, taille+6), self.cfg_app["couleur_accent"])
            bordure.paste(img, (3, 3))
            tk_img = ImageTk.PhotoImage(bordure)
            self._images_refs.append(tk_img)

            nom = os.path.splitext(os.path.basename(template))[0].replace("_", " ").title()

            # Cadre centré verticalement à droite du canvas
            self.cadre_vignette = tk.Frame(
                self.cadre_video,
                bg=self.cfg_app["couleur_fond"],
                padx=8,
                pady=8
            )
            # relx=1.0 = bord droit, rely=0.5 = milieu vertical
            #self.cadre_vignette.place(relx=0.98, rely=0.5, anchor="e")
            # Calculer le centre de la bande noire à droite
            self.cadre_video.update_idletasks()
            largeur_canvas = self.cadre_video.winfo_width()
            # La vidéo est centrée, donc la bande droite commence à video_w/2 + video_w/2
            bande_droite_debut = (largeur_canvas + self._video_w) // 2
            centre_bande_x = (bande_droite_debut + largeur_canvas) // 2

            self.cadre_vignette.place(x=centre_bande_x, rely=0.5, anchor="center")


            tk.Label(
                self.cadre_vignette,
                text="Votre choix",
                font="Arial 11 italic",
                fg="#aaaaaa",
                bg=self.cfg_app["couleur_fond"]
            ).pack(pady=(0, 5))

            tk.Label(
                self.cadre_vignette,
                image=tk_img,
                bg=self.cfg_app["couleur_fond"]
            ).pack()

            tk.Label(
                self.cadre_vignette,
                text=nom,
                font="Arial 13 bold",
                fg=self.cfg_app["couleur_accent"],
                bg=self.cfg_app["couleur_fond"],
                wraplength=150
            ).pack(pady=(5, 0))

        except Exception as e:
            print(f"Erreur vignette template : {e}")