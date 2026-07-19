from database import init_db

# Database sab se pehle initialize
init_db()


from fastapi import FastAPI
from collector import get_history
from logic_engine import weighted_vote


app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "Wingo AI Version 3 Running"
    }


@app.get("/predict")
def predict():

    history = get_history()

    result = weighted_vote(history)

    return {
        "history": history,
        "weighted_prediction": result
    }


@app.get("/stats")
def stats():

    from database import get_stats

    return get_stats()
