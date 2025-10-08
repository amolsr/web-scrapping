
import requests
import time
import csv
from datetime import datetime

HEADERS = {
    "User-Agent": "script:reddit-scraper:v1.0 (by /u/your_reddit_username)"
}


def fetch_subreddit_json(subreddit, limit=100, after=None, sort='hot'):
    """
    Fetch one page of subreddit listing in JSON.
    Returns (json_data, next_after)
    """
    base = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    params = {"limit": limit}
    if after:
        params["after"] = after
    resp = requests.get(base, headers=HEADERS, params=params, timeout=10)
    if resp.status_code == 429:
        raise RuntimeError("Rate-limited (429). Back off before continuing.")
    resp.raise_for_status()
    j = resp.json()
    next_after = j.get("data", {}).get("after")
    return j, next_after

def extract_posts_from_listing(json_data):
    """Extract a list of post dicts from subreddit listing JSON.

    Args:
        json_data (dict): JSON response from Reddit listing endpoint.

    Returns:
        list[dict]: List of simplified post dictionaries.
    """
    
    posts = []
    for child in json_data.get("data", {}).get("children", []):
        d = child.get("data", {})
        posts.append({
            "id": d.get("id"),
            "title": d.get("title"),
            "author": d.get("author"),
            "score": d.get("score"),
            "num_comments": d.get("num_comments"),
            "subreddit": d.get("subreddit"),
            "url": d.get("url"),
            "permalink": "https://www.reddit.com" + d.get("permalink") if d.get("permalink") else None,
            "created_utc": datetime.utcfromtimestamp(d.get("created_utc")).isoformat() if d.get("created_utc") else None,
            "selftext": d.get("selftext") or ""
        })
    return posts

def scrape_subreddit(subreddit, max_posts=200, sleep_between_requests=1.5, sort='hot'):
    """Scrape up to max_posts from a subreddit.

    Uses pagination until max_posts are collected or no more pages exist.

    Args:
        subreddit (str): Subreddit name.
        max_posts (int): Maximum number of posts to return.
        sleep_between_requests (float): Seconds to sleep between requests.
        sort (str): Listing type.

    Returns:
        list[dict]: Collected post dictionaries (length <= max_posts).
    """
    all_posts = []
    after = None
    while len(all_posts) < max_posts:
        remaining = max_posts - len(all_posts)
        limit = min(100, remaining)
        json_data, after = fetch_subreddit_json(subreddit, limit=limit, after=after, sort=sort)
        posts = extract_posts_from_listing(json_data)
        if not posts:
            break
        all_posts.extend(posts)
        if not after:
            break
        time.sleep(sleep_between_requests)
    return all_posts[:max_posts]

def save_to_csv(posts, filename="reddit_posts.csv"):
    """Write posts to CSV in ./output/ directory.

    Args:
        posts (list[dict]): List of post dictionaries.
        filename (str): Output CSV filename (created under ./output/).
    """
    
    keys = ["id","title","author","score","num_comments","subreddit","url","permalink","created_utc","selftext"]
    with open("./output/"+filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for p in posts:
            writer.writerow(p)

if __name__ == "__main__":
    subreddit = "learnpython"   # This can be changed to any subreddit
    posts = scrape_subreddit(subreddit, max_posts=250, sleep_between_requests=1.5, sort='hot')
    print(f"Scraped {len(posts)} posts from r/{subreddit}")
    save_to_csv(posts, f"reddit_{subreddit}_posts.csv")
    print("Saved to CSV.")
