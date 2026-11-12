from rich.table import Table


def format_quiz_search_line(quiz: dict):
    return f'{quiz["title"]} | Difficulty: {quiz["difficulty"]} | plays: {quiz["plays"]} | qs: {quiz["questionCount"]} | {" ".join(quiz["tags"])} | {quiz["id"]}'
