"""SVG-luonnos: vihjeet vastausten edellä, jaetut vihjeruudut tarvittaessa."""
import json
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import ImageFont
from piirra_puzzle2 import VIHJEET
from ristikkohaku import sanapaikat

JUURI = Path(__file__).resolve().parent
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def piirra():
    data = json.loads((JUURI / 'puzzle2.json').read_text(encoding='utf-8-sig'))
    grid = [['#']*data['columns'] for _ in range(data['rows'])]
    for cell in data['data']:
        if cell['type'] == 'input':
            grid[cell['row']][cell['col']] = cell['letter'].upper()
    grid[10][8] = 'U'
    slots = sanapaikat(grid)
    placements = defaultdict(list)
    for slot, (word, clue) in zip(slots, VIHJEET, strict=True):
        assert ''.join(grid[r][c] for r,c in slot) == word
        r,c = slot[0]
        horizontal = slot[1][0] == r
        source = (r,c-1) if horizontal else (r-1,c)
        assert min(source)>=0 and grid[source[0]][source[1]]=='#'
        placements[source].append((word, '' if word=='PIKSELIMÖSSÖ' else clue, horizontal, slot[0]))
    root = ET.Element(f'{{{NS}}}svg', {'viewBox':'0 0 1000 1700', 'width':'1000', 'height':'1700'})
    def el(name, attrs, parent=root, text=None):
        node=ET.SubElement(parent,f'{{{NS}}}{name}',{k:str(v) for k,v in attrs.items()})
        node.text=text
        return node
    el('title',{},text='Ristikko – sisäiset tekstivihjeet')
    el('desc',{},text='10 × 17 ruutua. Vihjeet ovat sanojen edellä. Pääkuva puuttuu. OLUT-korjaus mukana.')
    defs=el('defs',{})
    marker=el('marker',{'id':'nuoli','viewBox':'0 0 10 10','refX':9,'refY':5,'markerWidth':6,'markerHeight':6,'orient':'auto'},defs)
    el('path',{'d':'M 0 0 L 10 5 L 0 10 z','fill':'#173c53'},marker)
    for r,row in enumerate(grid):
        for c,ch in enumerate(row):
            el('rect',{'x':c*100,'y':r*100,'width':100,'height':100,'fill':'#edf1f3' if ch=='#' else 'white','stroke':'#243441','stroke-width':1.5})
    # Yhtenäinen alue on kokonaan vastausruudukon ulkopuolella.
    el('rect',{'x':0,'y':0,'width':500,'height':400,'fill':'#edf1f3','stroke':'#243441','stroke-width':1.5})
    el('text',{'x':250,'y':190,'text-anchor':'middle','font-family':'Arial, sans-serif','font-size':22,'fill':'#687984'},text='PÄÄKUVA-ALUE')
    el('text',{'x':250,'y':225,'text-anchor':'middle','font-family':'Arial, sans-serif','font-size':16,'fill':'#687984'},text='Kuva lisätään myöhemmin')
    for (r,c), clues in placements.items():
        height=100/len(clues)
        for n,(word,clue,horizontal,start) in enumerate(clues):
            x,y=c*100,r*100+n*height
            group=el('g',{'id':f'vihje-{word.lower()}'})
            el('title',{},group,text=f'{clue or "Pääkuva"} – {"vaaka" if horizontal else "pysty"}')
            if n:el('line',{'x1':x,'x2':x+100,'y1':y,'y2':y,'stroke':'#243441'},group)
            # Sovita vihje oikeilla Arial-mitoilla, katkaise myös pitkät sanat.
            lines=[]
            for size in range(21,9,-1):
                font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size)
                lines=['']
                for token in clue.split():
                    if font.getlength((lines[-1]+' '+token).strip())<=84:
                        lines[-1]=(lines[-1]+' '+token).strip()
                    else:
                        if lines[-1]:lines.append('')
                        for char in token:
                            if font.getlength(lines[-1]+char)>84:lines.append('')
                            lines[-1]+=char
                if len(lines)*(size+3)<=height-19:break
            assert len(lines)*(size+3)<=height-19,word
            clipid=f'clip-{r}-{c}-{n}'
            clip=el('clipPath',{'id':clipid},defs)
            el('rect',{'x':x+4,'y':y+3,'width':92,'height':height-13},clip)
            text=el('text',{'font-family':'Arial, sans-serif','font-size':size,'fill':'#142b3b','text-anchor':'middle','clip-path':f'url(#{clipid})'},group)
            for k,line in enumerate(lines):
                el('tspan',{'x':x+50,'y':y+(height-12-len(lines)*(size+3))/2+size+k*(size+3)},text,text=line)
            # Nuoli lähtee vihjeen omasta osasta vastaussanan alkuun.
            sr,sc=start
            if horizontal:
                d=f'M {x+87} {y+height-8} L {x+105} {y+height-8}'
            else:
                # Jaetun ruudun ylimmästä vihjeestä reitti ruudun reunaa pitkin.
                d=f'M {x+92} {y+height-8} L {x+96} {y+height-8} L {x+96} {(r+1)*100+6}'
            el('path',{'d':d,'fill':'none','stroke':'#173c53','stroke-width':1.8,'marker-end':'url(#nuoli)'},group)
    target=JUURI/'puzzle2_vihjeet.svg'
    with target.open('xb') as f:
        ET.indent(root)
        ET.ElementTree(root).write(f,encoding='utf-8',xml_declaration=True)
    assert len(placements)>0 and sum(map(len,placements.values()))==40
    ET.parse(target)
    print(target)


if __name__=='__main__':
    piirra()
