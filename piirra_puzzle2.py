"""Piirrä puzzle2:n ensimmäinen, reunavihjeinen PNG-luonnos."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

JUURI = Path(__file__).resolve().parent
VIHJEET = [
    ('KORI', 'KALJA-'), ('ALAN', 'SEBUN RAKAS'), ('TIIT', 'ruohoon kiinni'),
    ('KOKO', 'KUPPI-'), ('SAPARO', '-NIEKKA'), ('NEIL', 'PEART'),
    ('AASA', 'JUMALA'), ('ARKA', 'SENSITIIVINEN'), ('POST', '- MORTEM'),
    ('PAOT', 'VANKILASTA'), ('ALLI', '1. nainen / lintu'), ('NALLET', '"kolmoiset"'),
    ('ALTA', '- VISTA'), ('AMMU', '"lehmä"'), ('MYÖS', 'Lisäksi'),
    ('VIHA', 'h8'), ('ITSERAKAS', 'NARKISSOS'), ('OTSA', 'NUPISSA'),
    ('AARI', 'ala'), ('TYÖT', 'hommat'), ('NATA', 'ruohokasvi'),
    ('KATKOA', 'poikkaista'), ('OLIO', 'otus'), ('RAIKAS', 'freesi'),
    ('INTO', 'palo'), ('SNAP', '-CHAT'), ('AERO', 'Saab-malli'),
    ('PIKSELIMÖSSÖ', '[Pääkuvan vihje puuttuu]'), ('ALAT', 'ha, a'),
    ('ARAL', 'järvi'), ('AHTI', 'muinaisjumala'), ('PATA', 'maa'),
    ('OLUT', 'mallasjuoma'), ('NAAMIOT', 'maskit'), ('LIIKAA', 'yli äyräiden'),
    ('AFASIA', 'puhehäiriö'), ('MYTTY', 'vaatteista'), ('USEAT', 'monet'),
    ('VAAN', 'MUTTA'), ('HART', 'moke Joe'),
]


def piirra():
    from ristikkohaku import sanapaikat
    data = json.loads((JUURI / 'puzzle2.json').read_text(encoding='utf-8-sig'))
    grid = [['#'] * data['columns'] for _ in range(data['rows'])]
    for cell in data['data']:
        if cell['type'] == 'input':
            grid[cell['row']][cell['col']] = cell['letter'].upper()
    grid[10][8] = 'U'  # OLET -> OLUT; piilokirjain I11.
    slots = sanapaikat(grid)
    assert len(slots) == len(VIHJEET) == 40
    for slot, (word, _) in zip(slots, VIHJEET):
        assert ''.join(grid[r][c] for r, c in slot) == word
    starts = sorted({s[0] for s in slots})
    numbers = {rc: i+1 for i, rc in enumerate(starts)}
    fontdir = Path('C:/Windows/Fonts')
    def font(size, bold=False):
        return ImageFont.truetype(str(fontdir / ('arialbd.ttf' if bold else 'arial.ttf')), size)
    for solution in (False, True):
        image = Image.new('RGB', (1900, 1630), 'white')
        draw = ImageDraw.Draw(image)
        draw.text((60, 35), 'PIKSELIMÖSSÖ', font=font(44, True), fill='#192e40')
        draw.text((60, 95), 'Ratkaisu' if solution else 'Ristikko · ensimmäinen vihjeluonnos', font=font(24), fill='#4c5963')
        size, left, top = 78, 60, 175
        for r, row in enumerate(grid):
            for c, letter in enumerate(row):
                x,y = left+c*size, top+r*size
                draw.rectangle((x,y,x+size,y+size), fill='#e5e9ed' if letter=='#' else 'white', outline='#33434f', width=2)
                if letter=='#':
                    continue
                if (r,c) in numbers:
                    draw.text((x+5,y+3), str(numbers[r,c]), font=font(17), fill='#354c60')
                if solution:
                    draw.text((x+size/2,y+size/2+8), letter, anchor='mm', font=font(39,True), fill='#142c40')
        for direction, x, title in ((0,900,'VAAKA →'), (1,1390,'PYSTY ↓')):
            draw.text((x,175),title,font=font(28,True),fill='#192e40')
            y=235
            for slot, (_, clue) in zip(slots, VIHJEET):
                horizontal = slot[0][0] == slot[-1][0]
                if horizontal != (direction==0):
                    continue
                number = numbers[slot[0]]
                draw.text((x,y), str(number)+'.', font=font(23,True), fill='#192e40')
                # Wrap by rendered pixel width, retaining all punctuation.
                lines=[]; line=''
                for word in clue.split():
                    candidate=(line+' '+word).strip()
                    if line and draw.textlength(candidate,font=font(23))>380:
                        lines.append(line);line=word
                    else:line=candidate
                lines.append(line)
                for k,line in enumerate(lines):
                    draw.text((x+53,y+29*k),line,font=font(23),fill='#17232d')
                y+=max(53,29*len(lines)+17)
        draw.text((60,1540),'Harmaat ruudut eivät ole vastausruutuja. Numerot osoittavat sanan alun.',font=font(21),fill='#4c5963')
        draw.text((60,1575),'Vihjeet ovat tässä luonnoksessa ruudukon vieressä, eivät vihjeruuduissa.',font=font(21),fill='#4c5963')
        target=JUURI / ('puzzle2_ratkaisu.png' if solution else 'puzzle2_vihjeet.png')
        if target.exists():
            raise FileExistsError(target)
        image.save(target, dpi=(200,200))
        print(target)


if __name__ == '__main__':
    piirra()
