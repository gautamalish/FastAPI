from typing import Optional
from fastapi import FastAPI,status,HTTPException,Response,Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine,get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)
# Dependency
app=FastAPI()

class Post(BaseModel):
    title:str
    content:str
    published:bool=True

while True:
    try:
        conn=psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='admin',cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print('Database connection was successful!')
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ",error)
        time.sleep()
    
my_posts=[{"title":"First post title","content":"First Post Content","id":1},{"title":"Second post title","content":"Second Post Content","id":2}]

def findPost(id):
    for p in my_posts:
        if p['id']==id:
            return p
        
def findIndex(id):
    for i,p in enumerate(my_posts):
        if p['id']==id:
            return i
        

@app.get("/")
def root():
    return {"message":"Hello Message"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts=cursor.fetchall()
    return{"data":posts}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(post:Post):
    cursor.execute("""INSERT INTO posts (title,content,published) VALUES(%s,%s,%s) RETURNING * """,(post.title,post.content,post.published))
    new_post=cursor.fetchone()
    conn.commit()
    return {"data":new_post} 

# test
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts=db.query(models.Post).all()
    return {"data":posts}

@app.get("/posts/{id}")
def get_post(id:int):
    cursor.execute("SELECT * FROM posts WHERE id=%s",(str(id),))
    post=cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} was not found.')
    return {"post_detail":post}

@app.delete('/posts/{id}')
def delete_post(id:int,status_code=status.HTTP_204_NO_CONTENT):
    cursor.execute("DELETE FROM posts WHERE id=%s RETURNING *",(str(id),))
    deleted_post=cursor.fetchone()
    conn.commit()
    
    if deleted_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Post with id:{id} does not exist.')
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_Post(id:int,post:Post):
    cursor.execute("UPDATE posts SET title=%s,content=%s,published=%s WHERE id=%s RETURNING *",(post.title,post.content,post.published,str(id)),)
    updated_post=cursor.fetchone()
    conn.commit()
    if updated_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'The post with id:{id} was not found.')

    return {'message':updated_post}