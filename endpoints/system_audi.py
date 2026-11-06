from fastapi import APIRouter
from backend_service import SystemAuditService

router = APIRouter(
    prefix="/system",
    responses={404: {"description": "Not found"}},
)


@router.get("/telemetry", summary="Obtener telemetría del sistema", description="Retorna la telemetría del sistema operativo y ejecuta diagnósticos con subprocess.", tags=["Sistema"])
def read_telemetry():
    """Retorna la telemetría del sistema operativo y ejecuta diagnósticos con subprocess."""
    return SystemAuditService.get_telemetry()


