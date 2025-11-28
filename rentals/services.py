
import requests
from requests.utils import requote_uri

OPENLIB_SEARCH = "https://openlibrary.org/search.json?title={title}"
OPENLIB_WORKS = "https://openlibrary.org{key}.json"     
OPENLIB_EDITIONS = "https://openlibrary.org{key}/editions.json"

def fetch_book_by_title(title, max_results=5, timeout=6):
    """
    Search OpenLibrary by title and return a dict:
      { "title": ..., "openlibrary_id": ..., "number_of_pages": ..., "raw": { ... } }
    Returns None if nothing found or on error.
    """
    if not title:
        return None
    try:
        url = OPENLIB_SEARCH.format(title=requote_uri(title))
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None

    docs = data.get("docs", [])[:max_results]
    if not docs:
        return None

    # prefer docs with page count
    chosen = None
    for doc in docs:
        if doc.get("number_of_pages") or doc.get("number_of_pages_median"):
            chosen = doc
            break
    if not chosen:
        chosen = docs[0]

    pages = chosen.get("number_of_pages") or chosen.get("number_of_pages_median")
    key = chosen.get("key")  # e.g., "/works/OL123W"
    title_found = chosen.get("title") or title
    return {
        "title": title_found,
        "openlibrary_id": key,
        "number_of_pages": pages,
        "raw": chosen
    }
