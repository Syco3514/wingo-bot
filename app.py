import threading
import time
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Taake frontend easily data fetch kar sake

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://pakgames.pro/",
    "Origin": "https://pakgames.pro",
    "User-Agent": "Mozilla/5.0",
}

# --- GLOBAL DATA STRUCTURES ---
last_issue = None
game_history = []  # Last 50 results store karne k liye

# 200 Logics Initialize karne ka dynamic tariqa
# Har logic ka record: {'id': i, 'wins': 0, 'total': 0, 'last_pred': None}
logics_stats = [{"id": i, "wins": 0, "total": 0, "last_pred": None} for i in range(1, 201)]

# 4 Types ki predictions k Stages/Amounts (Martingale)
BASE_AMOUNT = 10
MULTIPLIER = 3

predictions_state = {
    "overall": {"predict": "WAIT", "stage": 1, "amount": BASE_AMOUNT, "last_pred": None},
    "rate_90": {"predict": "WAIT", "stage": 1, "amount": BASE_AMOUNT, "last_pred": None},
    "rate_80": {"predict": "WAIT", "stage": 1, "amount": BASE_AMOUNT, "last_pred": None},
    "rate_70": {"predict": "WAIT", "stage": 1, "amount": BASE_AMOUNT, "last_pred": None},
}


# --- UTILITY FUNCTIONS ---
def get_bs(num):
    return "SMALL" if int(num) <= 4 else "BIG"


# 200 Different Logics Generator
def execute_logic(logic_id, history):
    if not history:
        return "BIG" if logic_id % 2 == 0 else "SMALL"

    latest = history[0]
    latest_num = int(latest["number"])

    # Base patterns based on ID properties
    if logic_id <= 50:
        # Pattern 1: Follow or Flip last result based on periodicity
        return (
            latest["result"]
            if (latest_num + logic_id) % 2 == 0
            else ("BIG" if latest["result"] == "SMALL" else "SMALL")
        )
    elif logic_id <= 100:
        # Pattern 2: Multi-step historical skip check
        lookback = (logic_id % 5) + 1
        if len(history) >= lookback:
            return history[lookback - 1]["result"]
        return "SMALL"
    elif logic_id <= 150:
        # Pattern 3: Mathematical modulo operations on issue numbers
        issue_last_digit = int(str(latest["issue"])[-1])
        return "BIG" if (issue_last_digit + logic_id) % 3 == 0 else "SMALL"
    else:
        # Pattern 4: Hot/Cold count switching
        big_count = sum(1 for x in history[:10] if x["result"] == "BIG")
        return "BIG" if (big_count > 5 and logic_id % 2 == 0) else "SMALL"


def update_stages(pred_type, actual_result):
    state = predictions_state[pred_type]
    current_pred = state["last_pred"]

    if not current_pred or current_pred == "WAIT":
        return

    if actual_result == current_pred:
        # WIN -> Reset Stage
        state["stage"] = 1
        state["amount"] = BASE_AMOUNT
    else:
        # LOSS -> Next Stage Multiplier
        state["stage"] += 1
        state["amount"] = BASE_AMOUNT * (MULTIPLIER ** (state["stage"] - 1))


# --- MAIN ENGINE LOOP ---
def prediction_engine():
    global last_issue, game_history

    while True:
        try:
            ts = int(time.time() * 1000)
            url = f"{API_URL}?ts={ts}"
            res = requests.get(url, headers=HEADERS, timeout=10)
            data = res.json()

            if data.get("code") == 0 and data.get("data"):
                latest_data = data["data"]["list"][0]
                issue = latest_data["issueNumber"]
                number = latest_data["number"]
                actual_result = get_bs(number)

                if issue == last_issue:
                    time.sleep(2)
                    continue

                # 1. Agar Naya Issue Aya Hai, Pehle Purani Predictions Check Karo
                if last_issue is not None:
                    # Logics ka win rate update karo
                    for logic in logics_stats:
                        if logic["last_pred"] == actual_result:
                            logic["wins"] += 1
                        if logic["last_pred"] is not None:
                            logic["total"] += 1

                    # 4 Main Predictions k Stages Update Karo
                    update_stages("overall", actual_result)
                    update_stages("rate_90", actual_result)
                    update_stages("rate_80", actual_result)
                    update_stages("rate_70", actual_result)

                # History update karo
                last_issue = issue
                game_history.insert(0, {"issue": issue, "number": number, "result": actual_result})
                if len(game_history) > 50:
                    game_history.pop()

                # 2. AB NAYI PREDICTIONS GENERATE KARO (VOTING SYSTEM)
                votes_all = {"BIG": 0, "SMALL": 0}
                votes_90 = {"BIG": 0, "SMALL": 0}
                votes_80 = {"BIG": 0, "SMALL": 0}
                votes_70 = {"BIG": 0, "SMALL": 0}

                count_90, count_80, count_70 = 0, 0, 0

                for logic in logics_stats:
                    # Is logic ki prediction nikalo
                    pred = execute_logic(logic["id"], game_history)
                    logic["last_pred"] = pred  # Save for next round check

                    # Calculate Win Rate
                    win_rate = (logic["wins"] / logic["total"] * 100) if logic["total"] > 0 else 50.0

                    # Voting distribute karo
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

                # Decision Making Based on Rules
                # Prediction 1: Overall Voting (Must have 101+ votes)
                if votes_all["BIG"] >= 101:
                    predictions_state["overall"]["predict"] = "BIG"
                elif votes_all["SMALL"] >= 101:
                    predictions_state["overall"]["predict"] = "SMALL"
                else:
                    predictions_state["overall"]["predict"] = (
                        "BIG" if votes_all["BIG"] > votes_all["SMALL"] else "SMALL"
                    )

                # Prediction 2, 3, 4: Tiered Win Rates (Majority based)
                predictions_state["rate_90"]["predict"] = (
                    ("BIG" if votes_90["BIG"] >= votes_90["SMALL"] else "SMALL")
                    if count_90 > 0
                    else "NO LOGIC 90%+"
                )
                predictions_state["rate_80"]["predict"] = (
                    ("BIG" if votes_80["BIG"] >= votes_80["SMALL"] else "SMALL")
                    if count_80 > 0
                    else "NO LOGIC 80%+"
                )
                predictions_state["rate_70"]["predict"] = (
                    ("BIG" if votes_70["BIG"] >= votes_70["SMALL"] else "SMALL")
                    if count_70 > 0
                    else "NO LOGIC 70%+"
                )

                # Save current prediction as last_pred to check in next round
                for key in predictions_state:
                    predictions_state[key]["last_pred"] = predictions_state[key]["predict"]

                print(f"[Engine] Processed Issue #{issue}. Live predictions updated.")

            time.sleep(2)
        except Exception as e:
            print(f"[Engine Error]: {e}")
            time.sleep(5)


# Background Thread Start Karein taake Server k sath continuous chalta rahe
threading.Thread(target=prediction_engine, daemon=True).start()


# --- API ENDPOINTS FOR FRONTEND ---
@app.route("/api/data", methods=["GET"])
def get_data():
    latest_result = game_history[0] if game_history else {"issue": "N/A", "number": "-", "result": "-"}
    return jsonify(
        {
            "latest_result": latest_result,
            "predictions": predictions_state,
            "total_logics": len(logics_stats),
            "active_history_count": len(game_history),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
