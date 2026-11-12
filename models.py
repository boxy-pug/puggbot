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
    description: str  # max 2000 chars, can be null
    # categoryId: str  # can be null
    categoryName: str
    topic: str  # can be null
    difficulty: Difficulty
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
            difficulty=Difficulty(data["difficulty"]),
            tags=data["tags"],
            questionCount=data["questionCount"],
            plays=data["plays"],
            questions=[Question.from_dict(a) for a in data["questions"]],
        )


@dataclass
class Question:
    id: str
    # quizId: str
    text: str
    type: QuestionType
    difficulty: Difficulty
    answers: list[Answer]
    explanation: str | None = ""  # can be null

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            # quizId=data["quizId"],
            text=data["text"],
            type=QuestionType(data["type"]),
            difficulty=Difficulty(data["difficulty"]),
            answers=[Answer.from_dict(q) for q in data["answers"]],
            explanation=data.get("explanation"),
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
