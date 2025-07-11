from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.security import get_current_user
from fastapi.responses import FileResponse
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=schemas.Message)
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_message = models.Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/", response_model=list[schemas.Message])
def list_messages(db: Session = Depends(get_db)):
    return db.query(models.Message).all()

@router.post("/upload", response_model=dict)
def upload_file(message_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg", "text/plain"]:
        raise HTTPException(status_code=400, detail="Niedozwolony typ pliku.")

    contents = file.file.read()
    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Plik przekracza 25 MB.")
    file.file.seek(0)

    filename = f"{message_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Wiadomość nie istnieje.")

    message.file_path = filepath
    db.commit()

    return {"filename": filename}

@router.get("/download/{message_id}")
async def download_file(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message or not message.file_path:
        raise HTTPException(status_code=404, detail="Plik nie istnieje")

    if current_user.id not in [message.sender_id, message.receiver_id]:
        raise HTTPException(status_code=403, detail="Brak dostępu do pliku")

    return FileResponse(path=message.file_path, filename=os.path.basename(message.file_path))
