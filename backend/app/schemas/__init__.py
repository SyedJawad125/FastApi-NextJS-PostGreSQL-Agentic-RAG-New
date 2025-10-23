# # user schemas
# from .user import (
#     UserBase,
#     UserCreate,
#     LoginRequest,
#     UserUpdate,
#     UserOut,
#     Token,
#     TokenData,
#     TokenResponse
# )
# # employee schemas
# from .employee import (
#     Employee,
#     EmployeeCreate,
#     PaginatedEmployees,
#     EmployeeListResponse,
#     EmployeeUpdate
# )
# from .permission import (
#     PermissionBase,
#     PermissionCreate,
#     PermissionUpdate,
#     Permission,
#     PaginatedPermissions,
#     PermissionListResponse
# )
# from .role import (
#     RoleBase,
#     RoleCreate,
#     RoleUpdate,
#     Role,
#     PaginatedRoles,
#     RoleListResponse
# )
# from .image_category import (
#     ImageCategoryBase,
#     ImageCategoryCreate,
#     ImageCategoryUpdate,
#     PaginatedImageCategory,
#     ImageCategoryListResponse
# )       
# from .image import (
#     ImageBase,
#     ImageCreate,    
#     ImageUpdate,
#     ImageOut,
# )
# from app.schemas.rag_schemas import (
#     RAGQuery,
#     RAGResponse,
#     MultiAgentQuery,
#     MultiAgentResponse,
#     GraphQuery,
#     GraphQueryResponse,
#     DocumentUpload,
#     DocumentResponse,
#     DocumentList,
#     HealthCheck,
#     SystemStats
# )

# # define what will be exported on `from schemas import *`
# __all__ = [
#     'UserBase', 'UserCreate', 'LoginRequest', 'UserUpdate', 'UserOut',
#     'Token', 'TokenData', 'TokenResponse',
#     'Employee', 'EmployeeCreate','PaginatedEmployees','EmployeeListResponse','EmployeeUpdate',
#     'PermissionBase', 'PermissionCreate' ,'PermissionUpdate','Permission', 'PaginatedPermissions', 'PermissionListResponse',
#     'RoleBase', 'RoleCreate', 'RoleUpdate', 'Role', 'PaginatedRoles', 'RoleListResponse',
#     'ImageCategoryBase', 'ImageCategoryCreate', 'ImageCategoryUpdate', 'PaginatedImageCategory', 'ImageCategoryListResponse',
#     'ImageBase', 'ImageCreate', 'ImageUpdate', 'ImageOut', 
#     "RAGQuery",
#     "RAGResponse",
#     "MultiAgentQuery",
#     "MultiAgentResponse",
#     "GraphQuery",
#     "GraphQueryResponse",
#     "DocumentUpload",
#     "DocumentResponse",
#     "DocumentList",
#     "HealthCheck",
#     "SystemStats"
# ]




# app/schemas/__init__.py
# user schemas
from .user import (
    UserBase,
    UserCreate,
    LoginRequest,
    UserUpdate,
    UserOut,
    Token,
    TokenData,
    TokenResponse
)
# employee schemas
from .employee import (
    Employee,
    EmployeeCreate,
    PaginatedEmployees,
    EmployeeListResponse,
    EmployeeUpdate
)
from .permission import (
    PermissionBase,
    PermissionCreate,
    PermissionUpdate,
    Permission,
    PaginatedPermissions,
    PermissionListResponse
)
from .role import (
    RoleBase,
    RoleCreate,
    RoleUpdate,
    Role,
    PaginatedRoles,
    RoleListResponse
)
from .image_category import (
    ImageCategoryBase,
    ImageCategoryCreate,
    ImageCategoryUpdate,
    PaginatedImageCategory,
    ImageCategoryListResponse
)       
from .image import (
    ImageBase,
    ImageCreate,    
    ImageUpdate,
    ImageOut,
)
from app.schemas.rag_schemas import (
    RAGQuery,
    RAGQueryResponse,
    MultiAgentQuery,
    MultiAgentResponse,
    GraphQuery,
    GraphQueryResponse,
    DocumentUpload,
    DocumentUploadResponse,  # Add this
    DocumentResponse,
    DocumentList,
    HealthCheck,
    SystemStats
)

# define what will be exported on `from schemas import *`
__all__ = [
    'UserBase', 'UserCreate', 'LoginRequest', 'UserUpdate', 'UserOut',
    'Token', 'TokenData', 'TokenResponse',
    'Employee', 'EmployeeCreate','PaginatedEmployees','EmployeeListResponse','EmployeeUpdate',
    'PermissionBase', 'PermissionCreate' ,'PermissionUpdate','Permission', 'PaginatedPermissions', 'PermissionListResponse',
    'RoleBase', 'RoleCreate', 'RoleUpdate', 'Role', 'PaginatedRoles', 'RoleListResponse',
    'ImageCategoryBase', 'ImageCategoryCreate', 'ImageCategoryUpdate', 'PaginatedImageCategory', 'ImageCategoryListResponse',
    'ImageBase', 'ImageCreate', 'ImageUpdate', 'ImageOut', 
    "RAGQuery",
    "RAGQueryResponse",
    "MultiAgentQuery",
    "MultiAgentResponse",
    "GraphQuery",
    "GraphQueryResponse",
    "DocumentUpload",
    "DocumentUploadResponse",  # Add this
    "DocumentResponse",
    "DocumentList",
    "HealthCheck",
    "SystemStats"
]