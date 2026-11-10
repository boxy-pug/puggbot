import argparse
import os
import subprocess
import sys
from pathlib import Path
from pprint import pprint

import requests
from dotenv import load_dotenv
from rich.console import Console

from puggbot import Quiz, load_from_file, load_quiz_from_api

SEARCH_LIMIT = 50
SEARCH_SORTING_CONDITION = "popular"


def get_categories() -> dict:
    url = "https://quizapi.io/api/v1/categories"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data


def search_quiz(api_key: str, search_term: str) -> dict:
    url = "https://quizapi.io/api/v1/quizzes"
    params = {
        "topic": search_term,
        "limit": SEARCH_LIMIT,
        "sort": SEARCH_SORTING_CONDITION,
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    return data["data"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Puggbot", description="Pugg til eksamen i terminalen"
    )

    parser.add_argument(
        "--play",
        nargs=1,
        metavar="QUIZ",
        help="play quiz from api",
    )

    parser.add_argument(
        "--play-local",
        type=Path,
        metavar="QUIZ",
        help="play quiz from json file",
    )

    parser.add_argument("--user", metavar="USERNAME", help="provide username")

    parser.add_argument(
        "--show",
        nargs=1,
        choices=("categories", "quizzes", "users"),
        metavar="WHAT",
        help="show categories, quizzes and users",
    )

    parser.add_argument(
        "--search",
        nargs=1,
        metavar=("SEARCHWORD"),
        help="search for quizzes",
    )

    parser.add_argument(
        "--fzf",
        nargs=1,
        metavar=("SEARCH_TERM"),
        help="search, choose in fuzzy finder and play",
    )

    return parser.parse_args()


def get_quiz_id_from_search_line(search_line: str) -> str:
    return search_line.split()[-1].strip()


def run_fzf_search(search_term: str) -> str:

    # Run a puggbot --search as subprocess
    search_res = subprocess.run(
        [sys.executable, "cli.py", "--search", search_term],
        capture_output=True,
        text=True,
        check=True,
    )

    # Let user choose a quiz using fzf as subprocess
    picked = subprocess.run(
        ["fzf"], input=search_res.stdout, stdout=subprocess.PIPE, text=True
    )

    # Get quiz id from the full search line
    quiz_id = get_quiz_id_from_search_line(picked.stdout)
    print(f"id is {quiz_id}")

    return quiz_id


def play_quiz(quiz: Quiz) -> str:
    print("lets play")

    answers = quiz.play()

    return "test"


def main():

    # Get QuizAPI API key from .env, exit program if not found.
    load_dotenv()
    quizapi_key = os.getenv("QUIZAPI_KEY", default=None)

    if quizapi_key is None:
        sys.stderr.write("Please provide a 'QUIZAPI_KEY' in .env")
        sys.exit(1)

    # Load arguments from command line input
    args = parse_args()

    # start console and stderr
    console = Console()
    err_console = Console(stderr=True)

    if args.fzf:
        search_term = args.fzf[0]

        quiz_id = run_fzf_search(search_term)

        # TODO run play program here
        quiz = load_quiz_from_api(quizapi_key, quiz_id)
        result = play_quiz(quiz)
        print(result)

    if args.show:
        if "categories" in args.show:
            topics = get_categories()
            for topic in topics["data"]:
                print(f"{topic["name"]} - {topic["slug"]}")
                for category in topic["categories"]:
                    print(f"\t{category["name"]} - {category["slug"]}")
                # print(topic["tags"])

        elif args.show == "quizzes":
            print("quizzes")
        elif args.show == "users":
            print("users")
        else:
            print("unknown")

    if args.play:
        quiz_id = args.play

        # TODO try except here
        quiz = load_quiz_from_api(quizapi_key, quiz_id)

        result = quiz.play(console)
        print(result)

    if args.play_local:
        quiz_path = args.play_local

        quiz = None

        # todo: json.JSONDEcoderError, OSError
        try:
            quiz = load_from_file(quiz_path)
        except FileNotFoundError as exc:
            err_console.print(f"Could not open '{quiz_path}': {exc}")
            return 1
        except Exception as exc:
            err_console.print(
                f"Unexpected error trying to load quiz from {quiz_path}: {exc}"
            )
            return 1

        if quiz:
            result = quiz.play(console)
            print(result)

    if args.search:
        # TODO multiple words support?
        search_term = args.search[0].strip()
        if quizapi_key:
            quizzes = search_quiz(quizapi_key, search_term)
            for quiz in quizzes:
                print(
                    f"{quiz["title"]}  {quiz["difficulty"]}, plays: {quiz["plays"]}, q's: {quiz["questionCount"]} tags: {" ".join(quiz["tags"])} id: {quiz["id"]}"
                )


if __name__ == "__main__":
    main()
