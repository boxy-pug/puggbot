from enum import Enum
from random import choice

from rich.align import Align
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.theme import Theme

from models import Difficulty

PANEL_WIDTH = 70
PANEL_PADDING = 1


class ScreenType(Enum):
    INTRO = "INTRO"
    POSE = "POSE"
    EXPLAIN = "EXPLAIN"
    RESULTS = "RESULTS"


def get_pugg_theme() -> Theme:
    return Theme(
        {
            "title": "bold yellow",
            "dim_title": "bold dim",
            "correct_user_answer": "bold black on green",
            "incorrect_user_answer": "bold black on red",
            "correct_answer": "green",
            "incorrect_answer": "red",
        }
    )


def quiz_panel(
    top: str,
    title: str,
    main: str,
    body: list[str],
    screen_type: ScreenType,
):

    # content = Group(Align(title, align="center"), Syntax(main, "python"), Align(body))
    # consider using group

    body_text = "\n".join(body)
    bottom = ""

    if screen_type == ScreenType.INTRO:
        title = f"[title]{title}[/title]"
        bottom = "Press enter when ready"

    if screen_type == ScreenType.POSE:
        title = f"[dim_title]{title}[/dim_title]"
        body_text = "\n".join(
            [f"[title]{i + 1}:[/title] {text}" for i, text in enumerate(body)]
        )
        bottom = ""
    if screen_type == ScreenType.EXPLAIN:
        title = f"[dim_title]{title}[/dim_title]"
        bottom = "Enter to continue or q to quit"

    if screen_type == ScreenType.RESULTS:
        title = f"[title]{title}[/title]"
        bottom = "Thank you for playing"

    text = f"{title}\n\n{main}\n\n{body_text}"

    panel = Panel(
        text,
        title=top,
        subtitle=bottom,
        width=PANEL_WIDTH,
        padding=PANEL_PADDING,
        highlight=True,
    )
    return Align(panel, vertical="middle")


def generate_feedback(is_correct: bool) -> str:
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


def generate_results_text(
    correct_answers: int,
    question_count: int,
    difficulty: Difficulty,
    category_name: str,
) -> str:
    correct_percentage = (correct_answers / question_count) * 100
    difficulty_string = (
        f"{difficulty.value.lower()} difficulty"
        if difficulty == Difficulty.MEDIUM
        else difficulty.value.lower()
    )

    if correct_percentage >= 100:
        return f"Wow, you got {correct_answers} of {question_count} correct answers in a {difficulty_string} quiz about {category_name}, kudos!"
    elif correct_percentage >= 80:
        return f"Well done, you got {correct_answers} of {question_count} correct answers in a {difficulty_string} quiz about {category_name}, great job!"
    elif correct_percentage >= 60:
        return f"Good, you got {correct_answers} of {question_count} correct answers in a {difficulty_string} quiz about {category_name}, not bad!"
    elif correct_percentage >= 40:
        return f"Ok, you got {correct_answers} of {question_count} correct answers in a {difficulty_string} quiz about {category_name}, I have seen worse."
    elif correct_percentage >= 20:
        return f"Well, you got {correct_answers} of {question_count} correct answers in a {difficulty_string} quiz about {category_name}, it could be worse I guess."
    else:
        return f"Ouch, you got {correct_answers} of {question_count} correct answers in a {difficulty_string} quiz about {category_name}, that's a bit embarassing actually."


def style_solution_answer(answer: str, is_correct: bool, is_user_answer: bool) -> str:
    if is_user_answer:
        if is_correct:
            return "[correct_user_answer]" + answer + "[/correct_user_answer]"
        else:
            return "[incorrect_user_answer]" + answer + "[/incorrect_user_answer]"
    else:
        if is_correct:
            return "[correct_answer]" + answer + "[/correct_answer]"
        else:
            return "[incorrect_answer]" + answer + "[/incorrect_answer]"
