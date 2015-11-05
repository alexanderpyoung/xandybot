import csv
import random
import tweepy
import json
import time

def check_creds():
    try:
        cred_file = open("/home/ebooks/cred.json")
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
            cred_file = open("/home/ebooks/cred.json", 'w')
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
    with open("/home/ebooks/tweets.csv", newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        words = [line['text'] for line in reader]
    return ' '.join(words)

def generate_triplets(tweet_array):
    triplets = []
    words = tweet_array.split()
    for i in range(len(words) - 3):
        triplets.append((words[i], words[i+1], words[i+2]))
    return triplets
    #    for i in range(0, len(words) - 2):
    #        yield (words[i], words[i+1], words[i+2])

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

def generate_message(dictionary, triplets):
    message_length = 20
    # select a random starting word and succession word
    random_trip = random.randint(0, len(triplets))
    random_word = random.randint(0, 1)
    initial = triplets[random_trip][random_word]
    second = triplets[random_trip][random_word + 1]
    chosen_array = []
    for i in range(message_length):
        try:
            next_word = dictionary[(initial, second)][random.randint(0, len(dictionary[(initial, second)]) - 1 )]
            if not "@" in next_word and not next_word.startswith("http:") \
                    and not next_word.startswith("https:") and not next_word.startswith("#") \
                    and not next_word.startswith("RT"): 
                chosen_array.append(next_word)
                initial, second = second, next_word
            else:
                continue
        except KeyError as e:
            print(e.args)
            continue
    return ' '.join(chosen_array)

if __name__ == "__main__":
    credentials = check_creds()
    api = tweepy.API(credentials)
    generator = generate_triplets(load_tweets())
    dictionary = generate_dictionary(generator)
    while True:
        message = generate_message(dictionary, generator)
        try:
            api.update_status(status=message)
            time.sleep(600)
        except tweepy.error.TweepError as e:
            print(e.reason)
