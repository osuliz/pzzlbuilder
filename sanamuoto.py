"""Sanaston kirjoitusasun muunnos ristikon kirjainruuduiksi."""
import re

KIRJOITUSASU = re.compile(r'[a-zåäö]+(?:-[a-zåäö]+)*')


def sesti_loppuinen(sana):
    return sana.lower().replace('-', '').endswith('sesti')


def ruudukkomuoto(sana):
    """Palauta ruutukirjaimet tai None. Kutsuja tarkistaa pituuden."""
    sana = sana.lower()
    if not KIRJOITUSASU.fullmatch(sana):
        return None
    return sana.replace('-', '')
