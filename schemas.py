from pydantic import BaseModel, EmailStr, Field, SecretStr, model_validator, field_validator
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
    def validate_passowrd_strenth(cls, v : SecretStr) -> SecretStr:
        password = v.get_secret_value()
        
        rules = {
            r'[A-Z]' : 'Password must contain atleast one uppercase latter',
            r'[a-z]' : 'Password must contain atleast one lowercase latter',
            r'\d': 'Password must contain at least one number',
            r'^.{8,}$': 'Password must be at least 8 characters long',
            r'[!@#$%^&*(),.?":{}|<>]': 'Password must contain at least one special character'
        }
        
        for pattern,error_message in rules.items():
            if not re.search(pattern,password):
                raise ValueError(error_message)
        
        return v
        
    # Validator 2: Check password MATCH TO SAVE CPU POWER 
    @model_validator(mode="after")
    def check_password_match(self):
        if self.password.get_secret_value() != self.confirm_password.get_secret_value():
            raise ValueError("Passwords do not match")
        return self
    
    
class LoginRequest(BaseModel):
    email : EmailStr = Field(title="Mail", examples=["acb@gmail.com"])
    password : SecretStr = Field(min_length=8, max_length=255)
    
