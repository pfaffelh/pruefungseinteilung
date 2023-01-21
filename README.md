# Prüfungseinteilung

Das ist ein Python-Skript zum Verteilen von Prüfungen auf Prüfer. Etwas genauer ist es ein Jupyter-Notebook.

1) Um jupyter notebook zu installieren, muss man 

```
pip install ipykernel
pip install notebook
```

ausführen. Um das File einteilung.ipynb verwenden zu können, gibt man in der Kommandozeile im Ordner, der die entprechenden Dateien enthält (siehe 4)

```
jupyter notebook einteilung.ipynb
```

ein. Dies öffnet in einem Browser eine Ansicht, bei der man zunächst aus der linken Spalte Dateien auswählen kann. Die Datei, die nun alle Kommandos beinhaltet, ist einteilung.ipynb. Hier wechseln sich Text-Felder und Code-Felder ab. Mittels des Play-Buttons oder Shift+Return führt man jeweils eine Zelle (auch Chunk genannt) aus. 

2) Die nötigen python-Module müssen mittels

```
pip install -r requirements.txt
```

installiert werden. Möglicherweise funktioniert das Skript auch, wenn man die Versionen der Pakete durch andere ersetzt, oder man die in requirements.txt genannten Pakete einzeln installiert.

3) Auf dem System muss pdftk sowie pdflatex installiert sein (zur Erstellung derNiederschriften). Sind diese Programme nicht installiert, können die restlichen Schritte immer noch ausgeführt werden.

4) Um Prüfungen einteilen zu können, müssen folgende Dateien müssen vorhanden sein (siehe auch die Beschreibung im Jupyter file):
- anmeldungen_www: Ein Ordner, der die Anmeldungen (möglicherweise mit doppelten Anmeldungen) aus dem Web-Formular enthält.
- Einen Ordner "niederschriften", in dem am Ende alle Niederschriften abgelegt werden; anfangs ist dieser Ordner leer.
- Niederschrift-Hintergrund.pdf: Dies wird als Hintergrundbild bei der Erstellung der Niederschriften verwendet.
- niederschrift-template.tex: Das template für die Niederschriften.
- einteilung.py: Hier stehen die meisten der verwendeten Funktionen zur Prüfungseinteilung.
- einteilung.ipynb: Hier wird durch "clicken" (oder Shift+Return plus eventuelle Eingaben) der Prüfungsplan erstellt. 
Folgende Dateien sind der Input, der bei jeder Prüfungsperiode angepasst werden muss:
- A_HisInOne.csv: Eine Datei, die die Anmeldungen in HisInOne (in einer einzigen Datei für alle möglichen Studiengänge) erfasst.
- B_prüfungsnummern.csv: Hier wird jeder HisInOne-Prüfungsnummer der Studiengang und die genaue Prüfung zugeordnet.
- C_prüferwünsche.csv: Hier steht, was welcher Prüfer prüft, und wieviele Prüfen er/sie maximal abnimmt.
- D_prüfungsslots.csv: Hier werden die genauen Daten und Zeiten für den Prüfungsplan eingegeben.



