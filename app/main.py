from typing import Optional
from fastapi import FastAPI,status,HTTPException,Response
from pydantic import BaseModel
from random import randrange
app=FastAPI()

class Post(BaseModel):
    title:str
    content:str
    published:bool=True
    rating:Optional[int]=None

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
    return{"data":my_posts}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(post:Post):
    post_dict=post.model_dump()
    post_dict['id']=randrange(0,10000000)
    my_posts.append(post_dict)
    
    return {"data":post_dict}

@app.get("/posts/{id}")
def get_post(id:int):
    post=findPost(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} was not found.')
        # response.status_code=status.HTTP_404_NOT_FOUND
        # return {'message':f'Post with id: {id} was not found.'}
    return {"post_detail":post}

@app.delete('/posts/{id}')
def delete_post(id:int,status_code=status.HTTP_204_NO_CONTENT):
    index=findIndex(id)
    if index==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Post with id:{id} does not exist.')
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def updatePost(id:int,post:Post):
    index=findIndex(id)
    if index==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'The post with id:{id} was not found.')
    post_dict=post.model_dump()
    post_dict['id']=id
    my_posts[index]=post_dict
    return {'message':'Updated Post'}