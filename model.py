import json
import csv
from datetime import datetime
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from string import punctuation
from collections import defaultdict
import numpy as np
import logging
import warnings
import stanza
from transformers import pipeline
from sklearn.cluster import KMeans
from gensim.models import Word2Vec

stanza.download('en')

warnings.filterwarnings("ignore", category=UserWarning)
logging.basicConfig(level=logging.INFO)

class ExtractiveSummarizer:
    def __init__(self):
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="fine_tuned_roberta_sentiment",
            device=0,
        )

        self.tweebank_nlp = stanza.Pipeline(
            processors="tokenize,lemma,pos,depparse,ner",
            lang="en",
            tokenize_model_path="./twitter-stanza/saved_models/tokenize/en_tweet_tokenizer.pt",
        )

        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords")

        self.stop_words = set(stopwords.words("english") + list(punctuation))

    @staticmethod
    def flatten_comments(comments):
        flat_comments = []
        for item in comments:
            if isinstance(item, list):
                flat_comments.extend(ExtractiveSummarizer.flatten_comments(item))
            elif isinstance(item, dict):
                flat_comments.append(item)
        return flat_comments

    def preprocess_text(self, text):
        doc = self.tweebank_nlp(text)
        tokens = [word.lemma for sentence in doc.sentences for word in sentence.words]
        return [token for token in tokens if token not in self.stop_words]

    def get_sentence_scores(self, sentences, word_freq):
        sentence_scores = defaultdict(float)
        for sentence in sentences:
            words = self.preprocess_text(sentence)
            for word in words:
                if word in word_freq:
                    sentence_scores[sentence] += word_freq[word]
            sentence_scores[sentence] /= len(words) if words else 1
        return sentence_scores

    def cluster_sentences(self, sentences):
        tokenized_sentences = [self.preprocess_text(sentence) for sentence in sentences]
        model = Word2Vec(sentences=tokenized_sentences, vector_size=100, min_count=1, workers=4)

        def sentence_embedding(sentence):
            words = [word for word in sentence if word in model.wv]
            return np.mean([model.wv[word] for word in words], axis=0) if words else np.zeros(model.vector_size)

        embeddings = np.array([sentence_embedding(sentence) for sentence in tokenized_sentences])
        n_clusters = min(len(sentences), 5)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(embeddings)
        return kmeans.labels_

    def summarize(self, comments, title="", num_sentences=5):
        comments = self.flatten_comments(comments)
        all_text = " ".join(comment.get("text", "") for comment in comments if "text" in comment)
        sentences = nltk.sent_tokenize(all_text)
    
        for comment in comments:
            text = comment.get("text", "")
            sentiment_result = self.sentiment_analyzer(text[:512])
            comment["sentiment"] = {
                "label": sentiment_result[0]["label"].lower(),
                "score": sentiment_result[0]["score"],
            }
    
        word_freq = nltk.FreqDist(self.preprocess_text(all_text))
        sentence_scores = self.get_sentence_scores(sentences, word_freq)
    
        cluster_labels = self.cluster_sentences(sentences)
        cluster_representatives = []
        for cluster in range(max(cluster_labels) + 1):
            cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster]
            best_sentence = max(
                cluster_indices, key=lambda idx: sentence_scores.get(sentences[idx], 0)
            )
            cluster_representatives.append(sentences[best_sentence])
    
        summary_sentences = sorted(
            cluster_representatives, key=lambda x: sentences.index(x)
        )[:num_sentences]
    
        sentiment_distribution = {
            "positive": sum(1 for c in comments if c["sentiment"]["label"] == "positive"),
            "neutral": sum(1 for c in comments if c["sentiment"]["label"] == "neutral"),
            "negative": sum(1 for c in comments if c["sentiment"]["label"] == "negative"),
        }
    
        total_comments = len(comments)
        positive_comments = sentiment_distribution['positive']
        neutral_comments = sentiment_distribution['neutral']
        negative_comments = sentiment_distribution['negative']
    
        overall_sentiment_score = (positive_comments - negative_comments) / total_comments
        if overall_sentiment_score > 0.5:
            overall_sentiment = f"positive (Score: {overall_sentiment_score:.2f})"
        elif overall_sentiment_score < -0.5:
            overall_sentiment = f"negative (Score: {overall_sentiment_score:.2f})"
        else:
            overall_sentiment = f"neutral (Score: {overall_sentiment_score:.2f})"
    
        return {
            "title": title,
            "summary": summary_sentences,
            "summary_sentiment": overall_sentiment,
            "detailed_sentence_sentiments": [
                f"- {sent} \n  Sentiment: {comment['sentiment']['label']} (Score: {comment['sentiment']['score']:.2f})"
                for sent, comment in zip(sentences, comments)
            ],
            "metrics": {
                "Total Comments": total_comments,
                "Positive Comments": positive_comments,
                "Neutral Comments": neutral_comments,
                "Negative Comments": negative_comments
            }
        }

def generate_and_save_reports(input_file, output_dir="new"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(input_file, "r") as f:
        discussions = json.load(f)

    summarizer = ExtractiveSummarizer()
    reports = []

    for discussion in discussions:
        title = discussion.get("title", "")
        comments = discussion.get("comments", [])
        report = summarizer.summarize(comments, title)
        reports.append(report)

    tsv_file = Path(output_dir) / f"summary_{timestamp}.tsv"
    with open(tsv_file, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["Title", "Summary Sentiment", "Detailed Sentiments", "Metrics"])
        for report in reports:
            writer.writerow([
                report["title"],
                report["summary_sentiment"],
                "\n".join(report["detailed_sentence_sentiments"]),
                report["metrics"]
            ])

    text_file = Path(output_dir) / f"summary_{timestamp}.txt"
    with open(text_file, "w") as f:
        for report in reports:
            f.write(f"Discussion: {report['title']}\n")
            f.write(f"{'=' * len(report['title'])}\n")
            f.write(f"- Summary Sentiment: {report['summary_sentiment']}\n")
            f.write(f"- Detailed Sentence Sentiments:\n")
            f.write("\n".join(report['detailed_sentence_sentiments']))
            f.write(f"\nMetrics:\n")
            f.write(f"{report['metrics']}\n\n")

    return {"tsv_file": str(tsv_file), "text_file": str(text_file)}

if __name__ == "__main__":
    input_file = "post_comments_labeled.json"
    reports = generate_and_save_reports(input_file)
    print(f"Reports generated: {reports}")
