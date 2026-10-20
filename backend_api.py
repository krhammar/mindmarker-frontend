import random
import requests

API_BASE = "https://api.mindmarker.dev"

def get_articles(topic=None):
    params = {}
    if topic:
        params["topic"] = topic

    response = requests.get(
        f"{API_BASE}/articles",
        params=params,
        timeout=20
    )
    response.raise_for_status()
    return response.json()

def get_random_article(topic=None):
    articles = get_articles(topic)

    if isinstance(articles, dict):
        articles = articles.get("articles", [])

    if not articles:
        return None

    return random.choice(articles)

def get_quiz(quiz_id, difficulty="easy"):
    response = requests.get(
        f"{API_BASE}/quizzes/{quiz_id}/{difficulty}.json",
        timeout=20
    )