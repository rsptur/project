from flask import session
from db import db
from app import app
import users
from sqlalchemy.sql import text

def new_topic(topic,message,user_id): 
    try: 
        sql = text("INSERT INTO topics (topic,user_id) VALUES (:topic,:user_id)")
        db.session.execute(sql, {"topic":topic, "user_id":user_id})
        db.session.commit()  
        topic_id=get_topic_id(topic)
        if new_message(message,topic_id,user_id): 
            return True  
    except: 
        return False  

def list_topics(): 
    try: 
        sql =text("SELECT T.topic, COUNT(M.message), TO_CHAR(MAX(M.sent_at), 'YYYY-MM-DD') FROM topics T, messages M WHERE T.id=M.topic_id GROUP BY T.topic")
        result=db.session.execute(sql)  
        return result.fetchall()
    except: 
        return False 

def get_topic_id(topic): 
    try: 
        sql =text("SELECT id FROM topics WHERE topic=:topic")
        result=db.session.execute(sql,{"topic":topic})  
        topic_id=result.fetchone()[0]
        return topic_id
    except: 
        False

def new_message(message,topic_id,user_id): 
    try:
        visible=True
        sql = text("INSERT INTO messages (message,sent_at,visible, user_id,topic_id) VALUES (:message,current_timestamp,:visible,:user_id,:topic_id)")
        db.session.execute(sql, {"message":message,"visible":visible,"user_id":session['user_id'],"topic_id":topic_id})
        db.session.commit()  
        return True  
    except: 
        return False  
    
def list_messages(topic_id): 
    try: 
        sql = text("SELECT message FROM messages WHERE topic_id=:topic_id")
        result=db.session.execute(sql,{"topic_id":topic_id})  
        return result.fetchall() 
    except: 
        return False 

def admin_topics(user_id):
    if users.is_admin(user_id): 
        sql =text("SELECT id, topic FROM topics")
        result=db.session.execute(sql)  
        return result.fetchall() 

def admin_messages(user_id):
    if users.is_admin(user_id): 
        sql = text("SELECT id,message FROM messages")
        result=db.session.execute(sql)
        return result.fetchall()
    else: 
        return False

def delete_topics(topic_id,user_id):
    if users.is_admin(user_id): 
        try: 
            sql2 = text("DELETE FROM messages WHERE topic_id=:topic_id")
            db.session.execute(sql2,{"topic_id":topic_id})
            db.session.commit() 
            sql = text("DELETE FROM topics WHERE id=:topic_id")
            db.session.execute(sql,{"topic_id":topic_id})
            db.session.commit()           
            return True
        except:
            return False     

def modify_messages(message_id,user_id):
    if users.is_admin(user_id): 
        try: 
            sql = text("DELETE FROM messages WHERE id=:message_id")
            db.session.execute(sql,{"message_id":message_id})
            db.session.commit()
            return True
        except: 
            return False         
    elif users.is_users(message_id,user_id):
        try: 
            sql = text("DELETE FROM messages WHERE id=:message_id")
            db.session.execute(sql,{"message_id":message_id})
            db.session.commit()
            return True
        except: 
            return False   
    else: 
        return False            

def users_messages(user_id):
    try: 
        sql = text("SELECT id,message FROM messages WHERE user_id=:user_id")
        result=db.session.execute(sql,{"user_id":user_id})
        return result.fetchall()
    except: 
        return False

def list_areas():
    sql = text("SELECT id,area FROM areas")
    result=db.session.execute(sql)  
    return result.fetchall()     

def add_area(area,user_id):
    if users.is_admin(user_id): 
        try: 
            sql = text("INSERT INTO areas (area) VALUES (:area)")
            db.session.execute(sql, {"area":area})
            db.session.commit()  
            return True  
        except: 
            return False 
  
def list_smessages(id): 
    try: 
        sql = text("SELECT smessage FROM smessages WHERE area_id=:id")
        result=db.session.execute(sql,{"id":id})
        return result.fetchall()
    except: 
        return False
    
def add_smessage(smessage, area, user_id):
    #try: 
        sql = text("INSERT INTO smessages (smessage, user_id,area_id) VALUES (:smessage,:user_id,:area_id)")
        db.session.execute(sql, {"smessage":smessage,"user_id":user_id,"area_id":area})
        db.session.commit()  
        return True  
    #except: 
        #return False
