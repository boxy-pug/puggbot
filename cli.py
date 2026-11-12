import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from game import play
from models import Quiz
from quiz_loader import (
    get_all_categories_from_api,
    get_quiz_from_api,
    get_quiz_from_file,
    run_fzf_search_on_api,
)
from ui import get_pugg_theme


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Puggbot", description="Pugg til eksamen i terminalen"
    )

    parser.add_argument(
        "searchterm", nargs="?", metavar="SEARCHTERM", help="search for and play quiz"
    )

    parser.add_argument(
        "--file",
        type=Path,
        metavar="QUIZFILE",
        help="play quiz from local json file",
    )

    parser.add_argument(
        "--browse",
        action="store_true",
        help="browse topics, categories and choose quiz",
    )

    parser.add_argument(
        "--local",
        action="store_true",
        help="choose between local quizzes",
    )

    # parser.add_argument("--user", metavar="USERNAME", help="provide username")

    return parser.parse_args()


def main():

    # start console and stderr
    console = Console(theme=get_pugg_theme())
    err_console = Console(stderr=True)

    # Get QuizAPI API key from .env, exit program if not found.
    load_dotenv()
    quizapi_key = os.getenv("QUIZAPI_KEY", default=None)

    if quizapi_key is None:
        err_console.print("Please provide a 'QUIZAPI_KEY' in .env")
        sys.exit(1)

    # Load arguments from command line input
    args = parse_args()

    if args.file:
        quiz_path = args.file

        # quiz = None
        # todo: json.JSONDEcoderError, OSError
        try:
            quiz = get_quiz_from_file(quiz_path)
        except Exception as exc:
            err_console.print(
                f"Error trying to load local quiz from {quiz_path}: {exc}"
            )
            return 1

        if quiz:
            result = play(quiz, console)

    elif args.browse:
        if args.browse:
            topics = get_all_categories_from_api()
            for topic in topics:
                print(f"{topic["name"]}")
                for category in topic["categories"]:
                    print(f"\t{category["name"]}")
                # print(topic["tags"])

    else:
        search_term = args.searchterm
        if not search_term:
            search_term = (
                input(
                    "Welcome to Pugg, what do you want to quiz about today?\nEnter search term: "
                )
                .strip()
                .lower()
            )

        quiz_id = run_fzf_search_on_api(quizapi_key, search_term)
        quiz = get_quiz_from_api(quizapi_key, quiz_id)
        result = play(quiz, console)


if __name__ == "__main__":
    main()
