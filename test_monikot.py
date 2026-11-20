import csv
import unittest
import xml.etree.ElementTree as ET

from lataa_monikot import JUURI, monikko


class Monikkokoe(unittest.TestCase):
    def test_hakusanaparit_kotuksen_tiedoilla(self):
        odotetut = dict(aalto='aallot', talo='talot', auto='autot',
                        jalka='jalat', lintu='linnut', käsi='kädet',
                        lämmin='lämpimät', tehdas='tehtaat', varas='varkaat',
                        nainen='naiset', hame='hameet', aarre='aarteet',
                        puku='puvut', lapsi='lapset', tiili='tiilet')
        parit = set()
        for st in ET.parse(JUURI / 'kotus-sanalista_v1.xml').iter('st'):
            sana = st.findtext('s')
            if sana in odotetut:
                for t in st.findall('t'):
                    parit.add((sana, monikko(sana, int(t.findtext('tn')), t.findtext('av', ''))))
        self.assertEqual(parit, set(odotetut.items()))

    def tarkista_kotusparit(self, odotetut):
        """Odotusarvot ovat käsin valittuja, luokka ja aste luetaan XML:stä."""
        loytyneet = set()
        for st in ET.parse(JUURI / 'kotus-sanalista_v1.xml').iter('st'):
            sana = st.findtext('s')
            if sana not in odotetut:
                continue
            for t in st.findall('t'):
                tn = int(t.findtext('tn'))
                if not 1 <= tn <= 51:
                    continue
                av = t.findtext('av', '')
                loytyneet.add(sana)
                with self.subTest(sana=sana, tn=tn, av=av):
                    self.assertEqual(monikko(sana, tn, av), odotetut[sana])
        self.assertEqual(loytyneet, set(odotetut), 'Testihakusana puuttuu XML:stä.')

    def test_hyvaksytty_aika_era_001(self):
        self.tarkista_era('aika_001.tsv', '9', 'D')

    def test_hyvaksytty_aika_era_002(self):
        self.tarkista_era('aika_002.tsv', '9', 'D')

    def test_hyvaksytty_aika_era_003(self):
        self.tarkista_era('aika_003.tsv', '9', 'D', maara=69)

    def test_hyvaksytty_luokka34_era_001(self):
        self.tarkista_era('luokka34_001.tsv', '34', 'C')

    def tarkista_era(self, tiedosto, tn, av, maara=100):
        with (JUURI / 'katselmoinnit' / tiedosto).open(encoding='utf-8', newline='') as f:
            rivit = list(csv.DictReader(f, delimiter='\t'))
        self.assertEqual(len(rivit), maara)
        self.assertEqual(len({r['hakusana'] for r in rivit}), maara)
        for r in rivit:
            with self.subTest(hakusana=r['hakusana']):
                self.assertEqual(r['päätös'], 'hyväksytty')
                self.assertEqual((r['tn'], r['av']), (tn, av))
                self.assertEqual(monikko(r['hakusana'], int(r['tn']), r['av']), r['monikko'])
        self.tarkista_kotusparit({r['hakusana']: r['monikko'] for r in rivit})

    def test_aika_yhdyssanat(self):
        self.tarkista_kotusparit({
            'aika': 'ajat', 'adventtiaika': 'adventtiajat', 'hakuaika': 'hakuajat'})

    def test_luokka_34(self):
        self.tarkista_kotusparit({'onneton': 'onnettomat', 'alaston': 'alastomat'})

    def test_hopeakuusi_lahteen_luokituspoikkeus(self):
        # Lähde antaa luokan 27, vaikka puunnimen monikko ei ole hopeakuudet.
        self.tarkista_kotusparit({'hopeakuusi': 'hopeakuuset'})

    def test_valmiiksi_monikolliset_sailyvat(self):
        self.tarkista_kotusparit({
            'aivot': 'aivot', 'housut': 'housut', 'sakset': 'sakset', 'häät': 'häät'})

    def test_ei_arvata(self):
        self.assertIsNone(monikko('jalka', 9, '?'))
        self.assertIsNone(monikko('puhua', 52, ''))
