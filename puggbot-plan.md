# Plan: Puggbot 
*Lars Finborud, INFO132, sem02, høst 2026*

## Problem
Det begynner å nærme seg eksamenstid, og flere av eksamenene jeg skal ta i år inneholder multiple choice-oppgaver. Jeg trenger en gøy måte å pugge til eksamen på, og helst uten å forlate terminalen, selvsagt.

## API
Jeg skal bruke [QuizAPI.io](https://quizapi.io/) sin API, som har en fin free tier og inneholder mange relevante programmeringskategorier.

## Data

Her er json-objektet jeg får fra API'et, og som jeg skal bearbeide og representere i appen min:


```json
{
  "id": "ques_xyz789",
  "quizId": "quiz_abc123",
  "text": "What is the typeof null in JavaScript?",
  "type": "MULTIPLE_CHOICE",
  "difficulty": "MEDIUM",
  "explanation": "typeof null returns 'object' due to a legacy bug.",
  "category": "Programming",
  "answers": [
    { "id": "ans_1", "text": "null", "isCorrect": false },
    { "id": "ans_2", "text": "object", "isCorrect": true },
    { "id": "ans_3", "text": "undefined", "isCorrect": false },
    { "id": "ans_4", "text": "string", "isCorrect": false }
  ]
}

```

I python blir typene som følger:

```python
id: str
quizId: str
text: str
type: str # (eller egentlig Enum)
difficulty: str # eller enum
explanation: str | None # kan være None
category: str
answers: list[dict[str, str, bool]]

```

## Resultat

Brukeren skal kunne bruke dette programmet på kommandolinjen til å finne fram til relevante quizzer som er tilgjengelige gjennom QuizAPI, for eksempel ved å søke på `python` eller lignende søkeord. Deretter skal man kunne velge en enkelt quiz, og gjennomføre denne.

Når man gjennomfører en quiz blir man presentert for ett og ett spørsmål, med tilhørende nummererte svaralternativer. Man svarer ved å velge et nummer, og får deretter vite om man svarte riktig eller feil, og man får opp tilhørende forklaring, der dette er tilgjengelig. Etter at man har fullført en hel quiz får man en oversikt over hvor mange riktige svar man fikk.
