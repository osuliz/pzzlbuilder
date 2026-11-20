"""Ohjattu laadintakoe 15 × 18 -pohjalla. Istunnon valintoja ei kirjoiteta tiedostoon."""
import argparse
import re
from collections import defaultdict
from pathlib import Path
from time import monotonic

from pohjamuutoskoe import ALUEET, POHJA, POIS
from ristikkohaku import ratkaise, sanapaikat
from sanamuoto import ruudukkomuoto, sesti_loppuinen


TYHJA_OHJE = """Tyhjä pohja: piste on avoin ruutu, tyhjä kohta suljettu.
  aseta G17-O17 TRILOGIAT   Aseta oma sana hakua käynnistämättä.
  poista G17-O17            Poista oma sana, säilytä muut kiinnitykset.
  nayta                     Näytä omat ja hyväksytyt kirjaimet.
  ehdota B13-E18            Ehdota aluetta, jolla on kokonainen jatkotäyttö.
  toinen B13-B18            Kokeile ehdotuksessa toista sanaa tässä paikassa.
  lukitse B13-B18           Kiinnitä ehdotuksen sana kokonaisena.
  tayta                     Ehdota koko loppuristikon täyttöä.
  hyvaksy                   Kiinnitä viimeisin ehdotus:
                            ehdota → vain alue; tayta → koko ristikko.
Pikakoe käynnistetään terminaalista:
  python ohjattu_laadinta.py --tyhja --pikakoe --yrityksia 5 --yritysaika 3 --sekuntia 20
Aikaraja ei tarkoita umpikujaa. lopeta päättää istunnon ilman tallennusta."""

TAVALLINEN_OHJE = """Ohjattu täyttö: ohjelma ehdottaa ratkaisuja valittuun sanapaikkaan.
  paikka G17-O17      Valitse paikka ja hae täyttöä.
  oma TRILOGIAT       Kokeile omaa sanaa valittuun paikkaan.
  toinen / takaisin   Etsi eri sana tai palauta edellinen täyttö ilman hakua.
  lukitse / avaa      Kiinnitä valittu sana tai vapauta sen lukitus.
  suojaa B13-E18      Säilytä täytön nykyiset kirjaimet alueella.
  vapauta B13-E18     Poista tämän alueen suoja.
  nayta / hae         Näytä täyttö tai käynnistä uusi haku.
  lopeta              Päätä istunto ilman tallennusta."""


def osoite(rc):
    r, c = rc
    return f'{chr(65+c)}{r+1}'


def nimi(p):
    return osoite(p[0]) + '-' + osoite(p[-1])


def lue(g, p):
    return ''.join(g[r][c] for r,c in p)


def aluerajat(teksti, pohja):
    m = re.fullmatch(r'([A-Z])([1-9][0-9]?)\s*[-–]\s*([A-Z])([1-9][0-9]?)', teksti.strip().upper())
    if not m:
        raise ValueError('Anna alue kahdella kulmaruudulla, esim. B13-E18.')
    a, i, b, j = m.groups()
    r, y = sorted((int(i)-1, int(j)-1))
    c, x = sorted((ord(a)-65, ord(b)-65))
    if y >= len(pohja) or x >= len(pohja[0]):
        raise ValueError('Alue ulottuu ristikon ulkopuolelle.')
    return r,c,y,x


def lukittu(pohja, lukot):
    g = [list(rivi) for rivi in pohja]
    for paikka, sana in lukot.items():
        for (r,c), ch in zip(paikka, sana, strict=True):
            if g[r][c] not in ('.', ch):
                raise ValueError(f'Ristiriita ruudussa {osoite((r,c))}.')
            g[r][c] = ch
    return tuple(map(''.join,g))


def nayta_ruudukko(g):
    print('    ' + ' '.join(chr(65+c) for c in range(len(g[0]))))
    for i, row in enumerate(g, 1):
        print(f'{i:2}  ' + ' '.join(row.upper().replace('#', ' ')))


def tyhja_istunto(b, sanat, paikat, reunat, sekuntia, pikakoe=None):
    hyvaksytty = valmis = b
    omat = {}  # Omat sanat voi poistaa hyväksytyistä alueista riippumatta.
    ehdotus = None
    alue = set()
    nimet = {nimi(p): p for p in paikat}
    nayta_ruudukko(valmis)
    while True:
        try:
            osat = input('[aseta PAIKKA SANA / poista PAIKKA / tayta / ehdota ALUE / toinen SANAPAIKKA / lukitse SANAPAIKKA / hyvaksy / nayta / lopeta]> ').strip().split(maxsplit=1)
        except (EOFError, KeyboardInterrupt):
            return valmis
        cmd = osat[0].lower() if osat else ''
        arvo = osat[1].upper().replace('–', '-') if len(osat)>1 else ''
        try:
            if cmd in ('ohje', '?'):
                print(TYHJA_OHJE)
                continue
            if cmd == 'lopeta':
                return valmis
            if cmd == 'nayta':
                nayta_ruudukko(valmis)
                continue
            if cmd in ('aseta', 'poista'):
                syote = arvo.split()
                if len(syote) != (2 if cmd == 'aseta' else 1) or syote[0] not in nimet:
                    raise ValueError('Anna kokonainen sanapaikka, esim. aseta G17-O17 KAATOSADE tai poista G17-O17.')
                p = nimet[syote[0]]
                uudet = omat.copy()
                if cmd == 'aseta':
                    if sesti_loppuinen(syote[1]):
                        raise ValueError('SESTI-loppuinen vastaus ei ole sallittu.')
                    sana = ruudukkomuoto(syote[1])
                    if not sana or len(sana) != len(p) or sana in POIS:
                        raise ValueError(f'Sanan pitää olla sallittu ja {len(p)} kirjainta pitkä.')
                    uudet[p] = sana
                else:
                    if p not in uudet:
                        raise ValueError('Paikassa ei ole poistettavaa omaa sanaa.')
                    del uudet[p]
                kokeilu = lukittu(hyvaksytty, uudet)
                luetut = set()
                for q in paikat:
                    s = lue(kokeilu,q)
                    if '.' not in s:
                        if sesti_loppuinen(s):
                            raise ValueError(f'Risteykseen muodostuu kielletty sana {s.upper()}.')
                        if s in luetut:
                            raise ValueError(f'Sana {s.upper()} toistuu.')
                        luetut.add(s)
                omat, valmis, ehdotus = uudet, kokeilu, None
                nayta_ruudukko(valmis)
                continue
            if cmd in ('hyvaksy', 'lukitse'):
                if ehdotus is None:
                    raise ValueError('Pyydä ensin alue-ehdotus.')
                if cmd == 'lukitse':
                    p = nimet.get(arvo)
                    if not p or alue.isdisjoint(p):
                        raise ValueError('Anna ehdotusalueeseen osuva kokonainen sanapaikka.')
                    hyvaksytty = lukittu(hyvaksytty, {p:lue(ehdotus,p)})
                else:
                    hyvaksytty = lukittu(hyvaksytty, {((r,c),):ehdotus[r][c] for r,c in alue})
                    ehdotus = None
                valmis = lukittu(hyvaksytty, omat)
                nayta_ruudukko(valmis)
                continue
            estot = {}
            if cmd == 'tayta':
                uusi = {rc for p in paikat for rc in p}
                ehdotus = None
            elif cmd == 'ehdota':
                r,c,y,x = aluerajat(arvo,b)
                uusi = {(i,j) for i in range(r,y+1) for j in range(c,x+1) if b[i][j]!='#'}
                if not uusi:
                    raise ValueError('Alueella ei ole avoimia ruutuja.')
                ehdotus = None
            elif cmd == 'toinen' and ehdotus is not None:
                p = nimet.get(arvo)
                if not p or alue.isdisjoint(p):
                    raise ValueError('Anna ehdotusalueeseen osuva kokonainen sanapaikka.')
                uusi = alue
                estot[p] = {lue(ehdotus,p)}
            else:
                raise ValueError('Pyydä ehdotus komennolla ehdota ALUE, esim. ehdota B13-E18.')
            kiinteat = {lue(hyvaksytty,p) for p in paikat if '.' not in lue(hyvaksytty,p)}
            g = ratkaise(valmis, sanat | set(omat.values()) | kiinteat, strategia='vaiheet', reunapaikat=reunat,
                         paikkakiellot=estot, takaraja=monotonic()+sekuntia,
                         pikakoe=pikakoe if cmd == 'tayta' else None)
            if g is None:
                print('Näillä ehdoilla ei ole täyttöä. Hyväksyttyjä kirjaimia ei muutettu.')
                continue
            alue, ehdotus = uusi, g
            nayta_ruudukko(lukittu(valmis, {((r,c),):g[r][c] for r,c in alue}))
            if cmd == 'tayta':
                print('Täyttöehdotus. Hyväksy koko täyttö komennolla hyvaksy tai jatka omien sanojen asettamista.')
                continue
            print('Alueelta ulos jatkuvat sanat:')
            for p in paikat:
                if not alue.isdisjoint(p) and not alue.issuperset(p):
                    print(nimi(p), lue(g,p).upper())
        except TimeoutError:
            print('Aikaraja: jatkotäyttö ei selvinnyt. Hyväksyttyjä kirjaimia ei muutettu.')
        except ValueError as e:
            print(e)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tyhja', action='store_true', help='aloita ilman kirjaimia ja hyväksy alue kerrallaan')
    parser.add_argument('--paikka', default='G17-O17', help='kokonainen sanapaikka, esim. G17-O17')
    parser.add_argument('--sekuntia', default=30, type=int, help='aikaraja yhtä täyttöyritystä kohti')
    parser.add_argument('--pikakoe', action='store_true', help='kokeile eri pitkiä aloituksia komennolla tayta (--tyhja)')
    parser.add_argument('--yrityksia', type=int, help='aloitusten enimmäismäärä (oletus 5)')
    parser.add_argument('--yritysaika', type=int, help='sekunteja per aloitus (oletus 3)')
    args = parser.parse_args()
    if args.pikakoe and not args.tyhja:
        parser.error('--pikakoe vaatii --tyhja-tilan.')
    for arvo in (args.yrityksia,args.yritysaika):
        if arvo is not None and (not args.pikakoe or arvo < 1):
            parser.error('Yritysrajat vaativat --pikakoe-lipun ja positiivisen arvon.')
    if args.sekuntia < 1:
        parser.error('Aikarajan pitää olla positiivinen.')
    b = [list(row) for row in POHJA]
    for r in (13,15):  # F14 ja F16 kiinni, kuten nopeimmassa paikalliskokeessa.
        b[r][5] = '#'
    b = tuple(map(''.join,b))
    paikat = [tuple(p) for p in sanapaikat(b)]
    nimet = {nimi(p):p for p in paikat}
    def valitse(s):
        p = nimet.get(s.strip().upper().replace('–','-'))
        if not p:
            raise ValueError('Tuntematon sanapaikka. Vaihtoehdot: ' + ', '.join(nimet))
        return p
    try:
        p = valitse(args.paikka)
    except ValueError as e:
        parser.error(str(e))
    rajat = [{(i,x) for i in range(r,y+1)} for r,c,y,x in ALUEET]
    rajat += [{(y,j) for j in range(c,x+1)} for r,c,y,x in ALUEET]
    reunat = [q for q in paikat if any(reuna.issubset(q) for reuna in rajat)]
    sanat = set(Path(__file__).with_name('koesanasto').joinpath('sanat.txt').read_text(encoding='utf-8').splitlines()) - POIS
    print('Kirjoita ohje tai ?, jos haluat käyttöohjeet.')
    if args.tyhja:
        koe = (args.yrityksia or 5, args.yritysaika or 3) if args.pikakoe else None
        tyhja_istunto(b, sanat, paikat, reunat, args.sekuntia, koe)
        return
    kiellot = defaultdict(set)
    kiellot[nimet['G17-O17']].add('kromioida')  # Etsitään vaihtoehtoa aiemmalle täytölle.
    lukot = {}
    suojat = {}  # Alue -> kirjaimet; päällekkäiset alueet voi vapauttaa erikseen.
    historia = []  # Nykyisen paikan täytöt ja niiden aikaiset ohitukset.
    g = None
    komento = 'hae'
    while True:
        try:
            osat = komento.strip().split(maxsplit=1)
            cmd = osat[0].lower() if osat else ''
            arvo = osat[1] if len(osat)>1 else ''
            if cmd == 'lopeta':
                break
            if cmd == 'paikka':
                p = valitse(arvo)
                historia.clear()
                g = None
                cmd = 'hae'
            if cmd in ('ohje', '?'):
                print(TAVALLINEN_OHJE)
            elif cmd == 'takaisin':
                if historia:
                    g, kiellot[p] = historia.pop()
                    print('Palautettu:', nimi(p), lue(g,p).upper())
                else:
                    print('Ei aiempaa ehdotusta tässä paikassa.')
            elif cmd in ('suojaa','vapauta'):
                alue = aluerajat(arvo,b)
                r,c,y,x = alue
                if cmd == 'suojaa':
                    if g is None:
                        raise ValueError('Alueen suojaamiseen tarvitaan valmis täyttö.')
                    solut = {((i,j),):g[i][j] for i in range(r,y+1) for j in range(c,x+1) if b[i][j]!='#'}
                    if not solut:
                        raise ValueError('Alueella ei ole kirjaimia.')
                    suojat[alue] = solut
                    print('Suojattu:', arvo.upper(), f'({len(solut)} kirjainta)')
                else:
                    if alue not in suojat:
                        raise ValueError('Tälle alueelle ei ole asetettu suojaa.')
                    del suojat[alue]
                    print('Aluesuoja poistettu:', arvo.upper())
                historia.clear()
            elif cmd == 'lukitse' and g:
                historia.clear()
                lukot[p] = lue(g,p)
                print('Lukittu:', nimi(p), lukot[p].upper())
            elif cmd == 'avaa':
                lukot.pop(p,None)
                historia.clear()
                g = None
                print('Paikka vapautettu:', nimi(p))
            elif cmd == 'nayta' and g:
                print('    '+' '.join('ABCDEFGHIJKLMNO'))
                for j,row in enumerate(g,1):print(f'{j:2}  '+' '.join(row.upper().replace('#',' ')))
            elif cmd in ('hae','toinen','oma'):
                if cmd != 'hae' and p in lukot:
                    raise ValueError('Avaa lukitus ensin.')
                ehdot = dict(lukot)
                if cmd == 'oma':
                    if sesti_loppuinen(arvo):
                        raise ValueError('SESTI-loppuinen vastaus ei ole sallittu.')
                    sana = ruudukkomuoto(arvo)
                    if not sana or len(sana)!=len(p) or sana in POIS:
                        raise ValueError(f'Sanan pitää olla sallittu ja {len(p)} kirjainta pitkä.')
                    ehdot[p] = sana
                suojattu = lukittu(b, {q:ch for solut in suojat.values() for q,ch in solut.items()})
                pohja = lukittu(suojattu,ehdot)
                if g is not None:
                    historia.append((g, kiellot[p].copy()))
                    if cmd == 'toinen':
                        kiellot[p].add(lue(g,p))
                # Käyttäjä voi kokeilla aiemmin ohittamaansa sanaa nimeltä.
                estot = {q: k - {ehdot.get(q)} for q,k in kiellot.items()}
                g = None
                t = monotonic()
                g = ratkaise(pohja, sanat | set(ehdot.values()), strategia='vaiheet',
                             reunapaikat=reunat, paikkakiellot=estot, takaraja=t+args.sekuntia)
                if g:
                    print(f'{nimi(p)}: {lue(g,p).upper()} – täysi jatkotäyttö ({monotonic()-t:.2f} s)')
                    print('Risteävät:', ', '.join(nimi(q)+' '+lue(g,q).upper() for q in paikat if q!=p and set(p).intersection(q)))
                else:
                    print('Näillä ehdoilla ei ole täyttöä.')
            elif cmd not in ('lukitse','nayta'):
                print('Tuntematon komento.')
            elif not g:
                print('Ei näytettävää tai lukittavaa täyttöä.')
        except TimeoutError:
            print('Aikaraja: täyttöä ei löytynyt ajoissa. Tämä ei todista umpikujaa.')
        except ValueError as e:
            print(e)
        try:
            komento = input(f'{nimi(p)} [nayta / lukitse / avaa / suojaa ALUE / vapauta ALUE / toinen / takaisin / oma SANA / paikka ALKU-LOPPU / hae / lopeta]> ')
        except (EOFError, KeyboardInterrupt):
            break


if __name__=='__main__':
    main()
