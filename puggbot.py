import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from random import choice, shuffle

import requests
from dotenv import load_dotenv
from rich import console
from rich.align import Align
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.syntax import Syntax
from rich.table import Table

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
    # categoryId: str  # can be null
    categoryName: str
    topic: str  # can be null
    difficulty: str  # Enum? "EASY", "HARD", "MEDIUM", "EXPERT"
    tags: list[str]  # max 20 tags, max 50 chars each
    questionCount: int
    plays: int
    questions: list[Question]

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            # categoryId=data["categoryId"],
            categoryName=data["categoryName"],
            topic=data["topic"],
            difficulty=data["difficulty"],
            tags=data["tags"],
            questionCount=data["questionCount"],
            plays=data["plays"],
            questions=[Question.from_dict(a) for a in data["questions"]],
        )

    def show_intro(self, console: Console):

        title = f"[bold yellow]{self.title}[/]"
        main_text = f"[dim]Difficulty: {self.difficulty}[/]"
        top_text = f"Question {0}/{self.questionCount}"

        console.print(
            quiz_panel(
                top_text,
                title,
                main_text,
                self.description,
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
            answers.append(
                question.pose(
                    console,
                    question_number,
                    self.questionCount,
                    f"[dim]{self.title}[/]",
                )
            )

        console.clear()
        self.show_results(answers, console)

        return answers

    def show_results(self, answers: list[bool], console: Console):

        top_text = "Finished quiz"
        main_text = f"Congratulations!"
        body_text = f"{sum(answers)}/{self.questionCount}"

        console.print(
            quiz_panel(
                top_text,
                f"[dim]{self.title}[/]",
                main_text,
                body_text,
                "Thank you for playing",
            )
        )


def quiz_panel(
    top: str,
    title: str,
    main: str,
    body: str,
    bottom: str,
):

    # content = Group(Align(title, align="center"), Syntax(main, "python"), Align(body))
    # consider using group

    text = f"{title}\n\n{main}\n\n{body}"

    panel = Panel(text, title=top, subtitle=bottom, width=75, padding=1, highlight=True)
    return Align(panel, vertical="middle")


@dataclass
class Question:
    id: str
    # quizId: str
    text: str
    type: str  # enum? one of: MULTIPLE_CHOICE, TRUE_FALSE, OPEN_ENDED
    difficulty: str  # Enum? "EASY", "HARD", "MEDIUM", "EXPERT"
    answers: list[Answer]
    explanation: str | None = ""  # can be null

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            # quizId=data["quizId"],
            text=data["text"],
            type=data["type"],
            difficulty=data["difficulty"],
            answers=[Answer.from_dict(q) for q in data["answers"]],
            explanation=data.get("explanation"),
        )

    def pose(
        self,
        console: Console,
        question_number: int,
        question_count: int,
        quiz_title: str,
    ) -> bool:

        shuffle(self.answers)
        answer_texts = []
        answer_numbers = []
        correct_answers = []

        for i, answer in enumerate(self.answers):
            answer_number = i + 1

            answer_numbers.append(str(answer_number))

            if answer.isCorrect:
                correct_answers.append(answer_number)

            answer_texts.append(
                f"{NUMBERING_STYLE}{answer_number}:{CLEAR_STYLE} {answer.text}"
            )

        top_text = f"Question {question_number}/{question_count}"
        bottom_text = f"Choose {"/".join(answer_numbers)} and press enter"

        console.print(
            quiz_panel(
                top_text,
                quiz_title,
                self.text,
                "\n".join(answer_texts),
                bottom_text,
            )
        )

        user_guess = IntPrompt.ask("Answer", choices=answer_numbers)

        console.clear()

        # Feedback
        feedback = generate_feedback(user_guess in correct_answers, self.difficulty)

        solution_alternatives = []

        for i, answer in enumerate(self.answers):
            answer_number = i + 1
            answer_text = f"{answer_number}: {answer.text}"
            # style the answerlist
            solution_alternatives.append(
                style_solution_answer(
                    answer_text,
                    answer_number in correct_answers,
                    user_guess == answer_number,
                )
            )

        main_text = feedback
        if self.explanation:
            main_text += "\n\n" + self.explanation

        console.print(
            quiz_panel(
                top_text,
                quiz_title,
                main_text,
                "\n".join(solution_alternatives),
                "Enter to continue or q to quit",
            )
        )

        # handle better quitting
        if input("").strip().lower() == "q":
            sys.exit(1)

        return user_guess in correct_answers


def generate_feedback(is_correct: bool, difficulty: str) -> str:
    correct_feedback = [
        "Yes, exactly!",
        "Correct!",
        "Yes, that's correct.",
        "Yep, you guessed correctly.",
    ]
    wrong_feedback = [
        "Nope, that's not right.",
        "Incorrect.",
        "Wrong...",
        "No, wrong answer.",
    ]
    if is_correct:
        return f"[green bold]{choice(correct_feedback)}[/]"
    else:
        return f"[red bold]{choice(wrong_feedback)}[/]"


def style_solution_answer(answer: str, is_correct: bool, is_user_answer: bool) -> str:
    if is_user_answer:
        if is_correct:
            return CORRECT_USER_ANSWER + answer + CLEAR_STYLE
        else:
            return INCORRECT_USER_ANSWER + answer + CLEAR_STYLE
    else:
        if is_correct:
            return CORRECT_ANSWER + answer + CLEAR_STYLE
        else:
            return INCORRECT_ANSWER + answer + CLEAR_STYLE


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
