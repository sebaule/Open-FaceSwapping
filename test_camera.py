import cv2
import numpy as np

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Ignorer les premières frames
for _ in range(10):
    cap.read()

ret, frame = cap.read()
if ret:
    print(f"Taille frame : {frame.shape}")  # hauteur x largeur x canaux
    
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(float)
    moy_col = gris.mean(axis=0)
    col_min = int(moy_col.argmin())
    print(f"Colonne la plus sombre : {col_min}")
    print(f"Luminosité à cette colonne : {moy_col[col_min]:.1f}")
    print(f"Luminosité moyenne : {moy_col.mean():.1f}")
    
    # Sauvegarder la frame brute pour voir
    cv2.imwrite("test_frame.jpg", frame)
    print("Frame sauvegardée dans test_frame.jpg")
    
    # Afficher 5 secondes
    cv2.imshow("Test camera - appuie Q pour quitter", frame)
    cv2.waitKey(5000)

cap.release()
cv2.destroyAllWindows()