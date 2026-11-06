from pathlib import Path
from fastapi import APIRouter, status, HTTPException
from backend_service import AuthService, StorageService
from schemas import UserRegister, UserResponse, UserLogin


router = APIRouter(
    prefix="/authentication", 
    tags=["Autenticacion"]
)

# Definimos la ruta base del backend
BASE_DIR = Path.cwd() / "app_backend"

# Instanciamos nuestros servicios nativos
auth_service = AuthService(BASE_DIR)
storage_service = StorageService(BASE_DIR)



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Autenticación"])
def register(user_data: UserRegister):
    """Registra un nuevo usuario aplicando hashing SHA-256 a su contraseña."""
    success = auth_service.register_user(user_data.username, user_data.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario '{user_data.username}' ya está registrado."
        )
    return {"username": user_data.username, "registered": True}

@router.post("/login", tags=["Autenticación"])
def login(credentials: UserLogin):
    """Valida si el usuario y la contraseña coinciden con las credenciales hasheadas."""
    # Aquí llamamos al método login_user que implementaste en el Paso 1
    is_valid = auth_service.login_user(credentials.username, credentials.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas."
        )
    return {"message": "Inicio de sesión exitoso", "username": credentials.username}