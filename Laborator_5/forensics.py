"""
Forensics pe fisiere: tipul real, text ascuns, metadate EXIF/GPS, carving.

Rulare:
    python forensics.py tip probe/foto.jpg
    python forensics.py strings probe/ascuns.png
    python forensics.py exif probe/foto.jpg
    python forensics.py carve probe/ascuns.png
"""

import argparse
import re

from PIL import Image
from PIL.ExifTags import TAGS


# ---------------------------------------------------------------------------
# B1 - magic bytes: tipul real al fisierului, nu extensia din nume
# ---------------------------------------------------------------------------
SEMNATURI = {
    b"%PDF": "pdf",
    b"\x89PNG": "png",
    b"\xff\xd8": "jpeg",
    b"PK\x03\x04": "zip/docx",
}


def tip_real(cale):
    """Citeste primii octeti ai fisierului si ii compara cu semnaturile
    cunoscute. Daca nu recunoaste nimic, intoarce hexul brut (ca sa poti
    cauta manual semnatura)."""
    cap = open(cale, "rb").read(8)
    for semnatura, nume in SEMNATURI.items():
        if cap.startswith(semnatura):
            return nume
    return cap.hex()


# ---------------------------------------------------------------------------
# B2 - strings: secventele de caractere imprimabile dintr-un binar
# ---------------------------------------------------------------------------
def extrage_strings(date, lungime_minima=4):
    """Gaseste secvente de caractere ASCII tiparibile (0x20..0x7e), de cel
    putin `lungime_minima` octeti. Util pentru a gasi cai, mesaje sau nume
    de fisiere ascunse intr-un binar (poza, executabil etc.)."""
    model = rb"[ -~]{%d,}" % lungime_minima
    return [m.decode() for m in re.findall(model, date)]


# ---------------------------------------------------------------------------
# B3 - EXIF si GPS dintr-o poza
# ---------------------------------------------------------------------------
def _grade_zecimale(valoare, emisfera):
    """EXIF da coordonatele ca ((grade), (minute), (secunde)); emisfera
    S sau W inseamna valoare negativa."""
    grade, minute, secunde = valoare
    zecimal = float(grade) + float(minute) / 60 + float(secunde) / 3600
    if emisfera in ("S", "W"):
        zecimal = -zecimal
    return zecimal


def citeste_exif(cale):
    """Intoarce dictionarul EXIF complet (cu nume de taguri in loc de id-uri
    numerice) plus, daca exista, (latitudine, longitudine) in grade zecimale."""
    exif = Image.open(cale)._getexif() or {}
    exif_nume = {TAGS.get(id, id): val for id, val in exif.items()}

    gps_info = exif.get(34853)  # tagul GPSInfo
    coordonate = None
    if gps_info:
        lat = _grade_zecimale(gps_info[2], gps_info[1])   # GPSLatitude, GPSLatitudeRef
        lon = _grade_zecimale(gps_info[4], gps_info[3])   # GPSLongitude, GPSLongitudeRef
        coordonate = (lat, lon)

    return exif_nume, coordonate


# ---------------------------------------------------------------------------
# B4 - file carving: extrage un fisier ascuns, lipit la coada altuia
# ---------------------------------------------------------------------------
def carve(cale, semnatura=b"PK\x03\x04", iesire="gasit.zip"):
    """Cauta semnatura (implicit cea de ZIP) in interiorul fisierului si, daca
    o gaseste, salveaza tot ce urmeaza de la acel octet intr-un fisier nou."""
    date = open(cale, "rb").read()
    i = date.find(semnatura)
    if i == -1:
        return None
    with open(iesire, "wb") as f:
        f.write(date[i:])
    return i, iesire


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Forensics pe fisiere")
    sub = p.add_subparsers(dest="comanda", required=True)

    p_tip = sub.add_parser("tip", help="afiseaza tipul real (magic bytes)")
    p_tip.add_argument("cale")

    p_str = sub.add_parser("strings", help="afiseaza textul citibil dintr-un binar")
    p_str.add_argument("cale")

    p_exif = sub.add_parser("exif", help="afiseaza EXIF si GPS dintr-o poza")
    p_exif.add_argument("cale")

    p_carve = sub.add_parser("carve", help="extrage un fisier ascuns la coada")
    p_carve.add_argument("cale")
    p_carve.add_argument("--iesire", default="gasit.zip")

    a = p.parse_args()

    if a.comanda == "tip":
        print(tip_real(a.cale))

    elif a.comanda == "strings":
        date = open(a.cale, "rb").read()
        for s in extrage_strings(date):
            print(s)

    elif a.comanda == "exif":
        exif_nume, coordonate = citeste_exif(a.cale)
        for nume, val in exif_nume.items():
            if nume != "GPSInfo":  # e afisat separat, mai jos, in format util
                print(nume, "=", val)
        if coordonate:
            print(f"GPS: latitudine={coordonate[0]:.6f}, longitudine={coordonate[1]:.6f}")
        else:
            print("Nicio informatie GPS in acest fisier.")

    elif a.comanda == "carve":
        rezultat = carve(a.cale, iesire=a.iesire)
        if rezultat:
            pozitie, iesire = rezultat
            print(f"arhiva extrasa de la octetul {pozitie} -> {iesire}")
        else:
            print("nicio semnatura de arhiva gasita in fisier")


if __name__ == "__main__":
    main()
