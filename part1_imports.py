# Laborator: functii, metode si importuri pe web
# Student: Fratea Mihaela

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# --- Exercițiul 1 ---
import requests
print(requests.__version__)
import urllib.request
# Explicatie: request este un modul extern, care nu vine cu Python, deci trebuie instalat cu pip install.
# urllib face parte din biblioteca standard, care este inclusa in Python, deci nu trebuia instalata.

# --- Exercițiul 2 ---
# Stilul 1 : import requests
response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Stil 1:", response.status_code)

# Avataj pentru stilul 1 : arata clar de unde vine fiecare nume.

# Stilul 2 : from requests import get
from requests import get
response = get(BASE_URL, timeout=TIMEOUT)
print("Stil 2:", response.status_code)

# Avataj pentru stilul 2 : este mai scurt decat stilul 1, dar poate incurca daca este acelasi nume in program.

# --- Exercițiul 3 ---
import requests as rq
response = rq.get(BASE_URL, timeout=TIMEOUT)
print("Alias:", response.status_code)

# Un Alias face codul mai usor de citit cand numele modulului este lung si trebuie de scris de mai multe ori.

# Un Alias face codul mai greu de citit cand aliasul este arbitar sau e criptic(de exemplu import requests from x).
# Cineva care citeste codul trebuie sa se intoarca la inceput sa caute ce inseamna x.

# --- Exercițiul 4 ---
import urllib.request
import urllib.error

cerere = urllib.request.Request(
    BASE_URL,
    headers={"User-Agent": "WebLab-Fratea Mihaela"},
)

try:
    raspuns = urllib.request.urlopen(cerere, timeout=TIMEOUT)
    print("Status:", raspuns.status)
    corp = raspuns.read().decode("utf-8")
    print(corp[:200])
except urllib.error.HTTPError as e:
    print("Serverul a răspuns cu eroare:", e.code)

# urllib trimite implicit User-Agent "Python-urllib", pe care serverul
# l-a refuzat (403). Am setat un User-Agent propriu prin Request.

# --- Exercițiul 5 ---
print(dir(requests))

# 1. get este o functie, pentru ca trimite o cerere GET, fara o actiune
# 2. Session este o clasa care permite pastrarea anumitelor parametri 
# (cum ar fi cookie-urile sau header-ele) de la o cerere la alta, fără a le redefini.
# 3. models este un modul, pentru că este un fișier din pachetul requests,
# care conține clase precum Request și Response.

# --- Exercițiul 6 ---
help(requests.get)

response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Cu timeout:", response.status_code)

# Parametrul care setează timpul maxim de așteptare este timeout,
# exprimat în secunde. Dacă serverul nu răspunde în acest timp, cererea
# se oprește cu o eroare, în loc să aștepte la nesfârșit.

# --- Exercițiul 7 ---

import time
start = time.perf_counter()
response = requests.get(BASE_URL, timeout=TIMEOUT)
end = time.perf_counter()

print("perf_counter:", end - start, "secunde")
print("response.elapsed", response.elapsed.total_seconds(), "secunde")

# Comparație: perf_counter dă un timp puțin mai mare decât response.elapsed,
# pentru că măsoară toată durata apelului requests.get(), nu doar
# timpul dintre trimiterea cererii și primirea răspunsului.

# --- Exercițiul 8 ---
try:
    import bs4
    print("bs4 este instalat, versiunea:", bs4.__version__)
except ImportError:
    print("Instalati modul cu: pip install beautifulsoup4")

# Verificați-vă: diferența dintre modul, pachet și bibliotecă
# - Modul: un singur fișier .py care conține cod reutilizabil (funcții,
#   clase, constante). Exemplu: time, json.
# - Pachet: un director care conține mai multe module, grupate împreună.
#   Exemplu: requests (are în interior module ca api, models, sessions).
# - Bibliotecă: termen general pentru o colecție de cod gata făcut pe care
#   o folosim în programe; poate fi un modul sau un pachet. De exemplu,
#   biblioteca standard Python conține module precum time și urllib.