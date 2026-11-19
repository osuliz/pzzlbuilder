"""Valittavat siltapohjat. Siltaruudut luetellaan sanan lukusuunnassa."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Siltapohja:
    rivit: tuple[str, ...]
    silta: tuple[tuple[int, int], ...]

    def lukitse(self, sana=None):
        if sana is None:
            return self.rivit
        sana = sana.lower()
        if len(sana) != len(self.silta) or any(c not in 'abcdefghijklmnopqrstuvwxyzåäö' for c in sana):
            raise ValueError(f'Siltasanassa pitää olla tasan {len(self.silta)} kirjainta (A–Z, Å, Ä, Ö).')
        kartta = [list(rivi) for rivi in self.rivit]
        for (r, c), kirjain in zip(self.silta, sana, strict=True):
            kartta[r][c] = kirjain
        return tuple(''.join(rivi) for rivi in kartta)


def pystysilta(koko, sarake):
    alue = ('.' * koko,) * koko
    valirivi = '#' * sarake + '.' + '#' * (koko - sarake - 1)
    rivit = alue + (valirivi,) + alue
    return Siltapohja(rivit, tuple((r, sarake) for r in range(len(rivit))))


OLETUS = 'silta4'
POHJAT = {'silta4': pystysilta(4, 1), 'silta5': pystysilta(5, 2)}
