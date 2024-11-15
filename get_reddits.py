import praw
import re

# Step 1: Set up Reddit API (Replace with your credentials)
reddit = praw.Reddit(
    client_id="vbFzRNrXG0BqdyPWHfImTw",
    client_secret="rQ-bxF-Lr4vIuHyQOxnO5w4B8KR29w",
    user_agent="script:reddit-game-search:v1.0 (by u/xxProReapsxx35777)"
)

# Step 2: Read game titles from a text file
input_file = "multiplayer_games_limited.txt"
output_file = "game_subreddits_clean.txt"

with open(input_file, 'r', encoding='utf-8') as file:
    game_titles = [line.strip() for line in file.readlines()]

# Function to preprocess game titles
def preprocess_title(title):
    # Remove special characters, normalize spaces, and lowercase
    title = re.sub(r'[^a-zA-Z0-9 ]', '', title)
    return title.strip().lower()

# Step 3: Search for subreddits and save results
with open(output_file, 'w', encoding='utf-8') as out_file:
    for game_title in game_titles:
        preprocessed_title = preprocess_title(game_title)
        print(f"\nSearching for subreddit related to: {game_title}")

        # Search using Reddit's search API
        search_results = list(reddit.subreddits.search(query=preprocessed_title, limit=1))
        
        if search_results:
            # Get the first match
            first_subreddit = search_results[0]
            # Write to the file in the clean format
            out_file.write(f"{game_title}: r/{first_subreddit.display_name}\n")
        else:
            # Handle no subreddit found
            out_file.write(f"{game_title}: No subreddit found\n")
