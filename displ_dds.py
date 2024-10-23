import os
import subprocess
from win32com.client import Dispatch
from PIL import Image
import numpy as np
import shutil
import cv2
import pyautogui
import pygetwindow as gw
import threading
import time

titre_fenetre = "NVIDIA DDS Read Properties"
app = Dispatch("Photoshop.Application")
app.Visible = False

#Fermeture auto fenetre NVIDIA
def detecter_fenetre():
    while True:
        # Cherche les fenêtres ouvertes avec le titre donné
        fenetres = gw.getWindowsWithTitle(titre_fenetre)

        if fenetres:
            # Si une fenêtre correspond au titre, appuyer sur 'Entrée'
            pyautogui.press('enter')
            # Optionnel : sortir de la boucle si tu veux qu'il s'arrête après la première détection
            break



#Note pour le prochain dev, des trucs inutiles sont à virer
def is_displ_file(filename):
    return filename.endswith('_displ.dds')

def extract_alpha_to_graysclae(output_image_path):
    # Charger l'image TIFF
    img = cv2.imread(output_image_path, cv2.IMREAD_UNCHANGED)

    # Vérifier si l'image a un canal alpha (quatre canaux)
    if img.shape[2] == 4:
        # Extraire le canal alpha
        alpha_channel = img[:, :, 3]
        
        # Créer une nouvelle image RGB (noire par défaut)
        new_image = np.zeros((img.shape[0], img.shape[1], 1), dtype=np.uint8)

        # Remplir l'image RGB avec le canal alpha
        # Utiliser le canal alpha comme masque de transparence
        new_image[:, :, 0] = alpha_channel
        
        # Enregistrer l'image résultante
        cv2.imwrite(output_image_path, new_image)
        print(f"L'image avec le canal alpha a été enregistrée sous : {output_image_path}")
    else:
        print("L'image ne contient pas de canal alpha.")
        
    subprocess.run([r"C:\Users\drigu\Desktop\C3_CE5.7\Tools\rc\rc.exe", output_image_path.replace('dds', 'tif'),  r"/userdialog=0", r"/skipmissing=1", r"/refresh=1", "\powof2=1", "\mipgentype=average", "/pixelformat=BC4", "/mipmaps=1", "/colorspace=linear,linear"])


def process_dds_file(filepath):
    
    outfile1 = filepath.replace('dds', 'tif')
    
    # Créer et démarrer le thread
    thread_fenetre = threading.Thread(target=detecter_fenetre)
    thread_fenetre.start()
   
    app.Open(os.path.abspath(filepath))
    doc = app.Application.ActiveDocument
    
    if doc.Channels.Count > 3:  # RGB + Alpha = 4 channels
        print("Alpha channel found")
    else:
        print("No alpha channel found")


    # Set TIFF save options
    tif_options = Dispatch("Photoshop.TiffSaveOptions")
    tif_options.ImageCompression = 1  # None
    tif_options.AlphaChannels = True  # Grayscale does not use alpha channels

    # Save the resized image as a TIFF
    doc.SaveAs(os.path.abspath(outfile1), tif_options, AsCopy=True)

    doc.Close(Saving=2)  # 2 = psDoNotSaveChanges
    
    thread_fenetre.join() 
    
    #old
    old_folder = os.path.join(os.path.dirname(filepath), 'old')
    if not os.path.exists(old_folder):
        os.makedirs(old_folder)
    old_filepath = os.path.join(old_folder, os.path.basename(filepath))
    try:
        shutil.move(filepath, old_filepath)
        print(f"Fichier original déplacé vers {old_filepath}")
    except Exception as e:
        print(f"Erreur lors du déplacement du fichier {filepath} vers {old_folder}: {e}")
        return
        
    extract_alpha_to_graysclae(outfile1)
    
    

def process_all_displ_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if "old" in filepath:
                continue
            if is_displ_file(file):
                print(f"Traitement du fichier : {filepath}")
                process_dds_file(filepath)

process_all_displ_files('.')
app.Quit() 

