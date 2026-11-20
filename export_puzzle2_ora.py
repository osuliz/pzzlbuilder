"""Build an editable GIMP pilot, preserving puzzle2.json coordinates and answers."""
import json
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from random import Random
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_STORED

from PIL import Image, ImageColor, ImageDraw, ImageFont
from piirra_puzzle2 import VIHJEET
from ristikkohaku import sanapaikat

ROOT = Path(__file__).resolve().parent
INK = '#193346'
SCALE = 3  # Raster pixels per logical pixel in the player JSON.


def png(im):
    buf = BytesIO()
    im.save(buf, 'PNG')
    return buf.getvalue()


def label(text, width, height):
    im = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(im)
    for size in range(13*SCALE, 6*SCALE-1, -1):
        font = ImageFont.load_default(size=size)
        lines = ['']
        for word in text.split():
            trial = (lines[-1] + ' ' + word).strip()
            if font.getlength(trial) <= width-4*SCALE:
                lines[-1] = trial
            else:
                if lines[-1]:
                    lines.append('')
                for ch in word:
                    if font.getlength(lines[-1]+ch) > width-4*SCALE:
                        lines.append('')
                    lines[-1] += ch
        block = '\n'.join(lines)
        l,t,r,b = draw.multiline_textbbox((0,0), block, font=font, spacing=SCALE, align='center')
        if r-l <= width-2*SCALE and b-t <= height-2*SCALE:
            draw.multiline_text(((width-r+l)//2-l,(height-b+t)//2-t),block,font=font,fill=INK,spacing=SCALE,align='center')
            return im
    raise ValueError(f'Clue does not fit: {text}')


def export():
    data = json.loads((ROOT/'puzzle2.json').read_text(encoding='utf-8-sig'))
    cols, rows = data['columns'], data['rows']
    w,h = data['imgwidth']*SCALE, data['imgheight']*SCALE
    cw,ch = w//cols,h//rows
    assert (cw*cols,ch*rows)==(w,h)
    grid = [['#']*cols for _ in range(rows)]
    for cell in data['data']:
        if cell['type']=='input':
            grid[cell['row']][cell['col']] = cell['letter'].upper()
    clues = dict(VIHJEET)
    clues['OLET'] = 'Sinä ___'  # JSON original; previous PNG draft used OLUT instead.
    sites = defaultdict(list)
    for slot in sanapaikat(grid):
        word = ''.join(grid[r][c] for r,c in slot)
        r,c = slot[0]; across = slot[1][0]==r
        rr,cc = (r,c-1) if across else (r-1,c)
        assert min(rr,cc)>=0 and grid[rr][cc]=='#'
        sites[rr,cc].append((f'{chr(65+c)}{r+1}', across, 'Pääkuva' if word=='PIKSELIMÖSSÖ' else clues[word]))
    bg = Image.new('RGBA',(w,h),'white'); fills = ImageDraw.Draw(bg)
    lines = Image.new('RGBA',(w,h)); pen = ImageDraw.Draw(lines)
    for r,row in enumerate(grid):
        for c,letter in enumerate(row):
            rect = (c*cw,r*ch,(c+1)*cw-1,(r+1)*ch-1)
            if letter=='#': fills.rectangle(rect,fill='#edf1f3')
            if r<4 and c<5:
                assert letter=='#' and (r,c) not in sites
            else:
                pen.rectangle((rect[0],rect[1],rect[2],rect[1]+SCALE-1),fill=INK)
                pen.rectangle((rect[0],rect[1],rect[0]+SCALE-1,rect[3]),fill=INK)
    pen.rectangle((0,0,w-1,h-1),outline=INK,width=SCALE)
    layers = [('Background',bg,0,0)]  # bottom to top
    # An editable abstract pixel mosaic for the main-picture answer, not a stock photo.
    rng = Random(42); mosaic = Image.new('RGBA',(20,16))
    palette = ['#524b24','#6abe30','#5fcde4','#3f3f74','#d95763','#eec39a','#9badb7']
    mosaic.putdata([ImageColor.getcolor(rng.choice(palette),'RGBA') for _ in range(320)])
    layers.append(('Main picture - pixel mosaic',mosaic.resize((5*cw-12*SCALE,4*ch-12*SCALE),Image.Resampling.NEAREST),6*SCALE,6*SCALE))
    for (r,c),entries in sites.items():
        for i,(start,across,text) in enumerate(entries):
            x,y=c*cw,r*ch+i*ch//len(entries); bottom=r*ch+(i+1)*ch//len(entries)
            if i: pen.line((x,y,x+cw-1,y),fill=INK,width=SCALE)
            name = start+(' across' if across else ' down')
            layers.append(('Clue '+name,label(text,cw,bottom-y),x,y))
    layers.append(('Grid',lines,0,0))
    preview = Image.new('RGBA',(w,h)); stackroot=ET.Element('image',w=str(w),h=str(h),version='0.0.3',name='Puzzle 2'); stack=ET.SubElement(stackroot,'stack')
    for _,im,x,y in layers:
        assert 0<=x<=w-im.width and 0<=y<=h-im.height
        preview.alpha_composite(im,(x,y))
    dest=ROOT/'gimp_pilot'; dest.mkdir(exist_ok=True); ora=dest/'puzzle2-3x.ora'; flat=dest/'puzzle2-3x-preview.png'
    if ora.exists() or flat.exists(): raise FileExistsError('Pilot outputs already exist; preserve edited files.')
    with ZipFile(ora,'x') as z:
        z.writestr('mimetype','image/openraster',compress_type=ZIP_STORED)
        for i,(name,im,x,y) in enumerate(reversed(layers)):
            src=f'data/{i:03}.png'; z.writestr(src,png(im)); ET.SubElement(stack,'layer',name=name,src=src,x=str(x),y=str(y))
        z.writestr('stack.xml',ET.tostring(stackroot,encoding='utf-8',xml_declaration=True)); z.writestr('mergedimage.png',png(preview))
        thumb=preview.copy(); thumb.thumbnail((256,256)); z.writestr('Thumbnails/thumbnail.png',png(thumb))
    preview.save(flat)
    # Read back actual layer offsets and stack order, not just the merged preview.
    with ZipFile(ora) as z:
        check=Image.new('RGBA',(w,h)); nodes=ET.fromstring(z.read('stack.xml')).findall('stack/layer')
        for node in reversed(nodes):
            im=Image.open(BytesIO(z.read(node.get('src')))); check.alpha_composite(im,(int(node.get('x')),int(node.get('y'))))
        assert check.tobytes()==Image.open(flat).tobytes()
    print(f'{ora}: {len(nodes)} layers, no arrows, {w}x{h}; preview verified.')


if __name__=='__main__':
    export()
