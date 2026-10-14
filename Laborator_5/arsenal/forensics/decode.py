"""
Decoder universal de forensics.

Primeste un sir (sau un fisier, cu --fisier) si:
  1. ghiceste stratul de codare (url / hex / base64)
  2. il desface
  3. daca rezultatul tot nu e citibil, repeta (straturi multiple)
  4. daca octetii arata a text criptat cu XOR pe un octet, sparge cheia
     prin forta bruta (toate cele 256 de valori posibile)
  5. daca i se da un hash (prin --hash), incearca sa gaseasca parola
     intr-o wordlist

Rulare tipica:
    python arsenal/forensics/decode.py "NTM1OTU3NTk="
    python arsenal/forensics/decode.py probe/xor.bin --fisier
    python arsenal/forensics/decode.py --hash probe/hashuri.txt --wordlist probe/wordlist.txt
"""

import argparse
import base64
import hashlib
import json
from urllib.parse import unquote


# ---------------------------------------------------------------------------
# A1 - diferenta text / octeti (nu e nevoie de functie, doar de intelegere;
# o pastram aici ca referinta rapida)
# ---------------------------------------------------------------------------
def demo_text_octeti():
    s = "Salut"
    b = s.encode()           # text -> bytes
    hexa = b.hex()           # bytes -> sir hexazecimal
    inapoi = bytes.fromhex(hexa)  # hex -> bytes, ca sa verificam ca se potriveste
    return b, hexa, inapoi


# ---------------------------------------------------------------------------
# A2 - recunoaste stratul dupa forma sirului (fara sa-l decodeze inca)
# ---------------------------------------------------------------------------
def ghici_strat(s):
    """Clasifica un sir dupa alfabetul folosit. Ordinea verificarilor conteaza:
    URL (cel mai specific, are %xx) -> hex (strict: doar 0-9a-f, lungime para)
    -> base64 (alfabetul cel mai larg, deci verificat ultimul)."""
    if "%" in s and any(
        s[i] == "%" and len(s) > i + 2 and all(c in "0123456789abcdefABCDEF" for c in s[i + 1:i + 3])
        for i in range(len(s))
    ):
        return "url"

    hex_chars = set("0123456789abcdefABCDEF")
    if len(s) % 2 == 0 and len(s) > 0 and all(c in hex_chars for c in s):
        return "hex"

    b64_chars = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    )
    if len(s) > 0 and all(c in b64_chars for c in s):
        return "base64"

    return "necunoscut"


# ---------------------------------------------------------------------------
# A3 - desface stratul recunoscut si intoarce (strat, rezultat_bytes)
# ---------------------------------------------------------------------------
def desfa(s):
    strat = ghici_strat(s)
    if strat == "base64":
        return strat, base64.b64decode(s)
    if strat == "hex":
        return strat, bytes.fromhex(s)
    if strat == "url":
        return strat, unquote(s).encode()
    # "necunoscut": nu stim sa-l decodam, il intoarcem asa cum e
    return strat, s.encode()


# ---------------------------------------------------------------------------
# A4 - verifica daca niste octeti arata a text ASCII citibil
# ---------------------------------------------------------------------------
def citibil(b):
    """True daca toti octetii sunt in zona tiparibila ASCII (32..126)."""
    return all(32 <= c < 127 for c in b)


def decodeaza_straturi(val, incercari_max=8):
    """Desface repetat pana iese text citibil sau renunta dupa incercari_max
    pasi (ca sa nu intram intr-o bucla infinita pe un sir care nu e codat
    deloc, sau e stricat)."""
    istoric = []
    for _ in range(incercari_max):
        strat, b = desfa(val)
        istoric.append(strat)
        if citibil(b):
            return istoric, b
        try:
            val = b.decode()
        except UnicodeDecodeError:
            # nu mai avem cum sa continuam ca text -> ne oprim aici
            return istoric, b
    return istoric, b


# ---------------------------------------------------------------------------
# A5 - sparge un XOR cu cheie de un singur octet prin forta bruta
# ---------------------------------------------------------------------------
def sparge_xor(date):
    """Incearca toate cele 256 de chei posibile (un octet) si intoarce
    (cheie, text_clar) pentru prima varianta care arata a text citibil.
    Daca nimic nu se potriveste, intoarce (None, None)."""
    for k in range(256):
        clar = bytes(b ^ k for b in date)
        if citibil(clar):
            return k, clar.decode()
    return None, None


# ---------------------------------------------------------------------------
# A6 - sparge un hash de parola prin dictionar (wordlist)
# ---------------------------------------------------------------------------
ALGORITMI_DUPA_LUNGIME = {
    32: "md5",
    40: "sha1",
    64: "sha256",
}


def sparge_hash(tinta, cale_wordlist):
    """tinta = hash-ul hex citit din fisier. Alege algoritmul dupa lungimea
    hash-ului, apoi incearca fiecare cuvant din wordlist pana gaseste unul
    al carui hash se potriveste."""
    tinta = tinta.strip().lower()
    algoritm = ALGORITMI_DUPA_LUNGIME.get(len(tinta))
    if algoritm is None:
        return None, None  # lungime necunoscuta, nu stim ce algoritm sa folosim

    with open(cale_wordlist, encoding="latin1") as f:
        for cuv in f:
            cuv = cuv.strip()
            if not cuv:
                continue
            h = hashlib.new(algoritm, cuv.encode()).hexdigest()
            if h == tinta:
                return algoritm, cuv
    return algoritm, None


# ---------------------------------------------------------------------------
# A7 - interfata din linia de comanda si fisa JSON
# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Decoder universal de forensics")
    p.add_argument("intrare", nargs="?", help="sir de decodat, sau cale catre fisier")
    p.add_argument("--fisier", action="store_true", help="trateaza 'intrare' ca o cale, nu ca un sir")
    p.add_argument("--hash", metavar="CALE_HASHURI", help="cale catre un fisier cu hash-uri de spart")
    p.add_argument("--wordlist", default="probe/wordlist.txt", help="wordlist pentru spargerea hash-ului")
    a = p.parse_args()

    rezultat = {}

    if a.hash:
        tinta = open(a.hash).readline().strip()
        algoritm, parola = sparge_hash(tinta, a.wordlist)
        rezultat = {"tip": "hash", "algoritm": algoritm, "hash": tinta, "parola": parola}
        if parola:
            print(f"gasit ({algoritm}): {parola}")
        else:
            print(f"nu s-a gasit nicio parola in {a.wordlist} pentru hash-ul {tinta} (algoritm: {algoritm})")

    elif a.fisier:
        date = open(a.intrare, "rb").read()
        cheie, text = sparge_xor(date)
        if cheie is not None:
            rezultat = {"tip": "xor", "cheie": cheie, "rezultat": text}
            print(f"cheie XOR: {cheie}")
            print(text)
        else:
            rezultat = {"tip": "xor", "cheie": None, "rezultat": None}
            print("nicio cheie de un octet nu produce text citibil")

    elif a.intrare:
        istoric, b = decodeaza_straturi(a.intrare)
        try:
            text = b.decode()
        except UnicodeDecodeError:
            text = b.hex()
        rezultat = {"tip": "straturi", "straturi": istoric, "rezultat": text}
        print("straturi:", " -> ".join(istoric))
        print("rezultat:", text)

    else:
        p.print_help()
        return

    with open("arsenal/forensics/fisa.json", "w", encoding="utf-8") as f:
        json.dump(rezultat, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
