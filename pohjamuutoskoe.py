"""Paikallinen pohjamuutoskoe: python -B pohjamuutoskoe.py. Ei kirjoita tiedostoja."""
from itertools import combinations
from pathlib import Path
from time import monotonic

from ristikkohaku import Mittarit, ratkaise, sanapaikat, tarkista_pohja

POHJA = tuple('''############### ######......... ######....#.... ######......... ######....#....
#......##.#.#.# #....#......... #....##.#.##.#. #....#....#.... #.........#....
#....#......... ##.#.#.#.##.#.# #......#....... #.....###.##.#. #.........#....
#.........#.... #....#......... #....#....#....'''.split())
KOHTEET = (tuple((r, 5) for r in range(12, 16)), tuple((13, c) for c in range(1, 6)))
POIS = {'iankaiken', 'ussa', 'vesata', 'aulio', 'tuku', 'suotaa'}
# Aiemman vertailun paikalliset reunat. Uusi kokonainen sanapaikka kelpaa,
# jos se sisältää alkuperäisen reunajakson samassa suunnassa.
ALUEET = [(1,6,4,9), (1,11,4,14), (5,1,10,4), (12,1,17,4),
          (14,6,17,9), (14,11,17,14)]


def ehdota():
    lahella = sorted({(r+dr,c+dc) for p in KOHTEET for r,c in p
                      for dr,dc in ((0,0),(0,1),(0,-1),(1,0),(-1,0))
                      if 0 <= r+dr < len(POHJA) and 0 <= c+dc < len(POHJA[0])})
    tulokset = []
    for n in (1,2):
        for erot in combinations(lahella,n):
            rivit = [list(r) for r in POHJA]
            for r,c in erot:
                rivit[r][c] = '.' if rivit[r][c] == '#' else '#'
            pohja = tuple(map(''.join,rivit))
            try:
                raportti = tarkista_pohja(pohja)
            except ValueError:
                continue
            paikat = sanapaikat(pohja)
            piilot = set(raportti['piilokirjaimet'])
            if raportti['yhtenaisia_osia'] != 1 or raportti['piiloparit'] or any(p[0] in piilot for p in paikat):
                continue
            muuttuneet = sum(list(p) not in paikat for p in KOHTEET)
            # Ensin molempiin ongelmasanoihin vaikuttavat muutokset, sitten
            # vähiten muokattuja ruutuja ja vähiten piiloja. Ei täyttötakuuta.
            avain = (-muuttuneet,n,len(piilot),erot)
            tulokset.append((avain,pohja))
    return sorted(tulokset)


def koe():
    ehdotukset = ehdota()
    print('Rakenteellisesti kelvollisia:',len(ehdotukset))
    parhaat = ehdotukset[:3]
    for i, ((muutos,n,piilot,erot),_) in enumerate(parhaat,1):
        selite = ', '.join(f'{chr(65+c)}{r+1} ' + ('auki' if POHJA[r][c]=='#' else 'kiinni') for r,c in erot)
        print(i, selite, 'muuttuneita kohdesanoja:',-muutos,'piiloja:',piilot,flush=True)
    sanat = set(Path(__file__).with_name('koesanasto').joinpath('sanat.txt').read_text(encoding='utf-8').splitlines()) - POIS
    rajat = [set((i,x) for i in range(r,y+1)) for r,c,y,x in ALUEET]
    rajat += [set((y,j) for j in range(c,x+1)) for r,c,y,x in ALUEET]
    for i, (_,pohja) in enumerate(parhaat,1):
        reunat = [p for p in sanapaikat(pohja) if any(reuna.issubset(p) for reuna in rajat)]
        m = Mittarit(); t = monotonic()
        try:
            g = ratkaise(pohja,sanat,strategia='vaiheet',reunapaikat=reunat,mittarit=m,takaraja=t+30)
            tila = 'täytetty' if g else 'ei ratkaisua'
        except TimeoutError:
            g = None; tila = 'aikaraja'
        print(i, tila,round(monotonic()-t,2),m.valinnat,m.peruutukset,flush=True)
        if g:
            print('    '+' '.join('ABCDEFGHIJKLMNO'))
            for j,row in enumerate(g,1):print(f'{j:2}  '+' '.join(row.upper().replace('#',' ')))


if __name__ == '__main__':
    koe()
