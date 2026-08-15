from pydantic import BaseModel, EmailStr, Field, SecretStr, model_validator
from typing import Optional, Self 
from enum import Enum

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
    
    @model_validator(mode="after")
    def check_password_match(self):
        if self.password.get_secret_value() != self.confirm_password.get_secret_value():
            raise ValueError("Passwords do not match")
        return self
    
class LoginRequest(BaseModel):
    email : EmailStr = Field(title="Mail", examples=["acb@gmail.com"])
    password : SecretStr = Field(min_length=8, max_length=255)
    
