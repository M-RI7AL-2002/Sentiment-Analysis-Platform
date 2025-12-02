# studentdb/utils.py

import joblib
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.calibration import CalibratedClassifierCV
import re
from nltk.tokenize import word_tokenize
import os
from django.conf import settings
import numpy as np
# Construct the full paths using BASE_DIR
vectorizer_path = os.path.join(settings.BASE_DIR, 'studentdb', 'vectorizer.pkl')
model_path = os.path.join(settings.BASE_DIR, 'studentdb', 'calibrated_log_reg.pkl')

# Load the vectorizer and model
vectorizer = joblib.load(vectorizer_path)
calibrated_log_reg = joblib.load(model_path)



def handle_emojis(tweet):
    tweet = re.sub(r'(:\s?\)|:-\)|\(\s?:|\(-:|:\'\))|😀|😃|😄|🙂|😊|🥰|😍|😘|👌|👍|👏|🙏|🤝|💪', ' EMO_POS ', tweet)
    tweet = re.sub(r'(:\s?D|:-D|x-?D|X-?D)|😁|😆|🤩', ' EMO_POS ', tweet)
    tweet = re.sub(r'(<3|:\*)|❤|💘|💝|💖|💗|💓|💞|💕|💟', ' EMO_POS ', tweet)
    tweet = re.sub(r'(;-\)|;-?D|\(-?;)', ' EMO_POS ', tweet)
    tweet = re.sub(r'(:\s?\(|:-\(|\)\s?:|\)-:)|:@|😔|😕|☹|😢|😞|😖|😭|😤|😡|😠|🤬|💩|👎|💔', ' EMO_NEG ', tweet)
    tweet = re.sub(r'(:,\(|:\'\(|:"\()', ' EMO_NEG ', tweet)
    return tweet

def preprocess_word(word):
    # Remove punctuation
    word = word.strip('\'"?!,.():;')
    # Convert more than 2 letter repetitions to 2 letter
    # funnnnny --> funny
    word = re.sub(r'(.)\1+', r'\1\1', word)
    # Remove - & '
    word = re.sub(r'(-|\')', '', word)
    return word

stop_words = set(stopwords.words('english'))
stop_words.update(("chatgpt","openai","url","https","http"))

punct = re.compile(r'(\w+)')

def preprocess_tweet(tweet):
    
    # Convert to lower case
    tweet = tweet.lower()
    
    tokenized = [m.group() for m in punct.finditer(tweet)]
    tweet = ' '.join(tokenized)
    # Replaces URLs with the word URL
    tweet = re.sub(r'((www\.[\S]+)|(https?://[\S]+))', ' URL ', tweet)
    # Replace @handle with the word USER_MENTION
    tweet = re.sub(r'@[\S]+', 'USER_MENTION', tweet)
    # Replaces #hashtag with hashtag
    tweet = re.sub(r'#(\S+)', r' \1 ', tweet)
    # Remove RT (retweet)
    tweet = re.sub(r'\brt\b', '', tweet)
    # Replace 2+ dots with space
    tweet = re.sub(r'\.{2,}', ' ', tweet)
    # Strip space, " and ' from tweet
    tweet = tweet.strip(' "\'')
    # Replace emojis with either EMO_POS or EMO_NEG
    tweet = handle_emojis(tweet)
    # Replace multiple spaces with a single space
    tweet = re.sub(r'\s+', ' ', tweet)
    words = " ".join(tweet.split())
    no_digits = ''.join([i for i in words if not i.isdigit()])
    cleaner = " ".join(no_digits.split())
    word_tokens = word_tokenize(cleaner)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]

    #zedt lemmatizer
    lemmatizer = WordNetLemmatizer()
    filtered_sentence = [lemmatizer.lemmatize(token) for token in filtered_sentence]
    filtered_sentence = [preprocess_word(token) for token in filtered_sentence]
    filtered_sentence = " ".join(filtered_sentence)
    
    return filtered_sentence



def predict_sentiment(text):
    processed_text = preprocess_tweet(text)
    features = vectorizer.transform([processed_text])
    probs = calibrated_log_reg.predict_proba(features)
    pred_class = calibrated_log_reg.classes_[np.argmax(probs)]
    return pred_class, probs