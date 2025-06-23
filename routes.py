from flask import Flask
from flask import redirect, render_template, request, session, abort
import users
import topics
import secrets 
from db import db
from app import app
from sqlalchemy.sql import text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    while len(username)<1: 
        return render_template("error.html", message="Käyttäjätunnus puuttuu")
    while len(password)<1: 
        return render_template("error.html", message="Salasana puuttuu")
    if users.login_user(username,password): 
        user_id=users.get_user_id(username)
        session["user_id"] = user_id
        session["username"] = username
        return "Käyttäjä"+username+"on lisätty"
    else: 
        render_template("error.html", message="Väärä salasana tai et ole vielä rekisteröitynyt")

@app.route("/new",methods=["GET","POST"])
def new(): 
    if request.method=="GET": 
        return render_template("add.html")
    if request.method=="POST": 
        username = request.form["username"]
        password = request.form["password"]       
        if len(username)<1: 
            return render_template("error.html", message="Käyttäjätunnus puuttuu tai on liian lyhyt")
        elif len(username)>100: 
            return render_template("error.html", message="Käyttäjätunnus on liian pitkä")
        elif len(password)<1: 
            return render_template("error.html", message="Salasana puuttuu tai on liian lyhyt")
        elif len(password)>100: 
            return render_template("error.html", message="Salasana on liian pitkä")       
        if users.new_user(username,password): 
            return redirect("/")
        else: 
            return render_template("error.html", message="Käyttäjätunnus on jo käytössä tai sitä ei voitu luoda")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/add_topic",methods=["GET","POST"])
def new_topic():
    if request.method=="GET": 
        return render_template("addtopic.html")
    if request.method=="POST": 
        topic = request.form["topic"]
        message = request.form["message"]
        user_id=session["user_id"]
        if len(topic)<1: 
            return render_template("error.html", message="Aihe puuttuu")
        if len(topic)>5000: 
            return render_template("error.html", message="Aiheesi on liian pitkä")
        if len(message)<1: 
            return render_template("error.html", message="Viesti puuttuu")
        if len(message)>5000: 
            return render_template("error.html", message="Viestisi on liian pitkä")
        if topics.new_topic(topic,message,user_id):
            return redirect("/topics")
        else: 
            return render_template("error.html", message="Aihetta ei voitu tallentaa")

@app.route("/topics")
def topiclist(): 
    result=topics.list_topics() 
    return render_template("form.html", count=len(result),topics=result)

@app.route("/topic/<string:topic>")
def all_topics(topic): 
    topic_id=topics.get_topic_id(topic)
    result=topics.list_messages(topic_id)
    return render_template("topic.html",topics=result,headline=topic)

@app.route("/add_message",methods=["POST"])
def messages():
    if request.method=="POST": 
        topic = request.form["topic"]
        message = request.form["message"]
        user_id=session["user_id"] 
        if len(message)<1: 
            return render_template("error.html", message="Viesti on liian lyhyt")
        if len(message)>5000: 
            return render_template("error.html", message="Viesti on liian pitkä")
        if len(topic)<1: 
            return render_template("error.html", message="Aiheesi on liian lyhyt")
        if len(topic)>5000: 
            return render_template("error.html", message="Aiheesi on liian pitkä")
        topic_id=topics.get_topic_id(topic) 
        if topics.new_message(message,topic_id,user_id):
            return redirect("/topics")
        else: 
            return render_template("error.html", message="Viestiä ei voitu lähettää")

@app.route("/search",methods=["GET","POST"])
def search(): 
    if request.method=="GET": 
        return render_template("search_messages.html")
    if request.method=="POST":
        query= request.form["query"]
        if len(query)<1: 
            return render_template("error.html", message="Hakukenttä ei voi olla tyhjä")
        sql=text("SELECT message FROM messages WHERE message like (:query)")
        result = db.session.execute(sql, {"query":"%"+query+"%"})
        found = result.fetchall()
        return render_template("search_results.html",topics=found)

@app.route("/change_name",methods=["GET","POST"])
def change_name(): 
    if request.method=="GET": 
        return render_template("username_request.html")   
    if request.method=="POST": 
        user_id=session["user_id"] 
        username= request.form["username"]
        if users.change_username(username, user_id): 
            return render_template("error.html", message="Käyttäjänimi vaihdettu")            
        else: 
            return render_template("error.html", message="Käyttäjänimea ei voitu vaihtaa")

@app.route("/add_admin",methods=["GET","POST"])
def register_admin(): 
    if request.method=="GET": 
        return render_template("admin_request.html")   
    if request.method=="POST": 
        user_id=session["user_id"] 
        username= request.form["username"]
        if users.add_admin(username, user_id): 
            return redirect("/admin")
        else: 
            return render_template("error.html", message="Ylläpitäjää ei voitu lisätä")

@app.route("/admin",methods=["GET","POST"])    
def admin_page():
    allow = False
    if users.is_admin(session["user_id"]):
        allow = True
    if not allow:
        return render_template("error.html", error="Ei oikeutta nähdä sivua")
    if allow:
        if request.method=="GET":
            result=topics.admin_messages(session["user_id"])             
            return render_template("admin.html",topics=result)   
        if request.method=="POST":
            if request.method=="POST":
                if session["csrf_token"] != request.form["csrf_token"]:
                    abort(403)
                message_id= request.form["number"]
                while len(message_id)<1: 
                    return render_template("error.html", message="Kenttä ei voi olla tyhjä")
                if topics.modify_messages(message_id, session["user_id"]):
                    result=topics.admin_messages(session["user_id"])
                    return render_template("admin.html",topics=result)  
                else: 
                    return render_template("error.html", message="Viestiä ei voitu poistaa")      

@app.route("/delete_topics",methods=["GET","POST"])    
def delete_topics():
    if request.method=="GET":
        result=topics.admin_topics(session["user_id"])             
        return render_template("admin_topics.html",topics=result)   
    if request.method=="POST":
        if request.method=="POST":
            topic_id= request.form["number"]
            if len(topic_id)<1: 
                return render_template("error.html", message="Kenttä ei voi olla tyhjä")
            if topics.delete_topics(topic_id, session["user_id"]):
                result=topics.admin_topics(session["user_id"])
                return render_template("admin_topics.html",topics=result)  
            else: 
                return render_template("error.html", message="Viestiä ei voitu poistaa")

@app.route("/modify",methods=["GET","POST"])    
def user_page():
    if request.method=="GET":
        result=topics.users_messages(session["user_id"])           
        return render_template("user_messages.html",topics=result)   
    if request.method=="POST":
        if request.method=="POST":
            message_id= request.form["number"]
            if len(message_id)<1: 
                return render_template("error.html", message="Kenttä ei voi olla tyhjä")
            if topics.modify_messages(message_id,session["user_id"]):
                result=topics.users_messages(session["user_id"]) 
                return render_template("user_messages.html",topics=result)  
            else: 
                return render_template("error.html", message="Viestiä ei voitu poistaa")   

@app.route("/add_area",methods=["GET","POST"])
def area_add():
    if request.method=="GET":
        result=topics.list_areas()             
        return render_template("add_area.html",topics=result)   
    if request.method=="POST":
        if request.method=="POST":
            area= request.form["area"]
            if len(area)<1: 
                return render_template("error.html", message="Kenttä ei voi olla tyhjä")
            if topics.add_area(area, session["user_id"]):
                result=topics.list_areas()
                return render_template("add_area.html",topics=result)  
            else: 
                return render_template("error.html", message="Aluetta ei voitu luoda")   

@app.route("/area/<int:id>")
def area(id):
    allow = False
    if users.is_admin(session["user_id"]):
        allow = True
    elif users.is_vip(id,session["user_id"]):
        allow = True
    if not allow:
        return render_template("error.html", error="Ei oikeutta nähdä sivua")
    if allow:
        result=topics.list_smessages(id) 
        return render_template("area.html",topics=result,headline=id)
    
@app.route("/add_smessage",methods=["POST"])
def smessage_add():
    smessage= request.form["smessage"]
    area= request.form["area"]
    if len(smessage)<1: 
        return render_template("error.html", message="Kenttä ei voi olla tyhjä")
    if len(smessage)>5000: 
        return render_template("error.html", message="Viestisi on liian pitkä")
    if users.is_admin(session["user_id"]):
        if topics.add_smessage(smessage, area, session["user_id"]):
            return redirect("/add_area")  
    elif users.is_vip(area,session["user_id"]):
        if topics.add_smessage(smessage, area, session["user_id"]):
            return redirect("/")          
    else: 
        return render_template("error.html", message="Viestiä ei voitu lähettää")  

@app.route("/add_vip",methods=["POST"])
def vip_add():
    user_id= request.form["user_id"]
    area= request.form["area"]    
    if len(user_id)<1: 
        return render_template("error.html", message="Kenttä ei voi olla tyhjä")
    if users.is_admin(session["user_id"]):    
        if users.add_vip(user_id, area):
            result=topics.list_areas()
            return render_template("add_area.html",topics=result)  
    else:  
        return render_template("error.html", message="Käyttäjää ei voitu lisätä")  
