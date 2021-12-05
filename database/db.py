import os

import psycopg2
from fastapi import UploadFile

DATABASE = "postgres"
USER = "postgres"
PASSWORD = "postgres"
HOST = "127.0.0.1"
PORT = "5432"

POSTS_PER_PAGE = 5

con: psycopg2.extensions.connection


def wait():
    '''
    Wait pending requests
    '''
    global con
    while True:
        state = con.poll()
        if state == psycopg2.extensions.POLL_OK:
            break
        else:
            raise psycopg2.OperationalError("poll() returned %s" % state)


def commit_db(sql: str, params: tuple):
    '''
    Commit SQL query
    :param sql: prepared statement
    :param params: arguments for query
    :return: True or False
    '''
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(sql, params)
        con.commit()
    except Exception as er:
        print(er)
        con.rollback()
        return False
    return True


def fetchone_db(sql: str, params: tuple):
    '''
    Fetch one row
    :param sql: prepared statement
    :param params: arguments for query
    :return: list() or False
    '''
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


def fetchall_db(sql: str, params: tuple):
    '''
    Fetch all rows
    :param sql: prepared statement
    :param params: arguments for query
    :return: list()
    '''
    global con
    wait()
    cur = con.cursor()
    try:
        cur.execute(sql, params)
        con.commit()
        return cur.fetchall()
    except Exception as er:
        print(er)
        con.rollback()
        return list()


def connect_db():
    '''
    Connect to db or create new db
    :return: True or False
    '''
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
    '''
    Disconnect from db
    :return: True or False
    '''
    global con
    con.close()


def add_new_user_db(login: str, password: str, username: str):
    '''
    Add new user to USERS table
    :param login
    :param password
    :param username
    :return: True or False
    '''
    sql = """insert
             into user_data (login,password,username)
             values (%s,%s,%s) ;"""
    return commit_db(sql, (login, password, username,))


def get_user_by_login_db(login: str):
    '''
    Get user by login
    :param login
    :return: list() or False
    '''
    sql = """select *
             from user_data where login=%s"""
    return fetchone_db(sql, (login,))


def get_user_by_id_db(id: int):
    '''
    Get user by id
    :param id
    :return: list() or False
    '''
    sql = """select *
             from user_data where id=%s"""
    return fetchone_db(sql, (id,))


def update_user_db(password: str, username: str, id: int):
    '''
    Change user data
    :param password: Optional
    :param username: Optional
    :param id
    :return: True or False
    '''
    if password is None:
        sql = """update user_data 
                 set username=%s where id=%s"""
        return commit_db(sql, (username, id))
    else:
        sql = """update user_data 
                 set password=%s, username=%s where id=%s"""
        return commit_db(sql, (password, username, id))


def add_new_post(title: str, description: str, file_photo: UploadFile, owner_id: int):
    '''
    Add new post and add new file, associated with post
    :param title
    :param description
    :param file_photo
    :param owner_id
    :return: True or False
    '''
    data = file_photo.file.read()
    if len(data) == 0:
        return False
    sql = """insert into feed_data (title,description,owner_id,liked) values (%s,%s,%s,%s) ;"""
    if not commit_db(sql, (title, description, owner_id, 0)):
        return False
    sql = """select id from feed_data where title=%s and owner_id=%s;"""
    id = fetchone_db(sql, (title, owner_id,))
    if not id:
        return False
    try:
        with open(f'static/{id[0]}.png', mode='wb+') as f:
            f.write(data)
    except Exception as e:
        print(e)
        return False
    return id


def get_posts_of_user(owner_id: int):
    '''
    Get all posts of user by id
    :param owner_id
    :return: list() or False
    '''
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id 
             where owner_id=%s;"""
    return fetchall_db(sql, (owner_id,))


def get_post(feed_id: int):
    '''
    Get post by id
    :param feed_id
    :return: True or False
    '''
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id 
             where feed_data.id = %s """
    return fetchone_db(sql, (feed_id,))


def get_random_n_posts(number_of_posts: int):
    '''
    Get random user defined number of posts
    :param number_of_posts
    :return: list() or False
    '''
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id 
             order by random() limit %s;"""
    return fetchall_db(sql, (number_of_posts,))


def get_all_posts():
    '''
    Get all posts
    :return list() or False
    '''
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description ,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id"""
    return fetchall_db(sql, tuple())


def get_all_posts_with_paging(page: int):
    '''
    Get all posts using pages
    :param page: Counting starts with 1
    :return: list() or False
    '''
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description ,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id limit %s offset %s"""
    return fetchall_db(sql, (POSTS_PER_PAGE, (page - 1) * POSTS_PER_PAGE,))


def delete_post(feed_id: int):
    '''
    Delete post in feed, users, liked tables and delete file, associated with post
    :param feed_id
    :return: True or False
    '''
    sql = """delete from liked_data where feed_id = %s"""
    if not commit_db(sql, (feed_id,)):
        return False
    sql = """delete from feed_data where id = %s;"""
    if not commit_db(sql, (feed_id,)):
        return False
    try:
        os.remove(f'static/{feed_id}.png')
    except Exception as e:
        print(e)
    return True


def like_post(user_id: int, feed_id: int):
    '''
    Like post
    :param user_id
    :param feed_id
    :return: True or False
    '''
    sql = """insert into liked_data (user_id,feed_id) values (%s,%s);"""
    if not commit_db(sql, (user_id, feed_id,)):
        return False
    liked = count_likes(feed_id)
    if not liked:
        return False
    sql = """update feed_data set liked=%s where id=%s"""
    return commit_db(sql, (liked, feed_id,))


def unlike_post(user_id: int, feed_id: int):
    '''
    Delete like of post
    :param user_id
    :param feed_id
    :return: True or False
    '''
    sql = """delete from liked_data where user_id=%s and feed_id=%s ;"""
    if not commit_db(sql, (user_id, feed_id,)):
        return False
    liked = count_likes(feed_id)
    if not liked:
        return False
    sql = """update feed_data set liked=%s where id=%s"""
    return commit_db(sql, (liked, feed_id,))


def count_likes(feed_id: int):
    '''
    Count likes of post by id
    :param feed_id
    :return: int() or False
    '''
    sql = """select count(id) from liked_data where feed_id = %s;"""
    return fetchone_db(sql, (feed_id,))
