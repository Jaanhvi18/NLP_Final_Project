
1. Scraping Reddit Posts
Uses Reddit API PRAW to enable authenticated access to fetch data from Reddit. A list of gaming-related subreddits, such as r/gaming and r/VALORANT, is defined as the target sources for scraping.
The scraper iterates through the subreddit list and fetches posts using specific filters, including post_limit, time_filter (e.g., year), min_score, and min_comments. Key details, such as titles, post bodies, authors, scores, timestamps, and comments, are extracted. 


2. Processing Posts
Each post is analyzed to extract relevant information:
Bug-related keywords are identified to classify the post as a potential bug report.
Platform-specific keywords are detected to determine which gaming platform the post refers to.
Bug severity is classified into levels like critical, high, medium, or low.
Mentions of game titles are extracted using Named Entity Recognition (NER) with spaCy.
Sentiment analysis is performed to determine the tone of the post (polarity and subjectivity).
Posts are categorized into predefined labels, such as "Bug," "Feature Request," "Question," or "Other," based on detected keywords.

3. Processing Comments
Comments associated with each post are analyzed to gather additional insights:
Sentiment analysis is performed on the comment text.
Platform mentions are detected using predefined keywords.
The presence of solution-related keywords (e.g., "fixed," "resolved") is checked.
Comments from the original poster (OP) are flagged for further analysis.

4. Saving Scraped Data
The scraped and processed data is saved in two formats: JSON and CSV

5. Calculating Summary Statistics
Key metrics are calculated and displayed:
Total number of posts and comments processed.
Distribution of platform mentions across posts.
Severity distribution of bugs, showing the number of posts categorized as critical, high, medium, or low severity.

6. Aggregating Sentiment by Severity
Average sentiment polarity is calculated for each bug severity level to identify trends. This step helps reveal how user sentiment varies with different bug severities, offering valuable insights into user experiences.

1. Purpose
The script processes game-related discussions, extracts key points, and generates both a summary and metrics about the comments. The output includes:
Key takeaways (summarized sentences).
Metrics such as total comments, average scores, and sentiment distributions.
Reports saved as a TSV file and a detailed text report.

2. Key Components
This script processes the JSON file created by the prior script, which collects game-related discussions and metadata from DuckDuckGo. Using NLTK for text preprocessing and TextBlob for sentiment analysis, it processes the discussions by flattening nested comment structures, cleaning and tokenizing text, and scoring sentences based on word frequency. It then extracts the most important sentences to generate summaries. Sentiment analysis categorizes comments as positive, negative, or neutral, while metrics like the total number of comments, average scores, and sentiment distribution are calculated to provide insights into the discussions.

3. Generating and Saving Reports
The script organizes the processed data from the JSON file into two reports. A TSV report provides tabular summaries with key metrics, while a text report offers detailed analysis, including summaries and sentiment trends. Summaries are created by selecting the top-ranked sentences, and metrics are aggregated from the processed data. These reports are saved for easy sharing and further analysis.

4. Outputs
Using tools like NLTK for text preprocessing and TextBlob for sentiment analysis, the script produces structured reports. These include key discussion points, sentiment trends, and comment metrics, derived from the raw data collected by the previous script. The output helps users quickly understand and prioritize game-related community feedback.

Next steps:
Find a better text classifier than nltk
It does not really understand stuff like sarcasm 
NLTK is more frequency-based for how it classifies things and doesn't really look at the actual semantics of the text (num of positive vs num of negative)
We were thinking of using a text classifier that is trained on Twitter that we found instead since that's more similar to Reddit in the way that people talk about topics and might give better results compared to NLTK 
https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest




