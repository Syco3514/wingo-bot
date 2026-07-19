from fastapi import FastAPI
from database import *
from collector import *
from logic_engine import *


app=FastAPI()


init_db()



@app.get("/")
def home():

    return {
        "status":"Wingo AI Running"
    }




@app.get("/predict")
def predict():

    try:

        history=get_history()

        result=vote(history)


        return {

        "history":history,
        "prediction":result["prediction"],
        "votes":result["votes"]

        }


    except Exception as e:

        return {
            "error":str(e)
        }



@app.get("/stats")
def stats():

    return get_stats()
