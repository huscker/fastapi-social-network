import psycopg2

# TODO: add text limits
# TODO: change saving filenames from ids to hashes
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
                "create table feed_data (id serial primary key, owner_id integer not null references user_data(id), title text not null, description text,liked integer, unique(title,owner_id)) ;")
            con.commit()
        except Exception as er:
            print(er)
            con.close()
            return False



    try:
        cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('liked_data',))
    except Exception as er:
        print(2)
        print(er)
        con.close()
        return False

    if not cur.fetchone()[0]:
        try:
            cur.execute(
                "create table liked_data ("
                "id serial primary key,"
                "user_id integer not null references user_data(id),"
                "feed_id integer not null references feed_data(id),"
                "unique(user_id,feed_id)"
                ");")
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
    data = file_photo.file.read()
    if len(data) == 0:
        print('file is empty')
        return False
    try:
        cur.execute(
            "insert into feed_data (title,description,owner_id,liked) values (%s,%s,%s,%s) ;", (title, description, owner_id,0))
        con.commit()
        cur.execute(
            'select id from feed_data where title=%s and owner_id=%s;',(title,owner_id,)
        )
        con.commit()
        id = cur.fetchone()

        with open(f'static/{id[0]}.png',mode='wb+') as f:
            f.write(data)
        return id
    except Exception as er:
        print(er)
        con.rollback()
        return False

def get_posts_of_user(owner_id : int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            '''select 
            user_data.username,feed_data.id,user_data.id, 
            feed_data.title ,feed_data.description,feed_data.liked
            from feed_data inner join user_data 
            on user_data.id = feed_data.owner_id 
            where owner_id=%s;''', (owner_id,)
        )
        con.commit()
        items = cur.fetchall()
        return items
    except Exception as er:
        print(er)
        con.rollback()
        return list()

def get_post(feed_id:int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            '''select 
            user_data.username,feed_data.id,user_data.id, 
            feed_data.title ,feed_data.description,feed_data.liked
            from feed_data inner join user_data 
            on user_data.id = feed_data.owner_id 
            where feed_data.id = %s ''',(feed_id,)
        )
        con.commit()
        items = cur.fetchone()
        return items
    except Exception as er:
        print(er)
        con.rollback()
        return False

def get_random_n_posts(number_of_posts:int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            '''select 
            user_data.username,feed_data.id,user_data.id, 
            feed_data.title ,feed_data.description,feed_data.liked
            from feed_data inner join user_data 
            on user_data.id = feed_data.owner_id 
            order by random() limit %s;''', (number_of_posts,)
        )
        con.commit()
        items = cur.fetchall()
        return items
    except Exception as er:
        print(er)
        con.rollback()
        return list()

def get_all_posts():
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            '''select 
            user_data.username,feed_data.id,user_data.id, 
            feed_data.title ,feed_data.description ,feed_data.liked
            from feed_data inner join user_data 
            on user_data.id = feed_data.owner_id'''
        )
        con.commit()
        items = cur.fetchall()
        return items
    except Exception as er:
        print(er)
        con.rollback()
        return list()

def delete_post(feed_id:int,owner_id: int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            '''delete from liked_data where user_id = %s and feed_id = %s''',
            (owner_id,feed_id,)
        )
    except Exception as er:
        print(er)
        con.rollback()
        return False
    try:
        cur.execute(
            '''delete from feed_data where id = %s and owner_id = %s;''', (feed_id,owner_id)
        )
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True

def like_post(user_id:int,feed_id:int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            '''insert into liked_data (user_id,feed_id) values (%s,%s);''', (user_id,feed_id,)
        )
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    liked = count_likes(feed_id)
    if not liked:
        return False
    try:
        cur.execute(
            '''update feed_data set liked=%s where id=%s''', (liked,feed_id,) # aaaaa
        )
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True

def unlike_post(user_id:int,feed_id:int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            '''delete from liked_data where user_id=%s and feed_id=%s ;''', (user_id, feed_id,)
        )
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    liked = count_likes(feed_id)
    if not liked:
        return False
    try:
        cur.execute(
            '''update feed_data set liked=%s where id=%s''', (liked,feed_id,) # aaaaa
        )
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True

def count_likes(feed_id:int):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(
            '''select count(id) from liked_data where feed_id = %s;''', (feed_id,)
        )
        con.commit()
        return cur.fetchone()
    except Exception as er:
        print(er)
        con.rollback()
        return False

