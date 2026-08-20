from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from security import verify_access_token
from database import get_db
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Help to add new featuer later where we don't need to write same code again and again.
def get_current_active_user(
    token : str = Depends(oauth2_scheme),
    db : Session = Depends(get_db)
) -> User:
    payload = verify_access_token(token)
    
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()    
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is banned"
        )        
        
    return user