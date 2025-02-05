from flask import Flask
import asyncio

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello world</p>"

def fetch_sensebox_data():
    #todo
    return