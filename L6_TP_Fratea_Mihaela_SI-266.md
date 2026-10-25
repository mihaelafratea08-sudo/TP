# Laboratorul 6. GitHub, pas cu pas

**Disciplina:** Tehnici de programare (S.O.001)
**Universitatea:** UTM · FCIM · Securitate informațională · Anul I, Sem. 1


## Date generale

| Câmp | Valoare |
| --- | --- |
| Nume, prenume | Fratea Mihaela |
| Grupa | SI-266 |
| Username GitHub | mihaelafratea08-sudo |
| Data | 25.l0.2026 |

## Linkurile depozitelor

| Depozit | Link | Public? |
| --- | --- | --- |
| exercitiu-git | https://github.com/mihaelafratea08-sudo/exercitiu-git | da |
| exercitiu-2 | https://github.com/mihaelafratea08-sudo/exercitiu-2 | da |
| Depozitul al disciplinei | https://github.com/mihaelafratea08-sudo/TP | da |

## Scopul lucrării

Scopul lucrării a fost să învăț să folosesc git și GitHub de la zero. Git ține istoria unui proiect pe calculatorul meu, iar GitHub ține o copie a ei pe internet.
Am învățat să salvez schimbările (commit), să le trimit pe GitHub (push), să aduc înapoi schimbările de acolo (pull) și să citesc istoria proiectului.


## Ce am exersat, pas cu pas


### A1. Contul GitHub

Am avut deja cont GitHub.

### A2. Git pe calculator: verificare și configurare
...

Am verificat cu git --version că git este instalat și am setat cu git config --global numele, adresa de e-mail, 
ramura principală main și modul de unire la pull, apoi am verificat setările cu git config --global --list.

git --version
git version 2.56.0.windows.2

git config --global --list
filter.lfs.clean=git-lfs clean -- %f
filter.lfs.smudge=git-lfs smudge -- %f
filter.lfs.process=git-lfs filter-process
filter.lfs.required=true
user.name=Mihaela Fratea
user.email=mihaelafratea08@gmail.com
core.autocrlf=true
difftool.sourcetree.cmd=''
mergetool.sourcetree.cmd=''
mergetool.sourcetree.trustexitcode=false
mergetool.sourcetree.keepbackup=false
init.defaultbranch=main
pull.rebase=false

### A3. Primul depozit, creat pe GitHub

Am creat pe GitHub depozitul public exercitiu-git, cu fișierul README.md, pornind de la butonul New repository.

### A4. Clonarea: `git clone`

Am descărcat depozitul pe calculator cu git clone și am intrat în folderul exercitiu-git, 
deoarece comenzile git funcționează doar din folderul unui depozit.

### A5. `git status`, `git add`, `git commit`

Am creat fișierul salut.py, l-am rulat și am urmărit cu git status cum trece din „untracked" în „changes to be committed".
Apoi am făcut primul meu commit cu git add și git commit -m.

### A6. Trimiterea pe GitHub: `git push`

Am trimis commit-ul pe GitHub cu git push, m-am autentificat la prima trimitere și am verificat în browser că salut.py a apărut în depozit.

### A7. Aducerea schimbărilor: `git pull`

Am modificat README.md direct pe GitHub și am adus schimbarea pe calculator cu git pull, ca să înțeleg regula: pull înainte de lucru, push după lucru.


### A8. Fișierul `.gitignore`

Am creat mediul virtual .venv și am scris .gitignore, ca git să ignore .venv/ și __pycache__/, apoi am trimis regula pe GitHub.

### A9. Istoria și schimbările: `git log` și `git diff`
...
Am citit istoria cu git log --oneline, am văzut cu git diff ce rânduri am adăugat în salut.py înainte de commit și am anulat schimbarea cu git restore.

git log --oneline
0010230 (HEAD -> main, origin/main, origin/HEAD) Ignor mediul virtual
0f7e712 Merge branch 'main' of https://github.com/mihaelafratea08-sudo/exercitiu-git
fb78d41 Adaug salut.py
828aa86 Delete salut.py
ee25348 Add greeting message in salut.py
a56f0ee Initial commit

### A10. Al doilea depozit, pornit de pe calculator

Am pornit invers: am creat folderul exercitiu-2 cu git init, am făcut primul commit, am creat depozitul gol pe GitHub și l-am legat cu git remote add origin. 
Apoi am trimis codul cu git push -u origin main.

## Verificarea finală (A11)

- [ ] `exercitiu-git` este Public și conține `README.md`, `salut.py`, `.gitignore`
- [ ] `exercitiu-git` are minimum 4 commit-uri
- [ ] `exercitiu-2` este Public și conține `README.md`
- [ ] `exercitiu-2` a fost creat cu `git init` și trimis cu `git push -u origin main`

## Probleme întâlnite și cum le-am rezolvat


| Ce am văzut | Ce însemna | Ce am făcut |
| Your branch and 'origin/main' have diverged și All conflicts fixed but you are still merging la git status (A5)|Calculatorul și GitHub aveau commit-uri diferite, iar unirea nu fusese încheiată| Am verificat README.md, am încheiat unirea cu git commit, apoi am făcut git push|
| error: failed to push some refs la git push (A10) | GitHub avea un commit pe care calculatorul nu-l avea | depozit recreat fără README |

## Surse și ajutor primit

Am lucrat după fișa de laborator. Pentru a înțelege și a repara erorile de la A5 și A10 am cerut explicații asistentului AI Claude, apoi am rulat și verificat singur(ă) comenzile.

=

## Concluzii

Am învățat să folosesc fluxul de bază în git: status, add, commit, push și pull. Cel mai greu a fost să înțeleg erorile care apar când calculatorul și GitHub au istorii diferite. 
Am înțeles de ce e important git pull înainte de lucru și git push după. Git îmi va fi util pentru a păstra istoria lucrărilor de la disciplină și pentru a lucra în siguranță la proiecte.

## Predare

- [ ] Folderul `Laborator_6_GitHub` creat în depozitul privat `TP_Nume_Prenume_Grupa`
- [ ] Raportul este în folder, cu numele `L6_TP_Nume_Prenume_Grupa.md` (cu datele tale reale)
- [ ] Commit și push făcute în depozitul privat
- [ ] E-mail trimis la cristian.gonceari@isa.utm.md, cu subiectul `L6_TP_Nume_Prenume_Grupa`, linkul depozitului privat și codul ultimului commit
- [ ] Nicio parolă, token sau cheie API în raport sau în depozite
