from typing import Optional
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import String, Boolean,DateTime, ForeignKey
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    # JWT 
    id : Mapped[int] = mapped_column(primary_key= True, index= True)
    email : Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20),unique=True, index=True, nullable=True)
    hashed_password : Mapped[str] = mapped_column(String(255), nullable=False)
    # Account status flags
    is_active : Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified : Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps when the accound created and update?
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(), onupdate=func.now())
    # Relationship with "user_profile" (One-to-one relationship)
    profile : Mapped[Optional["UserProfile"]] = relationship(back_populates="user",uselist=False)
    
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, unique=True)
    full_name : Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gender : Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    # Relationship with "users" (One-to-one relationship)
    user :Mapped["User"] = relationship(back_populates="profile")
    