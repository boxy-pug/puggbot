import json
from pathlib import Path

import requests

from puggbot import Quiz

SEARCH_LIMIT = 50
SEARCH_SORTING_CONDITION = "popular"


def get_all_categories_from_api() -> dict:
    url = "https://quizapi.io/api/v1/categories"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data


def search_quiz_from_api(api_key: str, search_term: str) -> dict:
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
