"""
Moteur de face swap utilisant InsightFace + GFPGAN
Usage : python faceswap.py -s source.jpg -t template.jpg -o output.jpg
"""

import sys
import cv2
import insightface
import numpy as np
import argparse
import os

def ameliorer_visage(image, chemin_model):
    """Améliore la qualité du visage avec GFPGAN"""
    try:
        from gfpgan import GFPGANer
        restorer = GFPGANer(
            model_path=chemin_model,
            upscale=1,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=None
        )
        _, _, output = restorer.enhance(
            image,
            has_aligned=False,
            only_center_face=False,
            paste_back=True
        )
        return output
    except Exception as e:
        print(f"GFPGAN non disponible, on continue sans : {e}")
        return image  # retourne l'image non améliorée si erreur

def swap_face(source_path, target_path, output_path, model_path, gfpgan_path):
    # Charger les images
    source_img = cv2.imread(source_path)
    target_img = cv2.imread(target_path)

    if source_img is None:
        print(f"ERREUR: impossible de lire {source_path}")
        sys.exit(1)
    if target_img is None:
        print(f"ERREUR: impossible de lire {target_path}")
        sys.exit(1)

    # Initialiser le détecteur de visages
    app = insightface.app.FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=0, det_size=(640, 640))

    # Charger le modèle de swap
    swapper = insightface.model_zoo.get_model(model_path)

    # Détecter les visages
    source_faces = app.get(source_img)
    target_faces = app.get(target_img)

    if not source_faces:
        print("ERREUR_VISAGE_SOURCE: aucun visage détecté dans la photo source", flush=True)
        sys.exit(1)
    if not target_faces:
        print("ERREUR_VISAGE_TEMPLATE: aucun visage détecté dans le template", flush=True)
        sys.exit(1)
        
    # Prendre le visage source le plus grand (le plus proche de la caméra)
    source_face = max(source_faces, 
                      key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))

    # Swap sur tous les visages du template
    result = target_img.copy()
    for target_face in target_faces:
        result = swapper.get(result, target_face, source_face, paste_back=True)

    # Amélioration GFPGAN
    if os.path.exists(gfpgan_path):
        print("Amélioration GFPGAN en cours...")
        result = ameliorer_visage(result, gfpgan_path)
        print("GFPGAN terminé")
    else:
        print(f"Modèle GFPGAN non trouvé à {gfpgan_path}, on passe sans")

    # Sauvegarder
    cv2.imwrite(output_path, result)
    print(f"OK: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', required=True)
    parser.add_argument('-t', '--target', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-m', '--model', default='C:/Open-FaceSwapping/models/inswapper_128.onnx')
    parser.add_argument('-g', '--gfpgan', default='C:/Open-FaceSwapping/models/GFPGANv1.4.pth')
    args = parser.parse_args()

    swap_face(args.source, args.target, args.output, args.model, args.gfpgan)