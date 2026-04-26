@echo off
echo ====================================
echo Installation des dependances
echo Face Swap Borne
echo ====================================
echo.

echo [1/7] opencv-python...
pip install opencv-python

echo.
echo [2/7] pillow...
pip install pillow

echo.
echo [3/7] qrcode...
pip install "qrcode[pil]"

echo.
echo [4/7] requests...
pip install requests

echo.
echo [5/7] insightface (moteur face swap)...
pip install insightface

echo.
echo [6/7] onnxruntime (moteur IA)...
pip install onnxruntime

echo.
echo [7/7] gfpgan (amelioration qualite - peut prendre du temps)...
pip install gfpgan

echo.
echo ====================================











































echo Installation terminee !
echo.
echo IMPORTANT : Telechargez les modeles IA manuellement :
echo.
echo 1) inswapper_128.onnx (obligatoire) :
echo    https://huggingface.co/deepinsight/inswapper/resolve/main/inswapper_128.onnx
echo    -> Placer dans C:\Open-FaceSwapping\models\inswapper_128.onnx
echo.
echo 2) GFPGANv1.4.pth (optionnel, ameliore la qualite) :
echo    https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth
echo    -> Placer dans C:\Open-FaceSwapping\models\GFPGANv1.4.pth
echo.
echo Pour lancer la borne : python main.py
echo ====================================
pause
