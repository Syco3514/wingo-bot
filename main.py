from fastapi import FastAPI

from database import *
from collector import *
from logic_engine import *


app=FastAPI()


init_db()



@app.get("/")
def home():

    return {
    "status":"Wingo AI V2 Running"
    }



@app.get("/predict")
def predict():

    history=get_history()


    result=all_predictions(history)


    return {

    "history":history,

    "predictions":result

    }



@app.get("/stats")
def stats():

    return get_all()
