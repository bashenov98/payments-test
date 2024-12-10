from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import RoleCreate, PermissionCreate, UserCreate
from .auth import create_role, create_permission, create_user
from .auth import get_password_hash
from .schemas import Permission as PermissionSchema, Role, UserOut
from .models import Permission, Role as RoleModel


router = APIRouter()

@router.post("/roles/", response_model=Role)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    # Fetch permissions from the database
    permissions = db.query(Permission).filter(Permission.id.in_(role.permissions)).all()

    # Validate that all requested permissions exist
    if len(permissions) != len(role.permissions):
        raise HTTPException(
            status_code=400,
            detail="Some permissions do not exist"
        )
    
    # Create and save the new role
    new_role = RoleModel(
        name=role.name,
        description=role.description,
        permissions=permissions
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    # Return the newly created role
    return Role.from_orm(new_role)

@router.post("/permissions/", response_model=PermissionSchema)
def create_new_permission(permission: PermissionCreate, db: Session = Depends(get_db)):
    new_permission = create_permission(db, permission)
    return new_permission

@router.get("/permission/{permission_id}", response_model=PermissionSchema)
def get_permission(permission_id: int, db: Session = Depends(get_db)):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission 

@router.post("/users/", response_model=UserOut)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    new_user = create_user(db, user, hashed_password)
    return new_user
