# Käyttäjän hyväksyntä

Kerro ennen jokaista toimea, mitä aiot tehdä, ja odota käyttäjän nimenomaista hyväksyntää. Tämä koskee myös hakemiston listaamista, tiedostojen lukemista, komentojen ja testien ajamista sekä tiedostojen muuttamista. Ilman vahvistusta voit keskustella ja tehdä ehdotuksia, mutta et käyttää työkaluja.

## Ristikon säännöt

- Tavoitteena on suomenkielinen ristikko, jossa vihje voi olla kuva tai teksti. Kokonaisen vastauksen vähimmäispituus on neljä kirjainta. Pitkä vastaus voi kulkea usean alueen läpi.
- Hyväksy perusmuotoiset sanat, myös adjektiivit, sekä nominatiivin monikot. Verbeistä hyväksytään vain perusmuoto (esim. HUOLIA), ei persoonamuotoja (esim. HUOLIT) edes preesensissä. Henkilö- ja brändinimet käyvät taivuttamattomina.
- Tarkista kaikki vaaka- ja pystysuorat vastaukset, myös kokonaan risteyksistä syntyneet. Älä käytä samaa vastausta kahdesti. Sanalistaosuma ei yksin takaa oikeaa sanamuotoa.

## Sovelluksen rakenne

- `ristikkotyokalu.py` on käyttöliittymän ja tekstiajon käynnistyspiste. `ristikkohaku.py` sisältää koepohjan, sanalistojen latauksen ja haun.
- Nykyisessä koepohjassa kaksi 4×4-aluetta yhdistyy yhdellä 9-kirjaimisella pystysanalla. Nämä mitat eivät ole ristikon yleisiä sääntöjä. Parametrina annettu siltasana hyväksytään vain kyseiseen ajoon; sitä ei tallenneta sanalistaan.
- Haussa käytetään tiedostoja `kaikkisanat.txt`, `monikot.txt`, `erisnimet.txt`, `brandit.txt`, `eng_julkkikset.txt` ja `fi_julkkikset.txt`. `kotus-sanalista_v1.xml` on monikkogeneraattorin lähde, ei haun sanalista.

## Sanaston laadunvarmistus

- `lataa_monikot.py` lukee taivutusluokan (`tn`) ja astevaihtelutunnuksen (`av`) samasta XML:n `t`-elementistä. Jos sääntöä ei tunneta, raportoi tapaus sen sijaan, että arvaisit muodon.
- Tarkista hakusanan ja monikon pari: esimerkiksi `varas → varkaat`, ei `varaat`, vaikka jälkimmäinenkin on suomen sana.
- Koeajon tulokset kuuluvat kansioon `koeajo_monikot/`. Sen `vain_vanhassa.txt` on erotuslista, ei poistoluettelo. Älä korvaa käytössä olevaa `monikot.txt`:tä koelistalla ilman erillistä hyväksyntää.

## Testaus

Suorita projektin juuresta vasta käyttäjän hyväksynnän jälkeen:

- `python -m unittest test_ristikkohaku test_monikot` — tarkistaa ristikkohaun ja monikkogeneraattorin testit.
- `python ristikkotyokalu.py konnevesi --teksti` — kokeilee täyttöä ilman käyttöliittymää. Tarkista, että toinen sarake muodostaa sanan KONNEVESI; muu täyttö voi vaihdella sanaston muuttuessa.
