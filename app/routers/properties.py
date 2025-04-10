from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Property)
def create_property(property: schemas.PropertyCreate, db: Session = Depends(get_db)):
    db_property = models.Property(**property.dict())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

@router.get("/", response_model=list[schemas.Property])
def list_properties(db: Session = Depends(get_db)):
    return db.query(models.Property).all()

@router.get("/{property_id}", response_model=schemas.Property)
def get_property(property_id: int, db: Session = Depends(get_db)):
    property = db.query(models.Property).get(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@router.put("/{property_id}", response_model=schemas.Property)
def update_property(property_id: int, updated: schemas.PropertyCreate, db: Session = Depends(get_db)):
    property = db.query(models.Property).get(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in updated.dict().items():
        setattr(property, key, value)
    db.commit()
    return property

@router.delete("/{property_id}")
def delete_property(property_id: int, db: Session = Depends(get_db)):
    property = db.query(models.Property).get(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(property)
    db.commit()
    return {"ok": True}
