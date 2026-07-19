import sqlite3


DB="logic.db"


def connect():
    return sqlite3.connect(DB)


def init_db():

    con=connect()
    cur=con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logic_stats(
        id INTEGER PRIMARY KEY,
        logic TEXT,
        win INTEGER,
        loss INTEGER
    )
    """)

    con.commit()
    con.close()



def save_result(logic,win):

    con=connect()
    cur=con.cursor()

    cur.execute(
    "SELECT * FROM logic_stats WHERE logic=?",
    (logic,)
    )

    data=cur.fetchone()


    if data:

        if win:
            cur.execute(
            "UPDATE logic_stats SET win=win+1 WHERE logic=?",
            (logic,)
            )

        else:
            cur.execute(
            "UPDATE logic_stats SET loss=loss+1 WHERE logic=?",
            (logic,)
            )


    else:

        cur.execute(
        "INSERT INTO logic_stats(logic,win,loss) VALUES(?,?,?)",
        (logic,1 if win else 0,0 if win else 1)
        )


    con.commit()
    con.close()



def get_stats():

    con=connect()
    cur=con.cursor()

    cur.execute(
    "SELECT * FROM logic_stats"
    )

    rows=cur.fetchall()

    result=[]

    for r in rows:

        total=r[2]+r[3]

        rate=0

        if total:
            rate=round((r[2]/total)*100,2)


        result.append({

        "logic":r[1],
        "win":r[2],
        "loss":r[3],
        "rate":rate

        })


    return result