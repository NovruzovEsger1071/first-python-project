from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends, status
from typing import Optional, List, Dict, Annotated
from sqlalchemy.orm import Session, joinedload
from models import User, Post, Base
from database import engine, session_local
from schemas import UserCreate, UserResponse, PostCreate, PostResponse, UserUpdate, PostUpdate
app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.name == user.name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(name=user.name, age=user.age, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login")
async def login(name: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == name).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": f"Welcome {user.name}!"}


@app.put("/update-user/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.age is not None:
        user.age = user_update.age

    db.commit()
    db.refresh(user)
    return user


@app.get("/read-one-user/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/read-all-users/", response_model=List[UserResponse])
async def read_users(db: Session = Depends(get_db)) -> List[UserResponse]:
    return db.query(User).all()


@app.delete("/delete-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return


@app.delete("/delete-all-users/")
def delete_all_users(db: Session = Depends(get_db)):
    db.query(User).delete()
    db.commit()
    return {"message": "Bütün userlər silindi"}




@app.post("/create-post/", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    db_user = db.query(User).filter(User.id == post.author_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_post = Post(title=post.title, body=post.body, author_id=post.author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.put("/update-post/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_update.title is not None:
        post.title = post_update.title
    if post_update.body is not None:
        post.body = post_update.body
    if post_update.author_id is not None:
        db_user = db.query(User).filter(User.id == post_update.author_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        post.author_id = post_update.author_id

    db.commit()
    db.refresh(post)
    return post


@app.get("/read-one-post/{post_id}", response_model=PostResponse)
async def read_post(post_id: int, db: Session = Depends(get_db)) -> PostResponse:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.get("/read-all-posts/", response_model=List[PostResponse])
async def read_posts(db: Session = Depends(get_db)) -> List[PostResponse]:
    return db.query(Post).all()


@app.delete("/delete-post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return


@app.delete("/delete-all-posts/")
def delete_all_posts(db: Session = Depends(get_db)):
    db.query(Post).delete()
    db.commit()
    return {"message": "Bütün postlar silindi"}