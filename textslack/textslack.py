# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 23:53:32 2020

@author: Ankit Raj
"""
import re
import pandas as pd
import nltk
nltk.download('brown')
nltk.download('name')
nltk.download('universal_tagset')
from nltk.tokenize import word_tokenize, regexp_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from textblob import TextBlob
import string
from collections import Counter
from normalise import normalise

from sklearn.base import TransformerMixin, BaseEstimator

class TextSlack(BaseEstimator, TransformerMixin):
    def __init__(self, variety='BrE', user_abbrevs={}, stop_words=stopwords.words('english'), lemmatizer=WordNetLemmatizer()):
        self.variety = variety
        self.user_abbrevs = user_abbrevs
        self.stop_words = stop_words
        self.lemmatizer = lemmatizer

    def fit(self, X, y=None):
        return self

    def transform(self, X, *_):
        if isinstance(X, pd.Series):
            X_copy = X.copy()
        else:
            return self._preprocess_text(X)
        return X_copy.apply(self._preprocess_text)

    def _preprocess_text(self, text):
        normalised_text = self._normalise(text)
        normalised_text = re.sub(' +', ' ', normalised_text)
        words = regexp_tokenize(normalised_text.lower(), r'[A-Za-z]+')
        removed_punct = self._remove_punct(words)
        removed_stopwords = self._remove_stopwords(removed_punct)
        return self._lemmatize(removed_stopwords)

    def _normalise(self, text):
        try:
            return ' '.join(normalise(word_tokenize(text), variety=self.variety, user_abbrevs=self.user_abbrevs, verbose=False))
        except:
            return text

    def _remove_punct(self, words):
        return [w for w in words if w not in string.punctuation]

    def _remove_stopwords(self, words):
        return [w for w in words if w not in self.stop_words and len(w)>1]

    def _lemmatize(self, words):
        return ' '.join([self.lemmatizer.lemmatize(w) for w in words])
    
    def extract_nouns(self, text):
        processed_text = self._preprocess_text(text)
        pos_tags, _ = self._blob_features(processed_text)
        return ' '.join([w for w, p in pos_tags if p == 'NN'])
    
    def extract_verbs(self, text):
        processed_text = self._preprocess_text(text)
        pos_tags, _ = self._blob_features(processed_text)
        return ' '.join([w for w, p in pos_tags if p == 'VB'])
      
    def extract_adjectives(self, text):
        processed_text = self._preprocess_text(text)
        pos_tags, _ = self._blob_features(processed_text)
        return ' '.join([w for w, p in pos_tags if p == 'JJ'])
    
    def extract_adverbs(self, text):
        processed_text = self.preprocess_text(text)
        pos_tags, _ = self._blob_features(processed_text)
        return ' '.join([w for w, p in pos_tags if p == 'RB'])
    
    def sentiment(self, text):
        processed_text = self._preprocess_text(text)
        _, polarity = self._blob_features(processed_text)
        return 'pos' if polarity > 0.0 else 'neg' if polarity < 0.0 else 'neu'

    def _blob_features(self, text):
        blob = TextBlob(text)
        return blob.tags, blob.polarity
    
    def word_occurances(self, word, text):
        word_count_dic = dict(Counter([w for w in text.split()]))
        return [c for w, c in word_count_dic.items() if w==word][0]