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

    def test_ei_arvata(self):
        self.assertIsNone(monikko('jalka', 9, '?'))
        self.assertIsNone(monikko('puhua', 52, ''))
