import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import lataa_monikot
import ristikkohaku
from sanamuoto import ruudukkomuoto


class Yhdysviivat(unittest.TestCase):
    def test_lataus(self):
        with tempfile.TemporaryDirectory() as tmp:
            polku = Path(tmp) / 'lista.txt'
            polku.write_text('laina-aika\nlaina-ajat\nlaina--aika\n-alku\nloppu-\na-bc\na/bcd\na-b-cd\n', encoding='utf-8')
            with patch.object(ristikkohaku, '__file__', str(polku)), patch.object(ristikkohaku, 'LISTAT', ('lista',)):
                self.assertEqual(ristikkohaku.lataa_sanat(), {'lainaaika', 'lainaajat', 'abcd'})
        self.assertIsNone(ruudukkomuoto('laina--aika'))
        self.assertEqual(len(ruudukkomuoto('laina-aika')), 9)

    def test_vienti_sailyttaa_kirjoitusasun(self):
        with tempfile.TemporaryDirectory() as tmp:
            juuri = Path(tmp)
            (juuri / 'monikot.txt').write_text('', encoding='utf-8')
            (juuri / 'kotus-sanalista_v1.xml').write_text(
                '<root><st><s>laina-aika</s><t><tn>9</tn><av>D</av></t></st>'
                '<st><s>a-a</s><t><tn>9</tn></t></st></root>', encoding='utf-8')
            with patch.object(lataa_monikot, 'JUURI', juuri):
                lataa_monikot.koeajo()
            tulos = juuri / 'koeajo_monikot'
            self.assertEqual((tulos / 'monikot_koe.txt').read_text(encoding='utf-8').splitlines(), ['laina-ajat'])
            with (tulos / 'raportti.tsv').open(encoding='utf-8', newline='') as f:
                osuma, lyhyt = csv.DictReader(f, delimiter='\t')
            self.assertEqual((osuma['hakusana'], osuma['monikko'], osuma['tila']), ('laina-aika', 'laina-ajat', 'mukana'))
            self.assertEqual(lyhyt['tila'], 'ohitettu: lyhyt')
