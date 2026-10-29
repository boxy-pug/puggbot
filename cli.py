import argparse
import os
from pprint import pprint

import requests
from dotenv import load_dotenv

from puggbot import load_from_api


def get_categories() -> dict:
    response = requests.get(
        "https://quizapi.io/api/v1/categories",
        headers={
            "Content-Type": "application/json",
        },
        params={
            "topic": "python",
            "limit": 5,
        },
    )
    data = response.json()
    return data


def search_quiz(api_key: str, search_term: str) -> dict:

    response = requests.get(
        f"https://quizapi.io/api/v1/quizzes?topic={search_term}&sort=popular&limit=50",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
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
        help="play quiz, json file or api",
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

    return parser.parse_args()


def main():
    load_dotenv()
    quizapi_key = os.getenv("QUIZAPI_KEY")

    args = parse_args()

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
        print("lets play")
        # print(args.play)
        file = args.play
        quiz_id = file[-1].split()[-1].strip()
        print(f"quiz id: {quiz_id}")
        print(file)
        quiz = load_from_api(quizapi_key, quiz_id)

        answers = quiz.play()

        if all(answers):
            print("great you got them all correct")
        else:
            print("good try")

    if args.search:
        # TODO multiple words support?
        search_term = args.search[0].strip()
        if quizapi_key:
            quizzes = search_quiz(quizapi_key, search_term)
            for quiz in quizzes:
                print(
                    f"{quiz["title"]}  {quiz["difficulty"]}, plays: {quiz["plays"]}, question count: {quiz["questionCount"]} id: {quiz["id"]}"
                )


if __name__ == "__main__":
    main()
