import os
import psycopg2
from fastapi import UploadFile

DATABASE = "postgres"
USER = "postgres"
PASSWORD = ""
HOST = "127.0.0.1"
PORT = "5432"

POSTS_PER_PAGE = 2

con: psycopg2.extensions.connection

def wait():
    global con
    while True:
        state = con.poll()
        if state == psycopg2.extensions.POLL_OK:
            break
        else:
            raise psycopg2.OperationalError("poll() returned %s" % state)

def commit_db(sql:str,params:tuple):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(sql,params)
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True

def fetchone_db(sql:str,params:tuple):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(sql, params)
        con.commit()
        return cur.fetchone()
    except Exception as er:
        print(er)
        con.rollback()
        return False

def fetchall_db(sql:str,params:tuple):
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(sql,params)
        con.commit()
        return cur.fetchall()
    except Exception as er:
        print(er)
        con.rollback()
        return list()

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

def add_new_user_db(login: str, password: str, username: str):
    sql = """insert
             into user_data (login,password,username)
             values (%s,%s,%s) ;"""
    return commit_db(sql,(login,password,username,))

def get_user_by_login_db(login: str):
    sql = """select *
             from user_data where login=%s"""
    return fetchone_db(sql,(login,))

def get_user_by_id_db(id: int):
    sql = """select *
             from user_data where id=%s"""
    return fetchone_db(sql,(id,))


def update_user_db(password: str, username: str, id: int):
    if password is None:
        sql = """update user_data 
                 set username=%s where id=%s"""
        return commit_db(sql,(username,id))
    else:
        sql = """update user_data 
                 set password=%s, username=%s where id=%s"""
        return commit_db(sql,(password,username,id))

def add_new_post(title : str,description : str,file_photo: UploadFile,owner_id:int):
    data = file_photo.file.read()
    if len(data) == 0:
        return False
    sql = """insert into feed_data (title,description,owner_id,liked) values (%s,%s,%s,%s) ;"""
    if not commit_db(sql,(title, description, owner_id,0)):
        return False
    sql = """select id from feed_data where title=%s and owner_id=%s;"""
    id = fetchone_db(sql,(title,owner_id,))
    if not id:
        return False
    try:
        with open(f'static/{id[0]}.png', mode='wb+') as f:
            f.write(data)
    except Exception as e:
        print(e)
        return False
    return id

def get_posts_of_user(owner_id : int):
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id 
             where owner_id=%s;"""
    return fetchall_db(sql,(owner_id,))

def get_post(feed_id:int):
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id 
             where feed_data.id = %s """
    return fetchone_db(sql,(feed_id,))

def get_random_n_posts(number_of_posts:int):
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id 
             order by random() limit %s;"""
    return fetchall_db(sql,(number_of_posts,))

def get_all_posts():
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description ,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id"""
    return fetchall_db(sql,tuple())

def get_all_posts_with_paging(page : int):
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description ,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id limit %s offset %s"""
    return fetchall_db(sql,(POSTS_PER_PAGE,(page-1)*POSTS_PER_PAGE,))

def delete_post(feed_id:int):
    sql = """delete from liked_data where feed_id = %s"""
    if not commit_db(sql,(feed_id,)):
        return False
    sql = """delete from feed_data where id = %s;"""
    if not commit_db(sql,(feed_id,)):
        return False
    try:
        os.remove(f'static/{feed_id}.png')
    except Exception as e:
        print(e)
    return True

def like_post(user_id:int,feed_id:int):
    sql = """insert into liked_data (user_id,feed_id) values (%s,%s);"""
    if not commit_db(sql,(user_id,feed_id,)):
        return False
    liked = count_likes(feed_id)
    if not liked:
        return False
    sql = """update feed_data set liked=%s where id=%s"""
    return commit_db(sql,(liked,feed_id,))

def unlike_post(user_id:int,feed_id:int):
    sql = """delete from liked_data where user_id=%s and feed_id=%s ;"""
    if not commit_db(sql,(user_id,feed_id,)):
        return False
    liked = count_likes(feed_id)
    if not liked:
        return False
    sql = """update feed_data set liked=%s where id=%s"""
    return commit_db(sql,(liked,feed_id,))

def count_likes(feed_id:int):
    sql = """select count(id) from liked_data where feed_id = %s;"""
    return fetchone_db(sql,(feed_id,))


