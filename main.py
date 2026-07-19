from fastapi import FastAPI

from database import *
from collector import *

from logic_engine import *
from logic_engine import weighted_vote



init_db()


app=FastAPI()



@app.get("/")
def home():

    return {
    "status":"Wingo AI Version 3"
    }



@app.get("/predict")
def predict():


    history=get_history()


    result=weighted_vote(history)



    return {


    "history":history,


    "weighted_prediction":result


    }



@app.get("/stats")
def stats():

    return get_stats()
