import time
import gspread
import requests
import streamlit as st
from bs4 import BeautifulSoup
import bs4  # needed for catching ParserRejectedMarkup
from google.oauth2.service_account import Credentials
from pytrends.exceptions import TooManyRequestsError
from serpapi import GoogleSearch

# Define the scope for Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load service account info from Streamlit secrets
creds_dict = st.secrets["service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# Spreadsheet ID
spreadsheet_id = "1BzTJgX7OgaA0QNfzKs5AgAx2rvZZjDdorgAz0SD9NZg"
sheet = client.open_by_key(spreadsheet_id)

# Load SerpAPI key from Streamlit secrets
SERP_API_KEY = st.secrets["serpapi"]["api_key"]


def fetch_google_news():
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google",
        "no_cache": "true",
        "q": "asx 200",
        "google_domain": "google.com.au",
        "tbs": "qdr:d",
        "gl": "au",
        "hl": "en",
        "location": "Australia",
        "tbm": "nws",
        "num": "40"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("news_results", [])


def fetch_meta_description(url):
    if not url.startswith("http"):
        print(f"Invalid URL '{url}'")
        return "Invalid URL"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and 'content' in meta_tag.attrs:
                return meta_tag['content']
        return "No Meta Description"
    except bs4.builder.ParserRejectedMarkup as e:
        print(f"BeautifulSoup rejected the markup from {url}: {e}")
        return "Parser Error"
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return "Error Fetching Description"


def fetch_google_top_stories():
    params = {
        "api_key": SERP_API_KEY,
        "q": "asx+200",
        "hl": "en",
        "gl": "au"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("top_stories", [])


def fetch_google_trends():
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_trends",
        "q": "/m/0bl5c2",
        "geo": "AU",
        "data_type": "RELATED_QUERIES",
        "tz": "-600",
        "date": "now 4-H"
    }

    attempts = 0
    while attempts < 5:
        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            print("Google Trends API Response:", results)

            rising_queries = results.get("related_queries", {}).get("rising", [])
            top_queries = results.get("related_queries", {}).get("top", [])

            print("Rising Queries:", rising_queries)
            print("Top Queries:", top_queries)

            return rising_queries, top_queries

        except TooManyRequestsError:
            wait_time = (2 ** attempts) * 10
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            attempts += 1

    raise Exception("Failed to fetch Google Trends data after multiple attempts.")


def clean_data(data, default_values):
    cleaned_data = []
    for entry in data:
        cleaned_entry = [
            entry[i] if entry[i] else default_values[i]
            for i in range(len(entry))
        ]
        cleaned_data.append(cleaned_entry)
    return cleaned_data


def ensure_worksheet_exists(sheet_obj, title):
    try:
        worksheet = sheet_obj.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet_obj.add_worksheet(title=title, rows="100", cols="20")
    return worksheet


def store_data_in_google_sheets(news_data, top_stories_data, rising_data, top_data):
    # Google News
    news_sheet = ensure_worksheet_exists(sheet, "Google News")
    news_sheet.clear()
    news_headers = ["Title", "Link", "Snippet", "Meta Description"]
    news_sheet.append_row(news_headers)
    for article in news_data:
        meta_description = fetch_meta_description(article.get("link", ""))
        news_sheet.append_row([
            article.get("title", "No Title"),
            article.get("link", "No Link"),
            article.get("snippet", "No Snippet"),
            meta_description
        ])
        time.sleep(1)

    # Top Stories
    top_stories_sheet = ensure_worksheet_exists(sheet, "Top Stories")
    top_stories_sheet.clear()
    top_stories_headers = ["Title", "Link", "Snippet", "Meta Description"]
    top_stories_sheet.append_row(top_stories_headers)
    for story in top_stories_data:
        meta_description = fetch_meta_description(story.get("link", ""))
        top_stories_sheet.append_row([
            story.get("title", "No Title"),
            story.get("link", "No Link"),
            story.get("snippet", "No Snippet"),
            meta_description
        ])
        time.sleep(1)

    # Rising
    rising_sheet = ensure_worksheet_exists(sheet, "Google Trends Rising")
    rising_sheet.clear()
    rising_headers = ["Query", "Value"]
    rising_sheet.append_row(rising_headers)
    for query in rising_data:
        rising_sheet.append_row([
            query.get("query"),
            query.get("value")
        ])
        time.sleep(1)

    # Top
    top_sheet = ensure_worksheet_exists(sheet, "Google Trends Top")
    top_sheet.clear()
    top_headers = ["Query", "Value"]
    top_sheet.append_row(top_headers)
    for query in top_data:
        top_sheet.append_row([
            query.get("query"),
            query.get("value")
        ])
        time.sleep(1)


def main():
    """
    Main function that orchestrates data fetching from SerpAPI & storing in Google Sheets.
    """
    news_data = fetch_google_news()
    top_stories_data = fetch_google_top_stories()
    rising_data, top_data = fetch_google_trends()

    # Optional: Clean data into simplified forms (titles/links/snippets only)
    cleaned_news_data = clean_data(
        [[article.get("title", "No Title"),
          article.get("link", "No Link"),
          article.get("snippet", "No Snippet")] for article in news_data],
        ["No Title", "No Link", "No Snippet"]
    )

    cleaned_top_stories_data = clean_data(
        [[story.get("title", "No Title"),
          story.get("link", "No Link"),
          story.get("snippet", "No Snippet")] for story in top_stories_data],
        ["No Title", "No Link", "No Snippet"]
    )

    cleaned_rising_data = rising_data  # already dict format
    cleaned_top_data = top_data

    # You are still passing full data into Google Sheets
    store_data_in_google_sheets(news_data, top_stories_data, rising_data, top_data)


if __name__ == "__main__":
    main()
