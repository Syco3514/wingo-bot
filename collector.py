import requests


API="https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"


def get_history():

    try:

        r=requests.get(
            API,
            timeout=10,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )


        data=r.json()


        numbers=[]


        for item in data["data"]["list"][:20]:

            numbers.append(
                int(item["number"])
            )


        if len(numbers)==0:
            return [1,2,3,4,5]


        return numbers


    except Exception as e:

        print("API ERROR:",e)

        # backup data
        return [
            1,5,3,8,2,
            7,4,9,0,6
        ]
