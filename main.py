# pip install requests
# pip install beautifulsoup4

import sys
import requests
from urllib.parse import urlparse

from bs4 import BeautifulSoup








def main() -> None:
    if len(sys.argv) != 3 or not "https://" in sys.argv[1] or not ".csv" in sys.argv[2]:
        print("Použití: main.py <odkaz na územní celek> <jméno csv souboru>")
        return
    
    response = requests.get(sys.argv[1])
    soup = BeautifulSoup(response.text, features="html.parser")
 
    odkazy = [
        (a.get_text(strip=True), a["href"])
        for a in soup.select('td.cislo[headers="t1sa1 t1sb1"] a[href], td.cislo[headers="t2sa1 t2sb1"] a[href], td.cislo[headers="t3sa1 t3sb1"] a[href]')
    ]

    parsed_url = urlparse(sys.argv[1])  
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    base_url = base_url.rsplit("/", 1)[0] + "/"
    # print(base_url)

    radky = []
    for odk in odkazy:
        # print(f"{base_url}{odk[1]}")
        response = requests.get(base_url+odk[1])
        soup = BeautifulSoup(response.text, features="html.parser") 
        radek = [odk[0]]
        print(radek)
        
    



# print(response.text)
    


if __name__ == "__main__":
    main()
    
