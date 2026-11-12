import argparse
import os
import subprocess
import sys
from pathlib import Path
from pprint import pprint

import requests
from dotenv import load_dotenv
from rich.console import Console

from puggbot import Quiz
from quizloader import (
    get_all_categories_from_api,
    get_quiz_from_api,
    get_quiz_from_file,
    search_quiz_from_api,
)
from rich_formatting import format_quiz_search_line


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Puggbot", description="Pugg til eksamen i terminalen"
    )

    parser.add_argument("searchterm", nargs="?", metavar="SEARCHTERM")

    parser.add_argument(
        "--local",
        type=Path,
        metavar="QUIZ",
        help="play quiz from json file",
    )

    parser.add_argument("--user", metavar="USERNAME", help="provide username")

    parser.add_argument(
        "--browse",
        action="store_true",
        help="browse topics, categories and choose quiz",
    )

    return parser.parse_args()


def get_quiz_id_from_search_line(search_line: str) -> str:
    return search_line.split()[-1].strip()


def run_fzf_search(api_key: str, search_term: str) -> str:

    quizzes = search_quiz_from_api(api_key, search_term)
    quizzes_line_formatted = "\n".join(
        [format_quiz_search_line(quiz) for quiz in quizzes]
    )

    # Let user choose a quiz using fzf as subprocess
    picked = subprocess.run(
        ["fzf"], input=quizzes_line_formatted, stdout=subprocess.PIPE, text=True
    )

    # Get quiz id from the full search line
    quiz_id = get_quiz_id_from_search_line(picked.stdout)
    print(f"id is {quiz_id}")

    return quiz_id


def main():

    # start console and stderr
    console = Console()
    err_console = Console(stderr=True)

    # Get QuizAPI API key from .env, exit program if not found.
    load_dotenv()
    quizapi_key = os.getenv("QUIZAPI_KEY", default=None)

    if quizapi_key is None:
        err_console.print("Please provide a 'QUIZAPI_KEY' in .env")
        sys.exit(1)

    # Load arguments from command line input
    args = parse_args()

    if args.local:
        quiz_path = args.local

        quiz = None

        # todo: json.JSONDEcoderError, OSError
        try:
            quiz = get_quiz_from_file(quiz_path)
        except Exception as exc:
            err_console.print(
                f"Error trying to load local quiz from {quiz_path}: {exc}"
            )
            return 1

        if quiz:
            result = quiz.play(console)

    elif args.browse:
        if args.browse:
            topics = get_all_categories_from_api()
            for topic in topics["data"]:
                print(f"{topic["name"]} - {topic["slug"]}")
                for category in topic["categories"]:
                    print(f"\t{category["name"]} - {category["slug"]}")
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

        quiz_id = run_fzf_search(quizapi_key, search_term)
        quiz = get_quiz_from_api(quizapi_key, quiz_id)
        result = quiz.play(console)


if __name__ == "__main__":
    main()
