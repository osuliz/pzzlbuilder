import unittest
from unittest.mock import patch
from io import StringIO
from ohjattu_laadinta import lukittu, main, tyhja_istunto
from ristikkohaku import ratkaise, sanapaikat


class OhjattuKoe(unittest.TestCase):
    def test_kielto_on_paikallinen(self):
        b = ('....#....',)
        vasen, oikea = map(tuple, sanapaikat(b))
        self.assertEqual(ratkaise(b, {'auto', 'juna'}, paikkakiellot={vasen: {'auto'}}), ['juna#auto'])
        self.assertIsNone(ratkaise(lukittu(b, {oikea:'juna'}), {'auto','juna'}, paikkakiellot={vasen:{'auto'}}))

    def test_takaisin_palauttaa_koko_tayton_ilman_hakua(self):
        # Tekoruudukoissa myös kohdesanan ulkopuoliset kirjaimet eroavat.
        def kartta(c, sana):
            g = [c * 15 for _ in range(18)]
            g[16] = c * 6 + sana
            return g
        eka = kartta('a', 'trilogiat')
        for cmd, tulos in [('toinen', kartta('b', 'kromioida')),
                           ('oma kaatosade', TimeoutError()), ('toinen', None)]:
            with self.subTest(cmd=cmd, tulos=tulos), \
                 patch('sys.argv', ['ohjattu_laadinta.py']), \
                 patch('ohjattu_laadinta.Path.read_text', return_value='trilogiat'), \
                 patch('ohjattu_laadinta.ratkaise', side_effect=[eka, tulos]) as haku, \
                 patch('builtins.input', side_effect=[cmd,'ohje','takaisin','?','nayta','lukitse','lopeta']), \
                 patch('sys.stdout', new_callable=StringIO) as out:
                main()
                self.assertEqual(haku.call_count, 2)
                self.assertEqual(out.getvalue().count('Ohjattu täyttö:'), 2)
                self.assertIn('Lukittu: G17-O17 TRILOGIAT', out.getvalue())
                self.assertIn('18  ' + ' '.join('A'*15), out.getvalue())

    def test_suoja_hauissa_ja_historiassa(self):
        g = ['a'*15]*18
        commands = ['hae','suojaa G17-H17','takaisin','oma kaatosade',
                    'suojaa H17-I17','toinen','takaisin','vapauta G17-H17',
                    'hae','lopeta']
        with patch('sys.argv', ['ohjattu_laadinta.py']), \
             patch('ohjattu_laadinta.Path.read_text', return_value=''), \
             patch('ohjattu_laadinta.ratkaise', side_effect=[g,g,TimeoutError(),g]) as haku, \
             patch('builtins.input', side_effect=commands), \
             patch('sys.stdout', new_callable=StringIO) as out:
            main()
            self.assertIn('Ei aiempaa ehdotusta',out.getvalue())
            self.assertIn('Ristiriita ruudussa G17',out.getvalue())
            self.assertIn('Palautettu:',out.getvalue())
            self.assertEqual(haku.call_args_list[2].args[0][16][6:9], 'aaa')
            self.assertEqual(haku.call_args_list[3].args[0][16][6:9], '.aa')

    def test_kaksi_aluetta_oikealla_haulla(self):
        b = ('a##i','....','.##.','.##.')
        b = tuple(r.replace('a','.').replace('i','.') for r in b)
        p = list(map(tuple,sanapaikat(b)))
        with patch('builtins.input', side_effect=['ehdota A1-A2','ohje','hyvaksy',
                   'ehdota D1-D2','?','hyvaksy','lopeta']), patch('sys.stdout', new_callable=StringIO) as out:
            valmis = tyhja_istunto(b, {'arki','idea','raid'}, p, [], 5)
        self.assertEqual(out.getvalue().count('Tyhjä pohja:'), 2)
        self.assertEqual(valmis, ('a##i','r..d','.##.','.##.'))

    def test_omat_sanat_ja_poisto(self):
        b = ('.##.','....','.##.','.##.')
        p = list(map(tuple,sanapaikat(b)))
        cmds = ['aseta A1-A4 ARKI','aseta D1-D4 ARKI','aseta D1-D4 IDEA',
                'aseta A2-D2 AUTO','tayta','ehdota A2-D2','hyvaksy',
                'poista A1-A4','lopeta']
        with patch('builtins.input', side_effect=cmds), patch('sys.stdout', new_callable=StringIO) as out, \
             patch('ohjattu_laadinta.ratkaise', wraps=ratkaise) as haku:
            valmis = tyhja_istunto(b, {'raid'}, p, [], 5)
            self.assertEqual(haku.call_count, 2)
            self.assertEqual(haku.call_args_list[0].args[0], ('a##i','r..d','k##e','i##a'))
            self.assertIn('ARKI toistuu',out.getvalue())
            self.assertIn('Ristiriita ruudussa',out.getvalue())
            self.assertEqual(valmis, ('.##i','raid','.##e','.##a'))

    def test_pikakoe_vaihtaa_aloitusta_ja_sailyttaa_lukon(self):
        sanat = {'kaatosade','kaatolava','trilogiat'}
        # Ensimmäinen K-alkuinen haara ylittää kolmen sekunnin rajansa.
        with patch('ristikkohaku.monotonic', side_effect=[0,0,4,4,4]):
            self.assertEqual(ratkaise(('k........',), sanat, pikakoe=(2,3), takaraja=10), ['kaatosade'])
        for maara,raja in [(1,10),(2,3)]:
            with patch('ristikkohaku.monotonic', side_effect=[0,0,4,4]), self.assertRaises(TimeoutError):
                ratkaise(('k........',), sanat, pikakoe=(maara,3), takaraja=raja)

    def test_sesti_ei_hakuun_eika_omaksi_sanaksi(self):
        for sana in ('etiologisesti', 'insesti'):
            self.assertIsNone(ratkaise(('.'*len(sana),), {sana}))
        self.assertEqual(ratkaise(('.....',), {'sesti','viisi'}), ['viisi'])
        b = ('.......',)
        p = list(map(tuple,sanapaikat(b)))
        with patch('builtins.input', side_effect=['aseta A1-G1 IN-SES-TI','lopeta']), patch('sys.stdout', new_callable=StringIO) as out:
            self.assertEqual(tyhja_istunto(b,set(),p,[],5), b)
            self.assertIn('SESTI-loppuinen',out.getvalue())

    def test_lukitusristiriita(self):
        b = ('....',)*4
        p = list(map(tuple, sanapaikat(b)))
        with self.assertRaises(ValueError):
            lukittu(b, {p[0]:'auto', p[4]:'juna'})
