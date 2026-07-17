import threading
import time
import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

# Advanced Real-Browser Headers to bypass Cloud Server Block
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://pakgames.pro/",
    "Origin": "https://pakgames.pro",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Connection": "keep-alive"
}

TOTAL_LOGICS = 500
LOOKBACK_TRENDS = 50

logic_stats = {i: {"total_predictions": 0, "correct_predictions": 0, "accuracy": 100.0} for i in range(TOTAL_LOGICS)}

dashboard_data = {
    "last_issue": None,
    "actual_number": None,
    "actual_result": None,
    "stage": 1,
    "investment": 10,
    "tiers": {
        "all_500": {"prediction": "WAIT", "votes_big": 0, "votes_small": 0, "active_count": 500},
        "tier_90": {"prediction": "WAIT", "votes_big": 0, "votes_small": 0, "active_count": 0},
        "tier_80": {"prediction": "WAIT", "votes_big": 0, "votes_small": 0, "active_count": 0},
        "tier_70": {"prediction": "WAIT", "votes_big": 0, "votes_small": 0, "active_count": 0}
    }
}

current_predictions_held = {}
base_amount = 10
multiplier = 3

def bs(num):
    return "SMALL" if int(num) <= 4 else "BIG"

def execute_500_logics(history_list):
    votes = {}
    trends_count = min(LOOKBACK_TRENDS, len(history_list))
    outcomes = []
    numbers = []
    for item in history_list[:trends_count]:
        num = int(item["number"])
        numbers.append(num)
        outcomes.append(bs(num))
        
    if len(outcomes) < 5:
        return {i: "BIG" for i in range(TOTAL_LOGICS)}

    for i in range(TOTAL_LOGICS):
        category = i % 5
        seed = i + 1
        if category == 0:
            votes[i] = "BIG" if outcomes[seed % len(outcomes)] == "SMALL" else "SMALL"
        elif category == 1:
            w = (seed % 6) + 2
            votes[i] = "BIG" if len(set(outcomes[:w])) == 1 and outcomes[0] == "SMALL" else "SMALL"
        elif category == 2:
            w = (seed % 35) + 5
            votes[i] = "BIG" if (sum(numbers[:w]) / w) <= 4.5 else "SMALL"
        elif category == 3:
            w = min(10 + (seed % 40), len(outcomes))
            votes[i] = "SMALL" if (outcomes[:w].count("BIG") / w) > 0.5 else "BIG"
        else:
            votes[i] = "BIG" if (numbers[0] * seed + numbers[min(seed, len(numbers)-1)]) % 10 >= 5 else "SMALL"
            
    return votes

def background_brain_runner():
    global dashboard_data, current_predictions_held, logic_stats
    last_processed_issue = None
    stage = 1
    amount = base_amount
    
    # Using Session for connection persistence
    session = requests.Session()

    while True:
        try:
            ts = int(time.time() * 1000)
            # Fetch with timeout and custom headers session
            res = session.get(f"{API_URL}?ts={ts}&pageSize=60", headers=HEADERS, timeout=15)
            data = res.json()

            if data.get("code") == 0 and "data" in data and "list" in data["data"]:
                history = data["data"]["list"]
                if not history:
                    time.sleep(5)
                    continue
                    
                latest = history[0]
                issue = latest["issueNumber"]

                if issue == last_processed_issue:
                    time.sleep(2)
                    continue

                actual_num = latest["number"]
                actual_res = bs(actual_num)
                
                if last_processed_issue is not None and current_predictions_held:
                    main_pred = current_predictions_held.get("all_500")
                    if main_pred == actual_res:
                        stage = 1
                        amount = base_amount
                    else:
                        stage += 1
                        amount = base_amount * (multiplier ** (stage - 1))

                    past_votes = execute_500_logics(history[1:])
                    for idx, vote in past_votes.items():
                        logic_stats[idx]["total_predictions"] += 1
                        if vote == actual_res:
                            logic_stats[idx]["correct_predictions"] += 1
                        if logic_stats[idx]["total_predictions"] > 0:
                            logic_stats[idx]["accuracy"] = (logic_stats[idx]["correct_predictions"] / logic_stats[idx]["total_predictions"]) * 100

                fresh_votes = execute_500_logics(history)
                t_data = {
                    "all_500": {"b_w": 0, "s_w": 0, "cnt": 0},
                    "tier_90": {"b_w": 0, "s_w": 0, "cnt": 0},
                    "tier_80": {"b_w": 0, "s_w": 0, "cnt": 0},
                    "tier_70": {"b_w": 0, "s_w": 0, "cnt": 0},
                }

                for idx, vote in fresh_votes.items():
                    acc = logic_stats[idx]["accuracy"]
                    t_data["all_500"]["cnt"] += 1
                    if vote == "BIG": t_data["all_500"]["b_w"] += 1
                    else: t_data["all_500"]["s_w"] += 1

                    if acc >= 90.0:
                        t_data["tier_90"]["cnt"] += 1
                        if vote == "BIG": t_data["tier_90"]["b_w"] += 1
                        else: t_data["tier_90"]["s_w"] += 1
                    elif acc >= 80.0:
                        t_data["tier_80"]["cnt"] += 1
                        if vote == "BIG": t_data["tier_80"]["b_w"] += 1
                        else: t_data["tier_80"]["s_w"] += 1
                    elif acc >= 70.0:
                        t_data["tier_70"]["cnt"] += 1
                        if vote == "BIG": t_data["tier_70"]["b_w"] += 1
                        else: t_data["tier_70"]["s_w"] += 1

                new_preds = {}
                for tier_name, metrics in t_data.items():
                    if metrics["cnt"] > 0:
                        pred = "BIG" if metrics["b_w"] >= metrics["s_w"] else "SMALL"
                    else:
                        pred = "WAIT"
                    new_preds[tier_name] = pred
                    dashboard_data["tiers"][tier_name] = {
                        "prediction": pred, "votes_big": metrics["b_w"], "votes_small": metrics["s_w"], "active_count": metrics["cnt"]
                    }

                current_predictions_held = new_preds
                dashboard_data.update({"last_issue": issue, "actual_number": actual_num, "actual_result": actual_res, "stage": stage, "investment": amount})
                last_processed_issue = issue
            else:
                print("API response error or invalid code structure.")

        except Exception as e:
            print(f"Bypasser Loop Error: {str(e)}")
        time.sleep(3)

threading.Thread(target=background_brain_runner, daemon=True).start()

@app.route('/api/live_data', methods=['GET'])
def get_live_data():
    return jsonify(dashboard_data)

@app.route('/')
def home():
    return render_template_string(HTML_UI)

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Quantum 500-Logic Real-Time Predictor</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: auto; }
        header { text-align: center; border-bottom: 2px solid #21262d; padding-bottom: 20px; margin-bottom: 30px; }
        h1 { color: #58a6ff; margin: 0; }
        .grid-system { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .card h2 { margin-top: 0; font-size: 1.1rem; color: #8b949e; }
        .pred-val { font-size: 2rem; font-weight: bold; margin: 15px 0; padding: 5px; border-radius: 5px; }
        .BIG { background-color: rgba(46, 160, 67, 0.15); color: #3fb950; }
        .SMALL { background-color: rgba(248, 81, 73, 0.15); color: #f85149; }
        .WAIT { background-color: rgba(210, 153, 34, 0.15); color: #d29922; }
        .metrics-sub { font-size: 0.85rem; color: #8b949e; line-height: 1.5; }
        .highlight-blue { color: #58a6ff; font-weight: bold; }
        .highlight-yellow { color: #d29922; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔮 AI QUANTUM 500-LOGIC MULTI-TIER ENGINE</h1>
            <p>Cloud Server Status: <span style="color:#3fb950; font-weight:bold;">● 24/7 BACKGROUND ALIVE</span></p>
        </header>

        <div class="card" style="margin-bottom: 25px; text-align: left;">
            <h3>📊 LIVE GAME TRANSACTION META STATION</h3>
            <p>Processed Issue ID: <span class="highlight-blue" id="lbl-issue">Loading...</span> | 
               Last Number: <span class="highlight-yellow" id="lbl-num">--</span> (<span id="lbl-res">--</span>)</p>
            <p>Current Stage Phase: <span class="highlight-yellow" id="lbl-stage">1</span> | Recommended Trade Volume: <span style="color:#58a6ff; font-weight:bold;" id="lbl-capital">10</span> PKR</p>
        </div>

        <div class="grid-system">
            <div class="card">
                <h2>🌐 SECTION 1: ALL 500 LOGICS</h2>
                <div class="pred-val" id="all_500-pred">--</div>
                <div class="metrics-sub">
                    Logics Voted: <span id="all_500-count">0</span><br>
                    Votes Big: <span id="all_500-big">0</span> | Small: <span id="all_500-small">0</span>
                </div>
            </div>
            <div class="card" style="border-top: 4px solid #3fb950;">
                <h2>🔥 SECTION 2: TIER 90%+ ACCURACY</h2>
                <div class="pred-val" id="tier_90-pred">--</div>
                <div class="metrics-sub">
                    Active Logics: <span id="tier_90-count" class="highlight-blue">0</span><br>
                    Votes Big: <span id="tier_90-big">0</span> | Small: <span id="tier_90-small">0</span>
                </div>
            </div>
            <div class="card" style="border-top: 4px solid #d29922;">
                <h2>⚡ SECTION 3: TIER 80%+ ACCURACY</h2>
                <div class="pred-val" id="tier_80-pred">--</div>
                <div class="metrics-sub">
                    Active Logics: <span id="tier_80-count">0</span><br>
                    Votes Big: <span id="tier_80-big">0</span> | Small: <span id="tier_80-small">0</span>
                </div>
            </div>
            <div class="card" style="border-top: 4px solid #f85149;">
                <h2>📈 SECTION 4: TIER 70%+ ACCURACY</h2>
                <div class="pred-val" id="tier_70-pred">--</div>
                <div class="metrics-sub">
                    Active Logics: <span id="tier_70-count">0</span><br>
                    Votes Big: <span id="tier_70-big">0</span> | Small: <span id="tier_70-small">0</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        function fetchLiveBrainEngineUpdates() {
            fetch('/api/live_data')
                .then(response => response.json())
                .then(data => {
                    if(data.last_issue){
                        document.getElementById('lbl-issue').innerText = "#" + data.last_issue;
                        document.getElementById('lbl-num').innerText = data.actual_number;
                        document.getElementById('lbl-res').innerText = data.actual_result;
                        document.getElementById('lbl-stage').innerText = data.stage;
                        document.getElementById('lbl-capital').innerText = data.investment;

                        for (const [tierName, metrics] of Object.entries(data.tiers)) {
                            const predElement = document.getElementById(tierName + '-pred');
                            predElement.innerText = metrics.prediction;
                            predElement.className = 'pred-val ' + metrics.prediction;

                            document.getElementById(tierName + '-count').innerText = metrics.active_count;
                            document.getElementById(tierName + '-big').innerText = metrics.votes_big;
                            document.getElementById(tierName + '-small').innerText = metrics.votes_small;
                        }
                    }
                })
                .catch(error => console.error('Data Sync Error:', error));
        }
        setInterval(fetchLiveBrainEngineUpdates, 2000);
        fetchLiveBrainEngineUpdates();
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
