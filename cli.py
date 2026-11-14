import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from game import play
from models import Quiz
from quiz_loader import (
    DataType,
    download_quiz_from_api,
    fuzzy_search,
    get_all_topics_from_api,
    get_quiz_from_api,
    get_quiz_from_file,
    get_quizzes_from_api,
)
from ui import get_pugg_theme


def get_user_search_term() -> str:
    search_term = input(
        "Welcome to Pugg, what do you want to quiz about today?\nEnter search term: "
    )

    return str(search_term)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Puggbot", description="Pugg til eksamen i terminalen"
    )

    parser.add_argument(
        "searchterm",
        nargs="?",
        metavar="SEARCHTERM",
        help="fuzzy search for quiz to play",
    )

    parser.add_argument(
        "--file",
        type=Path,
        metavar="QUIZFILE",
        help="play quiz from json file",
    )

    parser.add_argument(
        "--download",
        action="store_true",
        help="download quiz to local",
    )

    parser.add_argument(
        "--browse",
        action="store_true",
        help="browse topics, categories and choose quiz",
    )

    return parser.parse_args()


def run(args: argparse.Namespace, console: Console):
    if args.file:
        quiz_path = args.file
        quiz = get_quiz_from_file(quiz_path)

        if quiz:
            result = play(quiz, console)

    elif args.browse:
        if args.browse:
            topics = get_all_topics_from_api()
            topic_id = fuzzy_search(topics, DataType.TOPICS)

            categories = next(
                topic["categories"] for topic in topics if topic["id"] == topic_id
            )

            category_id = fuzzy_search(categories, DataType.CATEGORIES)

            quizapi_key = load_quizapi_key_from_env()
            quizzes = get_quizzes_from_api(quizapi_key, category_id=category_id)
            quiz_id = fuzzy_search(quizzes, DataType.QUIZZES)
            quiz = Quiz.from_dict(get_quiz_from_api(quizapi_key, quiz_id))
            result = play(quiz, console)

    else:
        search_term = args.searchterm
        if not search_term:
            search_term = get_user_search_term()

        quizapi_key = load_quizapi_key_from_env()
        quizzes = get_quizzes_from_api(quizapi_key, search_term=search_term)
        quiz_id = fuzzy_search(quizzes, DataType.QUIZZES)

        if args.download:
            file_name = download_quiz_from_api(get_quiz_from_api(quizapi_key, quiz_id))
            print(f"Quiz saved as {file_name}")
        else:
            quiz = Quiz.from_dict(get_quiz_from_api(quizapi_key, quiz_id))
            result = play(quiz, console)


def load_quizapi_key_from_env() -> str:
    # Get QuizAPI API key from .env, exit program if not found.
    load_dotenv()
    quizapi_key = os.getenv("QUIZAPI_KEY", default=None)

    if not quizapi_key:
        raise RuntimeError("Please provide a 'QUIZAPI_KEY' in .env")

    return quizapi_key


def main():

    # start console and stderr
    console = Console(theme=get_pugg_theme())
    err_console = Console(stderr=True)

    # Load arguments from command line input
    args = parse_args()

    try:
        run(args, console)
    except Exception as exc:
        err_console.print(f"Error trying to play pugg: {exc}")
        return 1


if __name__ == "__main__":
    main()
