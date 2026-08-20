from pydantic import BaseModel, EmailStr, Field, SecretStr, model_validator, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Self 
from enum import Enum
import re

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHERS = "other"
    PREFER_NOT = "prefer_not_to_say"

class SignupRequest(BaseModel):
    email : EmailStr = Field(title="Mail", examples=["acb@gmail.com"])
    password : SecretStr = Field(min_length=8, max_length=255)
    confirm_password : SecretStr
    full_name : str = Field(max_length=50)
    gender : Gender
    phone_number : str | None = Field(pattern=r"^\+?[1-9]\d{1,14}$", examples=["+919876543210"], default=None)
   
    @field_validator('password')
    def validate_password_strength(cls, v : SecretStr) -> SecretStr:
        password = v.get_secret_value()
        
        rules = {
            r'[A-Z]' : 'Password must contain at least one uppercase letter',
            r'[a-z]' : 'Password must contain at least one lowercase letter',
            r'\d': 'Password must contain at least one number',
            r'[!@#$%^&*(),.?":{}|<>]': 'Password must contain at least one special character'
        }
        
        for pattern,error_message in rules.items():
            if not re.search(pattern,password):
                raise ValueError(error_message)
        
        return v
    
    @model_validator(mode="after")
    def check_password_match(self):
        if self.password.get_secret_value() != self.confirm_password.get_secret_value():
            raise ValueError("Passwords do not match")
        return self  
    
    
    
class LoginRequest(BaseModel):
    email : EmailStr = Field(title="Mail", examples=["acb@gmail.com"])
    password : SecretStr = Field(min_length=8, max_length=255)
    
class UserProfileResponse(BaseModel):
    full_name : str = Field(default=None)
    gender : Gender = Field(default=None)
    
class UserResponse(BaseModel):
    id : int  
    email : EmailStr 
    phone_number : str  | None = None
    is_active : bool = True
    is_verify : bool = True
    created_at : datetime 
    profile : Optional[UserProfileResponse]  | None = None
    model_config = ConfigDict(from_attributes=True)
    
    
class TokenRequest(BaseModel):
    refresh_token : Optional[str] = None