# Stažení volebních výsledků do CSV

## Účel skriptu
Tento skript slouží ke stažení volebních výsledků z webových stránek a jejich exportu do CSV souboru.

Skript:
- načte stránku s přehledem obcí pro zvolený územní celek,
- automaticky najde odkazy na detail jednotlivých obcí,
- z každé obce vytěží:
  - kód obce
  - název obce
  - počet registrovaných voličů
  - počet vydaných obálek
  - počet platných hlasů
  - počet hlasů pro jednotlivé politické strany
- vše zapíše do jednoho CSV souboru.

Výstupní CSV je strukturovaný tak, že každý řádek odpovídá jedné obci.

---

## Instalace

### Požadavky
- Python 3.10+
- Přístup k internetu

### Instalace závislostí

Spusť následující příkazy:

```bash
pip install requests
pip install beautifulsoup4