from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from multiprocessing import Process
from bson.objectid import ObjectId
import tensorflow as tf
from pymongo import MongoClient
import numpy as np


model = tf.keras.models.load_model('model')
client = MongoClient(
    "mongodb+srv://admin:123456789admin@cluster0.2nyyv4r.mongodb.net/GraduationProject?retryWrites=true&w=majority"
)
db = client['GraduationProject']


def train_retrieval(data):
    return data


def train_ranking(data):
    return data


def train_models():
    data = 0

    p1 = Process(target=train_retrieval, args=(data,))
    p2 = Process(target=train_ranking, args=(data,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()


def load_collection(collection_name):
    collection = db[collection_name]
    collection_ids = list(collection.find({}, {"_id": 1}))
    collection_ids = list(map(lambda x: np.array([str(x['_id'])]), collection_ids))
    return collection_ids


def recommend_for_customer(customer, items):
    recommendations = []

    for item in items:
        data = {
            'itemId': item,
            'customerId': customer
        }
        score = model.predict(data)
        recommendations.append({
            'itemId': item,
            'score': score
        })
    recommendations = sorted(recommendations, key=lambda d: d['score'], reverse=True)
    return recommendations[:10]


def save_customer_recommendations(customer, recommendations):

    recommendations = list(map(lambda x: ObjectId(str(x['itemId'][0])), recommendations))
    data = {'customerId': ObjectId(str(customer[0])),
            'itemsList': recommendations}
    print(data)
    recommendations_collection = db['recommendations']
    recommendations_collection.replace_one({'customerId': data['customerId']}, data, upsert=True)


def make_recommendations():
    customers = load_collection('customers')
    items = load_collection('items')
    for customer in customers:
        recommendations = recommend_for_customer(customer, items)
        save_customer_recommendations(customer, recommendations)


# scheduler = BackgroundScheduler(daemon=True)
# scheduler.add_job(make_recommendations, 'interval', seconds=60)
# scheduler.start()


app = Flask(__name__)
make_recommendations()
