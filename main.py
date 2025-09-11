from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends, status
from typing import Optional, List, Dict, Annotated
from sqlalchemy.orm import Session, joinedload
from models import User, Post, Base
from database import engine, session_local
from schemas import UserCreate, UserResponse, PostCreate, PostResponse, UserUpdate, PostUpdate
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from auth import verify_password, create_access_token, SECRET_KEY, ALGORITHM



app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()



def hash_password(password: str):
    return pwd_context.hash(password)



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user



@app.post("/users/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.name == user.name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(user.password)
    new_user = User(name=user.name, age=user.age, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
# @app.post("/register", response_model=UserResponse)
# async def register(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.name == user.name).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="User already exists")
#
#     new_user = User(name=user.name, age=user.age, password=user.password)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user






@app.post("/users/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):  # ✅ hash yoxlama
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # ✅ JWT yarat
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# @app.post("/login")
# async def login(name: str, password: str, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.name == name).first()
#     if not user or user.password != password:
#         raise HTTPException(status_code=401, detail="Invalid username or password")
#     return {"message": f"Welcome {user.name}!"}










@app.put("/update-user/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.name is not None:
        user.name = user_update.name
    if user_update.age is not None:
        user.age = user_update.age
    if user_update.password is not None:
        user.password = hash_password(user_update.password)  # parol hash-lənir

    db.commit()
    db.refresh(user)
    return user

# @app.put("/update-user/{user_id}", response_model=UserResponse)
# async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     if user_update.name is not None:
#         user.name = user_update.name
#     if user_update.age is not None:
#         user.age = user_update.age
#
#     db.commit()
#     db.refresh(user)
#     return user


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