import urllib.request
import re
import time

def siivoa_nimi(nimi):
    if not isinstance(nimi, str):
        return ""
    siivottu = nimi.strip().lower()
    siivottu = "".join(c for c in siivottu if c.isalpha())
    return siivottu

def haravoi_luokka(url):
    print(f"Ladataan: {url}...")
    nimet = set()
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # Poimitaan linkit muodossa >Matti Nykänen</a> tai >Urho Kekkonen</a>
            # Wikipedian luokkasivuilla kaikki artikkelit ovat siisteissä <li>-listoissa linkkeinä
            ehdokkaat = re.findall(r'>([^<]+)</a>', html)
            
            for ehdokas in ehdokkaat:
                # Suodatetaan pois järjestelmätekstit, päivämäärät ja ohjeet
                if any(p in ehdokas for p in [":", "Luokka", "Toiminnot", "Muokkaa", "Sivun", "Artikkeli", "Wikipedia", "Seuraava", "Edellinen", "luettelo", "Luettelo"]):
                    continue
                if len(ehdokas) < 3 or len(ehdokas) > 30:
                    continue
                
                # Puretaan etu- ja sukunimet erilleen ristikkosanoiksi
                if " " in ehdokas:
                    osat = ehdokas.split(" ")
                    for osa in osat:
                        p = siivoa_nimi(osa)
                        if 3 <= len(p) <= 10:
                            nimet.add(p)
                else:
                    p = siivoa_nimi(ehdokas)
                    if 3 <= len(p) <= 10:
                        nimet.add(p)
    except Exception as e:
        print(f" -> Virhe sivulla: {e}")
    return nimet

def aja_jattihaku():
    julkis_pankki = set()
    
    # Wikipedian massiivisimmat luokkasivut, joissa jokaisessa on satoja tai tuhansia ihmisiä
    luokat = [
        # Suomalaiset henkilöt aloituspisteinä
        "https://wikipedia.org",
        "https://wikipedia.org",
        "https://wikipedia.org",
        "https://wikipedia.org",
        "https://wikipedia.org",
        "https://wikipedia.org",
        "https://wikipedia.org",
        "https://wikipedia.org",
        # Ulkomaiset tunnetut luokat
        "https://wikipedia.org",
        "https://wikipedia.org",
        "https://wikipedia.org",
        "https://wikipedia.org"
    ]
    
    print("="*60)
    print("🚀 ALOITETAAN TEHOHAKU WIKIPEDIAN LUOKISTA (TAVOITE TUHANNET NIMET)")
    print("="*60)
    
    for url in luokat:
        uudet_nimet = haravoi_luokka(url)
        print(f" -> Löydetty {len(uudet_nimet)} nimen osaa tästä luokasta.")
        julkis_pankki.update(uudet_nimet)
        time.sleep(0.3) # Suojataan yhteys

    # Lisätään käsin tärkeimmät ristikkoturvat
    vakiot = ["kekkonen", "halonen", "niinistö", "stubb", "selänne", "räikkönen", "elvis", "obama", "trump", "biden", "elon", "brad", "keanu"]
    for v in vakiot:
        julkis_pankki.add(siivoa_nimi(v))

    if len(julkis_pankki) > 200:
        with open("erisnimet.txt", "w", encoding="utf-8") as f:
            for n in sorted(list(julkis_pankki)):
                f.write(n + "\n")
        print("\n" + "="*60)
        print(f"🏆 ONNISTUI TÄYSIN!")
        print(f"Kerätty yhteensä {len(julkis_pankki)} uniikkia nimen osaa tiedostoon: erisnimet.txt")
        print("="*60)
    else:
        print(f"\nLista jäi vieläkin pieneksi ({len(julkis_pankki)} nimeä).")

if __name__ == "__main__":
    aja_jattihaku()
