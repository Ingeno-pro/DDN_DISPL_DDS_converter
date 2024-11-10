import os
import cv2
import shutil
import subprocess
from PIL import Image
import numpy as np

def is_ddn_file(filename):
    return filename.endswith('_ddn.dds') or filename.endswith('_DDN.dds')

def process_dds_file(filepath):
    
    #Load the Image
    try:
        image = Image.open(filepath)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {filepath}: {e}")
        return
    
    #Check if the image is RGB
    if image.mode != 'RGB':
        print(f"Le fichier {filepath} n'est pas en mode RGB.")
        return
    
    # Image into matrix
    image_data = np.array(image)
    
    #buffer to make a save of the green channel
    image_data_buff2 = np.array(image)
    
    #get the red channel
    red_channel = image_data[:, :, 0]  
    
    #copy the green channel from the buffer
    green_channel = image_data_buff2[:, :, 1] 
    
    #swap both channel
    image_data[:, :, 1] = red_channel    # Le canal vert devient le rouge
    image_data[:, :, 0] = green_channel  # Le canal rouge devient le vert
    
    # Invert the blue channel 
    blue_channel = image_data[:, :, 2]  
    image_data[:, :, 2] = np.where(blue_channel == 0, 255, blue_channel)  
    
    
    
    # Save the image by creating a new image
    new_image = Image.fromarray(image_data, mode='RGB')
    
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
    
    output_filepath = filepath
    try:
        new_image.save(output_filepath, format='DDS')
        new_image.save(output_filepath.replace('dds', 'tif'), format='TIFF')
        new_image.close()
        print(f"Image traitée et sauvegardée dans {output_filepath}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du fichier {output_filepath}: {e}")
    
    subprocess.run([r"C:\Users\drigu\Desktop\C3_CE5.7\Tools\rc\rc.exe", output_filepath.replace('dds', 'tif'),  r"/userdialog=0", r"/mipmaps=1", r"/preset=game", r"/skipmissing=1", r"/refresh=1"])
    #subprocess.run(["rc.exe", "-f", "BC5_SNORM", output_filepath, "-y"]);

def process_all_ddn_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if is_ddn_file(file):
                filepath = os.path.join(root, file)
                print(f"Traitement du fichier : {filepath}")
                process_dds_file(filepath)

process_all_ddn_files('.')

