"""
Écran 5 - Traitement Roop + Upload serveur
"""

import tkinter as tk
import threading
import subprocess
import os
import uuid
import requests
from .base import EcranBase


class EcranTraitement(EcranBase):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.cfg_ecran = app.config["traitement"]
        self.cfg_debug = app.config["debug"]
        self._anim_id = None
        self._message_index = 0
        self._construire_ui()
        self._en_erreur = False

    def _construire_ui(self):
        # Tout est centré
        centre = tk.Frame(self, bg=self.cfg_app["couleur_fond"])
        centre.place(relx=0.5, rely=0.5, anchor="center")

        self.creer_titre(centre, self.cfg_ecran["titre"]).pack(pady=30)

        # Spinner animé (ASCII)
        self.label_spinner = tk.Label(
            centre,
            text="⏳",
            font="Arial 72",
            bg=self.cfg_app["couleur_fond"],
            fg=self.cfg_app["couleur_accent"]
        )
        self.label_spinner.pack(pady=20)

        # Message d'étape
        self.label_message = tk.Label(
            centre,
            text="Initialisation...",
            font="Arial 24",
            fg=self.cfg_app["couleur_texte"],
            bg=self.cfg_app["couleur_fond"]
        )
        self.label_message.pack(pady=15)

        # Barre de progression (simulée)
        self.cadre_barre = tk.Frame(centre, bg="#333333", width=700, height=20)
        self.cadre_barre.pack(pady=15)
        self.cadre_barre.pack_propagate(False)

        self.barre = tk.Frame(self.cadre_barre, bg=self.cfg_app["couleur_accent"], width=0, height=20)
        self.barre.place(x=0, y=0, height=20)

        # Label erreur (caché par défaut)
        self.label_erreur = tk.Label(
            centre,
            text="",
            font="Arial 18",
            fg="#ff6666",
            bg=self.cfg_app["couleur_fond"],
            wraplength=700,
            justify="center"
        )
        self.label_erreur.pack(pady=10)

        # Boutons sur la même ligne (cachés par défaut)
        self.cadre_boutons_erreur = tk.Frame(centre, bg=self.cfg_app["couleur_fond"])

        self.btn_retour = self.creer_bouton(
            self.cadre_boutons_erreur,
            "← Changer de personnage",
            lambda: self.app.aller_a("choix_template"),
            couleur="#555555",
            largeur=20
        )
        self.btn_retour.pack(side="left", padx=10)

        self.btn_retry = self.creer_bouton(
            self.cadre_boutons_erreur,
            "📸 Nouvelle photo →",
            lambda: self.app.aller_a("webcam"),  # ← webcam pas _lancer_traitement
            largeur=20
        )
        self.btn_retry.pack(side="left", padx=10)


    def afficher(self):
        """Démarre le traitement"""
        self._animer_spinner()
        self._lancer_traitement()

    def _lancer_traitement(self):
        self._en_erreur = False
        self.cadre_boutons_erreur.pack_forget()
        self.label_erreur.config(text="")
        self.label_spinner.config(text="⏳")
        self._message_index = 0
        self._maj_message()
        self._maj_barre(0)
        thread = threading.Thread(target=self._traiter, daemon=True)
        thread.start()

    def _traiter(self):
        """Logique de traitement (thread séparé)"""
        try:
            photo_source = self.app.donnees_session.get("photo_source")
            template = self.app.donnees_session.get("template")

            if not photo_source or not os.path.exists(photo_source):
                self._erreur("Photo source introuvable")
                return

            if not template or not os.path.exists(template):
                self._erreur("Template introuvable")
                return

            # Chemin de sortie
            dossier = self.cfg_ecran["output_dossier"]
            os.makedirs(dossier, exist_ok=True)
            nom_sortie = f"result_{uuid.uuid4().hex[:8]}.jpg"
            chemin_sortie = os.path.join(dossier, nom_sortie)

            # === ÉTAPE 1 : Roop ===
            self._maj_message_thread(0)
            self._maj_barre(20)

            if self.cfg_debug.get("simuler_roop", False):
                # Mode debug : copier la source comme résultat
                import shutil
                import time
                time.sleep(2)
                shutil.copy(photo_source, chemin_sortie)
            else:
                succes = self._executer_roop(photo_source, template, chemin_sortie)
                if not succes:
                    return
                print(f"Chemin sortie : {chemin_sortie}")
                print(f"Fichier existe : {os.path.exists(chemin_sortie)}")
                if os.path.exists(chemin_sortie):
                    print(f"Taille fichier : {os.path.getsize(chemin_sortie)} octets")


            self._maj_barre(60)
            self._maj_message_thread(2)

            # === ÉTAPE 2 : Upload ===
            self._maj_message_thread(3)
            self._maj_barre(80)

            cfg_upload = self.cfg_ecran["upload"]
            if cfg_upload.get("actif", True):
                if self.cfg_debug.get("simuler_upload", False):
                    import time
                    time.sleep(1)
                    id_photo = uuid.uuid4().hex
                else:
                    id_photo = self._uploader(chemin_sortie)
                    if id_photo is None:
                        return
            else:
                id_photo = uuid.uuid4().hex

            self._maj_barre(100)
            self._maj_message_thread(4)

            # Sauvegarder les données pour l'écran résultat
            self.app.donnees_session["chemin_resultat"] = chemin_sortie
            self.app.donnees_session["id_photo"] = id_photo

            # Aller à l'écran résultat (depuis le thread principal)
            self.after(500, lambda: self.app.aller_a("resultat"))

        except Exception as e:
            self._erreur(f"Erreur inattendue : {e}")
            
    def _executer_roop(self, source, template, sortie):
        python_path = self.cfg_ecran.get("roop_python_path", "python")
        script_path = self.cfg_ecran.get("roop_script_path", "faceswap.py")
        model = self.cfg_ecran.get("roop_model", "C:/facebooth/models/inswapper_128.onnx")
        gfpgan = self.cfg_ecran.get("roop_gfpgan", "C:/facebooth/models/GFPGANv1.4.pth")

        try:
            self._maj_message_thread(1)
            resultat = subprocess.run(
                [python_path, script_path,
                 "-s", source,
                 "-t", template,
                 "-o", sortie,
                 "-m", model,
                 "-g", gfpgan],
                capture_output=True,
                text=True,
                timeout=180  # 3 minutes car GFPGAN prend plus de temps
            )
#            print(f"=== RETURNCODE: {resultat.returncode}")
#            print(f"=== STDOUT COMPLET: {resultat.stdout}")
#            print(f"=== STDERR COMPLET: {resultat.stderr}")

            if resultat.returncode != 0:
                stdout = resultat.stdout + resultat.stderr
                if "ERREUR_VISAGE_SOURCE" in stdout:
                    self._erreur("", cle_config="visage_non_detecte")
                elif "ERREUR_VISAGE_TEMPLATE" in stdout:
                    self._erreur("", cle_config="template_non_detecte")
                elif "TimeoutExpired" in stdout:
                    self._erreur("", cle_config="timeout")
                else:
                    self._erreur("", cle_config="erreur_generique")
                return False
            return True
        except subprocess.TimeoutExpired:
            self._erreur("", cle_config="timeout")
            return False
        except Exception as e:
            self._erreur("", cle_config="erreur_generique")
            return False

    def _uploader(self, chemin_photo):
        """Upload la photo sur le serveur PHP"""
        cfg = self.cfg_ecran["upload"]
        url = cfg["url"]
        timeout = cfg.get("timeout_secondes", 30)

        try:
            with open(chemin_photo, "rb") as f:
                nom_fichier = os.path.basename(chemin_photo)
                response = requests.post(
                    url,
                    files={"file": (nom_fichier, f, "image/jpeg")},
                    timeout=timeout
                )

            if response.status_code == 200:
                # Le PHP retourne l'URL complète directement
                url_retournee = response.text.strip()
                print(f"Upload OK : {url_retournee}")
                
                # Raccourcissement optionnel
                if cfg.get("raccourcir_url", False):
                    url_courte = self._raccourcir_url(url_retournee)
                    print(f"URL courte : {url_courte}")
                else:
                    url_courte = url_retournee
                
                # Stocker l'URL complète pour affichage ET l'URL courte pour le QR
                self.app.donnees_session["url_photo_complete"] = url_retournee
                self.app.donnees_session["url_photo_courte"] = url_courte
                
                # Extraire juste le nom de fichier pour le QR code
                nom = os.path.basename(url_retournee)
                return nom
            else:
                self._erreur(f"Erreur serveur ({response.status_code})\n{response.text[:100]}")
                return None

        except requests.exceptions.Timeout:
            self._erreur("Délai d'upload dépassé")
            return None
        except requests.exceptions.ConnectionError:
            self._erreur("Impossible de se connecter au serveur\nVérifiez la connexion réseau")
            return None
        except Exception as e:
            self._erreur(f"Erreur upload : {e}")
            return None
            
    def _raccourcir_url(self, url_longue):
        """Raccourcit une URL via cleanuri.com"""
        try:
            response = requests.post(
                "https://cleanuri.com/api/v1/shorten",
                data={"url": url_longue},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                url_courte = data.get("result_url", "")
                if url_courte:
                    print(f"CleanURI OK : {url_courte}")
                    return url_courte
            print(f"CleanURI erreur : {response.text}")
            return url_longue
        except Exception as e:
            print(f"Raccourcissement échoué : {e}")
            return url_longue            
            
    def _maj_message(self):
        """Met à jour le message d'étape"""
        messages = self.cfg_ecran["messages_attente"]
        if self._message_index < len(messages):
            self.label_message.config(text=messages[self._message_index])

    def _maj_message_thread(self, index):
        """Met à jour le message depuis un thread"""
        self._message_index = index
        self.after(0, self._maj_message)

    def _maj_barre(self, pourcentage):
        """Met à jour la barre de progression"""
        def update():
            if self.winfo_exists():
                largeur = int(700 * pourcentage / 100)
                self.barre.config(width=largeur)
        self.after(0, update)

#    def _erreur(self, message):
#        """Affiche une erreur et propose de réessayer"""
#        def show():
#            if not self.winfo_exists():
#                return
#            self.label_erreur.config(text=f"⚠️ {message}")
#            self.label_spinner.config(text="❌")
#            self.btn_retry.pack(pady=20)
#        self.after(0, show)

    def _erreur(self, message, cle_config=None):
        def show():
            if not self.winfo_exists():
                return
            self._en_erreur = True  # ← marquer qu'on est en erreur
            if cle_config:
                msgs = self.cfg_ecran.get("messages_erreur", {})
                texte = msgs.get(cle_config, message)
            else:
                texte = message
            self.label_erreur.config(text=texte)
            self.label_spinner.config(text="❌")
            self.cadre_boutons_erreur.pack(pady=15)
        self.after(0, show)

    def _animer_spinner(self):
        """Animation du spinner"""
        spinners = ["⏳", "⌛", "⏳", "⌛"]
        index = [0]

        def animer():
            if not self.winfo_exists():
                return
            try:
                self.label_spinner.config(text=spinners[index[0] % len(spinners)])
                index[0] += 1
                self._anim_id = self.after(600, animer)
            except Exception:
                pass

        animer()

    def destroy(self):
        if self._anim_id:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
        super().destroy()
        
    def bouton_valider(self):
        """Bouton vert → Nouvelle photo si erreur, sinon rien"""
        if self._en_erreur:
            self.app.aller_a("webcam")

    def bouton_annuler(self):
        """Bouton rouge → Changer de personnage"""
        if self._en_erreur:
            self.app.aller_a("choix_template")