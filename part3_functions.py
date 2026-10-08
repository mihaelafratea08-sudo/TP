# Laborator: funcții, metode și importuri pe web
# Student: Fratea Mihaela

import time
from typing import Optional

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# --- Exercițiile 21 și 23: fetch ---
def fetch(url: str, timeout: int = 10) -> requests.Response:
    """Descarcă url și returnează obiectul răspuns.

    timeout (în secunde) are valoarea implicită 10.
    """
    return requests.get(url, timeout=timeout)


# Ex. 21: apel cu valoarea implicită
raspuns = fetch(BASE_URL)
print("Ex. 21 - cod de stare:", raspuns.status_code)

# Ex. 23: apel cu valoarea implicită și apoi cu timeout=3
time.sleep(1)
print("Ex. 23 - implicit:", fetch(BASE_URL).status_code)
time.sleep(1)
print("Ex. 23 - timeout=3:", fetch(BASE_URL, timeout=3).status_code)


# --- Exercițiul 22: get_status ---
def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa url."""
    response = requests.get(url, timeout=TIMEOUT)
    return response.status_code


for cale in ["/", "/robots.txt", "/sitemap.xml"]:
    print("Ex. 22 -", cale, get_status(BASE_URL + cale))
    time.sleep(1)


# --- Exercițiile 24 și 25: get_title ---
def get_title(html: str) -> str:
    """Returnează titlul paginii (textul dintre <title> și </title>).

    Primește doar un șir HTML, fără operații de rețea. Dacă pagina nu are
    tag <title>, returnează un șir gol.
    """
    inceput_tag = html.find("<title>")
    sfarsit_tag = html.find("</title>")
    if inceput_tag == -1 or sfarsit_tag == -1:
        return ""
    start = inceput_tag + len("<title>")
    return html[start:sfarsit_tag].strip()


# get_title nu face nicio cerere: descărcarea (fetch) și analiza (get_title)
# sunt separate, deci get_title poate fi testată și pe un HTML scris de noi.
print("Ex. 24 - titlu:", repr(get_title(fetch(BASE_URL).text)))
print("Ex. 24 - test local:", get_title("<html><title> Test </title></html>"))
help(get_title)  # Ex. 25: afișează docstring-ul


# --- Exercițiul 26: adnotări de tip ---
# Adnotările (url: str, -> int) sunt doar indicii pentru cititor și pentru
# unelte; Python nu le verifică la rulare, deci NU ne opresc să apelăm
# funcția cu alt tip. Eroarea de mai jos vine din requests, nu din adnotare.
try:
    get_status(123)
except requests.RequestException as eroare:
    print("Ex. 26 - eroare din requests, nu din adnotare:", type(eroare).__name__)


# --- Exercițiul 27: page_exists ---
def page_exists(url: str) -> bool:
    """Returnează True dacă pagina răspunde cu succes, altfel False.

    Nu se oprește cu eroare nici pentru domenii care nu există.
    """
    try:
        response = requests.get(url, timeout=TIMEOUT)
        return response.ok
    except requests.RequestException:
        return False


print("Ex. 27 -", page_exists(BASE_URL))
time.sleep(1)
print("Ex. 27 -", page_exists("https://this-domain-does-not-exist.invalid"))


# --- Exercițiul 28: check_paths ---
def check_paths(base: str, paths: list) -> dict:
    """Returnează un dicționar {cale: cod_de_stare} pentru fiecare cale din paths."""
    rezultate = {}
    for cale in paths:
        rezultate[cale] = get_status(base + cale)
        time.sleep(1)  # pauză între cereri
    return rezultate


print("Ex. 28 -", check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"]))


# --- Exercițiul 29: get_header ---
def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returnează valoarea antetului name pentru url, sau default dacă lipsește."""
    response = requests.get(url, timeout=TIMEOUT)
    return response.headers.get(name, default)


# Apel cu argumente cu nume
print("Ex. 29 - Server:", get_header(BASE_URL, name="Server"))
time.sleep(1)


# --- Exercițiul 30: security_headers ---
SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


def security_headers(url: str) -> dict:
    """Verifică cele cinci antete de securitate și returnează {antet: True/False}."""
    response = requests.get(url, timeout=TIMEOUT)
    return {antet: antet in response.headers for antet in SECURITY_HEADERS}


# --- Exercițiul 31: score_headers ---
def score_headers(results: dict) -> str:
    """Primește dicționarul din security_headers și returnează un scor ca "3/5"."""
    prezente = sum(1 for valoare in results.values() if valoare)
    return f"{prezente}/{len(results)}"


print("Ex. 30 -", security_headers(BASE_URL))
time.sleep(1)
print("Ex. 31 - scor:", score_headers(security_headers(BASE_URL)))
time.sleep(1)


# --- Exercițiul 32: fetch_robots și disallowed_paths ---
def fetch_robots(base: str) -> Optional[str]:
    """Returnează textul fișierului /robots.txt sau None dacă lipsește."""
    try:
        response = requests.get(base + "/robots.txt", timeout=TIMEOUT)
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    return response.text


def disallowed_paths(robots_text: Optional[str]) -> list:
    """Returnează lista valorilor Disallow: din robots.txt.

    Funcționează și când primește None (returnează o listă goală).
    """
    if robots_text is None:
        return []
    cai = []
    for linie in robots_text.splitlines():
        linie = linie.strip()
        if linie.lower().startswith("disallow:"):
            valoare = linie.split(":", 1)[1].strip()
            if valoare:
                cai.append(valoare)
    return cai


print("Ex. 32 -", disallowed_paths(fetch_robots(BASE_URL)))
print("Ex. 32 - cu None:", disallowed_paths(None))
time.sleep(1)


# --- Exercițiul 33: response_times ---
def response_times(*urls: str) -> dict:
    """Returnează {url: secunde} pentru oricâte adrese primește."""
    timpi = {}
    for url in urls:
        start = time.perf_counter()
        requests.get(url, timeout=TIMEOUT)
        timpi[url] = time.perf_counter() - start
        time.sleep(1)  # pauză între cereri
    return timpi


print("Ex. 33 -", response_times(BASE_URL, ECHO_URL))


# --- Exercițiul 34: log ---
def log(message: str, **details) -> None:
    """Afișează mesajul urmat de fiecare detaliu, în forma: mesaj | cheie=valoare."""
    text = message
    for cheie, valoare in details.items():
        text += f" | {cheie}={valoare}"
    print(text)


log("verificat", url=BASE_URL, status=200)

# Verificați-vă: diferența dintre print() și return
# - print() doar afișează o valoare pe ecran; valoarea nu mai poate fi
#   folosită în program după aceea.
# - return trimite valoarea înapoi către cine a apelat funcția, care o poate
#   salva într-o variabilă, o poate transmite altei funcții (ca la
#   score_headers(security_headers(...))) sau o poate salva într-un fișier.