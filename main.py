import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://pakgames.pro/",
    "Origin": "https://pakgames.pro",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

last_issue = None
game_history = []
logics_stats = [{"id": i, "wins": 0, "total": 0, "last_pred": None} for i in range(1, 201)]

BASE_AMOUNT = 10
multiplier = 3

predictions_state = {
    "overall": {"predict": "WAIT", "stage": 1, "amount": BASE_AMOUNT, "last_pred": None},
    "rate_90": {"predict": "WAIT", "stage": 1, "amount": BASE_AMOUNT, "last_pred": None},
    "rate_80": {"predict": "WAIT", "stage": 1, "amount": BASE_AMOUNT, "last_pred": None},
    "rate_70": {"predict": "WAIT", "stage": 1, "amount": BASE_AMOUNT, "last_pred": None},
}

def get_bs(num):
    return "SMALL" if int(num) <= 4 else "BIG"

def execute_logic(logic_id, history):
    if not history:
        return "BIG" if logic_id % 2 == 0 else "SMALL"
    
    latest = history[0]
    latest_num = int(latest["number"])
    
    if logic_id <= 50:
        return latest["result"] if (latest_num + logic_id) % 2 == 0 else ("BIG" if latest["result"] == "SMALL" else "SMALL")
    elif logic_id <= 100:
        lookback = (logic_id % 5) + 1
        if len(history) >= lookback:
            return history[lookback - 1]["result"]
        return "SMALL"
    elif logic_id <= 150:
        issue_last_digit = int(str(latest["issue"])[-1])
        return "BIG" if (issue_last_digit + logic_id) % 3 == 0 else "SMALL"
    else:
        big_count = sum(1 for x in history[:10] if x["result"] == "BIG")
        return "BIG" if (big_count > 5 and logic_id % 2 == 0) else "SMALL"

def update_stages(pred_type, actual_result):
    state = predictions_state[pred_type]
    current_pred = state["last_pred"]
    
    if not current_pred or current_pred == "WAIT":
        return
        
    if actual_result == current_pred:
        state["stage"] = 1
        state["amount"] = BASE_AMOUNT
    else:
        state["stage"] += 1
        state["amount"] = BASE_AMOUNT * (multiplier ** (state["stage"] - 1))

def prediction_engine():
    global last_issue, game_history
    while True:
        try:
            ts = int(time.time() * 1000)
            url = f"{API_URL}?ts={ts}"
            res = requests.get(url, headers=HEADERS, timeout=10)
            
            # Agar API response 200 OK nahi de rahi
            if res.status_code != 200:
                print(f"[Engine Warning] API returned status code {res.status_code}. Possible Cloudflare block.")
                time.sleep(5)
                continue
                
            try:
                data = res.json()
            except ValueError:
                print(f"[Engine Error] Response is not JSON. Text snippet: {res.text[:200]}")
                time.sleep(5)
                continue
            
            if data.get("code") == 0 and data.get("data"):
                latest_data = data["data"]["list"][0]
                issue = latest_data["issueNumber"]
                number = latest_data["number"]
                actual_result = get_bs(number)
                
                if issue == last_issue:
                    time.sleep(2)
                    continue
                    
                if last_issue is not None:
                    for logic in logics_stats:
                        if logic["last_pred"] == actual_result:
                            logic["wins"] += 1
                        if logic["last_pred"] is not None:
                            logic["total"] += 1
                            
                    update_stages("overall", actual_result)
                    update_stages("rate_90", actual_result)
                    update_stages("rate_80", actual_result)
                    update_stages("rate_70", actual_result)
                
                last_issue = issue
                game_history.insert(0, {"issue": issue, "number": number, "result": actual_result})
                if len(game_history) > 50:
                    game_history.pop()
                    
                votes_all = {"BIG": 0, "SMALL": 0}
                votes_90 = {"BIG": 0, "SMALL": 0}
                votes_80 = {"BIG": 0, "SMALL": 0}
                votes_70 = {"BIG": 0, "SMALL": 0}
                
                count_90, count_80, count_70 = 0, 0, 0
                
                for logic in logics_stats:
                    pred = execute_logic(logic["id"], game_history)
                    logic["last_pred"] = pred
                    
                    win_rate = (logic["wins"] / logic["total"] * 100) if logic["total"] > 0 else 50.0
                    votes_all[pred] += 1
                    
                    if win_rate >= 90:
                        votes_90[pred] += 1
                        count_90 += 1
                    if win_rate >= 80:
                        votes_80[pred] += 1
                        count_80 += 1
                    if win_rate >= 70:
                        votes_70[pred] += 1
                        count_70 += 1
                
                if votes_all["BIG"] >= 101:
                    predictions_state["overall"]["predict"] = "BIG"
                elif votes_all["SMALL"] >= 101:
                    predictions_state["overall"]["predict"] = "SMALL"
                else:
                    predictions_state["overall"]["predict"] = "BIG" if votes_all["BIG"] > votes_all["SMALL"] else "SMALL"
                    
                predictions_state["rate_90"]["predict"] = ("BIG" if votes_90["BIG"] >= votes_90["SMALL"] else "SMALL") if count_90 > 0 else "WAIT"
                predictions_state["rate_80"]["predict"] = ("BIG" if votes_80["BIG"] >= votes_80["SMALL"] else "SMALL") if count_80 > 0 else "WAIT"
                predictions_state["rate_70"]["predict"] = ("BIG" if votes_70["BIG"] >= votes_70["SMALL"] else "SMALL") if count_70 > 0 else "WAIT"
                
                for key in predictions_state:
                    predictions_state[key]["last_pred"] = predictions_state[key]["predict"]
                    
                print(f"[Engine] Issue #{issue} processed successfully.")
                
            time.sleep(2)
        except Exception as e:
            print(f"[Engine Fatal Error]: {e}")
            time.sleep(5)

threading.Thread(target=prediction_engine, daemon=True).start()

@app.get("/api/data")
def get_data():
    latest_result = game_history[0] if game_history else {"issue": "N/A", "number": "-", "result": "-"}
    return {
        "latest_result": latest_result,
        "predictions": predictions_state,
        "total_logics": len(logics_stats),
        "active_history_count": len(game_history)
    }
