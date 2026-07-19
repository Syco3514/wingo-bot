from database import *


def check_result(issue, history, actual, LOGICS):

    for name, logic in LOGICS.items():

        try:

            prediction = logic(history)

            if prediction == actual:
                result = "WIN"
                update_stat(name, True)

            else:
                result = "LOSS"
                update_stat(name, False)


            save_prediction(
                issue,
                name,
                prediction,
                actual,
                result
            )


        except Exception as e:

            print(
                "Tracker Error:",
                name,
                e
            )