"""Kotus-monikkojen koeajo: kirjoittaa vain koeajo_monikot/-hakemistoon."""
from pathlib import Path
import xml.etree.ElementTree as ET

from sanamuoto import ruudukkomuoto

JUURI = Path(__file__).resolve().parent
# Kotuksen vahva -> heikko aste. D (kato) käsitellään vain erikseen
# tunnetuille sanoille: esim. jalka -> jalat mutta aika -> ajat.
ASTE = dict(A=('kk','k'), B=('pp','p'), C=('tt','t'), E=('p','v'),
            F=('t','d'), G=('nk','ng'), H=('mp','mm'), I=('lt','ll'),
            J=('nt','nn'), K=('rt','rr'), L=('k','j'), M=('k','v'))
ERITYISET = {('jalka',9,'D'):'jalat', ('aika',9,'D'):'ajat',
             ('taika',9,'D'):'taiat',  # Ei aika-loppuinen yhdyssana.
             ('alaston',34,''):'alastomat',  # Ei -ton-vartalon kahdennusta.
             ('varas',41,'D'):'varkaat', ('lämmin',35,'H'):'lämpimät',
             ('lapsi',29,''):'lapset', ('mies',42,''):'miehet',
             # XML luokittelee puunnimen luokkaan 27 (kuusi-lukusanan tapaan).
             # Rajattu korjaus: ei yleistetä kaikkiin kuusi-loppuisiin sanoihin.
             ('hopeakuusi',27,''):'hopeakuuset',
             # Valmiiksi monikolliset hakusanat säilytetään vain näillä
             # tarkistetuilla luokka–aste-pareilla, ei kaikilla t-lopuilla.
             ('aivot',1,''):'aivot', ('housut',1,''):'housut',
             ('sakset',7,''):'sakset', ('häät',18,''):'häät'}
LOPUT = {1:'ouyö', 2:'ouyö', 3:'oaöä', 4:'oö', 5:'i', 6:'i', 7:'i',
         8:'e', 9:'aä', 10:'aä', 11:'aä', 12:'aä', 13:'aä', 14:'aä', 15:'aä'}


def monikko(sana, tn, av):
    avain = (sana, tn, av)
    if avain in ERITYISET:
        return ERITYISET[avain]
    # Aika ja sen yhdyssanat: muutos koskee vain loppuosaa,
    # ja edellyttää lähteen luokkaa 9 sekä katoastetta D.
    if tn == 9 and av == 'D' and sana.endswith('aika'):
        return sana[:-4] + 'ajat'
    # Luokka 34: onneton -> onnettomat, työtön -> työttömät.
    if tn == 34:
        if av == 'C':
            if sana.endswith('ton'):
                return sana[:-3] + 'ttomat'
            if sana.endswith('tön'):
                return sana[:-3] + 'ttömät'
        return None
    if tn in LOPUT and sana[-1:] in tuple(LOPUT[tn]):
        runko = sana[:-1]
        if av:
            if av not in ASTE:
                return None
            vahva, heikko = ASTE[av]
            if not runko.endswith(vahva):
                return None
            runko = runko[:-len(vahva)] + heikko
        return runko + ('e' if tn == 7 else sana[-1]) + 't'
    if not av:
        if tn in (23,24,25,26) and sana.endswith('i'):
            return sana[:-1] + 'et'
        if tn == 27 and sana.endswith('si'):
            return sana[:-2] + 'det'
        if tn == 38 and sana.endswith('nen'):
            return sana[:-3] + 'set'
        if tn == 39 and sana.endswith(('os','ös','us','ys')):
            return sana[:-1] + 'kset'
        if tn == 40 and sana.endswith(('us','ys')):
            return sana[:-1] + 'det'
    # Käänteinen astevaihtelu: tehdas -> tehtaat, aar­re -> aarteet.
    if (tn == 41 and sana.endswith(('as','äs'))) or (tn == 48 and sana.endswith('e')):
        runko, loppu = (sana[:-2], sana[-2]*2) if tn == 41 else (sana[:-1], 'ee')
        if av:
            if av not in ASTE:
                return None
            vahva, heikko = ASTE[av]
            if not runko.endswith(heikko):
                return None
            runko = runko[:-len(heikko)] + vahva
        return runko + loppu + 't'
    return None


def koeajo():
    kansio = JUURI / 'koeajo_monikot'
    kansio.mkdir(exist_ok=True)
    vanhat = set((JUURI / 'monikot.txt').read_text(encoding='utf-8-sig').splitlines())
    uudet = set()
    with (kansio / 'raportti.tsv').open('w', encoding='utf-8') as raportti:
        print('hakusana', 'tn', 'av', 'monikko', 'tila', sep='\t', file=raportti)
        for st in ET.parse(JUURI / 'kotus-sanalista_v1.xml').iter('st'):
            sana = st.findtext('s').lower()
            for t in st.findall('t'):
                tn = int(t.findtext('tn'))
                if not 1 <= tn <= 51:
                    continue
                av = t.findtext('av', '')
                muoto = monikko(sana, tn, av)
                ruudut = ruudukkomuoto(muoto) if muoto is not None else None
                if ruudukkomuoto(sana) is None:
                    tila = 'ohitettu: kirjoitusasu'
                elif muoto is None:
                    tila = 'ohitettu: ei sääntöä'
                elif ruudut is None:
                    tila = 'ohitettu: kirjoitusasu'
                elif len(ruudut) < 4:
                    tila = 'ohitettu: lyhyt'
                else:
                    tila = 'mukana'
                    uudet.add(muoto)
                print(sana, tn, av, muoto or '', tila, sep='\t', file=raportti)
    for nimi, sanat in [('monikot_koe', uudet), ('vain_uudessa', uudet-vanhat), ('vain_vanhassa', vanhat-uudet)]:
        (kansio / (nimi+'.txt')).write_text(''.join(w+'\n' for w in sorted(sanat)), encoding='utf-8')
        print(nimi, len(sanat))


if __name__ == '__main__':
    koeajo()
