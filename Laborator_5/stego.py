"""
Steganografie LSB: ascunde un mesaj in ultimul bit al fiecarui canal de
culoare (R, G, B) al fiecarui pixel dintr-o poza, si il dezvaluie inapoi.

Rulare:
    python stego.py ascunde probe/foto.jpg stego.png "FLAG{ascuns_in_pixeli}"
    python stego.py dezvaluie stego.png
"""

import argparse

from PIL import Image

# octet 0x00 marcheaza finalul mesajului, ca sa stim unde sa ne oprim la citire
TERMINATOR = b"\x00"


# ---------------------------------------------------------------------------
# B5 - ascunde mesajul in ultimii biti ai pixelilor
# ---------------------------------------------------------------------------
def ascunde(mesaj_bytes, cale_intrare, cale_iesire):
    img = Image.open(cale_intrare).convert("RGB")
    px = list(img.getdata())

    mesaj_bytes = mesaj_bytes + TERMINATOR
    biti = "".join(f"{x:08b}" for x in mesaj_bytes)

    if len(biti) > len(px) * 3:
        raise ValueError("mesajul e prea lung pentru aceasta poza")

    px_nou = []
    idx_bit = 0
    for (r, g, b) in px:
        canale = [r, g, b]
        for i in range(3):
            if idx_bit < len(biti):
                bit = int(biti[idx_bit])
                # pastram toti bitii, in afara de ultimul, si punem acolo bitul
                # mesajului nostru (canal & ~1 goleste ultimul bit)
                canale[i] = (canale[i] & ~1) | bit
                idx_bit += 1
        px_nou.append(tuple(canale))

    img.putdata(px_nou)
    img.save(cale_iesire)  # OBLIGATORIU .png: jpg recomprima si distruge bitii


# ---------------------------------------------------------------------------
# B6 - dezvaluie mesajul: exact invers, citim in loc sa scriem
# ---------------------------------------------------------------------------
def dezvaluie(cale):
    px = list(Image.open(cale).convert("RGB").getdata())

    biti = []
    for (r, g, b) in px:
        biti.append(str(r & 1))
        biti.append(str(g & 1))
        biti.append(str(b & 1))
    biti = "".join(biti)

    octeti = bytearray()
    for i in range(0, len(biti) - 7, 8):
        octet = int(biti[i:i + 8], 2)
        if octet == 0:
            break  # am dat de terminator, mesajul s-a incheiat
        octeti.append(octet)

    return bytes(octeti)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Steganografie LSB")
    sub = p.add_subparsers(dest="comanda", required=True)

    p_a = sub.add_parser("ascunde")
    p_a.add_argument("intrare")
    p_a.add_argument("iesire")
    p_a.add_argument("mesaj")

    p_d = sub.add_parser("dezvaluie")
    p_d.add_argument("cale")

    a = p.parse_args()

    if a.comanda == "ascunde":
        ascunde(a.mesaj.encode(), a.intrare, a.iesire)
        print(f"mesaj ascuns in {a.iesire}")

    elif a.comanda == "dezvaluie":
        mesaj = dezvaluie(a.cale)
        try:
            print(mesaj.decode())
        except UnicodeDecodeError:
            print(mesaj)


if __name__ == "__main__":
    main()
