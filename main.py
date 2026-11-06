#import hashlib
import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status

# Importamos los servicios nativos que construiste en el Paso 1
from backend_service import AuthService, StorageService


from endpoints.system_audi import router as system_audit_router
from endpoints.authentication import router as authentication_router
from endpoints.files import router as file_router

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
app.include_router(authentication_router, prefix="/api/v1", tags=["Autenticación"])


# -------------------------------------------------------------
# 3. ENDPOINTS DE ALMACENAMIENTO Y ARCHIVOS
# -------------------------------------------------------------
app.include_router(file_router, prefix="/api/v1", tags=["Almacenamiento"])