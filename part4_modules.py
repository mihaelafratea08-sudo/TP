# Laborator: funcții, metode și importuri pe web
# Student: Fratea Mihaela

import hashlib
import json
import re
import socket
import ssl
import time
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# --- Exercițiul 35: descompunerea unui URL ---
def parse_url_parts(url: str) -> dict:
    """Descompune un URL în scheme, netloc, path, query și fragment."""
    parti = urlparse(url)
    return {
        "scheme": parti.scheme,
        "netloc": parti.netloc,
        "path": parti.path,
        "query": parti.query,
        "fragment": parti.fragment,
    }


for nume, valoare in parse_url_parts("https://cybercor.org/path?x=1#top").items():
    print(f"Ex. 35 - {nume}: {valoare}")


# --- Exercițiul 36: compunerea URL-urilor ---
def make_absolute(base: str, links: list) -> list:
    """Transformă legăturile relative în URL-uri complete, pornind de la base."""
    return [urljoin(base, legatura) for legatura in links]


for complet in make_absolute(BASE_URL, ["/about", "contact.html", "../index.html"]):
    print("Ex. 36 -", complet)


# --- Exercițiul 37: extragerea legăturilor ---
def extract_links(html: str) -> list:
    """Returnează toate legăturile href din html, fără duplicate (în ordinea găsirii)."""
    legaturi = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(legaturi))  # dict.fromkeys elimină duplicatele


pagina = requests.get(BASE_URL, timeout=TIMEOUT)
legaturi = extract_links(pagina.text)
print("Ex. 37 -", len(legaturi), "legături unice:", legaturi)


# --- Exercițiul 38: interne sau externe? ---
def split_links(links: list, domain: str) -> tuple:
    """Împarte legăturile în (interne, externe) față de domain.

    Fiecare legătură este făcută mai întâi absolută cu urljoin(), apoi se
    compară domeniul (netloc). Legăturile care nu sunt http/https
    (mailto:, javascript: etc.) sunt ignorate.
    """
    interne = []
    externe = []
    for legatura in links:
        completa = urljoin("https://" + domain, legatura)
        parti = urlparse(completa)
        if parti.scheme not in ("http", "https"):
            continue
        if parti.netloc == domain:
            interne.append(completa)
        else:
            externe.append(completa)
    return interne, externe


interne, externe = split_links(legaturi, "cybercor.org")
print("Ex. 38 -", len(interne), "interne,", len(externe), "externe")


# --- Exercițiul 39: propria clasă care moștenește HTMLParser ---
class ImageFinder(HTMLParser):
    """Colectează atributul src al fiecărui tag <img> într-o listă."""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        # HTMLParser scrie numele tag-urilor cu litere mici, deci <IMG> e prins
        if tag == "img":
            src = dict(attrs).get("src")
            if src:  # ignorăm tag-urile <img> fără src
                self.images.append(src)


test_html = """
<html><body>
  <img src="/logo.png" alt="Logo">
  <IMG SRC="poza.jpg">
  <img alt="imagine fără src">
  <img src="https://cdn.example.com/banner.webp" />
  <a href="/despre">Aceasta nu este o imagine</a>
</body></html>
"""

finder = ImageFinder()
finder.feed(test_html)
print(finder.images)

assert finder.images == [
    "/logo.png",                            # imagine obișnuită
    "poza.jpg",                             # tag scris cu majuscule
    "https://cdn.example.com/banner.webp",  # tag care se închide singur
], "Parserul nu a găsit exact imaginile așteptate"
print("Testul a trecut!")

# Acum pe pagina reală
time.sleep(1)
response = requests.get(BASE_URL, timeout=TIMEOUT)
finder = ImageFinder()
finder.feed(response.text)
print(len(finder.images), "imagini găsite")
for src in finder.images:
    print(src)
print("Verificare cu count('<img'):", response.text.lower().count("<img"))


# --- Exercițiul 40: amprenta paginii ---
def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 (hash) a conținutului paginii de la url."""
    response = requests.get(url, timeout=TIMEOUT)
    return hashlib.sha256(response.content).hexdigest()


time.sleep(1)
amprenta1 = page_fingerprint(BASE_URL)
time.sleep(1)
amprenta2 = page_fingerprint(BASE_URL)
print("Ex. 40 - amprenta 1:", amprenta1)
print("Ex. 40 - amprenta 2:", amprenta2)
print("Ex. 40 - identice:", amprenta1 == amprenta2)

# Amprentele ar fi diferite dacă pagina s-ar schimba între cele două cereri
# (conținut nou, dată sau oră afișată, un token generat la fiecare cerere,
# reclame etc.): orice modificare, chiar de un singur caracter, schimbă hash-ul.


# --- Exercițiul 41: salvarea în JSON ---
def save_headers(response, filename: str) -> None:
    """Salvează antetele răspunsului în fișierul JSON filename."""
    with open(filename, "w", encoding="utf-8") as fisier:
        json.dump(dict(response.headers), fisier, indent=2)


time.sleep(1)
response = requests.get(BASE_URL, timeout=TIMEOUT)
save_headers(response, "headers.json")

with open("headers.json", "r", encoding="utf-8") as fisier:
    antete = json.load(fisier)
print("Ex. 41 - Content-Type din fișier:", antete.get("Content-Type", "lipsește"))


# --- Exercițiul 42: interogare DNS ---
def resolve(hostname: str) -> str:
    """Returnează adresa IP a domeniului hostname."""
    return socket.gethostbyname(hostname)


print("Ex. 42 - IP cybercor.org:", resolve("cybercor.org"))


# --- Exercițiul 43: expirarea certificatului ---
def cert_days_left(hostname: str) -> int:
    """Returnează câte zile mai sunt până la expirarea certificatului hostname."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            certificat = ssock.getpeercert()
    expira = ssl.cert_time_to_seconds(certificat["notAfter"])
    data_expirare = datetime.fromtimestamp(expira)
    return (data_expirare - datetime.now()).days


print("Ex. 43 - zile rămase:", cert_days_left("cybercor.org"))

# Verificați-vă: cine apelează handle_starttag() în exercițiul 39?
# O apelează parserul însuși, în interiorul metodei feed(): când parcurge
# HTML-ul și întâlnește un tag de deschidere, apelează automat
# handle_starttag(tag, attrs). Noi doar definim ce se întâmplă (suprascriem
# metoda) și apelăm feed(); nu apelăm niciodată handle_starttag direct.