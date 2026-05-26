# pip install requests
# pip install beautifulsoup4

"""Stažení volebních výsledků do CSV.

Skript očekává dva argumenty příkazové řádky:
1. odkaz na územní celek
2. název výstupního CSV souboru
"""

import sys
import csv
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from bs4.element import Tag


def main() -> None:
    """Hlavní vstupní bod programu.

    Zkontroluje argumenty, stáhne vstupní stránku, projde odkazy na obce,
    z každé obce vytěží volební výsledky a zapíše je do CSV souboru.
    """
    # Ověření počtu a základního formátu argumentů příkazové řádky.
    if len(sys.argv) != 3 or not "https://" in sys.argv[1] or not ".csv" in sys.argv[2]:
        print("Použití: main.py <odkaz na územní celek> <jméno csv souboru>")
        return

    # Stažení hlavní stránky s přehledem obcí.
    response: requests.Response = requests.get(sys.argv[1])
    soup: BeautifulSoup = BeautifulSoup(response.text, features="html.parser")

    # Získání seznamu odkazů na detail obcí.
    # Každá položka je tuple: (kód_obce, relativní_odkaz).
    odkazy: list[tuple[str, str]] = [
        (a.get_text(strip=True), a["href"])
        for a in soup.select(
            'td.cislo[headers="t1sa1 t1sb1"] a[href], '
            'td.cislo[headers="t2sa1 t2sb1"] a[href], '
            'td.cislo[headers="t3sa1 t3sb1"] a[href]'
        )
    ]

    # Sestavení základní URL adresy pro návazné relativní odkazy.
    parsed_url = urlparse(sys.argv[1])
    base_url: str = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    base_url = base_url.rsplit("/", 1)[0] + "/"

    # Seznam všech řádků, které budou zapsány do CSV.
    radky: list[dict[str, str]] = []

    for odk in odkazy:
        # Stažení detailní stránky jedné obce.
        response = requests.get(base_url + odk[1])
        soup = BeautifulSoup(response.text, features="html.parser")

        # Slovník reprezentující jeden řádek výstupního CSV.
        radek: dict[str, str] = {"code": odk[0]}

        # Vyhledání názvu obce v nadpisu <h3>.
        for h in soup.select("h3"):
            location: str = h.get_text(strip=True)
            if location.startswith("Obec: "):
                radek["location"] = location[6:]
                break

        # Získání počtu voličů v seznamu.
        registered_tag: Tag | None = soup.select_one('td.cislo[headers="sa2"]')
        registered: str = registered_tag.get_text(strip=True) if registered_tag else ""
        radek["registered"] = registered.replace("\xa0", " ")

        # Získání počtu vydaných obálek.
        envelopes_tag: Tag | None = soup.select_one('td.cislo[headers="sa3"]')
        envelopes: str = envelopes_tag.get_text(strip=True) if envelopes_tag else ""
        radek["envelopes"] = envelopes.replace("\xa0", " ")

        # Získání počtu platných hlasů.
        valid_tag: Tag | None = soup.select_one('td.cislo[headers="sa6"]')
        valid: str = valid_tag.get_text(strip=True) if valid_tag else ""
        radek["valid"] = valid.replace("\xa0", " ")

        # Průchod tabulkou stran a získání hlasů pro jednotlivé strany.
        rows: list[Tag] = soup.select("table.table tr")
        for row in rows:
            party: Tag | None = row.select_one('td[headers="t1sa1 t1sb2"]')
            votes: Tag | None = row.select_one('td[headers="t1sa2 t1sb3"]')
            if party and votes:
                radek[party.get_text(strip=True)] = votes.get_text(strip=True).replace("\xa0", " ")

        # Přidání zpracovaného řádku do seznamu všech řádků.
        radky.append(radek)

    # Zápis výsledků do CSV souboru.
    with open(sys.argv[2], mode="w", newline="") as volby_csv:
        # Hlavička CSV odpovídá klíčům posledního zpracovaného řádku.
        zahlavi: dict_keys[str, str] = radek.keys()
        zapisovac: csv.DictWriter = csv.DictWriter(volby_csv, delimiter=";", fieldnames=zahlavi)

        zapisovac.writeheader()
        zapisovac.writerows(radky)


if __name__ == "__main__":
    main()