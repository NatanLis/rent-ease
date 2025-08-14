from fastapi import APIRouter, UploadFile, File, HTTPException
import psycopg2
from psycopg2 import sql
import os

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "rentease_db_dev"),
        user=os.getenv("POSTGRES_USER", "root"),
        password=os.getenv("POSTGRES_PASSWORD", "pass"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Plik za duży (max 20MB)")
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO files (filename, mimetype, size, data) VALUES (%s, %s, %s, %s)",
            (file.filename, file.content_type, len(content), psycopg2.Binary(content))
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Plik zapisany!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))