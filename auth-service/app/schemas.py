from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permissions: List[int] = []

class Role(RoleBase):
    id: int
    permissions: List[Permission] = []
    class Config:
        orm_mode = True
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str 
    role_id: int = None  

class UserOut(UserBase):
    id: int
    username: str
    email: EmailStr
    role_id: int
    is_active: int
    is_admin: int

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None
    role_id: int
    user_id: int
