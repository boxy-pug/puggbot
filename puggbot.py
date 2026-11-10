import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from random import shuffle

import requests
from dotenv import load_dotenv
from rich import console
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

JSON_FILE = "./python-quiz.json"
CLEAR_SCREEN = "\033[2J"

RED = "\033[41m"
GREEN = "\033[42m"
YELLOW = "\033[43m"
RESET = "\033[0m"

NUMBERING_STYLE = "[yellow bold]"
CORRECT_USER_ANSWER = "[bold green]"
INCORRECT_USER_ANSWER = "[bold black on red]"
CORRECT_ANSWER = "[dim green]"
INCORRECT_ANSWER = "[dim red]"
CLEAR_STYLE = "[/]"


@dataclass
class Quiz:
    id: str
    title: str  # max 200 chars
    description: str  # max 2000 chars, can be null
    category: str  # max 100 chars, legacy
    categoryId: str  # can be null
    categoryName: str
    categorySlug: str  # can be null
    topic: str  # can be null
    topicSlug: str  # can be null
    difficulty: str  # Enum? "EASY", "HARD", "MEDIUM", "EXPERT"
    tags: list[str]  # max 20 tags, max 50 chars each
    questionCount: int
    plays: int
    slug: None  # ?
    questions: list[Question]

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            category=data["category"],
            categoryId=data["categoryId"],
            categoryName=data["categoryName"],
            categorySlug=data["categorySlug"],
            topic=data["topic"],
            topicSlug=data["topicSlug"],
            difficulty=data["difficulty"],
            tags=data["tags"],
            questionCount=data["questionCount"],
            plays=data["plays"],
            slug=data["slug"],
            questions=[Question.from_dict(a) for a in data["questions"]],
        )

    def show_intro(self, console: Console):
        alternative_text = f"difficulty: {self.difficulty}"

        console.print(
            quiz_panel(
                0,
                self.questionCount,
                self.description,
                alternative_text,
                "Press enter when ready",
            )
        )

    def play(self, console: Console) -> list[bool]:
        console.clear()

        self.show_intro(console)

        input("")

        answers = []
        for i, question in enumerate(self.questions):
            console.clear()
            question_number = i + 1
            answers.append(question.pose(console, question_number, self.questionCount))

        return answers


def quiz_panel(
    question_number: int,
    question_count: int,
    main: str,
    alternatives: str,
    bottom_text: str,
):

    text = f"""{main}

{alternatives}"""

    title = f"Question {question_number}/{question_count}"
    subtitle = bottom_text if bottom_text else "Thank you"

    panel = Panel(
        text, title=title, subtitle=subtitle, width=75, padding=1, highlight=True
    )
    return Align(panel, vertical="middle")


@dataclass
class Question:
    id: str
    # quizId: str
    text: str
    type: str  # enum? one of: MULTIPLE_CHOICE, TRUE_FALSE, OPEN_ENDED
    difficulty: str  # Enum? "EASY", "HARD", "MEDIUM", "EXPERT"
    explanation: str  # can be null
    # category: str  # can be null
    order: int  # whats this?
    answers: list[Answer]

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            # quizId=data["quizId"],
            text=data["text"],
            type=data["type"],
            difficulty=data["difficulty"],
            explanation=data["explanation"],
            # category=data["category"],
            order=data["order"],
            answers=[Answer.from_dict(q) for q in data["answers"]],
        )

    def pose(self, console: Console, question_number: int, question_count: int) -> bool:
        answer_alternatives = []
        correct = []
        shuffle(self.answers)

        for i, answer in enumerate(self.answers):
            answer_number = i + 1
            if answer.isCorrect:
                correct.append(answer_number)
            answer_alternatives.append(
                f"{NUMBERING_STYLE}{answer_number}:{CLEAR_STYLE} {answer.text}"
            )

        alternative_numbers = [str(i + 1) for i in range(len(answer_alternatives))]

        bottom_text = f"Choose {"/".join(alternative_numbers)} and press enter"

        console.print(
            quiz_panel(
                question_number,
                question_count,
                self.text,
                "\n".join(answer_alternatives),
                bottom_text,
            )
        )

        user_guess = IntPrompt.ask("Answer", choices=alternative_numbers)

        console.clear()

        # Feedback
        if user_guess in correct:
            feedback = "Correct!"
        else:
            feedback = "Wrong answer..."

        solution_alternatives = []
        for i, answer in enumerate(self.answers):
            answer_number = i + 1
            answer_line = f"{answer_number}: {answer.text}"

            if user_guess == answer_number:  # style the user answer
                if answer_number in correct:
                    solution_alternatives.append(
                        (CORRECT_USER_ANSWER + answer_line + CLEAR_STYLE)
                    )
                else:
                    solution_alternatives.append(
                        (INCORRECT_USER_ANSWER + answer_line + CLEAR_STYLE)
                    )
            else:  # style the rest of alternatives
                if answer_number in correct:
                    solution_alternatives.append(
                        (CORRECT_ANSWER + answer_line + CLEAR_STYLE)
                    )
                else:
                    solution_alternatives.append(
                        (INCORRECT_ANSWER + answer_line + CLEAR_STYLE)
                    )

        main_text = feedback

        if self.explanation:
            main_text += "\n\n" + self.explanation

        console.print(
            quiz_panel(
                question_number,
                question_count,
                main_text,
                "\n".join(solution_alternatives),
                "Press enter to continue",
            )
        )

        input("")

        return user_guess in correct


@dataclass
class Answer:
    id: str
    text: str
    isCorrect: bool

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            text=data["text"],
            isCorrect=data["isCorrect"],
        )


def load_quiz_from_api(api_key: str, quiz_id: str) -> Quiz:

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    url = f"https://quizapi.io/api/v1/quizzes/{quiz_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    json_response = response.json()
    # print(f"Found {data['total']} quizzes")
    # handle what happens when no data

    return Quiz.from_dict(json_response["data"])


def load_from_file(filepath: Path) -> Quiz:

    with open(filepath, "r") as file:
        root_object = json.load(file)
        data = root_object["data"]

        return Quiz.from_dict(data)
