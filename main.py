from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random


app = FastAPI(
    title="Wingo AI API",
    version="3.0"
)


# Netlify frontend allow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Demo history storage
history_data = [
    1,5,3,8,2,7,4,9,0,6
]


def big_small(number):
    if number >= 5:
        return "BIG"
    else:
        return "SMALL"


def ai_predict(history):

    small = 0
    big = 0

    for n in history:

        if n >= 5:
            big += 1
        else:
            small += 1


    # weighted logic
    last = history[-1]

    if last >= 5:
        small += 2
    else:
        big += 2


    if small > big:
        final = "SMALL"
    elif big > small:
        final = "BIG"
    else:
        final = random.choice(
            ["SMALL","BIG"]
        )


    return {
        "SMALL": small,
        "BIG": big,
        "final": final
    }



@app.get("/")
def home():

    return {
        "status":"Wingo AI Running",
        "version":"3.0",
        "time":str(datetime.now())
    }



@app.get("/history")
def history():

    return {
        "history":history_data
    }



@app.get("/predict")
def predict():

    result = ai_predict(history_data)


    return {

        "history":history_data,

        "weighted_prediction":{

            "SMALL":result["SMALL"],
            "BIG":result["BIG"]

        },

        "final":result["final"]

    }
