from flask import Flask, jsonify, request, render_template
import random
import os

app = Flask(__name__)

# Główna ścieżka do folderu fiszki
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_FISZKI = os.path.join(BASE_DIR, "fiszki")

# Endpoint do usuwania fiszki
@app.route("/usun/<osoba>/<plik>", methods=["POST"])
def usun(osoba, plik):
    data = request.json
    fiszki = load_fiszki(osoba, plik)
    if 0 <= data["id"] < len(fiszki):
        fiszki.pop(data["id"])  # usuwamy fiszkę
        save_fiszki(fiszki, osoba, plik)
    return jsonify({"status": "ok"})


def poprawianieWartosciFiszki(liczba):
    if liczba > 2:
        liczba = liczba * 2
    return liczba


def load_fiszki(nazwa_folderu, nazwa_pliku):
    """Wczytuje fiszki z pliku konkretnego użytkownika"""
    path = os.path.join(FOLDER_FISZKI, nazwa_folderu, nazwa_pliku)
    fiszki = []
    with open(path, "r", encoding="utf-8") as zapis:
        for line in zapis:
            linia = [elem.strip() for elem in line.split(";")]
            fiszki.append(linia)
    return fiszki


def save_fiszki(fiszki, nazwa_folderu, nazwa_pliku):
    path = os.path.join(FOLDER_FISZKI, nazwa_folderu, nazwa_pliku)
    with open(path, "w", encoding="utf-8") as file:
        for pytanie, odpowiedz, ocena in fiszki:
            file.write(f"{pytanie};{odpowiedz};{ocena}\n")


def losowanieFiszki(fiszki):
    while True:
        losowaFiszka = random.randint(0, len(fiszki) - 1)
        if random.random() < poprawianieWartosciFiszki(int(fiszki[losowaFiszka][2])) / 8:
            return losowaFiszka


# Strona startowa – lista użytkowników (folderów)
@app.route("/")
def index():
    osoby = [f for f in os.listdir(FOLDER_FISZKI) if os.path.isdir(os.path.join(FOLDER_FISZKI, f))]
    return render_template("index.html", osoby=osoby)


# Lista plików (działów) dla wybranej osoby
@app.route("/<osoba>")
def lista_fiszek(osoba):
    folder = os.path.join(FOLDER_FISZKI, osoba)
    pliki = [f for f in os.listdir(folder) if f.endswith(".txt")]
    pliki.sort()  # Dodajemy sortowanie alfabetyczne
    return render_template("fiszkilist.html", osoba=osoba, pliki=pliki)


# Endpoint losowania fiszki
@app.route("/losuj/<osoba>/<plik>")
def losuj(osoba, plik):
    fiszki = load_fiszki(osoba, plik)
    nrFiszki = losowanieFiszki(fiszki)
    return jsonify({
        "id": nrFiszki,
        "pytanie": fiszki[nrFiszki][0],
        "odpowiedz": fiszki[nrFiszki][1]
    })


# Endpoint do oceniania
@app.route("/ocena/<osoba>/<plik>", methods=["POST"])
def ocena(osoba, plik):
    data = request.json
    fiszki = load_fiszki(osoba, plik)
    fiszki[data["id"]][2] = str(data["ocena"])
    save_fiszki(fiszki, osoba, plik)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
