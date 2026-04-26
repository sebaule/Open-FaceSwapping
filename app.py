"""
Application principale - Gestionnaire des écrans
"""

import tkinter as tk
import json
import os

from screens.accueil import EcranAccueil
from screens.disclaimer import EcranDisclaimer
from screens.choix_template import EcranChoixTemplate
from screens.webcam import EcranWebcam
from screens.traitement import EcranTraitement
from screens.resultat import EcranResultat


class Application:
    def __init__(self, root):
        self.root = root
        self.config = self.charger_config()
        self.donnees_session = {}  # Données partagées entre écrans

        self._configurer_fenetre()
        self._nettoyer_vieux_fichiers()  # ← ajoute cette ligne
        self.ecran_actuel = None
        self.aller_a("accueil")

    def charger_config(self):
        """Charge le fichier de configuration JSON"""
        chemin = os.path.join(os.path.dirname(__file__), "config.json")
        with open(chemin, "r", encoding="utf-8") as f:
            return json.load(f)

    def _configurer_fenetre(self):
        """Configure la fenêtre principale"""
        cfg = self.config["app"]
        self.root.title(cfg["titre"])
        self.root.configure(bg=cfg["couleur_fond"])

        if cfg["plein_ecran"]:
            self.root.attributes("-fullscreen", True)
        else:
            self.root.geometry(f"{cfg['largeur']}x{cfg['hauteur']}")

        # Touche Echap pour quitter le plein écran (utile en dev)
        self.root.bind("<Escape>", self._toggle_plein_ecran)
        # F1 pour quitter l'app complètement
        self.root.bind("<F1>", lambda e: self.root.destroy())
        
        # Boutons physiques
        touches = self.config.get("boutons_physiques", {})
        if touches.get("actif", False):
            self.root.bind(touches.get("valider", "<Return>"),
                          lambda e: self._action_bouton("valider"))
            self.root.bind(touches.get("suivant", "<Right>"),
                          lambda e: self._action_bouton("suivant"))
            self.root.bind(touches.get("precedent", "<Left>"),
                          lambda e: self._action_bouton("precedent"))
            self.root.bind(touches.get("annuler", "<BackSpace>"),
                          lambda e: self._action_bouton("annuler"))

    def _action_bouton(self, action):
        """Transmet l'action au bouton de l'écran actuel"""
        if self.ecran_actuel and hasattr(self.ecran_actuel, f"bouton_{action}"):
            getattr(self.ecran_actuel, f"bouton_{action}")()


    def _toggle_plein_ecran(self, event=None):
        etat = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not etat)

    def aller_a(self, nom_ecran, **kwargs):
        """
        Navigation vers un écran.
        nom_ecran : 'accueil', 'disclaimer', 'choix_template', 
                    'webcam', 'traitement', 'resultat'
        """
        # Mettre à jour les données de session si besoin
        self.donnees_session.update(kwargs)

        # Détruire l'écran actuel
        if self.ecran_actuel is not None:
            self.ecran_actuel.destroy()

        # Créer le nouvel écran
        ecrans = {
            "accueil": EcranAccueil,
            "disclaimer": EcranDisclaimer,
            "choix_template": EcranChoixTemplate,
            "webcam": EcranWebcam,
            "traitement": EcranTraitement,
            "resultat": EcranResultat,
        }

        if nom_ecran not in ecrans:
            raise ValueError(f"Écran inconnu : {nom_ecran}")

        classe = ecrans[nom_ecran]
        #self.ecran_actuel = classe(self.root, self)
        #self.ecran_actuel.pack(fill="both", expand=True)
        #self.ecran_actuel.afficher()
        
        if self.ecran_actuel is None:
            # Premier écran : pas de transition
            self.ecran_actuel = classe(self.root, self)
            self.ecran_actuel.pack(fill="both", expand=True)
            self.ecran_actuel.afficher()
        else:
            # Transition avec fondu
            self._transition(classe)
        
        
    def _nettoyer_vieux_fichiers(self):
        import time
        dossier = self.config["traitement"]["output_dossier"]
        print(f"=== Nettoyage dossier : {dossier}")
        
        if not os.path.exists(dossier):
            print("=== Dossier inexistant, rien à nettoyer")
            return
        
        fichiers = os.listdir(dossier)
        print(f"=== {len(fichiers)} fichiers trouvés")
        
        supprimes = 0
        for f in fichiers:
            chemin = os.path.join(dossier, f)
            age = time.time() - os.path.getmtime(chemin)
            age_heures = age / 3600
            print(f"  {f} → âge: {age_heures:.1f}h")
            if age > 86400:  # 24h
                try:
                    os.remove(chemin)
                    print(f"  ✅ Supprimé : {f}")
                    supprimes += 1
                except Exception as e:
                    print(f"  ❌ Erreur suppression {f} : {e}")
        
        print(f"=== Nettoyage terminé : {supprimes} fichiers supprimés")
    
    
    def _transition(self, nouvelle_classe, duree=200, etapes=12):
        """Fondu enchaîné entre deux écrans via un Frame noir"""
        ecran_sortant = self.ecran_actuel
        delai = duree // etapes

        # Créer le nouvel écran caché
        nouvel_ecran = nouvelle_classe(self.root, self)
        nouvel_ecran.place(relx=0, rely=0, relwidth=1, relheight=1)
        nouvel_ecran.afficher()

        # Frame noir par-dessus tout
        frame_noir = tk.Frame(self.root, bg="black")
        frame_noir.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame_noir.tkraise()

        stipples_out = ["gray75", "gray50", "gray25", "gray12", ""]
        stipples_in  = ["", "gray12", "gray25", "gray50", "gray75"]

        def fade_out(etape):
            if etape >= len(stipples_out):
                # Écran noir complet — détruire l'ancien écran
                ecran_sortant.destroy()
                self.ecran_actuel = nouvel_ecran
                fade_in(0)
                return
            # Mettre à jour le frame noir avec stipple via canvas interne
            for w in frame_noir.winfo_children():
                w.destroy()
            c = tk.Canvas(frame_noir, bg="black", highlightthickness=0)
            c.place(relx=0, rely=0, relwidth=1, relheight=1)
            c.update_idletasks()
            c.create_rectangle(
                0, 0,
                self.root.winfo_width(),
                self.root.winfo_height(),
                fill="black",
                stipple=stipples_out[etape],
                outline=""
            )
            self.root.after(delai, lambda: fade_out(etape + 1))

        def fade_in(etape):
            if etape >= len(stipples_in):
                frame_noir.destroy()
                nouvel_ecran.place_forget()
                nouvel_ecran.pack(fill="both", expand=True)
                return
            for w in frame_noir.winfo_children():
                w.destroy()
            c = tk.Canvas(frame_noir, bg="black", highlightthickness=0)
            c.place(relx=0, rely=0, relwidth=1, relheight=1)
            c.update_idletasks()
            c.create_rectangle(
                0, 0,
                self.root.winfo_width(),
                self.root.winfo_height(),
                fill="black",
                stipple=stipples_in[etape],
                outline=""
            )
            self.root.after(delai, lambda: fade_in(etape + 1))

        fade_out(0)
        self.ecran_actuel = nouvel_ecran