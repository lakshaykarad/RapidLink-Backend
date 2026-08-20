from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any, Optional
from database import get_db
from models import User, UserProfile
from schemas import SignupRequest, UserResponse, LoginRequest, UserProfileResponse, TokenRequest
from jose import JWTError, ExpiredSignatureError

from security import (
    hash_password, create_access_token,verify_access_token,create_refresh_token,verify_refresh_token,verify_password
)

router  = APIRouter(prefix="/auth", tags=["Authentication"])
# OAuth2PasswordBearer -> If the user does not provide the token in the header, reject his request before checking the verifytoken. 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/signup", status_code= status.HTTP_201_CREATED)
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
    

@router.post("/login")
def login(
    response: Response,
    request : LoginRequest,
    db : Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()   
    
    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    if not verify_password(request.password.get_secret_value(), user.hashed_password):
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support."
        )
    
    # create token 
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    # Set cookies 
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly= True, # Stop JS to read cookie,
        secure= False, # For testing
        samesite="Strict",
        max_age= 7 * 24 * 60 * 60
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token, # Added for Android support!
        "token_type": "bearer",         # Fixed: Added missing comma
        "expires_in": 15 * 60,
        "user_id": user.id,
        "email": user.email
    }


@router.post("/refresh")
def refresh(
    request : Request,
    db : Session = Depends(get_db),
    token_request : Optional[TokenRequest] = None
):
    refresh_token = request.cookies.get("refresh_token") or (token_request.refresh_token if token_request else None)
      
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    payload = verify_refresh_token(refresh_token)

    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
        
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated"
        )

    return {
        "access_token" : create_access_token(user.id),
        "token_type" : "bearer",
        "expires_in" : 15 * 60
    }