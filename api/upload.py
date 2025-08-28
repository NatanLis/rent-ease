from fastapi import APIRouter, UploadFile, File, HTTPException, Response
import psycopg2
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
            "INSERT INTO files (filename, mimetype, size, data) VALUES (%s, %s, %s, %s) RETURNING id",
            (file.filename, file.content_type, len(content), psycopg2.Binary(content))
        )
        file_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Plik zapisany!", "id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_id}")
def download_file(file_id: int):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT filename, mimetype, data FROM files WHERE id = %s",
            (file_id,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Plik nie znaleziony")
        filename, mimetype, data = row
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        return Response(content=data, media_type=mimetype, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
