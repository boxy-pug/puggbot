import json
import subprocess
from collections.abc import Callable
from enum import Enum
from pathlib import Path

import requests

from models import Quiz

SEARCH_LIMIT = 50
SEARCH_SORTING_CONDITION = "popular"

LOCAL_QUIZ_DIR = "local"


class DataType(Enum):
    QUIZZES = "QUIZZES"
    CATEGORIES = "CATEGORIES"
    TOPICS = "TOPICS"


def get_all_topics_from_api() -> dict:
    url = "https://quizapi.io/api/v1/categories"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    root_object = response.json()
    data = get_data_from_root_object(root_object)
    return data


def get_quizzes_from_api(
    api_key: str, search_term: str = "", category_id: str = ""
) -> dict:
    url = "https://quizapi.io/api/v1/quizzes"
    params = {
        "limit": SEARCH_LIMIT,
        "sort": SEARCH_SORTING_CONDITION,
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    if search_term:
        params["topic"] = search_term

    if category_id:
        params["categoryId"] = category_id

    response = requests.get(url, params=params, headers=headers)
    root_object = response.json()
    data = get_data_from_root_object(root_object)
    return data


def get_quiz_from_api(api_key: str, quiz_id: str) -> dict:

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    url = f"https://quizapi.io/api/v1/quizzes/{quiz_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    root_object = response.json()
    data = get_data_from_root_object(root_object)

    return data


def download_quiz_from_api(quiz_dict: dict) -> str:

    local_dir = Path(__file__).resolve().parent / LOCAL_QUIZ_DIR
    local_dir.mkdir(parents=True, exist_ok=True)

    quiz_filename = quiz_dict.get("id", "default")
    quiz_path = local_dir / f"{quiz_filename}.json"

    with quiz_path.open("w") as file:
        json.dump(quiz_dict, file)

    return quiz_path.name


def fuzzy_search(data: dict, data_type: DataType) -> str:
    formatter: Callable[[dict], str]

    if data_type == DataType.TOPICS:
        formatter = format_topic_search_line
    elif data_type == DataType.CATEGORIES:
        formatter = format_category_search_line
    elif data_type == DataType.QUIZZES:
        formatter = format_quiz_search_line

    formatted_lines = "\n".join([formatter(line) for line in data])

    # Let user choose a quiz using fzf as subprocess
    picked = subprocess.run(
        ["fzf"], input=formatted_lines, stdout=subprocess.PIPE, text=True
    )

    # Get id from the full search line
    id = get_last_value_from_search_line(picked.stdout)

    return id


def get_data_from_root_object(obj: dict) -> dict:
    if "data" in obj:
        return obj["data"]
    return obj


def get_last_value_from_search_line(search_line: str) -> str:
    return search_line.split()[-1].strip()


def format_topic_search_line(topic: dict) -> str:
    return f"{topic["name"]} | {topic["id"]}"


def format_category_search_line(category: dict) -> str:
    return f"{category["name"]} | Quiz count: {category["quizCount"]} | Tags: {category["tags"]} | id: {category["id"]}"


def format_quiz_search_line(quiz: dict) -> str:
    return f'{quiz["title"]} | Difficulty: {quiz["difficulty"]} | plays: {quiz["plays"]} | qs: {quiz["questionCount"]} | {" ".join(quiz["tags"])} | {quiz["id"]}'


def get_quiz_from_file(filepath: Path) -> Quiz:

    with open(filepath, "r") as file:
        root_object = json.load(file)
        data = get_data_from_root_object(root_object)

        return Quiz.from_dict(data)
