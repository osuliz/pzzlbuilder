import unittest
from ristikkohaku import ratkaise, sanapaikat


class Vaihekokeet(unittest.TestCase):
    def test_reunapaikat_ja_ratkaisu(self):
        pohja = ('a##i', '....', '.##.', '.##.')
        paikat = sanapaikat(pohja)
        self.assertEqual(ratkaise(pohja, {'arki', 'idea', 'raid'},
                                 strategia='vaiheet', reunapaikat=[paikat[0]]),
                         ['a##i', 'raid', 'k##e', 'i##a'])
        self.assertIsNone(ratkaise(pohja, {'asti', 'idea', 'raid'},
                                  strategia='vaiheet', reunapaikat=[paikat[0]]))

    def test_osittainen_paikka_hylataan(self):
        with self.assertRaises(ValueError):
            ratkaise(('....',), {'auto'}, strategia='vaiheet',
                     reunapaikat=[[(0, 0), (0, 1)]])
