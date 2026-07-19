import random


def bs(number):

    return "SMALL" if int(number)<=4 else "BIG"



# Example logic collection
# Yahan future me 200 logics add ho sakte hain


def logic_1(history):

    last=int(history[0])

    return bs(last)



def logic_2(history):

    nums=list(map(int,history[:5]))

    avg=sum(nums)/len(nums)

    return "SMALL" if avg<5 else "BIG"



def logic_3(history):

    return random.choice(
        ["SMALL","BIG"]
    )



LOGICS={

"logic_1":logic_1,
"logic_2":logic_2,
"logic_3":logic_3

}



def vote(history):

    result={
        "SMALL":0,
        "BIG":0
    }


    for name,func in LOGICS.items():

        pred=func(history)

        result[pred]+=1


    final=max(
        result,
        key=result.get
    )


    return {

    "prediction":final,
    "votes":result

    }