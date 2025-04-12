from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import requests
from datetime import datetime, timedelta

from app.models import Base, User
from app.schemas import UserSchema, Token, TokenData
from app.database import engine, SessionLocal
from app.security import create_access_token, verify_password
from app.routers import properties, alerts, invoices, messages, payments

Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api", title="Rent-Ease API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get the DB session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.post("/adduser")
async def add_user(request: UserSchema, db: Session = Depends(get_db)):
    user = User(name=request.name, email=request.email, nickname=request.nickname)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/user/{user_name}")
async def get_user(user_name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == user_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/cat-fact")
def get_cat_fact():
    response = requests.get("https://catfact.ninja/fact")
    if response.status_code == 200:
        return response.json()
    else:
        return JSONResponse(status_code=404, content={"message": "No cat fact found"})

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(properties.router, prefix="/properties", tags=["Properties"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
