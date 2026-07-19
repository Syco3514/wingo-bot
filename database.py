import sqlite3


DB="logic.db"


def db():

    return sqlite3.connect(DB)



def init_db():

    con=db()
    cur=con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stats(

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logic TEXT UNIQUE,
    win INTEGER DEFAULT 0,
    loss INTEGER DEFAULT 0

    )
    """)

    con.commit()
    con.close()



def add_logic(name):

    con=db()
    cur=con.cursor()

    cur.execute(
    """
    INSERT OR IGNORE INTO stats(logic)
    VALUES(?)
    """,
    (name,)
    )

    con.commit()
    con.close()



def update_logic(name,result):

    con=db()
    cur=con.cursor()


    if result:

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


    con.commit()
    con.close()



def get_all():

    con=db()
    cur=con.cursor()


    cur.execute(
    "SELECT * FROM stats"
    )


    rows=cur.fetchall()


    data=[]


    for r in rows:

        total=r[2]+r[3]

        rate=0

        if total:
            rate=round(
            r[2]/total*100,2
            )


        data.append({

        "logic":r[1],
        "win":r[2],
        "loss":r[3],
        "rate":rate

        })


    return data
