import csv
import random
import tweepy
import json
import time

def check_creds():
    try:
        cred_file = open("cred.json")
        cred_data = json.load(cred_file)
        auth = tweepy.OAuthHandler(cred_data['consumer_token'],
            cred_data['consumer_secret'])
        auth.set_access_token(cred_data['access_token'],
            cred_data['access_token_secret'])
        cred_file.close()
        return auth
    except IOError:
        consumer_token = input("Enter consmer token: ")
        consumer_secret = input("Enter consumer secret: ")
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        redirect_url = auth.get_authorization_url()
        print("Get verifier from: " + redirect_url)
        verifier = input("Input verifier: ")
        try:
            auth.get_access_token(verifier)
            cred_file = open("cred.json", 'w')
            json.dump({'consumer_token': consumer_token, 
                'consumer_secret' : consumer_secret,
                'access_token' : auth.access_token, 
                'access_token_secret' : auth.access_token_secret}, cred_file)
            cred_file.close()
            check_creds()
        except tweepy.TweepError:
            print("Try again. Get verifier from: " + redirect_url)
            check_creds()

def load_tweets():
    with open("tweets.csv", newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        words = [line['text'] for line in reader if not line['text'].startswith("RT")]
    return ' '.join(words).split()

def generate_triplets(words):
    for i in range(len(words) - 2):
      yield (words[i], words[i+1], words[i+2])

def generate_dictionary(triplet_generator):
    return_dictionary = {}
    for i, j, k in triplet_generator:
        key = (i, j)
        value = k
        if key not in return_dictionary:
            return_dictionary[key] = [value]
        else:
            return_dictionary[key].append(value)
    return return_dictionary

def filter(word):
    if not "@" in word and not word.startswith("http:") \
        and not word.startswith("https:") and not word.startswith("#") \
        and not word.startswith("RT") and word is not None:
        return True
    else:
        return False        

def get_two_words(triplets):
    keys = list(triplets.keys())
    random_trip = random.choice(keys)
    initial = random_trip[0]
    second = random_trip[1]
    if filter(initial) and filter(second):
        return (initial, second)
    else:
        return get_two_words(triplets)

def get_next_word(initial, second, dictionary):
    next_dict = [word for word in dictionary[(initial, second)] if filter(word)]
    if len(next_dict) > 0:
        next_word = next_dict[random.randint(0, 
            len(next_dict) - 1)]
        return next_word

def generate_message(dictionary):
    message_length = 20
    # select a random starting word and succession word
    initial, second = get_two_words(dictionary)
    chosen_array = [initial, second]
    for i in range(message_length):
        try:
            next_word = get_next_word(initial, second, dictionary)
            if next_word is not None:
                chosen_array.append(next_word)
                initial, second = second, next_word
            else:
                break
        except KeyError:
            break
    return ' '.join(chosen_array)

if __name__ == "__main__":
    credentials = check_creds()
    api = tweepy.API(credentials)
    generator = generate_triplets(load_tweets())
    dictionary = generate_dictionary(generator)
    while True:
        message = generate_message(dictionary)
#        print(message)
        try:
            api.update_status(status=message)
            time.sleep(600)
        except tweepy.error.TweepError as e:
            print(str(e.response))
