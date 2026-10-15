# Laborator 5 — Forensics și Steganografie

Nume: Fratea Mihaela
Grupa: SI-266
## Lucrarea A — Decoder universal

### A4. Decodare pe straturi (`probe/mesaj.txt`)

Comanda rulată:
```
python arsenal/forensics/decode.py "$(cat probe/mesaj.txt)"
```

Straturi găsite: base64
Rezultat:  464c41477b6c61626f7261746f725f63696e63695f666f72656e736963735f73695f737465676f7d

### A5. Spargere XOR (`probe/xor.bin`)

Comanda rulată:
```
python arsenal/forensics/decode.py probe/xor.bin --fisier
```

Cheia găsită: 32
Mesajul decriptat: Parola temporara pentru arhiva este: Sch1mbaMa!2026 - cauta cheia prin forta bruta.

### A6. Spargere hash prin dicționar (`probe/hashuri.txt`)

Comanda rulată:
```
python arsenal/forensics/decode.py --hash probe/hashuri.txt --wordlist probe/wordlist.txt
```

Algoritm: md5
Parola găsită: parola123

## Lucrarea B — Forensics pe fișiere

### B1. Tipul real al fișierului (`probe/foto.jpg`)

Comanda rulată:
```
python forensics.py tip probe/foto.jpg
```

Rezultat:  jpeg

### B3. Metadate EXIF și GPS

Comanda rulată:
```
python forensics.py exif probe/foto.jpg
```

Make : LaboratorForensics
Model: Camera-Simulata
Coordonate GPS: latitudine=47.024500, longitudine=28.832397

### B4. File carving (`probe/ascuns.png`)

Comanda rulată:
```
python forensics.py carve probe/ascuns.png --iesire gasit.zip
```

Poziția 638 de unde a fost extrasă arhiva: gasit.zip
Ce era în arhivă: 
numele fișierului:  secret.txt 
cu mesajul: Daca citesti asta, ai gasit arhiva ascunsa la coada pozei!

### B5-B6. Steganografie LSB

Comenzi rulate:
```
python stego.py ascunde probe/foto.jpg stego.png "mesajul meu"
python stego.py dezvaluie stego.png
```

Mesajul ascuns: Mesajul meu
Mesajul dezvăluit: Mesajul meu
