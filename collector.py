import requests


API="https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"



def get_history():

    r=requests.get(API,timeout=10)

    data=r.json()

    arr=data["data"]["list"]


    nums=[]

    for x in arr[:20]:

        nums.append(
            x["number"]
        )


    return nums