import unittest
from pohjat import POHJAT
from ristikkohaku import Mittarit, POHJA, ratkaise, sanapaikat, tarkista_pohja


class Siltakoe(unittest.TestCase):
    rivit = ('auer', 'alla', 'ralf', 'ikea', '#e##', 'aste', 'ukot', 'muro', 'asia')
    sanat = set(rivit[:4] + rivit[5:]) | {'aari', 'elle', 'rafa', 'auma', 'tori', 'etoa', 'ulakeskus'}

    def test_geometria(self):
        self.assertEqual(sorted(map(len, sanapaikat(POHJA))), [4]*14 + [9])

    def test_silta5(self):
        malli = POHJAT['silta5']
        self.assertEqual(sorted(map(len, sanapaikat(malli.rivit))), [5]*18 + [11])
        self.assertEqual(tarkista_pohja(malli.rivit), {
            'sanapaikkoja': 19, 'yhtenaisia_osia': 1,
            'piilokirjaimet': [(5, 2)], 'piiloparit': []})
        lukittu = malli.lukitse('RISTISANOJA')
        self.assertEqual(''.join(r[2] for r in lukittu), 'ristisanoja')
        with self.assertRaises(ValueError):
            malli.lukitse('konnevesi')

    def test_sillan_piilo(self):
        self.assertEqual(tarkista_pohja(POHJA), {
            'sanapaikkoja': 15, 'yhtenaisia_osia': 1,
            'piilokirjaimet': [(4, 1)], 'piiloparit': []})

    def test_pitkan_sillan_piilopari(self):
        raportti = tarkista_pohja(POHJA[:4] + ('#.##',) + POHJA[4:])
        self.assertEqual(raportti['yhtenaisia_osia'], 1)
        self.assertEqual(raportti['piiloparit'], [((4, 1), (5, 1))])

    def test_irralliset_alueet(self):
        raportti = tarkista_pohja(POHJA[:4] + ('####',) + POHJA[5:])
        self.assertEqual(raportti['yhtenaisia_osia'], 2)
        self.assertEqual(raportti['piilokirjaimet'], [])

    def test_idea_raid(self):
        pohja = ('a##i', '....', '.##.', '.##.')
        sanat = {'arki', 'idea', 'raid'}
        for strategia in ('nykyinen', 'reunat', 'pitkat'):
            with self.subTest(strategia=strategia):
                self.assertEqual(ratkaise(pohja, sanat, strategia=strategia),
                                 ['a##i', 'raid', 'k##e', 'i##a'])
                # IDEA ja RAID yhä tarjolla, mutta RAIDin R ei sovi ASTIn S:ään.
                self.assertIsNone(ratkaise(pohja, {'asti', 'idea', 'raid'}, strategia=strategia))

    def test_mittarit(self):
        m = Mittarit()
        self.assertEqual(ratkaise(POHJA, self.sanat, mittarit=m), ratkaise(POHJA, self.sanat))
        self.assertGreaterEqual(m.valinnat, m.peruutukset)
        m = Mittarit()
        self.assertIsNone(ratkaise(('k...',), set(), mittarit=m))
        self.assertEqual(m.umpikujat, {(0, 'k...'): 1})
        with self.assertRaises(TimeoutError):
            ratkaise(POHJA, self.sanat, takaraja=0)

    def test_pitkat_ratkeaa(self):
        tulos = ratkaise(POHJA, self.sanat, strategia='pitkat')
        self.assertIsNotNone(tulos)
        self.assertEqual({''.join(tulos[y][x] for y,x in p) for p in sanapaikat(POHJA)}, self.sanat)
        self.assertIsNone(ratkaise(POHJA, self.sanat - {'ulakeskus'}, strategia='pitkat'))

    def test_ratkeaa(self):
        tulos = ratkaise(POHJA, self.sanat)
        self.assertIsNotNone(tulos)
        self.assertEqual(''.join(r[1] for r in tulos), 'ulakeskus')
        self.assertEqual({''.join(tulos[y][x] for y,x in p) for p in sanapaikat(POHJA)}, self.sanat)

    def test_silta_ei_sovi(self):
        self.assertIsNone(ratkaise(POHJA, self.sanat - {'ulakeskus'} | {'xxxxxxxxx'}))

    def test_valmiit_tarkistetaan(self):
        self.assertIsNone(ratkaise(self.rivit, self.sanat - {'ulakeskus'}))

    def test_virheellinen_pohja(self):
        for pohja in [('....', '.....'), ('...',)*4]:
            with self.assertRaises(ValueError):
                sanapaikat(pohja)
