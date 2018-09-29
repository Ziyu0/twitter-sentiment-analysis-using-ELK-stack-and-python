import json
import pytz
from datetime import datetime

from tweepy.streaming import StreamListener
from textblob import TextBlob
from elasticsearch import Elasticsearch

from tools.google_api_handler import GoogleAPIHandler

class TweetStreamListener(StreamListener):
    def __init__(self, google_api_key=None):
        super(TweetStreamListener, self).__init__()
        self.google_api_key = google_api_key

    def on_data(self, data):
        """"On success.
        To retrieve, process and organize tweets to get structured data
        and inject data into Elasticsearch
        """

        print("=> Retrievd a tweet")

        # Decode json
        dict_data = json.loads(data)

        # Process data
        polarity, subjectivity, sentiment = self._get_sentiment(dict_data)
        print("[sentiment]", sentiment)

        hashtags = self._get_hashtags(dict_data)
        print("[hashtags]", hashtags)

        country = self._get_geo_info(dict_data)
        print("[country]", country)

        timestamp = self._get_timestamp(dict_data)
        print("[time]", timestamp)

        # Inject data into Elasticsearch
        doc = {"author": dict_data["user"]["screen_name"],
               "timestamp": timestamp,
               "message": dict_data["text"],
               "polarity": polarity,
               "subjectivity": subjectivity,
               "sentiment": sentiment,
               "country": country,
               "hashtags":hashtags}
        
        es = Elasticsearch()
        es.index(index="tweet-sentiment",
                 doc_type="new-tweet",
                 body=doc)

        return True

    def on_error(self, status):
        """On failure"""
        print(status)
    
    def _get_sentiment(self, decoded):
        # Pass textual data to TextBlob to process
        tweet = TextBlob(decoded["text"]) if 'text' in decoded else ''

        # [0, 1] where 1 means very subjective
        subjectivity = tweet.sentiment.subjectivity
        # [-1, 1]
        polarity = tweet.sentiment.polarity
        
        # Determine if sentiment is positive, negative, or neutral
        if polarity < 0:
            sentiment = "negative"
        elif polarity == 0:
            sentiment = "neutral"
        else:
            sentiment = "positive"

        return polarity, subjectivity, sentiment
    
    def _get_hashtags(self, decoded):
        hashtags = None

        # Obtain hashtag if available
        if len(decoded["entities"]["hashtags"]) > 0:
            hashtags = decoded["entities"]["hashtags"][0]["text"].title()
        
        return hashtags
    
    def _get_geo_info(self, decoded):
        country = None

        if self.google_api_key:
            handler = GoogleAPIHandler(self.google_api_key)
            if 'coordinates' in decoded and decoded['coordinates'] is not None:
                latitude = str(decoded['coordinates']['coordinates'][1])
                longitude = str(decoded['coordinates']['coordinates'][0])
                country = handler.get_geo_info(latitude, longitude)
        
        return country
    
    def _get_timestamp(self, decoded):
        timestamp = datetime.strptime(decoded['created_at'],'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC).isoformat()
        return timestamp