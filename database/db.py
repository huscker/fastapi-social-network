import psycopg2

# TODO: add text limits
from fastapi import UploadFile

DATABASE = "postgres"
USER = "postgres"
PASSWORD = ""
HOST = "127.0.0.1"
PORT = "5432"

con: psycopg2.extensions.connection


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
        cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('user_data',))
    except Exception as er:
        print(1)
        print(er)
        con.close()
        return False
    if not cur.fetchone()[0]:
        try:
            cur.execute(
                "create table user_data (id serial primary key, login text not null unique, password text not null, username text not null unique) ;")
            con.commit()
        except Exception as er:
            print(er)
            con.close()
            return False

    try:
        cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('feed_data',))
    except Exception as er:
        print(2)
        print(er)
        con.close()
        return False

    if not cur.fetchone()[0]:
        try:
            cur.execute(
                "create table feed_data (id serial primary key, owner_id integer not null references user_data(id), title text not null, description text, unique(title,owner_id)) ;")
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


def add_new_user_db(login: str, password: str, username: str):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            "insert into user_data (login,password,username) values (%s,%s,%s) ;", (login, password, username,))
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True


def get_user_by_login_db(login: str):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            "select * from user_data where login=%s", (login,))
        con.commit()
        return cur.fetchone()
    except Exception as er:
        print(er)
        con.rollback()
        return False


def get_user_by_id_db(id: int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            "select * from user_data where id=%s", (id,))
        con.commit()
        return cur.fetchone()
    except Exception as er:
        print(er)
        con.rollback()
        return False


def update_user_db(password: str, username: str, id: int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            "update user_data set password=%s,username=%s where id=%s", (password, username, id))
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True

def add_new_post(title : str,description : str,file_photo: UploadFile,owner_id:int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            "insert into feed_data (title,description,owner_id) values (%s,%s,%s) ;", (title, description, owner_id,))
        con.commit()
        cur.execute(
            'select id from feed_data where title=%s and owner_id=%s;',(title,owner_id,)
        )
        con.commit()
        id = cur.fetchone()

        with open(f'static/{id[0]}.png',mode='wb+') as f:
            f.write(file_photo.file.read())
        print(id)
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True
