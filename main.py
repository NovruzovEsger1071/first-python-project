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
from fastapi import UploadFile, File, BackgroundTasks
from pathlib import Path
import shutil, uuid
import pandas as pd
from models import UploadedFile, SalesRecord, AnalyticsSummary
from schemas import UploadedFileResponse, AnalyticsSummaryResponse
from fastapi import Depends, HTTPException, status, FastAPI
from fastapi.security import OAuth2PasswordBearer





app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)



Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()




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


REQUIRED_COLUMNS = ["date", "product_name", "quantity", "price", "region"]

@app.post("/files/upload", response_model=UploadedFileResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Yalnız CSV və Excel faylları qəbul edilir")

    file_id = str(uuid.uuid4())
    file_path = UPLOAD_FOLDER / f"{file_id}_{file.filename}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    uploaded_file = UploadedFile(
        id=file_id,
        filename=file.filename,
        filepath=str(file_path),
        status="pending",
        user_id=current_user.id
    )
    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    background_tasks.add_task(process_file, uploaded_file.id)
    # background_tasks.add_task(process_file, uploaded_file.id, db)

    return uploaded_file


def process_file(file_id: str):
    db = session_local()  # yeni session açılır
    try:
        uploaded_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        if not uploaded_file:
            return

        uploaded_file.status = "processing"
        db.commit()

        if uploaded_file.filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file.filepath)
        else:
            df = pd.read_excel(uploaded_file.filepath)

        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            uploaded_file.status = "failed"
            uploaded_file.error_message = f"Əskik sütunlar: {missing_cols}"
            db.commit()
            return

        df = df.dropna(subset=REQUIRED_COLUMNS)
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.dropna(subset=["quantity", "price"])

        sales_records = [
            SalesRecord(
                uploaded_file_id=file_id,
                date=row["date"],
                product_name=row["product_name"],
                quantity=row["quantity"],
                price=row["price"],
                region=row["region"]
            ) for _, row in df.iterrows()
        ]
        db.bulk_save_objects(sales_records)
        db.commit()

        total_sales_product = df.groupby("product_name").apply(lambda x: (x.quantity * x.price).sum()).to_dict()
        total_sales_region = df.groupby("region").apply(lambda x: (x.quantity * x.price).sum()).to_dict()
        df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
        monthly_trends = df.groupby("month").apply(lambda x: (x.quantity * x.price).sum()).to_dict()

        analytics = AnalyticsSummary(
            uploaded_file_id=file_id,
            total_sales_product=total_sales_product,
            total_sales_region=total_sales_region,
            monthly_trends=monthly_trends
        )
        db.add(analytics)

        uploaded_file.status = "done"
        db.commit()

    except Exception as e:
        uploaded_file.status = "failed"
        uploaded_file.error_message = str(e)
        db.commit()
        print(f"Error processing file {file_id}: {e}")  # terminalda xətanı görmək üçün

    finally:
        db.close()

# def process_file(file_id: str, db: Session):
#     uploaded_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
#     if not uploaded_file:
#         return
#
#     uploaded_file.status = "processing"
#     db.commit()
#
#     try:
#         if uploaded_file.filename.endswith(".csv"):
#             df = pd.read_csv(uploaded_file.filepath)
#         else:
#             df = pd.read_excel(uploaded_file.filepath)
#
#         missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
#         if missing_cols:
#             uploaded_file.status = "failed"
#             uploaded_file.error_message = f"Əskik sütunlar: {missing_cols}"
#             db.commit()
#             return
#
#         df = df.dropna(subset=REQUIRED_COLUMNS)
#         df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
#         df["price"] = pd.to_numeric(df["price"], errors="coerce")
#         df = df.dropna(subset=["quantity", "price"])
#
#         sales_records = [
#             SalesRecord(
#                 uploaded_file_id=file_id,
#                 date=row["date"],
#                 product_name=row["product_name"],
#                 quantity=row["quantity"],
#                 price=row["price"],
#                 region=row["region"]
#             ) for _, row in df.iterrows()
#         ]
#         db.bulk_save_objects(sales_records)
#         db.commit()
#
#         total_sales_product = df.groupby("product_name").apply(lambda x: (x.quantity * x.price).sum()).to_dict()
#         total_sales_region = df.groupby("region").apply(lambda x: (x.quantity * x.price).sum()).to_dict()
#         df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
#         monthly_trends = df.groupby("month").apply(lambda x: (x.quantity * x.price).sum()).to_dict()
#
#         analytics = AnalyticsSummary(
#             uploaded_file_id=file_id,
#             total_sales_product=total_sales_product,
#             total_sales_region=total_sales_region,
#             monthly_trends=monthly_trends
#         )
#         db.add(analytics)
#
#         uploaded_file.status = "done"
#         db.commit()
#
#     except Exception as e:
#         uploaded_file.status = "failed"
#         uploaded_file.error_message = str(e)
#         db.commit()




@app.get("/files/{file_id}/status", response_model=UploadedFileResponse)
def file_status(file_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id, UploadedFile.user_id == current_user.id
    ).first()
    if not uploaded_file:
        raise HTTPException(status_code=404, detail="Fayl tapılmadı")
    return uploaded_file






def hash_password(password: str):
    return pwd_context.hash(password)






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