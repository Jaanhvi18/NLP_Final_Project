import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
import re
from textblob import TextBlob
import sqlite3
import json


class GameContentFinder:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def search_content(self, game_name, page_depth=3):
        """Search for any content related to the game across multiple pages"""
        all_results = []
        search_url = "https://html.duckduckgo.com/html/"

        for page in range(page_depth):
            try:
                params = {
                    "q": f"{game_name} game",
                    "s": str(page * 30),
                    "dc": str(page + 1),
                }
                response = requests.post(search_url, data=params, headers=self.headers)
                soup = BeautifulSoup(response.text, "html.parser")
                results = soup.find_all("div", class_="results_links")

                for result in results:
                    try:
                        title_elem = result.find("a", class_="result__a")
                        snippet_elem = result.find("a", class_="result__snippet")
                        source_elem = result.find("span", class_="result__url")
                        date_elem = result.find("span", class_="result__date")
                        author_elem = result.find("span", class_="result__author")

                        if title_elem and snippet_elem:
                            content_type, platform = self._categorize_content(
                                title_elem.text, snippet_elem.text
                            )
                            severity = self.assess_severity(snippet_elem.text)

                            content = {
                                "game": game_name,
                                "title": title_elem.text.strip(),
                                "description": snippet_elem.text.strip(),
                                "url": title_elem["href"],
                                "source": (
                                    source_elem.text.strip()
                                    if source_elem
                                    else "Unknown"
                                ),
                                "date_found": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "date_published": (
                                    date_elem.text.strip() if date_elem else "Unknown"
                                ),
                                "author": (
                                    author_elem.text.strip()
                                    if author_elem
                                    else "Unknown"
                                ),
                                "content_type": content_type,
                                "platform": platform,
                                "severity": severity,
                            }
                            all_results.append(content)
                    except Exception as e:
                        print(f"Error parsing result: {e}")
                        continue

                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"Error searching page {page + 1} for {game_name}: {e}")
                continue

        return all_results

    def _categorize_content(self, title, description):
        """Categorize the type of content based on keywords and detect platform"""
        text = (title + " " + description).lower()
        platform = None

        # Detect platform keywords
        platform_match = re.search(r"\b(pc|playstation|xbox|switch)\b", text)
        if platform_match:
            platform = platform_match.group(0).capitalize()

        categories = {
            "News": ["news", "announcement", "update", "patch", "release", "hotfix"],
            "Guide": ["guide", "how to", "tutorial", "tips", "strategy", "walkthrough"],
            "Review": ["review", "rating", "scored", "verdict"],
            "Discussion": ["forum", "discussion", "thread", "community"],
            "Bug/Issue": [
                "bug",
                "issue",
                "problem",
                "error",
                "crash",
                "freeze",
                "glitch",
                "lag",
            ],
            "Feature": ["feature", "preview", "upcoming", "dlc", "expansion", "addon"],
            "Download": ["download", "install", "free", "steam", "epic"],
            "Streaming": ["stream", "twitch", "youtube", "video", "watch"],
            "Competition": ["tournament", "competition", "esports", "championship"],
            "Modding": ["mod", "modding", "customization", "workshop"],
        }

        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category, platform

        return "General", platform

    def assess_severity(self, description):
        """Determine the severity of an issue based on sentiment analysis"""
        sentiment = TextBlob(description).sentiment.polarity
        if sentiment < -0.5:
            return "High"
        elif sentiment < 0:
            return "Medium"
        return "Low"

    def save_to_database(self, all_content):
        """Save data to SQLite database"""
        conn = sqlite3.connect("game_content.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS content (
                game TEXT, title TEXT, description TEXT, url TEXT, 
                source TEXT, date_found TEXT, date_published TEXT, author TEXT, 
                content_type TEXT, platform TEXT, severity TEXT
            )
        """
        )

        for content in all_content:
            cursor.execute(
                """
                INSERT INTO content VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    content["game"],
                    content["title"],
                    content["description"],
                    content["url"],
                    content["source"],
                    content["date_found"],
                    content["date_published"],
                    content["author"],
                    content["content_type"],
                    content.get("platform"),
                    content.get("severity"),
                ),
            )

        conn.commit()
        conn.close()


def clean_content(content):
    for key, value in content.items():
        # Handle nested dictionaries by converting to string representation
        if isinstance(value, dict):
            content[key] = str(value)
        # Convert other unexpected types to string for compatibility
        elif not isinstance(value, (str, int, float, list, type(None))):
            content[key] = str(value)
    return content


def main():
    finder = GameContentFinder()
    all_content = []

    games = ["Fortnite", "Minecraft", "Valorant"]

    for game in games:
        print(f"\nSearching for {game} content...")

        game_content = finder.search_content(game)
        game_content = [
            clean_content(item) for item in game_content
        ]  # Clean content here

        # Check the structure of each content item
        for i, content in enumerate(game_content):
            print(f"Item {i}: {content}")  # Inspect each item

        all_content.extend(game_content)

        print(f"Found {len(game_content)} items for {game}")

        time.sleep(random.uniform(3, 5))

    # Save everything as JSON if all_content has data
    if all_content:
        try:
            with open("game_content.json", "w") as json_file:
                json.dump(all_content, json_file, indent=4)
            print(f"\nSaved {len(all_content)} total items")
            print("File saved: game_content.json")

            finder.save_to_database(all_content)

            # Display some basic information about the content
            content_types = [
                item["content_type"] for item in all_content if "content_type" in item
            ]
            games = [item["game"] for item in all_content if "game" in item]
            print("\nTotal content by type:")
            print({type_: content_types.count(type_) for type_ in set(content_types)})
            print("\nContent by game:")
            print({game: games.count(game) for game in set(games)})
        except Exception as e:
            print(f"Error saving all_content as JSON: {e}")
    else:
        print("No content found!")


if __name__ == "__main__":
    main()
