"""Aja: python hakuvertailu.py. Jokainen ajo luo oman arvioitavan TSV-tiedoston."""
import csv
from datetime import datetime
from itertools import product
from pathlib import Path
from time import monotonic

from pohjat import POHJAT
from ristikkohaku import STRATEGIAT, Mittarit, lataa_sanat, ratkaise, sanapaikat

KOKEET = [('silta4', 'konnevesi'), ('silta4', 'ulakeskus'),
          ('silta5', 'sateenvarjo'), ('silta5', 'lastenvaunu')]


def vertaa():
    sanat = lataa_sanat()
    kansio = Path(__file__).with_name('hakuvertailut')
    kansio.mkdir(exist_ok=True)
    polku = kansio / (datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.tsv')
    with polku.open('x', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow('pohja silta strategia rivin_tyyppi tila sekunnit valinnat peruutukset rivi sarake suunta sana_tai_kaava osumia arvio perustelu'.split())
        for (nimi, silta), strategia in product(KOKEET, STRATEGIAT):
            pohja = POHJAT[nimi].lukitse(silta)
            paikat = sanapaikat(pohja)
            m = Mittarit()
            alku = monotonic()
            try:
                tulos = ratkaise(pohja, sanat | {silta}, mittarit=m, takaraja=alku+60, strategia=strategia)
                tila = 'täytetty' if tulos else 'ei ratkaisua'
            except TimeoutError:
                tulos, tila = None, 'aikaraja'
            sek = round(monotonic()-alku, 3)
            print(nimi, silta, strategia, tila, sek, m.valinnat, m.peruutukset, flush=True)
            w.writerow([nimi, silta, strategia, 'yhteenveto', tila, sek, m.valinnat, m.peruutukset] + ['']*7)

            def paikka_rivi(i, tyyppi, teksti, lkm=''):
                r,c = paikat[i][0]
                suunta = 'vaaka' if paikat[i][1][0] == r else 'pysty'
                w.writerow([nimi, silta, strategia, tyyppi, '', '', '', '', r+1, c+1, suunta, teksti, lkm, '', ''])

            for (i, kaava), lkm in m.umpikujat.most_common(10):
                paikka_rivi(i, 'umpikuja', kaava, lkm)
            if tulos:
                for i, paikka in enumerate(paikat):
                    paikka_rivi(i, 'arvioitava', ''.join(tulos[r][c] for r,c in paikka))
    print(polku)


if __name__ == '__main__':
    vertaa()
