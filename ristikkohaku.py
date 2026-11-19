"""Sanapaikkakohtainen haku. Ruudukon koordinaatit ovat (rivi, sarake)."""
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from time import monotonic

from pohjat import OLETUS, POHJAT

POHJA = POHJAT[OLETUS].rivit  # Vanhan rajapinnan oletuspohja
LISTAT = ('kaikkisanat', 'monikot', 'erisnimet', 'brandit', 'eng_julkkikset', 'fi_julkkikset')


def lataa_sanat():
    sanat = set()
    for nimi in LISTAT:
        with Path(__file__).with_name(nimi + '.txt').open(encoding='utf-8-sig') as f:
            for rivi in f:
                sana = rivi.strip().lower()
                if len(sana) >= 4 and all(c in 'abcdefghijklmnopqrstuvwxyzåäö' for c in sana):
                    sanat.add(sana)
    return sanat


def sanapaikat(pohja):
    if not pohja or not pohja[0] or any(len(r) != len(pohja[0]) for r in pohja):
        raise ValueError('Pohjan on oltava suorakulmio.')
    h, w = len(pohja), len(pohja[0])
    paikat = []
    for dr, dc in ((0, 1), (1, 0)):
        for r in range(h):
            for c in range(w):
                if pohja[r][c] == '#' or (r >= dr and c >= dc and pohja[r-dr][c-dc] != '#'):
                    continue
                ruudut = []
                y, x = r, c
                while y < h and x < w and pohja[y][x] != '#':
                    ruudut.append((y, x))
                    y, x = y + dr, x + dc
                if 1 < len(ruudut) < 4:
                    raise ValueError(f'Liian lyhyt sana kohdassa {(r, c)}.')
                if len(ruudut) >= 4:
                    paikat.append(ruudut)
    avoimet = {(r,c) for r in range(h) for c in range(w) if pohja[r][c] != '#'}
    if not paikat or avoimet != {rc for p in paikat for rc in p}:
        raise ValueError('Jokaisen avoimen ruudun pitää kuulua sanapaikkaan.')
    return paikat


def tarkista_pohja(pohja):
    """Raportoi sanapaikkojen yhteydet ja piilot; koordinaatit alkavat nollasta.

    Virheellinen sanapaikkageometria nostaa ValueErrorin kuten sanapaikat().
    Piilopari tarkoittaa kahta peräkkäistä piiloa samassa sanapaikassa.
    """
    paikat = sanapaikat(pohja)
    omistajat = defaultdict(list)
    for i, paikka in enumerate(paikat):
        for ruutu in paikka:
            omistajat[ruutu].append(i)

    piilot = {ruutu for ruutu, sanat in omistajat.items() if len(sanat) == 1}
    parit = [(a, b) for paikka in paikat for a, b in zip(paikka, paikka[1:])
             if a in piilot and b in piilot]

    kaymatta = set(range(len(paikat)))
    osia = 0
    while kaymatta:
        osia += 1
        pino = [kaymatta.pop()]
        while pino:
            for ruutu in paikat[pino.pop()]:
                for naapuri in omistajat[ruutu]:
                    if naapuri in kaymatta:
                        kaymatta.remove(naapuri)
                        pino.append(naapuri)

    return {'sanapaikkoja': len(paikat), 'yhtenaisia_osia': osia,
            'piilokirjaimet': sorted(piilot), 'piiloparit': parit}


@dataclass
class Mittarit:
    valinnat: int = 0
    peruutukset: int = 0
    umpikujat: Counter = field(default_factory=Counter)


STRATEGIAT = ('nykyinen', 'reunat')


def ratkaise(pohja, sanat, *, mittarit=None, takaraja=None, strategia='nykyinen'):
    """takaraja on monotonic()-kellon määrähetki. Aikakatkaisu nostaa TimeoutErrorin."""
    if strategia not in STRATEGIAT:
        raise ValueError(f'Tuntematon strategia: {strategia}')
    paikat = sanapaikat(pohja)
    naapurit = [[] for _ in paikat]
    ruudut = {}
    pituudet = defaultdict(set)
    for sana in sanat:
        pituudet[len(sana)].add(sana)
    ehdokkaat = []
    for i, paikka in enumerate(paikat):
        lukot = []
        for k, (r,c) in enumerate(paikka):
            if (r,c) in ruudut:
                j, l = ruudut[r,c]
                naapurit[i].append((j,k,l))
                naapurit[j].append((i,l,k))
            ruudut[r,c] = i,k
            if pohja[r][c] != '.':
                lukot.append((k,pohja[r][c].lower()))
        ehdokkaat.append({s for s in pituudet[len(paikka)] if all(s[k] == v for k,v in lukot)})

    def hae(d, muutokset):
        # Joukkoja ei muuteta paikallaan: haarat voivat jakaa ennallaan pysyvät joukot.
        jono = deque(muutokset)
        kirjattu = False

        def kirjaa(i):
            # Kirjaa vain haaran ensimmäinen tyhjentynyt paikka, ei seurannaisvirheitä.
            nonlocal kirjattu
            if mittarit is None or kirjattu:
                return
            kirjattu = True
            maski = [pohja[r][c].lower() for r,c in paikat[i]]
            for j,k,l in naapurit[i]:
                merkit = {s[l] for s in d[j]}
                if len(merkit) == 1:
                    maski[k] = merkit.pop()
            mittarit.umpikujat[i, ''.join(maski)] += 1

        while jono:
            if takaraja is not None and monotonic() >= takaraja:
                raise TimeoutError('Haun aikaraja täyttyi.')
            i = jono.popleft()
            if not d[i]:
                kirjaa(i)
                return None
            if len(d[i]) == 1:
                sana = next(iter(d[i]))
                for j, muut in enumerate(d):
                    if j != i and sana in muut:
                        d[j] = muut - {sana}
                        if not d[j]:
                            kirjaa(j)
                        jono.append(j)
            for j,k,l in naapurit[i]:
                kirjaimet = {s[k] for s in d[i]}
                uudet = {s for s in d[j] if s[l] in kirjaimet}
                if len(uudet) < len(d[j]):
                    d[j] = uudet
                    if not uudet:
                        kirjaa(j)
                    jono.append(j)

        avoimet = [i for i in range(len(d)) if len(d[i]) > 1]
        if not avoimet:
            return [next(iter(v)) for v in d]
        def paikan_avain(i):
            loppuja = 0
            if strategia == 'reunat':
                loppuja = sum(len(d[j]) > 1 and l == len(paikat[j])-1
                              for j, _, l in naapurit[i])
            return -loppuja, len(d[i]), -sum(len(d[j]) > 1 for j, _, _ in naapurit[i])

        i = min(avoimet, key=paikan_avain)
        tuet = [(k, Counter(s[l] for s in d[j])) for j,k,l in naapurit[i] if len(d[j]) > 1]

        def jarjestys(s):
            maarat = [t[s[k]] for k,t in tuet]
            return -min(maarat, default=0), -sum(maarat), s

        for sana in sorted(d[i], key=jarjestys):
            if mittarit is not None:
                mittarit.valinnat += 1
            haara = d.copy()
            haara[i] = {sana}
            vastaus = hae(haara, [i])
            if vastaus is not None:
                return vastaus
            if mittarit is not None:
                mittarit.peruutukset += 1
        return None

    vastaus = hae(ehdokkaat, range(len(paikat)))
    if vastaus is None:
        return None
    kartta = [list(r) for r in pohja]
    for paikka, sana in zip(paikat, vastaus):
        for (r,c), kirjain in zip(paikka, sana):
            kartta[r][c] = kirjain
    luetut = [''.join(kartta[r][c] for r,c in p) for p in paikat]
    if luetut != vastaus or len(set(luetut)) != len(luetut) or any(s not in pituudet[len(s)] for s in luetut):
        raise RuntimeError('Ratkaisun lopputarkistus epäonnistui.')
    return [''.join(r) for r in kartta]
