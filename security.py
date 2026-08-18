from passlib.context import CryptContext
import os 
import uuid
from jose import JOSEError, jwt
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = "HS256" # Help us to make Signature
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS   = 7

# Bcrypt the password with deprecated (if old one is week make newest, strongest bcrypt algorithm)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

# Hash password
def hash_password(password : str) -> str:
    return pwd_context.hash(password)

def verify_passwrod (plain_password : str, hashed_password : str) -> bool:
    # Check if the entered password matches the stored hash
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(user_id : int) -> str:
    now = datetime.now(timezone.utc) # currenttime based on timezone
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Expire time 
    
    # SUB -> user_id never change so we can update user information 
    payload = {
        "sub" : str(user_id), # Sub 
        "type" : "access",
        "iat" : now,
        "exp" : expire
    }
    
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

def create_refresh_token(user_id : int) -> str:
    
    now = datetime.now(timezone.utc) # currenttime based on timezone
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS) # Expire time 
    
    # SUB -> user_id never change so we can update user information 
    payload = {
        "sub" : str(user_id),  
        "type" : "refresh",
        "jti": str(uuid.uuid4()),  # Uniqe Id for access token 
        "iat" : now,
        "exp" : expire
    }
    
    return jwt.encode(payload,REFRESH_SECRET_KEY,algorithm=ALGORITHM)
