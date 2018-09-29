from tweepy import OAuthHandler
from tweepy import Stream

# Import twitter keys and tokens
# from config import *
from my_config import *

# Import listener
from tools.tweet_listener import TweetStreamListener

def main():
    """Pipelines"""

    print("==> Start retrieving tweets...")

    # Create instance of the tweepy tweet stream listener
    listener = TweetStreamListener(google_api_key)

    # Set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Set the program to restart automatically in case of errors
    while True:
        try:
            # Create instance of the tweepy stream
            stream = Stream(auth, listener)

            # Search twitter for topics of your interests
            stream.filter(track=['#interstellar', '#inception', '#dunkirk', 
                                'interstellar', 'inception', 'dunkirk'])
        except KeyboardInterrupt:
            # To stop the program
            stream.disconnect()
            print("==> Stop")
            break
        except:
            continue

if __name__ == '__main__':
    main()