# Laborator: funcții, metode și importuri pe web
# Student: Fratea Mihaela
#
# Rulare: python main.py https://cybercor.org

import argparse
import time

import webtools  # Ex. 44: importăm întregul modul
from webtools import DEFAULT_HEADERS, get_title, security_headers  # Ex. 45 și 47

# Ex. 45: dacă main.py ar avea și o funcție proprie get_title, definiția
# din main.py ar înlocui numele get_title importat din webtools (ultima
# definiție câștigă), deci apelurile ar folosi funcția din main.py, nu cea
# din webtools. De aceea importăm doar numele de care avem nevoie și
# evităm nume identice în ambele fișiere.

# Ex. 46: autotestul din webtools.py rulează doar la `python webtools.py`,
# pentru că atunci __name__ este "__main__". Când webtools este importat
# din main.py, __name__ este "webtools", deci blocul if nu se execută.


def main() -> None:
    """Citește URL-ul din linia de comandă și rulează toate verificările."""
    # Ex. 48: argumentul URL vine din linia de comandă, nu din BASE_URL
    parser = argparse.ArgumentParser(description="Raport despre un site web")
    parser.add_argument("url", help="adresa site-ului, ex: https://cybercor.org")
    args = parser.parse_args()
    url = args.url

    # Ex. 44: apel prin numele modulului
    raspuns = webtools.fetch(url)
    print("Titlu (webtools.get_title):", webtools.get_title(raspuns.text))
    time.sleep(1)

    # Ex. 45: apel direct, cu nume importate
    print("Titlu (get_title):", get_title(raspuns.text))
    print("Antete de securitate:", security_headers(url))
    time.sleep(1)

    # Ex. 47: constanta importată din webtools
    print("DEFAULT_HEADERS:", DEFAULT_HEADERS)

    # Ex. 49: raport CSV cu rezultatul funcției check_paths()
    rezultate = webtools.check_paths(url, ["/", "/robots.txt", "/sitemap.xml"])
    webtools.write_report_csv(rezultate, "report.csv")
    print("Salvat în report.csv")
    print()

    # Ex. 50: raportul complet (afișat și salvat în report.json)
    webtools.site_report(url)


if __name__ == "__main__":
    main()