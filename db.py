from flask import Flask
from flask_pymongo import pymongo
from os import environ 
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
app = Flask(__name__)

usr = environ.get('MONGO_USER')
pwd = environ.get('MONGO_PASSWORD')
db = environ.get('MONGO_DB')
connect = "mongodb+srv://" + usr + ":" + pwd +"@cluster0.v8xls.mongodb.net/gcb-products?retryWrites=true&w=majority"
client = pymongo.MongoClient(connect)
mongodb = client[db]
collection = mongodb['products']