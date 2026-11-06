import shutil
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from backend_service import AuthService, StorageService


router = APIRouter(
    prefix="/storage",
    tags=["Almacenamiento"]
)

# Definimos la ruta base del backend
BASE_DIR = Path.cwd() / "app_backend"

auth_service = AuthService(BASE_DIR)
storage_service = StorageService(BASE_DIR)


@router.post("/upload/{username}", tags=["Almacenamiento"])
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