from dataclasses import dataclass
from enum import Enum


class Difficulty(Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    EXPERT = "EXPERT"


class QuestionType(Enum):
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TRUE_FALSE = "TRUE_FALSE"
    OPEN_ENDED = "OPEN_ENDED"


@dataclass
class Quiz:
    id: str
    title: str  # max 200 chars
    categoryName: str
    difficulty: Difficulty
    tags: list[str]  # max 20 tags, max 50 chars each
    questionCount: int
    plays: int
    questions: list[Question]
    topic: str | None = ""
    description: str | None = ""  # max 2000 chars

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            categoryName=data["categoryName"],
            difficulty=Difficulty(data["difficulty"]),
            tags=data["tags"],
            questionCount=data["questionCount"],
            plays=data["plays"],
            topic=data.get("topic", ""),
            questions=[Question.from_dict(a) for a in data["questions"]],
        )


@dataclass
class Question:
    id: str
    text: str
    type: QuestionType
    difficulty: Difficulty
    answers: list[Answer]
    explanation: str | None = ""

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            text=data["text"],
            type=QuestionType(data["type"]),
            difficulty=Difficulty(data["difficulty"]),
            answers=[Answer.from_dict(q) for q in data["answers"]],
            explanation=data.get("explanation", ""),
        )


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
