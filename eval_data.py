import json
import nltk
from rouge_score import rouge_scorer

nltk.download('punkt')

def evaluate_summarization_and_sentiment(eval_file, generated_summaries_file):
    """Evaluate summarization and sentiment classification."""

    with open(eval_file, "r") as f:
        eval_data = json.load(f)
    with open(generated_summaries_file, "r") as f:
        generated_summaries = json.load(f)


    if len(generated_summaries) < len(eval_data):
        print(f"Warning: `generated_summaries` has fewer entries ({len(generated_summaries)}) than `eval_data` ({len(eval_data)}).")
        eval_data = eval_data[:len(generated_summaries)]  

    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    rouge_scores = []
    sentiment_accuracy = []

    for i in range(len(eval_data)):
        item = eval_data[i]
        reference_summary = item["reference_summary"]
        generated_summary = generated_summaries[i]["predicted_summary"]  

        # Display reference and generated summaries
        print(f"Reference Summary {i}: {reference_summary}")
        print(f"Generated Summary {i}: {generated_summary}")
        print()

        rouge = scorer.score(reference_summary, generated_summary)
        rouge_scores.append(rouge)
        ref_sentiment = item["reference_sentiment"]["polarity"]
        gen_sentiment = generated_summaries[i]["predicted_sentiment"]["polarity"]
        sentiment_accuracy.append(int(ref_sentiment == gen_sentiment))


    avg_rouge = {
        "rouge1": sum(score["rouge1"].fmeasure for score in rouge_scores) / len(rouge_scores),
        "rouge2": sum(score["rouge2"].fmeasure for score in rouge_scores) / len(rouge_scores),
        "rougeL": sum(score["rougeL"].fmeasure for score in rouge_scores) / len(rouge_scores),
    }

    print("Evaluation Results:")
    print(f"Average ROUGE-1: {avg_rouge['rouge1']:.4f}")
    print(f"Average ROUGE-2: {avg_rouge['rouge2']:.4f}")
    print(f"Average ROUGE-L: {avg_rouge['rougeL']:.4f}")
    # print(f"Sentiment Classification Accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    eval_file = "evaluation_data_sum.json" 

    generated_summaries_file = " withsentiment.json"


    evaluate_summarization_and_sentiment(eval_file, generated_summaries_file)
