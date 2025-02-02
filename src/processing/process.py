import os
import shutil
from PIL import Image
import numpy as np
from src.processing.process_fields import process_fields
from src.processing.filtre import capitalize_words

reader = None  # Inițializăm variabila reader

def set_reader(ocr_reader):
    global reader
    reader = ocr_reader

# Funcția pentru procesarea unei zone
def proceseaza_zona(coord, idx, image):
    zona_decupata = image.crop(coord)  # Decupează zona
    zona_decupata = zona_decupata.resize((zona_decupata.width * 4, zona_decupata.height * 4))  # Mărire imagine
    zona_np = np.array(zona_decupata)  # Convertește în array NumPy
    rezultate = reader.readtext(zona_np)  # OCR
    text = " ".join([rezultat[1] for rezultat in rezultate])  # Extrage textul
    print(f"OCR text pentru zona {idx}: {text}")  # Afișează textul OCR pentru debug
    return text

# Funcția pentru procesarea fișierelor
def proceseaza_fisier(image_path, output_folder, coordonate):
    image = Image.open(image_path)  # Încarcă imaginea
    print(f"Procesăm fișierul: {image_path}")  # Debug: Afișăm numele fișierului procesat

    # Inițializăm variabilele pentru fiecare câmp
    strada, numar, localitate, judet, bloc, scara, etaj, apartament, cp, prenume, nume, cnp_total, email, phone, doiani = [""] * 15
    initiala_tatalui = ""
    folder_localitate_sec = ""
    temp_folder_localitate_mare = ""
    temp_folder_localitate_med = ""
    temp_folder_localitate_mic = ""
    folder_localitate = ""

    # Parcurgem coordonatele și procesăm fiecare zonă
    for idx, coord in enumerate(coordonate):
        text_initial = proceseaza_zona(coord, idx, image)
        print(f"Text inițial pentru zona {idx}: {text_initial}")  # Debug: Afișăm textul inițial
        temp_prenume, temp_nume, temp_initiala_tatalui, temp_strada, temp_numar, temp_cnp_total, temp_email, temp_judet, temp_localitate, temp_cp, temp_bloc, temp_scara, temp_etaj, temp_apartament, temp_phone, temp_doiani, temp_folder_localitate_mic, temp_folder_localitate_med, temp_folder_localitate_mare = process_fields(text_initial, idx, False)  # debug_switch este True pentru debug
        # Atribuire valorilor returnate la variabilele finale
        if temp_prenume:
            prenume = temp_prenume
        if temp_nume:
            nume = temp_nume
        if temp_initiala_tatalui:
            initiala_tatalui = temp_initiala_tatalui
        if temp_strada:
            strada = temp_strada
        if temp_numar:
            numar = temp_numar
        if temp_cnp_total:
            cnp_total = temp_cnp_total
        if temp_email:
            email = temp_email
        if temp_judet:
            judet = temp_judet
        if temp_localitate:
            localitate = temp_localitate
        if temp_cp:
            cp = temp_cp
        if temp_bloc:
            bloc = temp_bloc
        if temp_scara:
            scara = temp_scara
        if temp_etaj:
            etaj = temp_etaj
        if temp_apartament:
            apartament = temp_apartament
        if temp_phone:
            phone = temp_phone
        if temp_doiani:
            doiani = temp_doiani
        if temp_folder_localitate_mic:
            folder_localitate_mic = temp_folder_localitate_mic
        if temp_folder_localitate_med:
            folder_localitate_med = temp_folder_localitate_med
        if temp_folder_localitate_mare:
            folder_localitate_mare = temp_folder_localitate_mare
        # Debug: Afișăm valorile actualizate după fiecare iterație
        print(f"Variabile după process_fields: prenume={prenume}, nume={nume}, strada={strada}, etc.")  # Debug

    # Generăm adresa
    adresa = f"Str. {strada} NR. {numar} LOC. {localitate} JUD. {judet}"
    if bloc:
        adresa += f" Bl. {bloc}"
    if scara:
        adresa += f" Sc. {scara}"
    if etaj:
        adresa += f" Et. {etaj}"
    if apartament:
        adresa += f" Ap. {apartament}"
    if cp:
        adresa += f" CP. {cp}"

    # Debug: Afișăm adresa generată
    print(f"Rezultate procesare: {nume} {prenume}, {email}, {phone}, {adresa}")  # Debug: Afișăm rezultatele procesării

    # Nume fișier nou
    nume_fisier = os.path.basename(image_path)
    nume_fisier_nou = f"{nume} {prenume}.jpg"

    # Creează folderul pentru localitate
    folder_localitate = os.path.join(output_folder, folder_localitate_mic)
    print(f"Creăm folderul: {folder_localitate}")  # Debug
    if not os.path.exists(folder_localitate):
        os.makedirs(folder_localitate)

    # Mutăm și redenumim imaginea
    noua_cale_imagine = os.path.join(folder_localitate, nume_fisier_nou)
    print(f"Mutăm imaginea la: {noua_cale_imagine}")  # Debug
    shutil.move(image_path, noua_cale_imagine)

    # Debug: Afișăm calea imaginii mutate
    print(f"Imaginea {nume_fisier_nou} a fost mutată și redenumită în folderul {folder_localitate}")

    # Creează fișierul text
    fisier_txt = os.path.join(folder_localitate, f"{nume} {prenume}.txt")
    print(f"Creăm fișierul text la: {fisier_txt}")  # Debug
    with open(fisier_txt, 'w', encoding='utf-8') as f:
        f.write(f"{nume}\n{initiala_tatalui}\n{prenume}\n{cnp_total}\n{adresa}\n{email}\n{phone}\n{doiani}")

    # Debug: Afișăm calea fișierului text creat
    print(f"Fișierul text {fisier_txt} a fost creat.")

    # Mută folder_localitate_mic în folder_localitate_med
    folder_localitate_mic_path = os.path.join(output_folder, folder_localitate_mic)
    folder_localitate_med_path = os.path.join(output_folder, folder_localitate_med)
    print(f"Mutăm {folder_localitate_mic_path} în {folder_localitate_med_path}")  # Debug
    if not os.path.exists(folder_localitate_med_path):
        os.makedirs(folder_localitate_med_path, exist_ok=True)
    if os.path.exists(folder_localitate_mic_path) and folder_localitate_mic_path != folder_localitate_med_path:
        move_folder(folder_localitate_mic_path, folder_localitate_med_path)
        print(f"Folderul {folder_localitate_mic_path} a fost mutat în {folder_localitate_med_path}")

    # Mută folder_localitate_med în folder_localitate_mare
    folder_localitate_mare_path = os.path.join(output_folder, folder_localitate_mare)
    print(f"Mutăm {folder_localitate_med_path} în {folder_localitate_mare_path}")  # Debug
    if not os.path.exists(folder_localitate_mare_path):
        os.makedirs(folder_localitate_mare_path, exist_ok=True)
    if os.path.exists(folder_localitate_med_path) and folder_localitate_med_path != folder_localitate_mare_path:
        move_folder(folder_localitate_med_path, folder_localitate_mare_path)
        print(f"Folderul {folder_localitate_med_path} a fost mutat în {folder_localitate_mare_path}")
        
def move_contents(src, dest):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            if not os.path.exists(d):
                os.makedirs(d)
            move_contents(s, d)
        else:
            if os.path.exists(d):
                base, extension = os.path.splitext(d)
                new_d = f"{base}{extension}"
                d = new_d
            shutil.move(s, d)

def move_folder(src, dest):
    if os.path.exists(dest):
        print("e pe if")
        complete_dest = os.path.join(dest, os.path.basename(src))
        print("asta1")
        print(src)
        print(complete_dest)
        if os.path.exists(complete_dest):
            print("if1")
            move_contents(src, complete_dest)
            print("if1.1")
        else:
            print("if2")
            os.makedirs(complete_dest)
            shutil.move(src, complete_dest)  # Mută folderul sursă în destinație
        print("asta2")
    else:
        print("e pe else")
        os.makedirs(dest)
        shutil.move(src, dest)