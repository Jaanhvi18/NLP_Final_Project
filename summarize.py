from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import json
from collections import defaultdict

# Define development-related keywords
development_keywords = ["update", "release", "patch", "fix", "new feature", "development", "improvement"]

def summarize_text(text, sentence_count=5):
    """Generate a summary for the given text with sumy."""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    
    # Join the summary sentences into a single string
    return " ".join(str(sentence) for sentence in summary)

# Load the JSON data from the file
with open("game_bugs_data.json", "r", encoding="utf-8") as f:
    all_posts = json.load(f)

# Group posts by game titles, filtering for development-related content
game_posts = defaultdict(list)

for post in all_posts:
    for game in post["potential_games"]:
        full_text = f"{post['title']} {post['text']}".lower()
        
        # Check if the post contains any development-related keywords
        if any(keyword in full_text for keyword in development_keywords):
            game_posts[game].append(full_text)

# Generate a summary for each game
game_summaries = {}

for game, texts in game_posts.items():
    combined_text = " ".join(texts)  # Combine all texts related to the game
    game_summary = summarize_text(combined_text, sentence_count=5)  # Adjust sentence count as needed
    game_summaries[game] = game_summary

# Print or save the summaries
for game, summary in game_summaries.items():
    print(f"Game: {game}")
    print("Summary:", summary)
    print("\n" + "-"*50 + "\n")
