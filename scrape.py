import praw
import pandas as pd
from datetime import datetime
import json
from time import sleep
from collections import Counter
import re
from textblob import TextBlob

class RedditGameScraper:
    def __init__(self, client_id, client_secret, user_agent):
        """Initialize the scraper with Reddit API credentials"""
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Default keywords and filters
        self.bug_keywords = [
            'bug', 'glitch', 'issue', 'broken', 'crash', 'error',
            'problem', 'not working', 'buggy', 'fix', 'patch',
            'freeze', 'stuck', 'lag', 'fps drop', 'graphics issue'
        ]
        
        # Platform-specific keywords
        self.platform_keywords = {
            'pc': ['pc', 'steam', 'epic', 'desktop', 'computer', 'windows', 'fps','valorant'],
            'playstation': ['ps4', 'ps5', 'playstation', 'psn'],
            'xbox': ['xbox', 'series x', 'series s', 'xsx', 'xss'],
            'switch': ['switch', 'nintendo']
        }
        
        # Severity indicators
        self.severity_keywords = {
            'critical': ['crash', 'unplayable', 'broken', 'game breaking', 'save corrupted'],
            'high': ['freeze', 'stuck', 'cant progress', "can't progress"],
            'medium': ['graphics', 'audio', 'visual', 'ui'],
            'low': ['minor', 'cosmetic', 'typo', 'text']
        }

    def detect_platform(self, text):
        """Detect gaming platform from text"""
        if not text:
            return ['unspecified']
        
        text = text.lower()
        detected_platforms = []
        
        for platform, keywords in self.platform_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_platforms.append(platform)
                
        return detected_platforms if detected_platforms else ['unspecified']

    def detect_severity(self, text):
        """Detect bug severity from text"""
        if not text:
            return 'unspecified'
            
        text = text.lower()
        
        for severity, keywords in self.severity_keywords.items():
            if any(keyword in text for keyword in keywords):
                return severity
                
        return 'unspecified'

    def analyze_sentiment(self, text):
        """Analyze sentiment of text using TextBlob"""
        if not text:
            return {'polarity': 0, 'subjectivity': 0}
            
        analysis = TextBlob(text)
        return {
            'polarity': analysis.sentiment.polarity,
            'subjectivity': analysis.sentiment.subjectivity
        }

    def extract_game_mentions(self, text):
        """Extract potential game titles from text using regex"""
        if not text:
            return []
            
        # Look for text in quotes or text followed by common game-related terms
        game_patterns = [
            r'"([^"]+)"',  # Text in quotes
            r'playing ([A-Za-z0-9\s:]+)',  # After "playing"
            r'in ([A-Za-z0-9\s:]+) game',  # Before "game"
        ]
        
        potential_games = []
        for pattern in game_patterns:
            matches = re.findall(pattern, text)
            potential_games.extend(matches)
            
        return list(set(potential_games))

    def get_subreddit_posts(self, subreddit_name, post_limit=100, time_filter='month', 
                           min_score=10, min_comments=5):
        """
        Scrape posts from a specified subreddit with enhanced filtering
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts_data = []
            
            # Test if subreddit exists
            subreddit.id
            
            # Get posts from subreddit based on time filter
            for post in subreddit.top(time_filter=time_filter, limit=post_limit):
                try:
                    # Apply basic filters
                    if post.score < min_score or post.num_comments < min_comments:
                        continue
                    
                    # Check for bug-related keywords
                    if not any(keyword in post.title.lower() or 
                              (post.selftext and keyword in post.selftext.lower()) 
                              for keyword in self.bug_keywords):
                        continue
                    
                    # Process comments with advanced analysis
                    processed_comments = self.process_comments(post)
                    
                    # Combine post title and text for analysis
                    full_text = f"{post.title} {post.selftext}"
                    
                    # Get author karma safely
                    try:
                        author_karma = post.author.link_karma if post.author else None
                    except:
                        author_karma = None
                    
                    # Create enhanced post data dictionary
                    post_data = {
                        'post_id': post.id,
                        'title': post.title,
                        'text': post.selftext,
                        'score': post.score,
                        'upvote_ratio': post.upvote_ratio,
                        'num_comments': post.num_comments,
                        'author': str(post.author) if post.author else '[deleted]',
                        'author_karma': author_karma,
                        'subreddit': subreddit_name,
                        'timestamp': datetime.fromtimestamp(post.created_utc).isoformat(),
                        'url': post.url,
                        'platform': self.detect_platform(full_text),
                        'severity': self.detect_severity(full_text),
                        'sentiment': self.analyze_sentiment(full_text),
                        'potential_games': self.extract_game_mentions(full_text),
                        'comments': processed_comments,
                        'bug_keywords_found': [kw for kw in self.bug_keywords 
                                             if kw in full_text.lower()],
                        'is_resolved': any(keyword in full_text.lower() 
                                         for keyword in ['resolved', 'fixed', 'solved']),
                    }
                    
                    posts_data.append(post_data)
                    sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error processing post in r/{subreddit_name}: {str(e)}")
                    continue
                    
            return posts_data
            
        except Exception as e:
            print(f"Error accessing r/{subreddit_name}: {str(e)}")
            return []

    def process_comments(self, post):
        """Process comments with advanced analysis"""
        processed_comments = []
        
        try:
            post.comments.replace_more(limit=0)
            for comment in post.comments[:10]:  # Limit to top 10 comments
                try:
                    # Skip deleted/removed comments
                    if not comment.author or comment.body in ['[deleted]', '[removed]']:
                        continue
                    
                    comment_data = {
                        'comment_id': comment.id,
                        'text': comment.body,
                        'score': comment.score,
                        'author': str(comment.author),
                        'timestamp': datetime.fromtimestamp(comment.created_utc).isoformat(),
                        'sentiment': self.analyze_sentiment(comment.body),
                        'platform_mentioned': self.detect_platform(comment.body),
                        'has_solution': any(keyword in comment.body.lower() 
                                          for keyword in ['solution', 'fix', 'solved', 'resolved']),
                        'is_op_response': str(comment.author) == str(post.author),
                    }
                    
                    processed_comments.append(comment_data)
                except Exception as e:
                    print(f"Error processing comment: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error accessing comments: {str(e)}")
            
        return processed_comments

    def save_data(self, data, output_format='json', filename='game_bugs_data'):
        """Save scraped data in specified format with error handling"""
        try:
            if output_format.lower() == 'json':
                with open(f'{filename}.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            
            elif output_format.lower() == 'csv':
                # Create flattened version for CSV
                flattened_data = []
                for post in data:
                    base_post = {k: v for k, v in post.items() 
                               if k != 'comments' and not isinstance(v, (dict, list))}
                    
                    # Handle lists and dicts
                    base_post['platforms'] = ','.join(post['platform'])
                    base_post['potential_games'] = ','.join(post['potential_games'])
                    base_post['bug_keywords'] = ','.join(post['bug_keywords_found'])
                    base_post['sentiment_polarity'] = post['sentiment']['polarity']
                    base_post['sentiment_subjectivity'] = post['sentiment']['subjectivity']
                    
                    flattened_data.append(base_post)
                
                df = pd.DataFrame(flattened_data)
                df.to_csv(f'{filename}.csv', index=False, encoding='utf-8')
            
            print(f"Data successfully saved as '{filename}.{output_format}'")
            
        except Exception as e:
            print(f"Error saving data: {str(e)}")

def main():
    # Initialize scraper
    scraper = RedditGameScraper(
        client_id="nst2HH1aa7Bbvc9igR3Vuw",
        client_secret="k8o-MuaK7vB2LbxtVeQ73uq8Qr92UA",
        user_agent="nlp final",
    )
    
    # List of gaming subreddits to scrape
    subreddits = [
        'gaming',
        'pcgaming',
        'GameBugs',
        'PS5',
        'XboxSeriesX',
        'NintendoSwitch'
    ]
    
    all_posts = []
    
    # Scrape each subreddit
    for subreddit in subreddits:
        print(f"Scraping r/{subreddit}...")
        posts = scraper.get_subreddit_posts(
            subreddit,
            post_limit=100,
            time_filter='month',
            min_score=10,
            min_comments=5
        )
        all_posts.extend(posts)
        print(f"Found {len(posts)} bug-related posts in r/{subreddit}")
    
    # Save data in both formats
    scraper.save_data(all_posts, 'json')
    scraper.save_data(all_posts, 'csv')
    
    # Print summary statistics
    total_posts = len(all_posts)
    total_comments = sum(len(post['comments']) for post in all_posts)
    platforms_found = Counter([platform for post in all_posts for platform in post['platform']])
    severity_counts = Counter(post['severity'] for post in all_posts)
    
    print("\nScraping Summary:")
    print(f"Total posts scraped: {total_posts}")
    print(f"Total comments processed: {total_comments}")
    print("\nPlatform distribution:")
    for platform, count in platforms_found.most_common():
        print(f"- {platform}: {count}")
    print("\nSeverity distribution:")
    for severity, count in severity_counts.most_common():
        print(f"- {severity}: {count}")

if __name__ == "__main__":
    main()