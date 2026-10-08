# Laborator: funcții, metode și importuri pe web
# Student: Fratea Mihaela
#
# webtools.py - modulul propriu (Partea 5): funcții reutilizabile pe care
# le importă alte programe (de exemplu main.py), la fel ca requests.

import csv
import json
import re
import socket
import ssl
import time
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests

TIMEOUT = 10  # secunde

# Ex. 47: constantă de modul, folosită în fetch() și importabilă din main.py
DEFAULT_HEADERS = {"User-Agent": "WebLab-Fratea Mihaela"}

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


def fetch(url: str, timeout: int = 10) -> requests.Response:
    """Descarcă url (cu antetele din DEFAULT_HEADERS) și returnează răspunsul."""
    return requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)


def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa url."""
    return fetch(url).status_code


def get_title(html: str) -> str:
    """Returnează titlul paginii (textul dintre <title> și </title>).

    Dacă pagina nu are tag <title>, returnează un șir gol.
    """
    inceput_tag = html.find("<title>")
    sfarsit_tag = html.find("</title>")
    if inceput_tag == -1 or sfarsit_tag == -1:
        return ""
    start = inceput_tag + len("<title>")
    return html[start:sfarsit_tag].strip()


def security_headers(url: str) -> dict:
    """Verifică cele cinci antete de securitate și returnează {antet: True/False}."""
    response = fetch(url)
    return {antet: antet in response.headers for antet in SECURITY_HEADERS}


def score_headers(results: dict) -> str:
    """Primește dicționarul din security_headers și returnează un scor ca "3/5"."""
    prezente = sum(1 for valoare in results.values() if valoare)
    return f"{prezente}/{len(results)}"


def check_paths(base: str, paths: list) -> dict:
    """Returnează un dicționar {cale: cod_de_stare} pentru fiecare cale din paths."""
    rezultate = {}
    for cale in paths:
        rezultate[cale] = get_status(base + cale)
        time.sleep(1)  # pauză între cereri
    return rezultate


def fetch_robots(base: str) -> Optional[str]:
    """Returnează textul fișierului /robots.txt sau None dacă lipsește."""
    try:
        response = fetch(base + "/robots.txt")
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    return response.text


def disallowed_paths(robots_text: Optional[str]) -> list:
    """Returnează lista valorilor Disallow: din robots.txt (listă goală pentru None)."""
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


def extract_links(html: str) -> list:
    """Returnează toate legăturile href din html, fără duplicate."""
    legaturi = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(legaturi))


def split_links(links: list, domain: str) -> tuple:
    """Împarte legăturile în (interne, externe) față de domain.

    Legăturile care nu sunt http/https (mailto:, javascript: etc.) sunt ignorate.
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


def resolve(hostname: str) -> str:
    """Returnează adresa IP a domeniului hostname."""
    return socket.gethostbyname(hostname)


def cert_days_left(hostname: str) -> int:
    """Returnează câte zile mai sunt până la expirarea certificatului hostname."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            certificat = ssock.getpeercert()
    expira = ssl.cert_time_to_seconds(certificat["notAfter"])
    return (datetime.fromtimestamp(expira) - datetime.now()).days


def redirect_chain(url: str) -> list:
    """Pornește de la varianta http:// a lui url și returnează lanțul de redirecționări.

    Fiecare element are forma "301 -> https://exemplu.org/".
    """
    host = urlparse(url).netloc
    raspuns = requests.get("http://" + host, headers=DEFAULT_HEADERS, timeout=TIMEOUT)
    lant = []
    for pas in raspuns.history:
        destinatie = pas.headers.get("Location", "?")
        lant.append(f"{pas.status_code} -> {destinatie}")
    return lant


def write_report_csv(results: dict, filename: str) -> None:
    """Salvează {cale: status} în CSV, cu coloanele path, status și checked_at."""
    with open(filename, "w", newline="", encoding="utf-8") as fisier:
        scriitor = csv.writer(fisier)
        scriitor.writerow(["path", "status", "checked_at"])
        for cale, status in results.items():
            scriitor.writerow([cale, status, datetime.now().isoformat()])


def site_report(url: str) -> dict:
    """Colectează informații despre site, le afișează și le salvează în report.json.

    Folosește funcțiile din acest modul. Dacă o informație nu poate fi aflată
    (de exemplu fără rețea pentru DNS sau certificat), valoarea ei este None.
    """
    host = urlparse(url).netloc

    raspuns = fetch(url)
    titlu = get_title(raspuns.text)
    time.sleep(1)

    try:
        ip = resolve(host)
    except OSError:
        ip = None

    try:
        lant = redirect_chain(url)
    except requests.RequestException:
        lant = []
    time.sleep(1)

    scor = score_headers(security_headers(url))
    time.sleep(1)

    try:
        zile = cert_days_left(host)
    except (OSError, ssl.SSLError, KeyError):
        zile = None

    interne, externe = split_links(extract_links(raspuns.text), host)
    interzise = disallowed_paths(fetch_robots(url))

    raport = {
        "url": url,
        "final_url": raspuns.url,
        "status_code": raspuns.status_code,
        "title": titlu,
        "ip": ip,
        "redirects": lant,
        "security_score": scor,
        "cert_days_left": zile,
        "internal_links": len(interne),
        "external_links": len(externe),
        "disallowed_paths": interzise,
        "checked_at": datetime.now().isoformat(),
    }

    redirectionari = ", ".join(lant) if lant else "fără redirecționări"
    if zile is None:
        certificat = "necunoscut"
    elif zile == 1:
        certificat = "o zi rămasă"
    elif 1 < abs(zile) % 100 < 20:
        certificat = f"{zile} zile rămase"  # 2-19: fără "de"
    else:
        certificat = f"{zile} de zile rămase"  # 20+, sau 0: cu "de"
    interzise_text = ", ".join(interzise) if interzise else "niciuna"

    print(f"=== Raport site: {url} ===")
    print(f"{'Cod de stare:':<19}{raspuns.status_code}")
    print(f"{'Titlu:':<19}{titlu if titlu else '(fără titlu)'}")
    print(f"{'Adresă IP:':<19}{ip if ip else 'necunoscută'}")
    print(f"{'Redirecționări:':<19}{redirectionari}")
    print(f"{'Scor securitate:':<19}{scor}")
    print(f"{'Certificat:':<19}{certificat}")
    print(f"{'Legături:':<19}{len(interne)} interne, {len(externe)} externe")
    print(f"{'Căi interzise:':<19}{interzise_text}")

    with open("report.json", "w", encoding="utf-8") as fisier:
        json.dump(raport, fisier, indent=2, ensure_ascii=False)
    print("Salvat în report.json")

    return raport


# Ex. 46: acest bloc rulează doar când fișierul este pornit direct
# (python webtools.py). Când este importat din main.py, nu rulează.
if __name__ == "__main__":
    print("Autotest:", get_status("https://cybercor.org"))