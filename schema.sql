CREATE TABLE users (
    id SERIAL PRIMARY KEY, 
    username TEXT UNIQUE, 
    password TEXT,
    admin BOOLEAN);  

CREATE TABLE topics (
    id SERIAL PRIMARY KEY, 
    topic TEXT UNIQUE, 
    visible BOOLEAN, 
    user_id INTEGER REFERENCES users);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY, 
    message TEXT, 
    sent_at TIMESTAMP,
    visible BOOLEAN,
    user_id INTEGER REFERENCES users, 
    topic_id INTEGER REFERENCES topics); 

CREATE TABLE areas (
    id SERIAL PRIMARY KEY, 
    area TEXT UNIQUE); 

CREATE TABLE vip (
    id SERIAL PRIMARY KEY, 
    user_id INTEGER REFERENCES users,
    area_id INTEGER REFERENCES areas); 

CREATE TABLE smessages (
    id SERIAL PRIMARY KEY, 
    smessage TEXT,
    user_id INTEGER REFERENCES users,
    area_id INTEGER REFERENCES areas);
