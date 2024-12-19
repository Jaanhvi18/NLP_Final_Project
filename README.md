# NLP_Final_Project


## Valorant Game Outcome Classification

Since some of the files are too big to be in the github, all of them can be found in this linked google drive: https://drive.google.com/drive/folders/1Yq1FoID2--xH3WDt12w25N4uAWQiM4zE?usp=sharing

Many of the files are found in the TweeBankNLP zip which you have to unzip:

The models we used for sentiment analysis are as follows:
- distilbert/distilbert-base-uncased-finetuned-sst-2-english
- cardiffnlp/twitter-roberta-base-sentiment-latest
- siebert/sentiment-roberta-large-english

To get the roberta twitter model finetuned on Reddit you will have to run the file which first finetunes the model and creates it as a folder and then use that as your model path.
