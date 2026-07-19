import random
from database import *


def bs(n):

    if int(n)<=4:
        return "SMALL"

    return "BIG"



# 200 logic generator

def create_logics():


    logics={}


    for i in range(1,201):

        name=f"logic_{i}"


        def logic(history):

            mode=i%5


            nums=list(
            map(int,history)
            )


            if mode==0:

                return bs(nums[0])


            elif mode==1:

                return bs(
                sum(nums[:3])//3
                )


            elif mode==2:

                return bs(
                max(nums[:5])
                )


            elif mode==3:

                return bs(
                min(nums[:5])
                )


            else:

                return random.choice(
                ["SMALL","BIG"]
                )


        logics[name]=logic
        add_logic(name)


    return logics



LOGICS=create_logics()



def voting(history,minimum=0):


    small=0
    big=0


    active=[]


    stats=get_all()


    for s in stats:

        if s["rate"]>=minimum:

            active.append(
            s["logic"]
            )


    for name in active:


        pred=LOGICS[name](history)


        if pred=="SMALL":
            small+=1

        else:
            big+=1



    return {

    "SMALL":small,
    "BIG":big,

    "final":
    "SMALL"
    if small>big
    else "BIG"

    }




def all_predictions(history):


    return {


    "prediction_1":
    voting(history,0),


    "prediction_2":
    voting(history,90),


    "prediction_3":
    voting(history,80),


    "prediction_4":
    voting(history,70)


    }
