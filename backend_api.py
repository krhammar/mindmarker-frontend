import random
import requests

API_BASE = "https://api.mindmarker.dev"

# returns a list of articles with input "topic" as a parameter
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

# returns a random article file
def get_random_article(topic=None):
    articles = get_articles(topic)

    if isinstance(articles, dict):
        articles = articles.get("articles", [])

    if not articles:
        return None

    return random.choice(articles)

# returns the text of an article, given it's filename within the Api base
def get_article_content(filename):
    response = requests.get(
        f"{API_BASE}/articles/{filename}.md",
        timeout=20
    )
    response.raise_for_status()
    return response.text


# returns a quiz given an article-id and difficulty
def get_quiz(quiz_id, difficulty="easy"):
    response = requests.get(
        f"{API_BASE}/quizzes/{quiz_id}/{difficulty}.json",
        timeout=20
    )