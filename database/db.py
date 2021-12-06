import os

import asyncpg
from fastapi import UploadFile
from configs.db import *

con : asyncpg.connection.Connection


async def connect_db():
    '''
    Connect to db or create new db
    :return: True or False
    '''
    global con
    try:
        con = await asyncpg.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
    except Exception as er:
        print(er)
        con = None
        return False
    try:
        a = await con.fetch("select exists(select * from information_schema.tables where table_name = $1)",'user_data')
    except Exception as er:
        print(er)
        await con.close()
        return False
    if not a[0][0]:
        try:
            await con.execute(
                "create table user_data (id serial primary key, login text not null unique, password text not null, username text not null unique) ;")
        except Exception as er:
            print(er)
            await con.close()
            return False

    try:
        a = await con.fetch("select exists(select * from information_schema.tables where table_name=$1)", 'feed_data')
    except Exception as er:
        print(er)
        await con.close()
        return False

    if not a[0][0]:
        try:
            await con.execute(
                "create table feed_data (id serial primary key, owner_id integer not null references user_data(id), title text not null, description text,liked integer, unique(title,owner_id)) ;")
        except Exception as er:
            print(er)
            await con.close()
            return False

    try:
        a = await con.fetch("select exists(select * from information_schema.tables where table_name=$1)", 'liked_data')
    except Exception as er:
        print(er)
        await con.close()
        return False

    if not a[0][0]:
        try:
            await con.execute(
                "create table liked_data ("
                "id serial primary key,"
                "user_id integer not null references user_data(id),"
                "feed_id integer not null references feed_data(id),"
                "unique(user_id,feed_id)"
                ");")
        except Exception as er:
            print(er)
            await con.close()
            return False
    return True


async def disconnect_db():
    '''
    Disconnect from db
    :return: True or False
    '''
    global con
    await con.close()


async def add_new_user_db(login: str, password: str, username: str):
    '''
    Add new user to USERS table
    :param login
    :param password
    :param username
    :return: True or False
    '''
    sql = """insert
             into user_data (login,password,username)
             values ($1,$2,$3) ;"""
    global con
    try:
        return await con.execute(sql,login,password,username)
    except Exception as e:
        print(e)
        return False


async def get_user_by_login_db(login: str):
    '''
    Get user by login
    :param login
    :return: list() or False
    '''
    sql = """select *
             from user_data where login=$1"""
    global con
    try:
        return list(await con.fetchrow(sql,login))
    except Exception as e:
        print(e)
        return False


async def get_user_by_id_db(id: int):
    '''
    Get user by id
    :param id
    :return: list() or False
    '''
    sql = """select *
             from user_data where id=$1"""
    global con
    try:
        return list(await con.fetchrow(sql, id))
    except Exception as e:
        print(e)
        return False


async def update_user_db(password: str, username: str, id: int):
    '''
    Change user data
    :param password: Optional
    :param username: Optional
    :param id
    :return: True or False
    '''
    global con
    if password is None:
        sql = """update user_data 
                 set username=$1 where id=$2"""
        try:
            return await con.execute(sql,username,id)
        except Exception as e:
            print(e)
            return False
    else:
        sql = """update user_data 
                 set password=$1, username=$2 where id=$3"""
        try:
            return await con.execute(sql,password,username,id)
        except Exception as e:
            print(e)
            return False


async def add_new_post(title: str, description: str, file_photo: UploadFile, owner_id: int):
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
    sql = """insert into feed_data (title,description,owner_id,liked) values ($1,$2,$3,$4) ;"""
    global con
    try:
        await con.execute(sql,title,description,owner_id,0)
    except Exception as e:
        print(e)
        return False
    sql = """select id from feed_data where title=$1 and owner_id=$2;"""
    id = []
    try:
        id = await con.fetchrow(sql,title,owner_id)
    except Exception as e:
        print(e)
        return False
    if not id:
        return False
    try:
        with open(f'static/{id[0]}.png', mode='wb+') as f:
            f.write(data)
    except Exception as e:
        print(e)
        return False
    return id


async def get_posts_of_user(owner_id: int):
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
             where owner_id=$1;"""
    global con
    try:
        res = await con.fetch(sql,owner_id)
        res = list(map(list,res))
        return res
    except Exception as e:
        print(e)
        return list()


async def get_post(feed_id: int):
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
             where feed_data.id = $1 """
    global con
    try:
        return list(await con.fetchrow(sql, feed_id))
    except Exception as e:
        print(e)
        return list()


async def get_random_n_posts(number_of_posts: int):
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
             order by random() limit $1;"""
    global con
    try:
        res = await con.fetch(sql, number_of_posts)
        res = list(map(list, res))
        return res
    except Exception as e:
        print(e)
        return list()


async def get_all_posts():
    '''
    Get all posts
    :return list() or False
    '''
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description ,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id"""
    global con
    try:
        res = await con.fetch(sql)
        res = list(map(list, res))
        return res
    except Exception as e:
        print(e)
        return list()


async def get_all_posts_with_paging(page: int):
    '''
    Get all posts using pages
    :param page: Counting starts with 1
    :return: list() or False
    '''
    sql = """select 
             user_data.username,feed_data.id,user_data.id, 
             feed_data.title ,feed_data.description ,feed_data.liked
             from feed_data inner join user_data 
             on user_data.id = feed_data.owner_id limit $1 offset $2"""
    global con
    try:
        res = await con.fetch(sql, POSTS_PER_PAGE, (page - 1) * POSTS_PER_PAGE)
        res = list(map(list, res))
        return res
    except Exception as e:
        print(e)
        return list()


async def delete_post(feed_id: int):
    '''
    Delete post in feed, users, liked tables and delete file, associated with post
    :param feed_id
    :return: True or False
    '''
    sql = """delete from liked_data where feed_id = $1"""
    global con
    try:
        await con.execute(sql, feed_id)
    except Exception as e:
        print(e)
        return False
    sql = """delete from feed_data where id = $1;"""
    try:
        await con.execute(sql, feed_id)
    except Exception as e:
        print(e)
        return False
    try:
        os.remove(f'static/{feed_id}.png')
    except Exception as e:
        print(e)
    return True


async def like_post(user_id: int, feed_id: int):
    '''
    Like post
    :param user_id
    :param feed_id
    :return: True or False
    '''
    sql = """insert into liked_data (user_id,feed_id) values ($1,$2);"""
    global con
    try:
        await con.execute(sql, user_id,feed_id)
    except Exception as e:
        print(e)
        return False
    liked = await count_likes(feed_id)
    if not liked:
        return False
    sql = """update feed_data set liked=$1 where id=$2"""
    try:
        return await con.execute(sql, liked,feed_id)
    except Exception as e:
        print(e)
        return False


async def unlike_post(user_id: int, feed_id: int):
    '''
    Delete like of post
    :param user_id
    :param feed_id
    :return: True or False
    '''
    sql = """delete from liked_data where user_id=$1 and feed_id=$2 ;"""
    global con
    try:
        await con.execute(sql, user_id,feed_id)
    except Exception as e:
        print(e)
        return False
    liked = await count_likes(feed_id)
    sql = """update feed_data set liked=$1 where id=$2"""
    try:
        await con.execute(sql, liked, feed_id)
    except Exception as e:
        print(e)
        return False
    return True


async def count_likes(feed_id: int):
    '''
    Count likes of post by id
    :param feed_id
    :return: int() or False
    '''
    sql = """select count(id) from liked_data where feed_id = $1;"""
    global con
    try:
        return list(await con.fetchrow(sql, feed_id))[0]
    except Exception as e:
        print(e)
        return list()
