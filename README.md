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
