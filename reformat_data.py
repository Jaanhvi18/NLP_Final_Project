import json

def reformat_summaries(input_txt, output_json):
    """Reformat summaries from a .txt file into a JSON structure, ensuring the title is included once."""
    generated_summaries = []
    with open(input_txt, "r") as f:
        lines = f.readlines()
    
    current_summary = []
    current_sentiment = None
    current_title = None
    
    for line in lines:
        line = line.strip()
        
 
        if line.startswith("Discussion:"):
            if current_summary:
 
                full_summary = f"{current_title}\n" + "\n".join(current_summary) if current_title else "\n".join(current_summary)
                generated_summaries.append({
                    "predicted_summary": full_summary,
                    "predicted_sentiment": {"polarity": current_sentiment}
                })
                current_summary = []
                current_sentiment = None
                current_title = None
            
            current_title = line.split("Discussion:", 1)[-1].strip()
        

        elif line.startswith("Summary Sentiment:"):
            sentiment_parts = line.split(" ")
            try:
                current_sentiment = float(sentiment_parts[-1].strip("()"))  
            except ValueError:
                current_sentiment = None 
        

        elif line.startswith("-"):
            current_summary.append(line)
    

    if current_summary:
        full_summary = f"{current_title}\n" + "\n".join(current_summary) if current_title else "\n".join(current_summary)
        generated_summaries.append({
            "predicted_summary": full_summary,
            "predicted_sentiment": {"polarity": current_sentiment}
        })
    

    with open(output_json, "w") as f:
        json.dump(generated_summaries, f, indent=4)
    
    print(f"Reformatted summaries saved to {output_json}")


input_txt = "reports/discussion_detailed_20241218_194204.txt"
output_json = "withsentiment.json"
reformat_summaries(input_txt, output_json)
