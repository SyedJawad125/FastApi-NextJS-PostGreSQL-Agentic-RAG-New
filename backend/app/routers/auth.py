# from fastapi import APIRouter, Depends, status, HTTPException
# from fastapi.security.oauth2 import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from passlib.context import CryptContext

# from .. import database, schemas, models, oauth2

# router = APIRouter(tags=['Authentication'])

# # Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Password verification functions
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify a plain password against a hashed password"""
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     """Hash a password"""
#     return pwd_context.hash(password)

# def get_user_password_field(user):
#     """Get the password field from user object, trying different possible field names"""
#     if hasattr(user, 'password'):
#         return user.password
#     elif hasattr(user, 'hashed_password'):
#         return user.hashed_password
#     elif hasattr(user, 'password_hash'):
#         return user.password_hash
#     elif hasattr(user, 'encrypted_password'):
#         return user.encrypted_password
#     else:
#         # If no password field found, check all string attributes
#         for attr_name in dir(user):
#             if not attr_name.startswith('_') and not callable(getattr(user, attr_name)):
#                 attr_value = getattr(user, attr_name)
#                 if isinstance(attr_value, str) and len(attr_value) > 10:  # Likely a hash
#                     return attr_value
#         return None

# # JSON login model
# class JSONLoginRequest(BaseModel):
#     email: str
#     password: str

# # Debug endpoint to check user model structure
# @router.get('/debug/user-fields')
# def debug_user_fields(db: Session = Depends(database.get_db)):
#     """Debug endpoint to check User model structure"""
#     user = db.query(models.User).first()
    
#     if not user:
#         return {"message": "No users found in database"}
    
#     # Get all attributes of the user object
#     user_attrs = [attr for attr in dir(user) if not attr.startswith('_') and not callable(getattr(user, attr))]
    
#     # Check for password fields
#     password_fields = []
#     for attr in user_attrs:
#         attr_value = getattr(user, attr)
#         if isinstance(attr_value, str) and len(attr_value) > 10:
#             password_fields.append({
#                 "field_name": attr,
#                 "value_preview": attr_value[:20] + "..." if len(attr_value) > 20 else attr_value,
#                 "length": len(attr_value)
#             })
    
#     return {
#         "user_exists": True,
#         "user_id": getattr(user, 'id', 'NOT_FOUND'),
#         "user_email": getattr(user, 'email', 'NOT_FOUND'),
#         "all_attributes": user_attrs,
#         "possible_password_fields": password_fields,
#         "has_password_attr": hasattr(user, 'password'),
#         "password_value": getattr(user, 'password', 'NOT_FOUND')
#     }

# @router.post('/login-json', response_model=schemas.TokenResponse)
# def login_json(
#     user_credentials: JSONLoginRequest,
#     db: Session = Depends(database.get_db)
# ):
#     # Find user by email
#     user = db.query(models.User).filter(
#         models.User.email == user_credentials.email).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, 
#             detail="Invalid Credentials"
#         )

#     # Get the password field dynamically
#     hashed_password = get_user_password_field(user)
    
#     if not hashed_password:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Could not find password field in User model"
#         )

#     # Verify password using our local function
#     if not verify_password(user_credentials.password, hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, 
#             detail="Invalid Credentials"
#         )

#     # Create both access and refresh tokens
#     access_token = oauth2.create_access_token(data={"user_id": user.id})
#     refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }

# # Original OAuth2 form login (updated to use local function)
# @router.post('/login', response_model=schemas.TokenResponse)
# def login(
#     user_credentials: OAuth2PasswordRequestForm = Depends(), 
#     db: Session = Depends(database.get_db)
# ):
#     # OAuth2 uses 'username' field instead of 'email'
#     user = db.query(models.User).filter(
#         models.User.email == user_credentials.username).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, 
#             detail="Invalid Credentials"
#         )

#     # Get the password field dynamically
#     hashed_password = get_user_password_field(user)
    
#     if not hashed_password:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Could not find password field in User model"
#         )

#     if not verify_password(user_credentials.password, hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, 
#             detail="Invalid Credentials"
#         )

#     access_token = oauth2.create_access_token(data={"user_id": user.id})
#     refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }

# @router.post('/refresh', response_model=schemas.TokenResponse)
# def refresh_token(refresh_token: str, db: Session = Depends(database.get_db)):
#     # Verify the refresh token
#     payload = oauth2.verify_refresh_token(refresh_token)
    
#     # Get user from payload
#     user_id = payload.get("user_id")
#     if not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token"
#         )
    
#     # Verify user still exists
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User no longer exists"
#         )
    
#     # Create new tokens
#     access_token = oauth2.create_access_token(data={"user_id": user.id})
#     new_refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})
    
#     return {
#         "access_token": access_token,
#         "refresh_token": new_refresh_token,
#         "token_type": "bearer"
#     }

# @router.post('/logout')
# def logout(current_user: models.User = Depends(oauth2.get_current_user)):
#     return {"message": "Successfully logged out"}

# # Registration endpoint with flexible field handling
# @router.post('/register', response_model=dict)
# def register(
#     user_data: JSONLoginRequest,
#     db: Session = Depends(database.get_db)
# ):
#     # Check if user already exists
#     existing_user = db.query(models.User).filter(
#         models.User.email == user_data.email).first()
    
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="User already exists"
#         )
    
#     # Hash password
#     hashed_password = get_password_hash(user_data.password)
    
#     # Create user - try different field names
#     user_kwargs = {"email": user_data.email}
    
#     # Try to determine the correct password field name
#     sample_user = models.User()
#     if hasattr(sample_user, 'password'):
#         user_kwargs["password"] = hashed_password
#     elif hasattr(sample_user, 'hashed_password'):
#         user_kwargs["hashed_password"] = hashed_password
#     elif hasattr(sample_user, 'password_hash'):
#         user_kwargs["password_hash"] = hashed_password
#     else:
#         # Default to 'password'
#         user_kwargs["password"] = hashed_password
    
#     user = models.User(**user_kwargs)
    
#     db.add(user)
#     db.commit()
#     db.refresh(user)
    
#     return {
#         "id": user.id,
#         "email": user.email,
#         "message": "User created successfully"
#     }




from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.TokenResponse)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # Create both access and refresh tokens
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post('/refresh', response_model=schemas.TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(database.get_db)):
    # Verify the refresh token
    payload = oauth2.verify_refresh_token(refresh_token)
    
    # Get user from payload
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user still exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )
    
    # Create new tokens
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    new_refresh_token = oauth2.create_refresh_token(data={"user_id": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post('/logout')
def logout(current_user: models.User = Depends(oauth2.get_current_user)):
    # In a real implementation, you would add the token to a blacklist
    # This could be done using Redis or a database table
    return {"message": "Successfully logged out"}