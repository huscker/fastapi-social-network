import psycopg2

DATABASE = "postgres"
USER = "postgres"
PASSWORD = ""
HOST = "127.0.0.1"
PORT = "5432"

con : psycopg2.extensions.connection

def connect_db():
    global con
    try:
        con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
    except Exception as er:
        print(er)
        con = None
        return False
    cur = con.cursor()
    try:
        cur.execute("select exists(select * from information_schema.tables where table_name='user_data')")
    except Exception as er:
        print(er)
        con.close()
        return False
    if not cur.fetchone()[0]:
        try:
            cur.execute("create table user_data (Id SERIAL PRIMARY KEY, LOGIN TEXT NOT NULL UNIQUE, PASSWORD TEXT NOT NULL, USERNAME TEXT NOT NULL UNIQUE) ;")
            con.commit()
        except Exception as er:
            print(er)
            con.close()
            return False
    return True

def disconnect_db():
    global con
    con.close()

def wait():
    global con
    while True:
        state = con.poll()
        if state == psycopg2.extensions.POLL_OK:
            break
        else:
            raise psycopg2.OperationalError("poll() returned %s" % state)

def add_new_user_db(login:str,password:str,username:str):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            "insert into user_data (login,password,username) values (%s,%s,%s) ;",(login,password,username,))
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True

def get_user_from_db(login:str):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            "select * from user_data where login=%s",(login,))
        con.commit()
        return cur.fetchone()
    except Exception as er:
        print(er)
        con.rollback()
        return False

def update_user_db(password:str,username:str,id:int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            "update user_data set password=%s,username=%s where id=%s", (password,username,id))
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True
