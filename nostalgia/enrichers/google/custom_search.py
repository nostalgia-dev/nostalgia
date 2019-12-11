import os
import just
from googleapiclient.discovery import build
from googleapiclient.http import HttpError
from datetime import datetime
import diskcache
import dotenv
from nostalgia.cache import get_cache

CACHE = get_cache("google_custom_search")

dotenv.load_dotenv("google_custom_search/.env")
dotenv.load_dotenv(".env")

errored_count = 0


def google_custom_search(search_term, **kwargs):
    global errored_count
    search_term = search_term.lower()
    if search_term in CACHE:
        return CACHE[search_term]
    if errored_count > 4:
        return []
    service = build("customsearch", "v1", developerKey=os.environ.get("MY_API_KEY"))
    try:
        res = service.cse().list(q=search_term, cx=os.environ.get("MY_CSE_ID"), **kwargs).execute()
    except HttpError as e:
        print("error", e)
        errored_count += 1
        return []
    items = res.get("items", [])
    CACHE[search_term] = items
    return items
