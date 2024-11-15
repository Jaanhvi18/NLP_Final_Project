import json
import csv
from datetime import datetime
from pathlib import Path
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from string import punctuation
from collections import defaultdict
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

class ExtractiveSummarizer:
    def __init__(self):
        try:
            nltk.data.find("tokenizers/punkt")
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("punkt")
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
            else:
                logging.warning(f"Unexpected comment format: {item}")
        return flat_comments

    def preprocess_text(self, text):
        """Clean and tokenize text."""
        words = word_tokenize(text.lower())
        return [word for word in words if word not in self.stop_words]

    def get_sentence_scores(self, sentences, word_freq):
        """Score sentences based on word frequencies."""
        sentence_scores = defaultdict(float)
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            word_count = len([word for word in words if word not in self.stop_words])
            if word_count <= 0:
                continue
            for word in words:
                if word in word_freq:
                    sentence_scores[sentence] += word_freq[word]
            sentence_scores[sentence] /= word_count
        return sentence_scores

    def summarize(self, comments, title="", num_sentences=3):
        comments = self.flatten_comments(comments)
        comments = [
            comment
            for comment in comments
            if isinstance(comment, dict)
            and comment.get("text", "").strip() not in ["[deleted]", "[removed]"]
        ]

        all_text = " ".join(comment.get("text", "") for comment in comments)
        if not all_text.strip():
            return {
                "title": title,
                "summary": ["No valid text found for summarization"],
                "metrics": {
                    "total_comments": 0,
                    "average_score": 0,
                    "sentiment_distribution": {
                        "positive": 0,
                        "negative": 0,
                        "neutral": 0,
                    },
                },
            }

        sentences = sent_tokenize(all_text)
        words = self.preprocess_text(all_text)
        word_freq = FreqDist(words)
        sentence_scores = self.get_sentence_scores(sentences, word_freq)

        top_sentences = sorted(
            sentence_scores.items(), key=lambda x: x[1], reverse=True
        )[:num_sentences]
        top_sentences = sorted(top_sentences, key=lambda x: sentences.index(x[0]))

        valid_comments = [c for c in comments if "score" in c]
        scores = [c.get("score", 0) for c in valid_comments]
        avg_score = np.mean(scores) if scores else 0

        sentiments = {
            "positive": sum(
                1 for c in valid_comments
                if c.get("sentiment", {}).get("polarity", 0) > 0
            ),
            "negative": sum(
                1 for c in valid_comments
                if c.get("sentiment", {}).get("polarity", 0) < 0
            ),
            "neutral": sum(
                1 for c in valid_comments
                if c.get("sentiment", {}).get("polarity", 0) == 0
            ),
        }

        return {
            "title": title,
            "summary": [sent[0] for sent in top_sentences],
            "metrics": {
                "total_comments": len(valid_comments),
                "average_score": avg_score,
                "sentiment_distribution": sentiments,
            },
        }

def generate_and_save_reports(input_file, output_dir="reports"):
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for file names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Read input data
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        summarizer = ExtractiveSummarizer()
        
        # Prepare data for TSV
        tsv_rows = []
        text_report = []
        
        # Convert input to list if it's a single dictionary
        if isinstance(data, dict):
            data = [data]
            
        # Process each discussion
        for idx, entry in enumerate(data):
            if not isinstance(entry, dict):
                continue
                
            title = entry.get("title", f"Discussion {idx + 1}")
            comments = entry.get("comments", [])
            
            summary_result = summarizer.summarize(comments, title)
            
            # Prepare TSV row
            tsv_row = {
                'Title': title,
                'Total Comments': summary_result['metrics']['total_comments'],
                'Average Score': f"{summary_result['metrics']['average_score']:.2f}",
                'Positive Comments': summary_result['metrics']['sentiment_distribution']['positive'],
                'Negative Comments': summary_result['metrics']['sentiment_distribution']['negative'],
                'Neutral Comments': summary_result['metrics']['sentiment_distribution']['neutral'],
                'Key Points': ' | '.join(summary_result['summary'])
            }
            tsv_rows.append(tsv_row)
            
            # Prepare text report
            text_report.append(f"""
Discussion: {title}
{'=' * (len(title) + 11)}
Key Points:
{chr(10).join('- ' + point for point in summary_result['summary'])}

Metrics:
- Total Comments: {summary_result['metrics']['total_comments']}
- Average Score: {summary_result['metrics']['average_score']:.2f}
- Sentiment Distribution:
  * Positive: {summary_result['metrics']['sentiment_distribution']['positive']}
  * Negative: {summary_result['metrics']['sentiment_distribution']['negative']}
  * Neutral: {summary_result['metrics']['sentiment_distribution']['neutral']}
""")
        
   
        tsv_file = Path(output_dir) / f"game_discussion_summary_{timestamp}.tsv"
        with open(tsv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=tsv_rows[0].keys(), delimiter='\t')
            writer.writeheader()
            writer.writerows(tsv_rows)
            

        text_file = Path(output_dir) / f"game_discussion_detailed_{timestamp}.txt"
        with open(text_file, 'w') as f:
            f.write("Game Development Discussions Analysis\n")
            f.write("=" * 35 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("\n".join(text_report))
            
        return {
            'tsv_file': str(tsv_file),
            'text_file': str(text_file),
            'processed_discussions': len(tsv_rows)
        }
            
    except Exception as e:
        logging.error(f"Error generating reports: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        input_file = "game_bugs_data.json" 
        result = generate_and_save_reports(input_file)
        print(f"""
Reports generated successfully!
- TSV Summary: {result['tsv_file']}
- Detailed Report: {result['text_file']}
- Processed {result['processed_discussions']} discussions
""")
    except FileNotFoundError:
        print(f"Error: Input file not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in input file.")
    except Exception as e:
        print(f"Error: {str(e)}")