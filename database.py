import sqlite3


DB="logic.db"


def con():
    return sqlite3.connect(DB)



def init_db():

    c=con()
    cur=c.cursor()


    cur.execute("""
    CREATE TABLE IF NOT EXISTS stats(

    logic TEXT PRIMARY KEY,
    win INTEGER DEFAULT 0,
    loss INTEGER DEFAULT 0

    )
    """)



    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions(

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue TEXT,
    logic TEXT,
    prediction TEXT,
    actual TEXT,
    result TEXT

    )
    """)


    c.commit()
    c.close()



def add_logic(name):

    c=con()
    cur=c.cursor()

    cur.execute(
    """
    INSERT OR IGNORE INTO stats(logic)
    VALUES(?)
    """,
    (name,)
    )

    c.commit()
    c.close()



def update_stat(name,win):

    c=con()
    cur=c.cursor()


    if win:

        cur.execute(
        """
        UPDATE stats
        SET win=win+1
        WHERE logic=?
        """,
        (name,)
        )

    else:

        cur.execute(
        """
        UPDATE stats
        SET loss=loss+1
        WHERE logic=?
        """,
        (name,)
        )


    c.commit()
    c.close()



def save_prediction(issue,logic,pred,actual,result):

    c=con()
    cur=c.cursor()


    cur.execute(
    """
    INSERT INTO predictions
    (issue,logic,prediction,actual,result)
    VALUES(?,?,?,?,?)
    """,
    (
    issue,
    logic,
    pred,
    actual,
    result
    )
    )


    c.commit()
    c.close()



def get_stats():

    c=con()
    cur=c.cursor()

    cur.execute(
    "SELECT * FROM stats"
    )

    rows=cur.fetchall()

    data=[]


    for r in rows:

        total=r[1]+r[2]

        rate=0

        if total:
            rate=round(
            r[1]/total*100,2
            )


        data.append({

        "logic":r[0],
        "win":r[1],
        "loss":r[2],
        "rate":rate

        })


    return data
