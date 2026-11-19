import os
from collections import Counter

def etsi_yleisimmat_paatteet(tiedostopolut, top_n=40):
    """
    Etsii tiedostoista vähintään 4 merkkiä pitkät sanat,
    kerää niiden 4-kirjaimiset päätteet (suffiksit),
    ja tulostaa tilastot (määrät ja prosenttiosuudet).
    """
    kaikki_paatteet = []
    sanojen_kokonaismaara = 0
    
    print("Luetaan tiedostoja...")
    for polku in tiedostopolut:
        if not os.path.exists(polku):
            print(f"HUOMIO: Tiedostoa '{polku}' ei löytynyt, hypätään yli.")
            continue
            
        laskuri = 0
        with open(polku, "r", encoding="utf-8") as f:
            for rivi in f:
                sana = rivi.strip().lower()
                # Huomioidaan vain puhtaat sanat (ei erikoismerkkejä), jotka ovat vähintään 4 merkkiä pitkiä
                if sana.isalpha() and len(sana) >= 4:
                    paate = sana[-4:]
                    kaikki_paatteet.append(paate)
                    laskuri += 1
        
        print(f"-> Ladattu {laskuri:,d} laillista sanaa tiedostosta: {polku}".replace(",", " "))
        sanojen_kokonaismaara += laskuri

    if not kaikki_paatteet:
        print("\nVirhe: Ei löytynyt yhtään sanaa tilastoitavaksi. Varmista tiedostonimet.")
        return

    # Lasketaan esiintymismäärät dynaamisesti
    paate_laskuri = Counter(kaikki_paatteet)
    yleisimmat = paate_laskuri.most_common(top_n)
    
    # TULOSTUSMUOTOILU
    print("\n" + "="*60)
    print(f" TILASTAT YLEISIMMISTÄ 4-KIRJAIMISISTA PÄÄTTEISTÄ")
    print(f" Sanoja analysoitu yhteensä: {sanojen_kokonaismaara:,d}".replace(",", " "))
    print(f" Erilaisia löydettyjä päätteitä: {len(paate_laskuri):,d}".replace(",", " "))
    print("="*60)
    print(f"{'Sija':<6}{'Pääte':<12}{'Esiintymät':<15}{'Prosenttiosuus'}")
    print("-"*60)
    
    for sija, (paate, maara) in enumerate(yleisimmat, 1):
        prosentti = (maara / sanojen_kokonaismaara) * 100
        maara_muotoiltu = f"{maara:,d}".replace(",", " ")
        print(f"#{sija:<4} -{paate:<11} {maara_muotoiltu:<14} {prosentti:.2f} %")
    print("="*60)

if __name__ == "__main__":
    # Tähän on listattu ne kolme tiedostoa, jotka koodistasi löytyvät
    sanalistat = ["kaikkisanat.txt", "monikot.txt", "erisnimet.txt"]
    
    # Etsitään 40 kaikkein yleisintä päätettä
    etsi_yleisimmat_paatteet(sanalistat, top_n=40)