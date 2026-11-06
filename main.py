#import hashlib
import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status

# Importamos los servicios nativos que construiste en el Paso 1
from backend_service import AuthService, StorageService

# Importamos los esquemas de Pydantic
from schemas import UserLogin, UserRegister, UserResponse

from endpoints.system_audi import router as system_audit_router

app = FastAPI(
    title="Bridge API - Servidor Backend",
    description="API que conecta operaciones del sistema de archivos, seguridad y auditoría con FastAPI.",
    version="1.0.0"
)

# Definimos la ruta base del backend
BASE_DIR = Path.cwd() / "app_backend"

# Instanciamos nuestros servicios nativos
auth_service = AuthService(BASE_DIR)
storage_service = StorageService(BASE_DIR)


# -------------------------------------------------------------
# 1. ENDPOINTS DE AUDITORÍA Y SISTEMA
# -------------------------------------------------------------
app.include_router(system_audit_router, prefix="/api/v1", tags=["Sistema"])


# -------------------------------------------------------------
# 2. ENDPOINTS DE AUTENTICACIÓN
# -------------------------------------------------------------
@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Autenticación"])
def register(user_data: UserRegister):
    """Registra un nuevo usuario aplicando hashing SHA-256 a su contraseña."""
    success = auth_service.register_user(user_data.username, user_data.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario '{user_data.username}' ya está registrado."
        )
    return {"username": user_data.username, "registered": True}


@app.post("/api/v1/auth/login", tags=["Autenticación"])
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


# -------------------------------------------------------------
# 3. ENDPOINTS DE ALMACENAMIENTO Y ARCHIVOS
# -------------------------------------------------------------
@app.post("/api/v1/storage/upload/{username}", tags=["Almacenamiento"])
def upload_file(username: str, file: UploadFile = File(...)):  # noqa: B008
    """Recibe un archivo por HTTP, lo guarda en el disco del servidor con pathlib/shutil y calcula su checksum SHA-256."""
    
    # Ruta temporal para procesar la carga
    temp_dir = BASE_DIR / "temp"
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / file.filename

    # Guardar el flujo de bytes en el disco usando pathlib
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Delegar la persistencia y firma digital al StorageService
    destination = storage_service.upload_document(temp_file_path, username)

    # Limpiar archivo temporal
    if temp_file_path.exists():
        temp_file_path.unlink()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo procesar y firmar el archivo."
        )

    return {
        "filename": file.filename,
        "saved_location": str(destination),
        "status": "Archivado y firmado con éxito"
    }