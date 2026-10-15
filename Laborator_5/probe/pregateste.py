"""
Script de pregatire pentru Laboratorul 5 (Forensics si Steganografie).

Genereaza, in folderul probe/, toate fisierele-tinta pe care le vei analiza
cu decode.py / forensics.py / stego.py:

    probe/mesaj.txt     - un sir codat in mai multe straturi
    probe/xor.bin       - text criptat cu XOR pe un octet
    probe/hashuri.txt   - un hash de parola, de spart prin dictionar
    probe/wordlist.txt  - dictionarul folosit la spargerea hash-ului
    probe/foto.jpg      - poza cu EXIF si coordonate GPS
    probe/ascuns.png    - poza cu o arhiva ZIP lipita la coada
    probe/challenge.bin - (bonus) un strat de encoding peste un XOR

Ruleaza o singura data, din radacina Laborator_5:
    python probe/pregateste.py

Are nevoie de: pip install pillow piexif
"""

import base64
import hashlib
import os
import random
import zipfile
from io import BytesIO

import piexif
from PIL import Image

PROBE = "probe"
os.makedirs(PROBE, exist_ok=True)

random.seed(2026)  # reproducibil: aceleasi tinte de fiecare data cand rulezi


def cale(nume):
    return os.path.join(PROBE, nume)


# ---------------------------------------------------------------------------
# mesaj.txt - sir codat pe doua straturi: text -> hex -> base64
# ---------------------------------------------------------------------------
def fa_mesaj_straturi():
    text = "FLAG{laborator_cinci_forensics_si_stego}"
    strat_hex = text.encode().hex()
    strat_b64 = base64.b64encode(strat_hex.encode()).decode()
    with open(cale("mesaj.txt"), "w") as f:
        f.write(strat_b64)


# ---------------------------------------------------------------------------
# xor.bin - text criptat cu o cheie de un singur octet
# ---------------------------------------------------------------------------
def fa_xor():
    text = b"Parola temporara pentru arhiva este: Sch1mbaMa!2026 - cauta cheia prin forta bruta."
    # Nota despre alegerea cheii: testul "citibil = toti octetii in 32..126" e o
    # aproximare; pentru text ASCII normal exista mereu un grup de chei vecine
    # care produc, din intamplare, tot octeti "citibili". Am verificat empiric
    # ca aceasta pereche text+cheie face ca brute-force-ul din decode.py (care
    # se opreste la PRIMA cheie potrivita, testand 0,1,2,...) sa gaseasca exact
    # cheia corecta, nu un fals-pozitiv de dinaintea ei.
    cheie = 0x20
    criptat = bytes(b ^ cheie for b in text)
    with open(cale("xor.bin"), "wb") as f:
        f.write(criptat)


# ---------------------------------------------------------------------------
# hashuri.txt + wordlist.txt - o parola de spart prin dictionar
# ---------------------------------------------------------------------------
def fa_hashuri():
    parola = "parola123"
    md5 = hashlib.md5(parola.encode()).hexdigest()
    with open(cale("hashuri.txt"), "w") as f:
        f.write(md5 + "\n")

    cuvinte = [
        "123456", "parola", "parola123", "admin", "qwerty", "password",
        "laborator", "student", "chisinau", "moldova", "bunicuta",
        "iubire1", "welcome1", "forensics",
    ]
    random.shuffle(cuvinte)
    with open(cale("wordlist.txt"), "w", encoding="latin1") as f:
        f.write("\n".join(cuvinte) + "\n")


# ---------------------------------------------------------------------------
# foto.jpg - poza cu EXIF si GPS (undeva in Chisinau)
# ---------------------------------------------------------------------------
def grade_in_rational(valoare_zecimala):
    """GPS EXIF vrea (grade, minute, secunde), fiecare ca fractie (num, den)."""
    grade = int(valoare_zecimala)
    minute_zecimale = (valoare_zecimala - grade) * 60
    minute = int(minute_zecimale)
    secunde = (minute_zecimale - minute) * 60
    return [(grade, 1), (minute, 1), (int(secunde * 100), 100)]


def fa_foto_cu_exif():
    img = Image.new("RGB", (640, 480), color=(90, 130, 170))
    buf = BytesIO()
    img.save(buf, format="jpeg")
    buf.seek(0)

    lat, lon = 47.0245, 28.8324  # Chisinau

    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: "N",
        piexif.GPSIFD.GPSLatitude: grade_in_rational(lat),
        piexif.GPSIFD.GPSLongitudeRef: "E",
        piexif.GPSIFD.GPSLongitude: grade_in_rational(lon),
    }
    zeroth_ifd = {
        piexif.ImageIFD.Make: "LaboratorForensics",
        piexif.ImageIFD.Model: "Camera-Simulata",
    }
    exif_bytes = piexif.dump({"0th": zeroth_ifd, "GPS": gps_ifd})

    with open(cale("foto.jpg"), "wb") as f:
        f.write(buf.getvalue())
    piexif.insert(exif_bytes, cale("foto.jpg"))


# ---------------------------------------------------------------------------
# ascuns.png - poza normala + arhiva ZIP lipita la coada (file carving)
# ---------------------------------------------------------------------------
def fa_poza_cu_arhiva_ascunsa():
    img = Image.new("RGB", (300, 200), color=(40, 180, 100))
    img.save(cale("ascuns.png"))

    buf_zip = BytesIO()
    with zipfile.ZipFile(buf_zip, "w") as z:
        z.writestr("secret.txt", "Daca citesti asta, ai gasit arhiva ascunsa la coada pozei!")

    with open(cale("ascuns.png"), "ab") as f:
        f.write(buf_zip.getvalue())


# ---------------------------------------------------------------------------
# challenge.bin (bonus) - un strat de encoding peste un XOR, cu hash de verificat
# ---------------------------------------------------------------------------
def fa_challenge_bonus():
    text = b"BONUS{incodare_peste_xor_cu_verificare_md5}"
    cheie = 0x5A
    criptat = bytes(b ^ cheie for b in text)
    continut = base64.b64encode(criptat)

    with open(cale("challenge.bin"), "wb") as f:
        f.write(continut)

    with open(cale("challenge_hash.txt"), "w") as f:
        f.write(hashlib.sha256(text).hexdigest() + "\n")


def main():
    fa_mesaj_straturi()
    fa_xor()
    fa_hashuri()
    fa_foto_cu_exif()
    fa_poza_cu_arhiva_ascunsa()
    fa_challenge_bonus()
    print("Gata! Fisierele de proba sunt in probe/:")
    for nume in sorted(os.listdir(PROBE)):
        print(" -", nume)


if __name__ == "__main__":
    main()