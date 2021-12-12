from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from app.chat.emoji import get_score_from_emoji
import pandas as pd
import json

BATCH = 20

LABELS_SCORES = {
    "NEU": 0.5,
    "POS": 0.99,
    "NEG": 0.01
}


class Model:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("finiteautomata/beto-sentiment-analysis")
        self.model = AutoModelForSequenceClassification.from_pretrained("finiteautomata/beto-sentiment-analysis")
        self.nlp = pipeline('sentiment-analysis', model=self.model, tokenizer=self.tokenizer)

    def predict(self, sentence):
        return self.nlp(sentence)

    def generate_df_with_scores(self, telegram_chat):
        df = pd.DataFrame(telegram_chat["messages"])
        df["scores"] = df[df['sticker_emoji'].notna()]["sticker_emoji"].apply(get_score_from_emoji)
        df["date"] = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S')
        for i in range(-(len(df)//-BATCH)):
            df_chunk = df[BATCH*i:BATCH*i+BATCH]
            text_df = df_chunk[(df_chunk['text'].notna()) & df_chunk['text']]['text'].to_frame()
            prediction_scores = self.predict(text_df['text'].to_list())
            scores = [LABELS_SCORES[i["label"]] * i["score"] for i in prediction_scores]
            text_df["scores"] = scores
            df["scores"] = text_df["scores"].combine_first(df["scores"])
        return df
