import json
import os
import sys
from dataclasses import dataclass
from random import shuffle

import requests
from dotenv import load_dotenv

JSON_FILE = "./python-quiz.json"
CLEAR_SCREEN = "\033[2J"


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

    def show_intro(self):
        print(self.title, end="\n\n")
        print(self.description, end="\n\n")
        print(f"{self.questionCount} questions. Difficulty: {self.difficulty}")

    def play(self) -> list[bool]:
        print(CLEAR_SCREEN)
        self.show_intro()
        if input("Ready? (y/n) ").strip().lower() == "n":
            sys.exit(0)

        answers = []
        for question in self.questions:
            print(CLEAR_SCREEN)
            answers.append(question.pose())

        return answers


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

    def pose(self) -> bool:
        print(self.text, end="\n\n")
        correct = []
        shuffle(self.answers)
        for i, answer in enumerate(self.answers):
            if answer.isCorrect:
                correct.append(i + 1)
            print(i + 1, answer.text)

        print()
        user_guess = int(input("Guess an answer "))
        if user_guess in correct:
            print("yes correct")
        else:
            print("no, bad")

        print()

        print(self.explanation)
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


def load_from_file():
    with open(JSON_FILE, "r") as file:
        root_object = json.load(file)
        data = root_object["data"]

        return Quiz.from_dict(data)

    return None


def load_from_api():
    # TODO
    load_dotenv()

    print(os.getenv("TEST_KEY"))

    quizapi_key = os.getenv("QUIZAPI_KEY")

    response = requests.get(
        "https://quizapi.io/api/v2/quizzes",
        headers={
            "Authorization": f"Bearer {quizapi_key}",
            "Content-Type": "application/json",
        },
        params={
            "topic": "python",
            "limit": 5,
        },
    )

    data = response.json()
    print(f"Found {data['total']} quizzes")

    return


def main():

    quiz = load_from_file()
    answers = quiz.play()

    if all(answers):
        print("great you got them all correct")
    else:
        print("good try")

    pass


if __name__ == "__main__":
    main()
