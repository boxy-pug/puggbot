# Pugg

Quiz-app i terminalen. Fuzzy søk eller bla gjennom kategorier, last ned og spill. 

## Hvorfor?
En morsommere måte å øve til multiple choice eksamen på, uten å forlate terminalen.

## Hvordan?
 Henter quizzer fra QuizAPI.io. Du kan finne en relevant quiz ved å søke eller bla gjennom kategorier. Du får ett spørsmål om gangen, du svarer med et nummer og får deretter se fasit og en kort forklaring. Til slutt ser du hvor mange spørsmål du greide.

## Installer
Aktiver et [virtuelt miljø](https://www.geeksforgeeks.org/python/create-virtual-environment-using-venv-python/) og installer eksterne python biblioteker med pip:
```bash
# cd til root dir
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Gå til [QuizAPI](quizapi.io), lag en gratis konto, opprett og kopier en api-nøkkel, og putt denne i `.env`, som du kan lage slik:

```bash
cp .env.example .env
# bytt ut nøkkel i .env
```

Du trenger kommandolinjeverktøyet `fzf` i path for at browse og search skal fungere, se [hvordan fzf installeres her](https://junegunn.github.io/fzf/installation/).


## Usage
```bash
usage: Puggbot [-h] [--file QUIZFILE] [--download] [--browse] [SEARCHTERM]

Pugg til eksamen i terminalen

positional arguments:
  SEARCHTERM       fuzzy search for quiz to play

options:
  -h, --help       show this help message and exit
  --file QUIZFILE  play quiz from json file
  --download       download quiz to local
  --browse         browse topics, categories and choose quiz
```

## Dette har jeg lært
### Dataclasses
En dataclass er en type klasse som er fin å bruke for objekter som primært er databeholdere. Det er enkelt å definere klassen og hvilke datafelter den skal ha, og du slipper å skrive en egen __init__, @dataclass lager dette for deg. 

### Metode vs. vanlig funksjon
Jeg begynte med å definere metoder på Quiz-objektet som quiz.play(), quiz.show_intro() osv. Jeg valgte senere å flytte disse til sin egen modul (game.py) og heller sende quiz inn som et vanlig parameter til disse funksjonene, altså play(quiz). Definert som en metode kommer objektet automatisk inn som self, mens som en funksjon utenfor klassen må man sende det inn selv.

Det er egentlig uklart for meg hva som ville vært fordelen med å definere play som en metode på Quiz vs. en funksjon i en annen modul. Det virker ihvertfall ryddig for meg å ha datamodellene Quiz, Question og Answer i en modul, og ikke blande dette med gameplay logic som jeg nå har samlet i game.py.
