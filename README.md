# 🎭 Open-FaceSwapping

Application Python pour borne photo événementielle avec face-swapping par intelligence artificielle.
L'utilisateur choisit un personnage, prend sa photo via webcam, et reçoit un QR code pour télécharger sa photo transformée.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## ✨ Fonctionnalités

- 🖥️ Interface plein écran, navigation par écrans enchaînés avec transitions animées
- 📋 Écran de consentement RGPD avec checkbox obligatoire
- 🎭 Choix du personnage cible parmi des templates personnalisables
- 📸 Capture webcam avec compte à rebours et prévisualisation
- 🤖 Face swap par IA via **InsightFace** (inswapper_128)
- ✨ Amélioration de la qualité via **GFPGAN** (optionnel)
- ☁️ Upload automatique sur serveur distant (PHP)
- 📱 QR code pour téléchargement sur smartphone
- 🎮 Support boutons physiques arcade (clavier USB)
- ⚙️ 100% configurable via `config.json`
- 🧹 Nettoyage automatique des photos de plus de 24h

---

## 📁 Structure du projet

```
faceswap-borne/
├── config.json              ← Toute la configuration
├── main.py                  ← Point d'entrée
├── app.py                   ← Navigation entre écrans
├── faceswap.py              ← Moteur IA (InsightFace + GFPGAN)
├── lancer.bat               ← Lance l'application
├── install.bat              ← Installe les dépendances
├── screens/
│   ├── base.py              ← Classe parente des écrans
│   ├── accueil.py           ← Écran d'accueil
│   ├── disclaimer.py        ← Consentement RGPD
│   ├── choix_template.py    ← Choix du personnage
│   ├── webcam.py            ← Capture photo
│   ├── traitement.py        ← IA + upload
│   └── resultat.py          ← QR code résultat
├── assets/
│   ├── templates/           ← Mettre vos images cibles ici (.jpg/.png)
│   ├── logo.png             ← Logo de votre borne (optionnel)
│   └── background.jpg       ← Fond d'écran (optionnel)
└── output/                  ← Généré automatiquement (ignoré par git)
```

---

## 🚀 Installation (étape par étape)

### 1. Prérequis

- **Python 3.10.x** — [Télécharger ici](https://www.python.org/downloads/release/python-3100/)
  - ⚠️ Cocher **"Add Python to PATH"** lors de l'installation
- **Git** — [Télécharger ici](https://git-scm.com/download/win)
- Webcam USB ou intégrée
- 8 Go de RAM minimum
- 5 Go d'espace disque libre (modèles IA)

### 2. Cloner le dépôt

```bash
git clone https://github.com/VOTRE_USERNAME/faceswap-borne.git
cd faceswap-borne
```

### 3. Installer les dépendances

Double-cliquez sur `install.bat` ou tapez dans une invite de commandes :

```bash
pip install opencv-python pillow "qrcode[pil]" requests insightface onnxruntime numpy gfpgan
```

> ⏳ L'installation peut prendre 5-15 minutes selon votre connexion.

### 4. Télécharger les modèles IA

> ⚠️ Les modèles ne sont pas inclus dans le dépôt (trop lourds). À télécharger manuellement.

#### Modèle InsightFace — **obligatoire**

Télécharger `inswapper_128.onnx` :
```
https://huggingface.co/deepinsight/inswapper/resolve/main/inswapper_128.onnx
```
→ Placer dans `C:\Open-FaceSwapping\models\inswapper_128.onnx`

#### Modèle GFPGAN — *optionnel mais recommandé*

Télécharger `GFPGANv1.4.pth` :
```
https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth
```
→ Placer dans `C:\Open-FaceSwapping\models\GFPGANv1.4.pth`

> 💡 Sans GFPGAN, le face swap fonctionne mais sans amélioration de qualité.

### 5. Ajouter vos templates

Copiez vos images JPG/PNG dans `assets/templates/`.
Le nom du fichier devient le nom affiché (ex: `iron_man.jpg` → "Iron Man").

### 6. Configurer `config.json`

Paramètres importants à modifier :

#### Chemins des modèles IA
```json
"traitement": {
    "roop_script_path": "C:/Open-FaceSwapping/Faceswap-borne/faceswap.py",
    "roop_python_path": "python",
    "roop_model": "C:/Open-FaceSwapping/models/inswapper_128.onnx",
    "roop_gfpgan": "C:/Open-FaceSwapping/models/GFPGANv1.4.pth"
}
```

#### Serveur d'upload
```json
"upload": {
    "actif": true,
    "url": "https://votre-serveur.com/upload.php",
    "raccourcir_url": false
}
```

#### URL du QR Code
```json
"resultat": {
    "texte_url_base": "https://votre-serveur.com/photos/"
}
```

### 7. Mode debug (test sans IA ni serveur)
```json
"debug": {
    "simuler_roop": true,
    "simuler_upload": true
}
```

### 8. Lancer l'application

Double-cliquez sur `lancer.bat` ou tapez :
```bash
python main.py
```

---

## ⚙️ Configuration détaillée

### Apparence
```json
"app": {
    "couleur_fond": "#0d0d0d",
    "couleur_accent": "#e91e8c",
    "couleur_texte": "#ffffff",
    "couleur_bouton": "#e91e8c",
    "police_titre": "Arial 48 bold",
    "police_bouton": "Arial 28 bold",
    "plein_ecran": true
}
```

### Webcam
```json
"webcam": {
    "index_camera": 0,
    "compte_a_rebours": 5,
    "nb_essais_max": 3,
    "miroir": true
}
```

### Messages d'erreur personnalisables
```json
"messages_erreur": {
    "visage_non_detecte": "😕 Aucun visage détecté...\nRepositionnez-vous et réessayez !",
    "template_non_detecte": "😕 Problème avec le personnage choisi.",
    "timeout": "⏱️ Traitement trop long, réessayez.",
    "erreur_generique": "😕 Une erreur est survenue, réessayez."
}
```

### Boutons physiques arcade
```json
"boutons_physiques": {
    "actif": true,
    "annuler": "<BackSpace>",
    "precedent": "<Left>",
    "suivant": "<Right>",
    "valider": "<Return>"
}
```

---

## 🎮 Boutons physiques arcade

Compatible avec tout clavier USB ou encodeur arcade Zero Delay.

**Matériel recommandé (~15-20€) :**
- Encodeur USB Zero Delay (~3€ sur AliExpress)
- 4 boutons arcade LED 30mm (~2€ pièce)
- Fils Dupont pour la connexion

| Bouton | Couleur | Touche | Action |
|--------|---------|--------|--------|
| 1 | 🔴 Rouge | BackSpace | Annuler / Retour |
| 2 | 🟡 Jaune | ← Gauche | Précédent |
| 3 | 🔵 Bleu | → Droite | Suivant |
| 4 | 🟢 Vert | Entrée | Valider |

---

## 🖥️ Serveur PHP (upload.php)

```php
<?php
$target_dir = "photos/";
if (!file_exists($target_dir)) mkdir($target_dir, 0775, true);

if ($_FILES["file"]["error"] == UPLOAD_ERR_OK) {
    $filename = basename($_FILES["file"]["name"]);
    if (move_uploaded_file($_FILES["file"]["tmp_name"], $target_dir . $filename)) {
        echo "https://votre-serveur.com/photos/" . urlencode($filename);
    } else {
        http_response_code(500);
        echo "Upload failed";
    }
} else {
    http_response_code(400);
    echo "No file uploaded";
}
?>
```

---

## ⌨️ Raccourcis clavier (développement)

| Touche | Action |
|--------|--------|
| `Echap` | Basculer plein écran / fenêtre |
| `F1` | Quitter l'application |

---

## 🔧 Problèmes courants

**La caméra ne s'ouvre pas**
→ Changez `"index_camera"` de 0 à 1 ou 2 dans `config.json`

**Aucun visage détecté**
→ Assurez-vous d'être bien face à la caméra, dans une pièce éclairée
→ Le modèle fonctionne uniquement sur des visages humains réels

**L'upload échoue**
→ Activez `"simuler_upload": true` pour tester sans serveur
→ Vérifiez l'URL dans `config.json`

**Erreur PIL/Pillow**
→ Relancez `pip install pillow --upgrade`

**Modèle introuvable**
→ Vérifiez les chemins dans `config.json`
→ Vérifiez que les fichiers `.onnx` et `.pth` sont bien téléchargés

---

## 🚀 Mise à jour sur le PC de production

```bash
cd C:\Open-FaceSwapping\Faceswap-borne
git pull origin main
```

Les modèles IA, les templates et les photos ne sont jamais écrasés par `git pull` (ignorés par `.gitignore`).

---

## 📝 License

MIT License — libre d'utilisation, modification et distribution.
