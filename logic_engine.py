import random

from database import *



def bs(n):

    return "SMALL" if int(n)<=4 else "BIG"



def create_logics():

    logs={}


    for i in range(1,201):

        name=f"logic_{i}"


        def logic(history,i=i):

            nums=list(map(int,history))


            mode=i%6


            if mode==0:
                return bs(nums[0])


            if mode==1:
                return bs(sum(nums[:3])/3)


            if mode==2:
                return bs(max(nums[:5]))


            if mode==3:
                return bs(min(nums[:5]))


            if mode==4:

                return "SMALL" if nums.count(1)>nums.count(8) else "BIG"


            return random.choice(
            ["SMALL","BIG"]
            )



        logs[name]=logic

        add_logic(name)


    return logs




LOGICS=create_logics()



def weighted_vote(history):


    small=0
    big=0


    stats=get_stats()


    for s in stats:


        name=s["logic"]

        rate=s["rate"]


        weight=1


        if rate>=90:
            weight=5

        elif rate>=80:
            weight=4

        elif rate>=70:
            weight=3



        pred=LOGICS[name](history)



        if pred=="SMALL":

            small+=weight

        else:

            big+=weight



    return {

    "SMALL":small,
    "BIG":big,

    "final":
    "SMALL"
    if small>big
    else "BIG"

    }
