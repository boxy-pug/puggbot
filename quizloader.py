import json
import subprocess
from pathlib import Path

import requests

from puggbot import Quiz

SEARCH_LIMIT = 50
SEARCH_SORTING_CONDITION = "popular"


def get_all_categories_from_api() -> dict:
    url = "https://quizapi.io/api/v1/categories"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    root_object = response.json()
    return root_object["data"]


def search_quizzes_from_api(api_key: str, search_term: str) -> dict:
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


def get_quiz_id_from_search_line(search_line: str) -> str:
    return search_line.split()[-1].strip()


def format_quiz_search_line(quiz: dict):
    return f'{quiz["title"]} | Difficulty: {quiz["difficulty"]} | plays: {quiz["plays"]} | qs: {quiz["questionCount"]} | {" ".join(quiz["tags"])} | {quiz["id"]}'


def run_fzf_search_on_api(api_key: str, search_term: str) -> str:

    quizzes = search_quizzes_from_api(api_key, search_term)
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


def get_quiz_from_api(api_key: str, quiz_id: str) -> Quiz:

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    url = f"https://quizapi.io/api/v1/quizzes/{quiz_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    json_response = response.json()
    # print(f"Found {data['total']} quizzes")
    # handle what happens when no data

    return Quiz.from_dict(json_response["data"])


def get_quiz_from_file(filepath: Path) -> Quiz:

    with open(filepath, "r") as file:
        root_object = json.load(file)
        data = root_object["data"]

        return Quiz.from_dict(data)
