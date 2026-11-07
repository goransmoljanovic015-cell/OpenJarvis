# Od teme do paketa za pregled

Ovaj proces pravi stvarne carousel slike i tekst. Ima red od sedam različitih
tema, istraživačke bilješke, AI pisanje i uredničku AI provjeru, ograničene
pokušaje dorade, PNG izvoz i ručno odobrenje konkretne verzije paketa.

## Pokretanje bez AI ključa

Iz korijena repozitorija, Python 3.10 ili noviji:

```powershell
python -m pip install -r .ig-growth/requirements-content.txt
python .ig-growth/generate.py build --id 02-gmail-filter
```

Otvori `.ig-growth/packages/02-gmail-filter/index.html`. U folderu su šest
slika 1080 × 1350, `pregled.jpg`, `opis.txt`, `alternativni-tekst.txt`,
`content.json`, `sources.json`, `izvori.md`, kopija brenda i `status.json`.
Primjer je urednički pripremljen prema aktuelnom Gmail vodiču; nije AI izlaz
predstavljen kao stvarno korisničko iskustvo. Primjer ostaje za tvoje odobrenje.

## Automatsko pisanje novih tema

Postavi ključ u okruženje, nikad u JSON ili Git. Izaberi model kojem tvoj
račun ima pristup i koji podržava Chat Completions JSON format:

```powershell
$env:OPENAI_API_KEY = "tvoj-api-kljuc"
$env:IG_MODEL = "ime-modela"
python .ig-growth/generate.py build --refresh-sources
```

Model se ne bira automatski. API pozivi mogu imati trošak. Podržan je i
kompatibilan servis kroz `OPENAI_BASE_URL` ili `--base-url` i njegov ključ.
OpenAI klijent koristi isti obrazac kao cloud engine ovog repozitorija.
Ključ se ne uključuje u prompt ili paket.

Prvi poziv piše sadržaj. Drugi zasebno ocjenjuje slijede li tvrdnje iz izvora.
Prije svakog poziva validiraju se izvor i struktura. Poslije pisanja provjeravaju
se reference, citati, dužina, rizične brojke i izmišljena lična iskustva. Ako
provjera ne prođe, AI dobije greške i ponovo pokuša, najviše tri puta po temi
(`--attempts 1` do `5`). Prelom teksta i veličina fonta provjeravaju se stvarnim
mjerenjem. Predugačak tekst se vraća na doradu umjesto nečitljivog izvoza.

Za jednu novu temu:

```powershell
python .ig-growth/generate.py build --id 03-prije-poslije --refresh-sources
```

## Brend, red i istraživanje

- `content/brand.json`: jezik, publika, ton, urednička pravila i boje.
- `content/queue.json`: zasebni ID, tema, cilj, format i izvori po objavi.
- `content/sources.json`: zvanični URL-ovi, datum provjere, tekst i izvori dokaza.
- `content/sample-gmail.json`: primjer koji radi bez mreže i AI servisa.

Za novu temu dodaj jedinstven ID i relevantne izvore. Izostavi `content_file`
za AI pisanje; navedi ga za vlastiti već napisani JSON. Format je vidljiv u
primjeru. Ne pretvaraj naslov u „studiju slučaja” bez stvarnih podataka.
Srijeda je ovdje carousel umjesto Reela, a subota praktičan primjer umjesto
nepotvrđene priče o zaradi.

`--refresh-sources` preuzima **unaprijed odabrane URL-ove**, uklanja skripte i
HTML, te sprema tekst, datum preuzimanja i hash odgovora. Ne pretražuje cijeli
internet i ne prijavljuje neuspjelo preuzimanje kao provjeren izvor. Ograničenje
je 2 MB po stranici, 20 sekundi po zahtjevu i 14.000 znakova konteksta po izvoru.
Izvori stariji od 30 dana ili s budućim datumom blokiraju izvoz i odobrenje.
Stranice koje traže JavaScript ili blokiraju pristup zahtijevaju ručno čitanje
i ažurirane bilješke. Za velike stranice `start_at` određuje početni naslov.

Doslovan citat dokazuje da tekst postoji u izvoru; sam po sebi ne dokazuje da
je izvedeni zaključak tačan. AI provjera takođe može pogriješiti. Zato paket
dobije `ready_for_review`, nikad automatsko uredničko odobrenje.

## Odobrenje, verzije i ponovni pokušaji

Pregledaj slike, pravopis, sve tvrdnje i dokaze pa zabilježi odobrenje:

```powershell
python .ig-growth/generate.py approve .ig-growth/packages/02-gmail-filter --reviewer Goran
```

Odobrenje bilježi ime i UTC vrijeme. Hash svake datoteke veže ga za tačno
pregledan sadržaj. Izmjena teksta ili slike blokira odobrenje i ponovno
pokretanje. Promijenjeni brend, tema, izvori ili model zahtijevaju novi ID ili
novi izlazni folder, npr. `--output .ig-growth/packages-v2`. Postojeći odobreni
paket se ne prepisuje. Neizmijenjen paket se vraća iz cachea.

`batch-report.json` pokazuje status svake obrađene teme. Neuspjeh jedne teme ne
zaustavlja druge, a izlazni kod je nenulti ako barem jedna zahtijeva pažnju.
Privremeni izvoz postaje paket tek nakon što su sve slike i datoteke gotove.
Sedam naslova se više ne mapira na isti sadržaj. Dupli naslovi paketa se odbijaju.

## Granice ove verzije

Ovo implementira proizvodnju i urednički red za carousel pakete. Ne povezuje
Instagram, Facebook ili X račune, ne zakazuje objave na mrežama, ne šalje
poruke i ne preuzima stvarne metrike. Takve radnje zahtijevaju zaseban adapter,
autorizovan račun i važeći pristup platformi. `approved` znači spremno za
objavljivanje, ne „objavljeno”.

Nema video/glas generatora za Reels. Dizajn koristi tipografiju i boje brenda;
nema automatski dodanog logotipa niti AI generisanih ilustracija. Na Windowsu,
Linuxu i macOS-u traži Arial ili DejaVu Sans; vlastite Unicode TTF datoteke
možeš zadati kroz `IG_FONT_REGULAR` i `IG_FONT_BOLD`.

## Provjera implementacije

```powershell
python -m unittest discover -s .ig-growth/tests -v
```

Testovi ne pozivaju plaćeni servis. Provjeravaju stvaran izvoz slika, izvore,
nedokazane tvrdnje, zastarjelost, doradu kroz ograničen broj pokušaja, izolaciju
neuspjele teme, nečitljiv tekst, cache i izmjene poslije odobrenja. AI putanja
koristi kontrolisani testni provider; produkcijski AI poziv zahtijeva stvarni ključ.

Referentni izvori za uključene bilješke:
[Gmail filteri](https://support.google.com/mail/answer/6579?hl=en),
[upute modelu](https://developers.openai.com/api/docs/guides/prompt-engineering),
[ponavljajući događaji](https://support.google.com/calendar/answer/37115?hl=en).
