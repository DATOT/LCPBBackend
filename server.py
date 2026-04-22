from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
import os
from datetime import datetime

from vercel_blob import put

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "/tmp/posts.json"


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

@app.post("/posts")
async def create_post(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    try:
        print("START UPLOAD")

        posts = load_posts()

        filename = f"{int(datetime.now().timestamp()*1000)}_{file.filename}"

        content = await file.read()

        blob = put(
            f"uploads/{filename}",
            content,
        )

        print("BLOB URL:", blob["url"])

        post = {
            "id": int(datetime.now().timestamp() * 1000),
            "title": title,
            "description": description or "",
            "author": author or "Ẩn Danh",
            "image": blob["url"],
            "date": datetime.now().isoformat(),
        }

        posts.insert(0, post)
        save_posts(posts)

        return post

    except Exception as e:
        print("ERROR:", str(e)) 
        return {"error": str(e)}
