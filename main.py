import json
import os
import imagehash  # pip install imagehash
from PIL import Image  # pip install pillow
import pickle
import redis
import logging
import configparser
config = configparser.ConfigParser()


logger = logging.getLogger()
logging.basicConfig(filename='logs.log', filemode='w', encoding='utf-8', level=logging.INFO)

# create config.ini in the following format
# [redis]
# password = <YOUR PASSWORD FROM upstash.io>

config.read('config.ini')

# https://zetcode.com/python/configparser/
# print(config['redis']['password'])

r = redis.Redis(
    host='us1-modern-cat-38535.upstash.io',
    port=38535,
    password=config['redis']['password'],
    ssl=True
)


# read a directory and calculate whash of images and store the array in the redis. return hash array
def update_hash_array(redis, images_dir):
    arr = []
    images_list = [img for img in os.listdir(images_dir)]
    for count, f in enumerate(images_list):
        img = Image.open(''.join([images_dir, '/', f]))
        img_hash = imagehash.whash(img)
        arr.append(img_hash)
    pickled_object = pickle.dumps(arr)

    redis.set('bad', pickled_object)
    return arr


# get hashes for bad image set from redis, calculate avg distance from bad hashes and return the distance avg of img
def hamming_distance_avg(redis, img):
    g = imagehash.whash(img)
    bad = pickle.loads(redis.get('bad'))
    total = 0
    for b in bad:
        diff = g - b
        total = total + diff
    avg = total / len(bad)
    return avg


# open the quotes.json and put it in redis
def update_quotes():
    q = open("quotes.json", "r")
    qj = json.load(q)
    pickled_object = pickle.dumps(qj)
    r.set('quotes', pickled_object)
    quotes = pickle.loads(r.get('quotes'))
    return quotes


if __name__ == '__main__':
    update_hash_array(r, 'bad')
    img1 = Image.open('bad/0059.png')

    hamming_distance_avg(r, img1)
