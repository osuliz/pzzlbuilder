"""Täytä valittu pohja. Esimerkki: python ristikkotyokalu.py --pohja silta5 --teksti"""
import argparse
from queue import Empty, Queue
from threading import Thread

from pohjat import POHJAT, OLETUS
from ristikkohaku import lataa_sanat, ratkaise


def hae_ratkaisu(pohja, silta):
    sanat = lataa_sanat()
    if silta:
        sanat.add(silta)  # Käyttäjän antama erisnimi kelpaa tämän ajon ajan.
    return ratkaise(pohja, sanat)


def ikkuna(pohja, silta):
    import tkinter as tk
    root = tk.Tk()
    root.title('Ristikkotyökalu – kaksi aluetta ja silta')
    ruudut = {}
    for r, rivi in enumerate(pohja):
        for c, kirjain in enumerate(rivi):
            solu = tk.Label(root, width=3, height=2, bg='#333333' if kirjain == '#' else 'white', font=('Arial', 16))
            solu.grid(row=r, column=c, padx=1, pady=1)
            if kirjain != '#':
                solu.config(text='' if kirjain == '.' else kirjain.upper())
                ruudut[r,c] = solu
    tila = tk.StringVar(value='Valmis hakuun')
    tulokset = Queue()

    def hae():
        try:
            tulokset.put((hae_ratkaisu(pohja, silta), None))
        except Exception as virhe:
            tulokset.put((None, str(virhe)))

    def nayta():
        try:
            kartta, virhe = tulokset.get_nowait()
        except Empty:
            root.after(50, nayta)
            return
        nappi.config(state='normal')
        tila.set(virhe or ('Ratkaistu' if kartta else 'Ei ratkaisua tällä sanastolla'))
        for (r,c), solu in ruudut.items():
            kirjain = (kartta or pohja)[r][c]
            solu.config(text='' if kirjain == '.' else kirjain.upper())

    def aloita():
        nappi.config(state='disabled')
        tila.set('Haetaan…')
        Thread(target=hae, daemon=True).start()
        root.after(50, nayta)

    nappi = tk.Button(root, text='Täytä ristikko', command=aloita)
    nappi.grid(row=len(pohja), columnspan=len(pohja[0]))
    tk.Label(root, textvariable=tila).grid(row=len(pohja)+1, columnspan=len(pohja[0]))
    root.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--teksti', action='store_true', help='ratkaise ilman käyttöliittymää')
    parser.add_argument('--pohja', choices=POHJAT, default=OLETUS, help='käytettävä pohja (oletus: %(default)s)')
    parser.add_argument('silta', nargs='?', type=str.lower, help='lukittu siltasana (silta4: 9, silta5: 11 kirjainta)')
    args = parser.parse_args()
    try:
        pohja = POHJAT[args.pohja].lukitse(args.silta)
    except ValueError as virhe:
        parser.error(str(virhe))
    if args.teksti:
        tulos = hae_ratkaisu(pohja, args.silta)
        print('\n'.join(tulos).upper() if tulos else 'Ei ratkaisua tällä sanastolla')
    else:
        ikkuna(pohja, args.silta)
