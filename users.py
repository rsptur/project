from flask import session
from db import db
from app import app
from sqlalchemy.sql import text

def login_user(username,password):
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if not user:
        return False
    else:
        if user.password==password:
            return True 
        else:
            return False  
        
def new_user(username,password): 
    try: 
        admin=False
        sql = text("INSERT INTO users (username, password,admin) VALUES (:username, :password, :admin)")
        db.session.execute(sql, {"username":username, "password":hash_value, "admin":admin})
        db.session.commit()    
    except: 
        return False
    return login_user(username,password)   

def get_user_id(username): 
    sql = text("SELECT id FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user=result.fetchone()[0]
    return user      

def change_username(username,user_id): 
    try: 
        sql = text("UPDATE users SET username='" + username + "' WHERE user_id=" + str(user_id))
        db.session.execute(sql)
        db.session.commit() 
        return True
    except: 
        return False 

def add_admin(user_id): 
    try: 
        sql = text("UPDATE users SET admin =(:admin) WHERE id=(:user_id)")      
        db.session.execute(sql, {"user_id":user_id, "admin":True})
        db.session.commit() 
        return True
    except: 
        return False 

def is_admin(user_id):
    sql = text("SELECT admin FROM users WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id":user_id})
    user = result.fetchone()[0]
    return user

def is_users(message_id,user_id):
    sql = text("SELECT user_id FROM messages WHERE id = :message_id")
    result = db.session.execute(sql, {"message_id":message_id})
    user = result.fetchone()[0]
    if user==user_id: 
        return True
    
def add_vip(user_id,area_id): 
    try: 
        sql = text("INSERT INTO vip (user_id,area_id) VALUES (:user_id, :area_id)")
        db.session.execute(sql, {"user_id":user_id, "area_id":area_id})
        db.session.commit() 
        return True
    except: 
        return False 

def is_vip(user_id,id):
    try: 
        sql = text("SELECT user_id FROM vip WHERE area_id = :id")
        result = db.session.execute(sql, {"id":id})
        user = result.fetchone()[0]
        if user_id==user: 
            return True
    except: 
        return False