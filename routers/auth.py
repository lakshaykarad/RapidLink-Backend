from fastapi import APIRouter, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import User, UserProfile
from schemas import SignupRequest

from security import (
    hash_password
)

routes = APIRouter(prefix="/auth", tags=["Authentication"])
# OAuth2PasswordBearer -> If the user does not provide the token in the header, reject his request before checking the verifytoken. 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@routes.post("/signup", status_code= status.HTTP_201_CREATED)
def signup(request : SignupRequest, db : Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == request.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail= "Email already registered. Please login"
        )
    
    # hased the user passwrod
    hashed_pw = hash_password(request.password.get_secret_value())
    
    new_user = User(
        email = request.email,
        hashed_password = hashed_pw,
        phone_number = request.phone_number,
        is_active = True,
        is_verified = False
    )
    
    db.add(new_user)
    db.flush() # Forced Sql to genrate Id so we can use below 
    
    user_profile = UserProfile(
        user_id = new_user.id,
        full_name = request.full_name,
        gender = request.gender
    )
    
    db.add(user_profile)
    
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred during registration. Please try again."
        )
    
       
    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "email": new_user.email
    }