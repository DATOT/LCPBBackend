from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
import json
import os
import shutil
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
DB_FILE = "posts.json"


def load_posts():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_posts(posts):
    with open(DB_FILE, "w") as f:
        json.dump(posts, f)


@app.get("/posts")
def get_posts():
    return load_posts()


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/posts")
async def create_post(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    posts = load_posts()
    print("title:", title)
    print("author:", author)
    print("file:", file.filename)
    filename = f"{int(datetime.now().timestamp()*1000)}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    post = {
        "id": int(datetime.now().timestamp() * 1000),
        "title": title,
        "description": description or "",
        "author": author or "Ẩn Danh",
        "image": f"https://lcpb-backend-s83m.vercel.app/uploads/{filename}",
        "date": datetime.now().isoformat(),
    }

    posts.insert(0, post)
    save_posts(posts)

    return post
