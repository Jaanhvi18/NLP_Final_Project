# NLP Final Project

Since some of the files are too large to include in the GitHub repository, all necessary files can be found in the following Google Drive link:  
[Google Drive Folder](https://drive.google.com/drive/folders/1Yq1FoID2--xH3WDt12w25N4uAWQiM4zE?usp=sharing)

### File Information
Many of the files are included in the `TweeBankNLP.zip`, which you will need to unzip.

### Models Used for Sentiment Analysis
The following models were utilized for sentiment analysis:
1. `distilbert/distilbert-base-uncased-finetuned-sst-2-english`
2. `cardiffnlp/twitter-roberta-base-sentiment-latest`
3. `siebert/sentiment-roberta-large-english`

To get the `roberta` Twitter model fine-tuned on Reddit:
- Run the provided script, which fine-tunes the model and saves it as a folder. 
- Use the resulting folder path as the model path for subsequent tasks.

### Files Overview
- **`model.py`**: Contains the code for sentiment analysis.
- **`eval.py`**: Implements the ROUGE metric for evaluation.

---

### Instructions
1. **Accessing the Necessary Files**:
   - Download the files from the linked Google Drive folder.
   - Extract `TweeBankNLP.zip`.

2. **Fine-Tuning the Roberta Model**:
   - Locate the script for fine-tuning within the project directory.
   - Execute the script to create a folder for the fine-tuned model.
   - Use the folder path for loading the fine-tuned model.

3. **Sentiment Analysis**:
   - Use `model.py` to perform sentiment analysis with the specified models.

4. **Evaluation**:
   - Use `eval.py` to compute the ROUGE score for performance evaluation.
