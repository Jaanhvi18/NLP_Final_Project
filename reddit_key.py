import praw
import re
import spacy
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

# Initialize spaCy for noun phrase extraction
nlp = spacy.load("en_core_web_sm")
import nltk
nltk.download('stopwords')

# Stop words
stop_words = set(stopwords.words("english"))

class KeywordExtractor:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def clean_text(self, text):
        # Remove URLs, punctuation, numbers, and lowercase
        text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
        text = re.sub(r'\W+', ' ', text)
        return text.lower()

    def get_subreddit_posts(self, subreddit_name, post_limit=100):
        # Scrape post titles and selftexts
        subreddit = self.reddit.subreddit(subreddit_name)
        text_data = []
        for post in subreddit.hot(limit=post_limit):
            title = self.clean_text(post.title)
            selftext = self.clean_text(post.selftext)
            text_data.append(f"{title} {selftext}")
        return text_data

    def get_frequent_keywords(self, text_data, top_n=20):
        # Combine all texts and remove stopwords
        words = ' '.join(text_data).split()
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Use Counter to get the most common words
        word_counts = Counter(words)
        return word_counts.most_common(top_n)

    def extract_noun_phrases(self, text_data):
        # Extract noun phrases from each post
        noun_phrases = []
        for doc in nlp.pipe(text_data, batch_size=50):
            noun_phrases.extend([chunk.text for chunk in doc.noun_chunks])
        
        return Counter(noun_phrases).most_common(20)

    def extract_keywords_with_tfidf(self, text_data):
        # Use TF-IDF to get unique keywords for each subreddit
        vectorizer = TfidfVectorizer(max_df=0.8, max_features=1000, min_df=2, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(text_data)
        feature_names = vectorizer.get_feature_names_out()
        
        # Sum up the tf-idf values for each word and get top keywords
        tfidf_scores = tfidf_matrix.sum(axis=0).tolist()[0]
        keywords = [(feature_names[i], tfidf_scores[i]) for i in range(len(feature_names))]
        keywords.sort(key=lambda x: x[1], reverse=True)
        return keywords[:20]

def main():
    extractor = KeywordExtractor(
        client_id="nst2HH1aa7Bbvc9igR3Vuw",
        client_secret="k8o-MuaK7vB2LbxtVeQ73uq8Qr92UA",
        user_agent="nlp final",
    )
    
    # Choose a subreddit to analyze
    subreddit = "playitforward"
    post_data = extractor.get_subreddit_posts(subreddit, post_limit=100)
    
    # Get frequent keywords
    frequent_keywords = extractor.get_frequent_keywords(post_data)
    print("Frequent Keywords:", frequent_keywords)
    
    # Extract noun phrases
    noun_phrases = extractor.extract_noun_phrases(post_data)
    print("Noun Phrases:", noun_phrases)
    
    # Extract keywords using TF-IDF
    tfidf_keywords = extractor.extract_keywords_with_tfidf(post_data)
    print("TF-IDF Keywords:", tfidf_keywords)

if __name__ == "__main__":
    main()
