# from fastapi import APIRouter, Depends, status, HTTPException
# from sqlalchemy.orm import Session
# from typing import List
# from fastapi.responses import JSONResponse
# from passlib.context import CryptContext

# from app import models, schemas, oauth2, database
# from app.database import get_db

# # Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# router = APIRouter(
#     tags=['Users']
# )


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify a password against its hash"""
#     return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password: str) -> str:
#     """Hash a password"""
#     return pwd_context.hash(password)


# @router.post("/signup", response_model=schemas.Token)
# async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     try:
#         # Check if user already exists
#         db_user = db.query(models.User).filter(models.User.email == user.email).first()
#         if db_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email already registered"
#             )

#         # Hash password
#         hashed_password = get_password_hash(user.password)

#         # Superuser flag (optional)
#         is_superuser = getattr(user, "is_superuser", False)

#         # Validate role only if not superuser
#         role = None
#         if not is_superuser:
#             if user.role_id is None:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="role_id is required for non-superusers"
#                 )

#             role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
#             if not role:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="Role not found"
#                 )

#         # Create user
#         new_user = models.User(
#             username=user.username,
#             email=user.email,
#             hashed_password=hashed_password,
#             is_active=True,
#             is_superuser=is_superuser,
#             role_id=user.role_id if not is_superuser else None
#         )

#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)

#         # Create token
#         access_token = oauth2.create_access_token(data={"user_id": new_user.id})
#         return {"access_token": access_token, "token_type": "bearer"}

#     except HTTPException:
#         raise
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Internal server error")


# @router.post("/login")
# def login(user_credentials: schemas.LoginRequest, db: Session = Depends(database.get_db)):
#     # Step 1: Authenticate user
#     user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

#     if not user or not verify_password(user_credentials.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Incorrect email or password"
#         )

#     # Step 2: Check if user is active
#     if hasattr(user, "is_active") and not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Account is disabled"
#         )

#     # Step 3: Load all permissions and initialize permissions_dict
#     all_permissions = db.query(models.Permission).all()
#     permissions_dict = {perm.code: False for perm in all_permissions}

#     # Step 4: Determine is_superuser based on role
#     is_superuser_response = False

#     if user.is_superuser and not user.role:
#         for perm in all_permissions:
#             permissions_dict[perm.code] = True
#         is_superuser_response = True

#     elif user.role:
#         for perm in user.role.permissions:
#             permissions_dict[perm.code] = True

#     else:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="User has no role assigned"
#         )

#     # Step 5: Create access and refresh tokens
#     access_token = oauth2.create_access_token(data={"user_id": user.id})
#     refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})

#     # Step 6: Prepare response
#     response_data = {
#         "message": "Successful",
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#         "user_id": user.id,
#         "username": user.username,
#         "email": user.email,
#         "is_superuser": is_superuser_response,
#         "role_id": user.role.id if user.role else None,
#         "role_name": user.role.name if user.role else None,
#         "permissions": permissions_dict
#     }

#     # Step 7: Return response with status code
#     return JSONResponse(status_code=status.HTTP_200_OK, content=response_data)


# @router.get("/me", response_model=schemas.UserOut)
# def get_me(current_user: models.User = Depends(oauth2.get_current_user)):
#     return current_user


# @router.get("/{id}", response_model=schemas.UserOut)
# def get_user(id: int, db: Session = Depends(database.get_db),
#              current_user: models.User = Depends(oauth2.get_current_user)):
#     if current_user.id != id and not current_user.is_admin:
#         raise HTTPException(
#             status_code=403, 
#             detail="Not authorized to access this user's information"
#         )
    
#     user = db.query(models.User).filter(models.User.id == id).first()
#     if not user:
#         raise HTTPException(
#             status_code=404, 
#             detail=f"User with id {id} not found"
#         )
    
#     return user


# @router.get("/", response_model=List[schemas.UserOut])
# def get_all_users(db: Session = Depends(database.get_db), 
#                  current_user: models.User = Depends(oauth2.get_current_user)):
#     # Only allow admin to view all users
#     if not current_user.is_admin:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only admin users can view all users"
#         )
    
#     users = db.query(models.User).all()
#     return users


# @router.put("/{id}", response_model=schemas.UserOut)
# def update_user(id: int, updated_user: schemas.UserCreate, 
#                db: Session = Depends(database.get_db), 
#                current_user: models.User = Depends(oauth2.get_current_user)):
#     # Only allow users to update their own profile or admin to update any profile
#     if current_user.id != id and not current_user.is_admin:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update this user's information"
#         )
    
#     user_query = db.query(models.User).filter(models.User.id == id)
#     user = user_query.first()
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"User with id {id} not found"
#         )
    
#     # Hash the password if it's being updated
#     if updated_user.password:
#         updated_user.password = get_password_hash(updated_user.password)
    
#     user_query.update(updated_user.dict(), synchronize_session=False)
#     db.commit()
#     return user_query.first()


# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_user(id: int, db: Session = Depends(database.get_db), 
#                current_user: models.User = Depends(oauth2.get_current_user)):
#     # Only allow admin to delete users or users to delete themselves
#     # Uncomment below if you want to restrict deletion
#     # if current_user.id != id and not current_user.is_admin:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_403_FORBIDDEN,
#     #         detail="Not authorized to delete this user"
#     #     )
    
#     user_query = db.query(models.User).filter(models.User.id == id)
#     user = user_query.first()
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"User with id {id} not found"
#         )
    
#     user_query.delete(synchronize_session=False)
#     db.commit()
#     return




from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import database, schemas, models, oauth2
from typing import List
from app.schemas.user import UserOut
from ..schemas import LoginRequest, Token
from fastapi.security import OAuth2PasswordRequestForm
from ..database import get_db
from fastapi.responses import JSONResponse
from app import models, schemas, oauth2, database
import traceback
from passlib.context import CryptContext

# ✅ Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Password utility functions defined in this file
def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


router = APIRouter(
    # prefix="/users",
    tags=['Users']
)

@router.post("/signup", response_model=schemas.Token)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # ✅ Validate that employee exists and is not already linked to a user
        employee = db.query(models.Employee).filter(models.Employee.id == user.employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with id {user.employee_id} not found"
            )

        # ✅ Check if employee is already linked to another user
        existing_user_with_employee = db.query(models.User).filter(
            models.User.employee_id == user.employee_id
        ).first()
        if existing_user_with_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with id {user.employee_id} is already linked to another user"
            )

        # ✅ Optional: Check if email matches employee email (for consistency)
        if user.email != employee.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email must match the employee's email"
            )

        # ✅ Hash password using local function
        hashed_password = get_password_hash(user.password)

        # Superuser flag (optional)
        is_superuser = getattr(user, "is_superuser", False)

        # Validate role only if not superuser
        role = None
        if not is_superuser:
            if user.role_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="role_id is required for non-superusers"
                )

            role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )

        # ✅ Create user with employee_id
        new_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=is_superuser,
            role_id=user.role_id if not is_superuser else None,
            employee_id=user.employee_id  # ✅ Link to employee
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create token
        access_token = oauth2.create_access_token(data={"user_id": new_user.id})
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise  # Re-raise HTTPExceptions without modification
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login")
def login(user_credentials: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    # Step 1: Authenticate user
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    # ✅ Using local verify_password function
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect email or password"
        )

    # Step 2: Check if user is active (optional)
    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Step 3: Load all permissions and initialize permissions_dict
    all_permissions = db.query(models.Permission).all()
    permissions_dict = {perm.code: False for perm in all_permissions}

    # Step 4: Determine is_superuser based on role
    is_superuser_response = False

    if user.is_superuser and not user.role:
        for perm in all_permissions:
            permissions_dict[perm.code] = True
        is_superuser_response = True

    elif user.role:
        for perm in user.role.permissions:
            permissions_dict[perm.code] = True

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no role assigned"
        )

    # Step 5: Create access and refresh tokens
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})

    # ✅ Step 6: Get employee information if linked
    employee_info = None
    if user.employee_id and user.employee:
        employee_info = {
            "id": user.employee.id,
            "name": user.employee.name,
            "job_title": user.employee.job_title,
            "department_id": user.employee.department_id
        }

    # Step 7: Prepare response
    response_data = {
        "message": "Successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_superuser": is_superuser_response,
        "role_id": user.role.id if user.role else None,
        "name": user.role.name if user.role else None,
        "employee_info": employee_info,  # ✅ Include employee info
        "permissions": permissions_dict
    }

    # Step 8: Return response with status code
    return JSONResponse(status_code=status.HTTP_200_OK, content=response_data)


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(database.get_db),
             current_user: models.User = Depends(oauth2.get_current_user)):
    # ✅ Check authorization properly
    if current_user.id != id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this user's information"
        )
    
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with id {id} not found"
        )
    
    return user


@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(database.get_db), 
                 current_user: models.User = Depends(oauth2.get_current_user)):
    # ✅ Only allow superuser to view all users
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superuser can view all users"
        )
    
    users = db.query(models.User).all()
    return users


@router.put("/{id}", response_model=schemas.UserOut)
def update_user(id: int, updated_user: schemas.UserUpdate, 
               db: Session = Depends(database.get_db), 
               current_user: models.User = Depends(oauth2.get_current_user)):
    # ✅ Only allow users to update their own profile or superuser to update any profile
    if current_user.id != id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's information"
        )
    
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )
    
    # ✅ Get only the fields that are not None
    update_data = updated_user.model_dump(exclude_unset=True)
    
    # ✅ Hash the password if it's being updated (using local function)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]  # Remove plain password from update
    
    # ✅ Apply updates
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(database.get_db), 
               current_user: models.User = Depends(oauth2.get_current_user)):
    # ✅ Only allow superuser to delete users
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superuser can delete users"
        )
    
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )
    
    user_query.delete(synchronize_session=False)
    db.commit()
    return


# ✅ Additional endpoint to get employees without users (for signup)
@router.get("/available-employees/", response_model=List[schemas.Employee])
def get_available_employees(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """Get employees that don't have a user account yet"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superuser can view available employees"
        )
    
    # ✅ Query employees that don't have a linked user
    available_employees = db.query(models.Employee).outerjoin(
        models.User, models.Employee.id == models.User.employee_id
    ).filter(models.User.employee_id.is_(None)).all()
    
    return available_employees


# ✅ Endpoint to link existing user to employee
@router.patch("/{user_id}/link-employee/{employee_id}")
def link_user_to_employee(
    user_id: int,
    employee_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """Link an existing user to an employee"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superuser can link users to employees"
        )
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Check if employee exists
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )
    
    # Check if employee is already linked
    existing_link = db.query(models.User).filter(
        models.User.employee_id == employee_id
    ).first()
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with id {employee_id} is already linked to another user"
        )
    
    # Link user to employee
    user.employee_id = employee_id
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User successfully linked to employee",
        "user_id": user_id,
        "employee_id": employee_id
    }