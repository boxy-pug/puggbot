import sys
from random import shuffle

from rich.console import Console
from rich.prompt import IntPrompt

from models import Question, Quiz
from ui import ScreenType, generate_feedback, quiz_panel, style_solution_answer


def play(quiz: Quiz, console: Console) -> list[bool]:
    console.clear()

    show_intro(quiz, console)

    input("")

    answers = []
    for i, question in enumerate(quiz.questions):
        console.clear()
        question_number = i + 1
        answers.append(
            pose(
                question,
                console,
                question_number,
                quiz.questionCount,
                quiz.title,
            )
        )

    console.clear()
    show_results(quiz, answers, console)

    return answers


def show_intro(quiz: Quiz, console: Console):

    title = quiz.title
    main_text = f"Category: {quiz.categoryName}\nDifficulty: {quiz.difficulty.value}"
    top_text = f"Question {0}/{quiz.questionCount}"

    console.print(
        quiz_panel(
            top_text,
            title,
            main_text,
            [quiz.description],
            ScreenType.INTRO,
        )
    )


def show_results(quiz: Quiz, answers: list[bool], console: Console):

    top_text = "Finished quiz"
    main_text = f"Congratulations!"
    body_text = [f"{sum(answers)}/{quiz.questionCount}"]

    console.print(
        quiz_panel(
            top_text,
            quiz.title,
            main_text,
            body_text,
            ScreenType.RESULTS,
        )
    )


def pose(
    question: Question,
    console: Console,
    question_number: int,
    question_count: int,
    quiz_title: str,
) -> bool:

    shuffled_answers = question.answers.copy()
    shuffle(shuffled_answers)

    answer_texts = []
    answer_numbers = []
    correct_answers_numbers = []

    for i, answer in enumerate(shuffled_answers):
        answer_number = i + 1

        answer_numbers.append(str(answer_number))

        if answer.isCorrect:
            correct_answers_numbers.append(answer_number)

        answer_texts.append(answer.text)

    top_text = f"Question {question_number}/{question_count}"
    bottom_text = f"Choose {"/".join(answer_numbers)} and press enter"

    console.print(
        quiz_panel(
            top_text,
            quiz_title,
            question.text,
            answer_texts,
            ScreenType.POSE,
        )
    )

    user_guess = IntPrompt.ask("Choose an answer", choices=answer_numbers)
    console.clear()

    # Feedback
    feedback = generate_feedback(
        user_guess in correct_answers_numbers, question.difficulty.value
    )

    solution_alternatives = []

    for i, answer in enumerate(shuffled_answers):
        answer_number = i + 1
        answer_text = f"{answer_number}: {answer.text}"
        # style the answerlist
        solution_alternatives.append(
            style_solution_answer(
                answer_text,
                answer_number in correct_answers_numbers,
                user_guess == answer_number,
            )
        )

    main_text = feedback
    if question.explanation:
        main_text += "\n\n" + question.explanation

    console.print(
        quiz_panel(
            top_text,
            quiz_title,
            main_text,
            solution_alternatives,
            ScreenType.EXPLAIN,
        )
    )

    # handle better quitting
    if input("").strip().lower() == "q":
        sys.exit(1)

    return user_guess in correct_answers_numbers
