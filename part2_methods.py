# Laborator: funcții, metode și importuri pe web
# Student: Fratea Mihaela

import time
import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# --- Exercițiul 9 ---
response = requests.get(BASE_URL, timeout=TIMEOUT)

print(response.status_code)  # atribut (valoare, fără paranteze)
print(response.ok)           # atribut (True dacă cererea a reușit)
print(response.url)          # atribut (adresa finală a răspunsului)
print(response.encoding)     # atribut (codificarea textului)


# --- Exercițiul 10 ---
# Pagina principală există, deci raise_for_status() nu face nimic
response.raise_for_status()
print("Pagina principală e în regulă:", response.status_code)

time.sleep(1)  # pauză între cereri

# Pagina inexistentă: serverul răspunde cu o eroare (de obicei 404)
try:
    r404 = requests.get(BASE_URL + "/this-page-does-not-exist", timeout=TIMEOUT)
    r404.raise_for_status()
except requests.HTTPError:
    print("Pagina nu a fost găsită, dar programul continuă normal.")

# raise_for_status() este o metodă: ridică requests.HTTPError dacă codul de
# stare indică o eroare (4xx sau 5xx), iar pentru coduri bune nu face nimic.
# Prin try / except prindem eroarea, deci programul nu se oprește cu traceback.


# --- Exercițiul 11 ---
time.sleep(1)  # pauză între cereri
response = requests.get(BASE_URL, timeout=TIMEOUT)

for nume, valoare in response.headers.items():
    print(f"{nume}: {valoare}")

# response.headers este un atribut care se comportă ca un dicționar
# (perechi nume - valoare). Metoda .items() returnează toate perechile,
# iar bucla for le parcurge pe rând, afișându-le în forma Nume: valoare.


# --- Exercițiul 12 ---
print("Server:", response.headers.get("Server", "lipsește"))
print("Content-Type:", response.headers.get("Content-Type", "lipsește"))
print("content-type (litere mici):", response.headers.get("content-type", "lipsește"))

# Observație: și cu litere mici obținem aceeași valoare. Antetele din
# requests nu țin cont de majuscule/minuscule (dicționar insensibil la
# litere), spre deosebire de un dicționar obișnuit. get() returnează
# valoarea implicită ("lipsește") dacă antetul nu există.


# --- Exercițiul 13 ---
# Reutilizăm răspunsul de la exercițiul 11 (fără cerere nouă)
numar = response.text.lower().count("cyber")
print("Cuvântul 'cyber' apare de", numar, "ori")

# Putem înlănțui .lower() și .count() pentru că .lower() returnează tot un
# șir de caractere (str), iar .count() este o metodă a șirurilor, deci poate
# fi apelată direct pe rezultatul lui .lower().


# --- Exercițiul 14 ---
html = response.text
inceput_tag = html.find("<title>")
sfarsit_tag = html.find("</title>")

if inceput_tag == -1 or sfarsit_tag == -1:
    # find() returnează -1 când textul nu e găsit
    print("Pagina nu conține un tag <title> în codul HTML")
else:
    start = inceput_tag + len("<title>")
    titlu = html[start:sfarsit_tag].strip()
    print("Titlu:", titlu)


# --- Exercițiul 15 ---
linii = html.splitlines()
print("Număr de linii:", len(linii))
print("Lungimea celei mai lungi linii:", len(max(linii, key=len)))

# max(linii, key=len) alege linia cu cea mai mare lungime, iar len() ne dă
# apoi numărul ei de caractere.


# --- Exercițiul 16 ---
if response.url.startswith("https://"):
    print("Conexiune securizată")
else:
    print("Conexiune nesecurizată")


# --- Exercițiul 17 ---
time.sleep(1)  # pauză între cereri
r_http = requests.get("http://cybercor.org", timeout=TIMEOUT)

for pas in r_http.history:
    print("Redirecționare:", pas.status_code, pas.url)
print("URL final:", r_http.url)

# response.history conține răspunsurile intermediare (de exemplu 301),
# prin care serverul ne-a mutat de la http:// la adresa finală.


# --- Exercițiul 18 ---
time.sleep(1)  # pauză între cereri
r_head = requests.head(BASE_URL, timeout=TIMEOUT)
time.sleep(1)
r_get = requests.get(BASE_URL, timeout=TIMEOUT)

print("HEAD - dimensiunea corpului:", len(r_head.content))
print("GET  - dimensiunea corpului:", len(r_get.content))

# HEAD cere doar antetele, fără corpul paginii, deci len(content) este 0.
# GET returnează și corpul (codul HTML), deci conținutul are mulți octeți.


# --- Exercițiul 19 ---
if len(r_get.cookies) == 0:
    print("Niciun cookie setat")
else:
    for cookie in r_get.cookies:
        print(cookie.name, cookie.secure)

# Cookie-urile sunt mici date pe care serverul le cere browserului să le
# rețină. Atributul .secure arată dacă cookie-ul se trimite doar prin HTTPS.


# --- Exercițiul 20 ---
session = requests.Session()
session.headers.update({"User-Agent": "WebLab-Fratea Mihaela"})

time.sleep(1)  # pauză între cereri
r_echo = session.get(ECHO_URL + "/headers", timeout=TIMEOUT)
print(r_echo.json()["headers"]["User-Agent"])

# httpbin.org/headers returnează antetele primite de server. Dacă apare
# "WebLab-Fratea Mihaela", antetul setat în sesiune a fost trimis. O sesiune
# reține setările (aici User-Agent) pentru toate cererile făcute cu ea.

# Verificați-vă: response.text este un atribut (valoare deja pregătită, fără
# paranteze), iar response.json() este o metodă (face o acțiune: analizează
# corpul ca JSON și returnează un dicționar), deci se apelează cu paranteze.