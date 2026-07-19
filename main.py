from fastapi import FastAPI

from database import init_db
from collector import get_history


# pehle database banao
init_db()


from logic_engine import all_predictions


app = FastAPI()



@app.get("/")
def home():

    return {
        "status":"Wingo AI V2 Running"
    }



@app.get("/predict")
def predict():

    history = get_history()

    result = all_predictions(history)


    return {

        "history":history,
        "predictions":result

    }



@app.get("/stats")
def stats():

    from database import get_all

    return get_all()
