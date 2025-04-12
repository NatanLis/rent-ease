from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=list[schemas.Alert])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).all()
